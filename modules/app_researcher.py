import requests
from bs4 import BeautifulSoup
import html2text
import re
import os
import streamlit as st
from modules import app_constants
import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import spacy
from duckduckgo_search import DDGS
from modules import common_utils
from modules import app_logger
nlp = spacy.load("en_core_web_sm")

# Use the logger from app_config
app_logger = app_logger.app_logger

TMP_DIRECTORY = app_constants.WORKSPACE_DIRECTORY + 'tmp'
DEFAULT_SEARCH_COUNT = app_constants.DEFAULT_SEARCH_COUNT

def download_and_clean(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style", "img", "a"]):
            script.extract()

        body_text = soup.get_text()
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True
        h.ignore_tables = True
        clean_text = h.handle(body_text)
        clean_text = re.sub(r'[^\w\s\n<>/\.]+', '', clean_text)  # Include '.' in the allowed characters
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

    except requests.exceptions.RequestException as e:
        app_logger.error(f"Error while downloading and cleaning URL {url}: {str(e)}")
        st.error("Error while downloading and cleaning URL: " + str(e))
        return None

def save_notes_to_file(topic, note, source_url):
    # Process the text
    doc = nlp(note)

    # Ensure the temp directory exists
    if not os.path.exists(TMP_DIRECTORY):
        os.makedirs(TMP_DIRECTORY)

    # Sanitize the filename and create the full path
    sanitized_filename = common_utils.sanitize_filename(topic)+'.jsonl'
    full_path = os.path.join(TMP_DIRECTORY, sanitized_filename)

    # Initialize variables for accumulating sentences
    text_block = ""
    word_count = 0

    # Append each sentence to form a text block and write it to the file
    with open(full_path, 'a') as file:
        for sent in doc.sents:
            sentence_word_count = len(sent.text.split())
            if word_count + sentence_word_count > 240:  # If adding the sentence exceeds the max limit
                # Write the current text block to the file
                if word_count >= 120:  # Ensure the text block meets the minimum word count
                    data = {
                        "note": text_block,
                        "source_url": source_url
                    }
                    file.write(json.dumps(data) + '\n')
                # Reset text block and word count
                text_block = sent.text
                word_count = sentence_word_count
            else:
                # Add the sentence to the text block
                text_block += ' ' + sent.text if text_block else sent.text
                word_count += sentence_word_count

        # Write any remaining text block to the file if it meets the minimum word count
        if word_count >= 300:
            data = {
                "note": text_block,
                "source_url": source_url
            }
            file.write(json.dumps(data) + '\n')

    app_logger.info(f"Notes saved to file {full_path}")
    return full_path


def url_list_downloader(url_list, topic):
    notes_file = None
    for url in url_list:
        try:
            text = download_and_clean(url)
            if text:
                notes_file = save_notes_to_file(topic, text, url)
        except Exception as e:
            app_logger.error(f"Error during processing for URL {url}: {e}")
    return notes_file

def search_term_ddg(topic,count=DEFAULT_SEARCH_COUNT):
    try:
        llm = ChatOpenAI(
            model_name=app_constants.MODEL_NAME,
            openai_api_key=app_constants.openai_api_key,
            base_url=app_constants.local_model_uri,
            streaming=True
        )
        prompt = [
            SystemMessage(content="Generate 5 plain keywords in comma separated based on user input. For example ['word 1','word 2','word 3','word 4','word 5']"),
            HumanMessage(content=topic),
        ]
        response = llm(prompt)
        # Extract string content from the response object
        if hasattr(response, 'content'):
            search_keywords = response.content
        else:
            raise ValueError("Invalid response format")
        
        # Splitting and trimming the keywords
        search_keywords = [keyword.strip() for keyword in search_keywords.split(',')]
        print(search_keywords)
        # Limiting keywords to a maximum of 8
        search_keywords = search_keywords[:8]

        urls = []
        # Initialize DDGS with a timeout
        with DDGS(timeout=3) as ddgs:
            for term in search_keywords:
                # Fetch results for each search term
                results = ddgs.text(f"{topic} {term}", max_results=count)
                for result in results:
                    url = result['href']
                    if not url.endswith(('.pdf', '.ppt', '.pptx', '.doc', '.docx')):
                        urls.append(url)
        return sorted(set(urls))

    except Exception as e:
        app_logger.error(f"An error occurred while searching for topic {topic}: {e}")
        return []

def explore_url_on_internet(topic, count=DEFAULT_SEARCH_COUNT):
    app_logger.info(f"Starting research on topic {topic}")
    # Sanitize the filename and create the full path
    sanitized_filename = common_utils.sanitize_filename(topic)+'.jsonl'
    full_path = os.path.join(TMP_DIRECTORY, sanitized_filename)

    # Check if the file already exists
    if os.path.exists(full_path):
        st.write("File already exists skipping download: ",full_path)
        note_file = full_path
    else:
        url_list = search_term_ddg(topic,count)
        note_file = url_list_downloader(url_list, topic)
    st.write(f"Research on Internet completed for {topic} here is your file", note_file)
    app_logger.info(f"Research on Internet completed for {topic}, file: {note_file}")
    return note_file

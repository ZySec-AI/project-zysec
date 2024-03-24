
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.chains import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.prompts import PromptTemplate
from modules import app_page_definitions, app_logger,app_constants,file_utils

# Use the logger from app_config
app_logger = app_logger.app_logger

# Configurable batch size (4 pages per batch)
batch_size = app_constants.SUMMARIZER_BATCH
WORKSPACE_DIRECTORY = app_constants.WORKSPACE_DIRECTORY


def process_file(file_path, file_type):
    if file_type == "text/plain":
        loader = TextLoader(file_path)
    elif file_type == "application/pdf":
        loader = PyPDFLoader(file_path)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        loader = UnstructuredWordDocumentLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    app_logger.info(f"Processing file {file_path} of type {file_type}")
    return loader.load_and_split()

def app():
    app_logger.info("Starting Streamlit app - Summarizer Tool page")

    # Fetch page configuration from app_page_definitions
    page_config = app_page_definitions.PAGE_CONFIG.get("nav_summarize")

    st.title(page_config["title"])
    st.caption(page_config["caption"])
    st.session_state.current_page = "nav_summarize"

    uploaded_file = st.file_uploader("Upload your document here:", type=['txt', 'pdf', 'docx'], key="file_uploader")

    if uploaded_file is not None:
        file_path = file_utils.save_uploaded_file(uploaded_file,uploads_path=WORKSPACE_DIRECTORY + "/tmp")
        docs = process_file(file_path, uploaded_file.type)

        total_docs = len(docs)
        app_logger.info(f"Total documents processed: {total_docs}")

        if total_docs > 1:
            doc_range = st.slider("Select document range for summarization", 1, total_docs, (1, total_docs))
        else:
            doc_range = (1, 1)

        progress_bar = st.progress(0)

        if st.button("Summarize"):
            with st.spinner('Processing... Please wait'):
                llm = ChatOpenAI(
                    model_name=app_constants.MODEL_NAME,
                    openai_api_key=app_constants.openai_api_key,
                    base_url=app_constants.model_uri,
                    streaming=True
                )

                prompt_template = """Write a concise summary of the following:
                {text}
                CONCISE SUMMARY:"""
                prompt = PromptTemplate.from_template(prompt_template)

                refine_template = (
                    "You are a content writer and your job is to produce a summary of input\n"
                    "We have provided an existing summary up to a certain point: {existing_answer}\n"
                    "Start and end properly and refine the existing summary "
                    "with some more context below.\n"
                    "------------\n"
                    "{text}\n"
                    "------------\n"
                    "Given the new context, refine the original summary. "
                    "If the context isn't useful, return the original summary."
                )
                refine_prompt = PromptTemplate.from_template(refine_template)

                chain = load_summarize_chain(
                    llm=llm,
                    chain_type="refine",
                    question_prompt=prompt,
                    refine_prompt=refine_prompt,
                    return_intermediate_steps=True,
                    input_key="input_documents",
                    output_key="output_text",
                )

                start_doc, end_doc = doc_range
                for i in range(start_doc - 1, min(end_doc, total_docs), batch_size):
                    batch_docs = docs[i:min(i + batch_size, total_docs)]

                    progress_value = (i + len(batch_docs)) / total_docs
                    progress_bar.progress(progress_value)

                    with st.expander(f"Processing Documents {i + 1} - {i + len(batch_docs)}", expanded=False):
                        intermediate_summary = chain.invoke({"input_documents": batch_docs}, return_only_outputs=True)
                        st.write(intermediate_summary)

                selected_docs = docs[start_doc - 1:end_doc]
                final_summary_response = chain.invoke({"input_documents": selected_docs}, return_only_outputs=True)
                final_summary = final_summary_response['output_text'] if 'output_text' in final_summary_response else "No summary generated."
                st.text_area("Final Summary", final_summary, height=300)

                st.success("Summarization Completed!")
            progress_bar.empty()
    else:
        st.warning("Please upload a document to summarize.")
        app_logger.warning("No document uploaded for summarization")
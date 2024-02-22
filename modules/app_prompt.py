# app_combined_prompt.py
import modules.app_constants as app_constants  # Ensure this is correctly referenced
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from openai import OpenAI
from modules import app_logger, common_utils, app_st_session_utils

# Use the logger from app_config
app_logger = app_logger.app_logger

# Define a function to query the language model
def query_llm(prompt, page="nav_private_ai", retriever=None, message_store=None, use_retrieval_chain=False, last_page=None, username=""):
    try:
        # Choose the language model client based on the use_retrieval_chain flag
        if use_retrieval_chain:
            app_logger.info("Using ChatOpenAI with RetrievalQAWithSourcesChain")
            llm = ChatOpenAI(
                model_name=app_constants.MODEL_NAME,
                openai_api_key=app_constants.openai_api_key,
                base_url=app_constants.local_model_uri,
                streaming=True
            )
            qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,
                chain_type=app_constants.RAG_TECHNIQUE,
                retriever=retriever,
                return_source_documents=False
            )
        else:
            app_logger.info("Using direct OpenAI API call")
            llm = OpenAI(
                base_url=app_constants.local_model_uri,
                api_key=app_constants.openai_api_key
            )

        # Update page messages if there's a change in the page
        if last_page != page:
            app_logger.info(f"Updating messages for new page: {page}")
            common_utils.get_system_role(page, message_store)

        # Construct messages to send to the LLM, excluding timestamps
        messages_to_send = common_utils.construct_messages_to_send(page, message_store, prompt)
        app_logger.debug(messages_to_send)
        # Sending the messages to the LLM and retrieving the response
        response = None
        if use_retrieval_chain:
            response = qa.invoke(prompt)
        else:
            response = llm.chat.completions.create(
                model=app_constants.MODEL_NAME,
                messages=messages_to_send
            )

        # Process the response
        raw_msg = response.get('answer') if use_retrieval_chain else response.choices[0].message.content
        source_info = response.get('sources', '').strip() if use_retrieval_chain else ''
        formatted_msg = app_st_session_utils.format_response(raw_msg + "Source: " + source_info if source_info else raw_msg)

        return formatted_msg

    except Exception as e:
        error_message = f"An error occurred while querying the language model: {e}"
        app_logger.error(error_message)
        return error_message

import streamlit as st
from modules import app_logger, app_page_definitions, app_prompt, app_constants, app_st_session_utils,common_utils,file_utils
import time
# Use the logger from app_config
app_logger = app_logger.app_logger

def app(message_store, current_page="nav_private_ai", use_retrieval_chain=False):
    app_logger.info(f"Starting Streamlit app - {current_page}")

    # Fetch page configuration from app_page_definitions
    page_config = app_page_definitions.PAGE_CONFIG.get(current_page, app_page_definitions.PAGE_CONFIG["default"])
    files_indexed = file_utils.get_indexed_files_for_page(current_page)
    # Use configurations for title, caption, and greeting from page_config
    st.title(page_config["title"])
    st.caption(page_config["caption"])

    # Initialize or update session state variables
    app_st_session_utils.initialize_session_state('current_page', current_page)
    app_st_session_utils.initialize_session_state('page_loaded', False)
    app_st_session_utils.initialize_session_state('message_store', message_store)
    db_retriever_playbooks = False
    if use_retrieval_chain:
        db_retriever_playbooks = True
        # Initialize or retrieve the database
        persistent_db = app_constants.LOCAL_PERSISTANT_DB + current_page + '_chroma_db'
        db_retriever_playbooks = app_st_session_utils.initialize_or_retrieve_db(persistent_db)

    message_store = st.session_state['message_store']

    # Manage message history
    app_st_session_utils.manage_message_history(current_page)
    greeting_message = common_utils.get_page_greeting(st.session_state['current_page'], st.session_state.get('username', ''),files_indexed)
    st.chat_message("assistant").markdown(greeting_message, unsafe_allow_html=True)

    # Display chat messages
    for message in st.session_state.get("messages", []):
        app_st_session_utils.display_chat_message(message["role"], message["content"])

    # Handle user prompt
    prompt = st.chat_input("Let's talk! Enter your query below.")
    if prompt:
        st.chat_message("user").write(prompt)
        app_logger.info(f"Processed user prompt: {prompt}")
        start_time = time.time()
        with st.spinner("Processing request..."):
            if use_retrieval_chain:
                if db_retriever_playbooks:
                    formatted_response = app_prompt.query_llm(prompt,page=current_page, retriever=db_retriever_playbooks.as_retriever(search_type="similarity", search_kwargs={"k": app_constants.RAG_K}), message_store=message_store, use_retrieval_chain=use_retrieval_chain)
                    app_st_session_utils.display_chat_message("assistant", formatted_response)  # Updated line
                    app_st_session_utils.add_message_to_session("user", prompt)
                    app_st_session_utils.add_message_to_session("assistant", formatted_response)           
                else:
                    st.error("Unable to initialize the database. Please try again later.")
            else:
                formatted_response = app_prompt.query_llm(prompt,page=current_page, message_store=message_store, retriever=False)
                app_st_session_utils.display_chat_message("assistant", formatted_response)  # Updated line
                app_st_session_utils.add_message_to_session("user", prompt)
                app_st_session_utils.add_message_to_session("assistant", formatted_response)
        end_time = time.time()  # End timing
        processing_time = end_time - start_time  # Calculate processing time
        st.info(f"Processing time: {processing_time:.2f} seconds")  # Log processing time

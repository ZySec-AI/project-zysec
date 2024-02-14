# nav_talk_to_docs.py
import streamlit as st
from modules import app_logger, app_page_definitions, common_utils, app_to_vectorstore, app_prompt, app_st_session_utils

# Use the logger from app_config
app_logger = app_logger.app_logger

def app(message_store, current_page="nav_playbooks"):
    # Fetch page configuration from app_constants
    page_config = app_page_definitions.PAGE_CONFIG.get(current_page, app_page_definitions.PAGE_CONFIG["nav_playbooks"])

    persistent_db = page_config["persistent_db"]
    app_logger.info(f"Starting Streamlit app - {current_page}")

    # Use configurations for title and caption
    st.title(page_config["title"])
    st.caption(page_config["caption"])

    # Initialize or update session state variables
    app_st_session_utils.initialize_session_state('current_page', current_page)
    app_st_session_utils.initialize_session_state('page_loaded', False)
    app_st_session_utils.initialize_session_state('message_store', message_store)

    app_logger.info(f"Initialized session state variables for {current_page}")

  # File uploader
    uploaded_files = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt', 'html'], accept_multiple_files=True)

    # Check if any files were uploaded
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_size = uploaded_file.size / (1024 * 1024)  # Size in MB
            if file_size > 10:
                st.warning(f"The file {uploaded_file.name} exceeds the 10MB limit. Please upload a smaller file.")
            else:
                # Process each file here
                with st.spinner(f"Indexing {uploaded_file.name}..."):
                    file_path = common_utils.save_uploaded_file(uploaded_file)
                    if not common_utils.is_file_processed(file_path):
                        app_logger.info(f"Processing new file: {uploaded_file.name}")
                        db, status = app_to_vectorstore.get_chroma_index(file_path)
                        app_logger.info(f"File processed: {uploaded_file.name} to {db}. Status: {status}")
                    else:
                        app_logger.info(f"File already processed: {uploaded_file.name}")
                        st.info(f"File '{uploaded_file.name}' has already been processed.")

    # Initialize or retrieve the database
    db_retriever = app_st_session_utils.initialize_or_retrieve_db(persistent_db)

    message_store = st.session_state['message_store']
    username = st.session_state.get('username', '')

    # Manage message history
    app_st_session_utils.manage_message_history(current_page)

    # Display page greeting message
    if not st.session_state['page_loaded']:
        app_st_session_utils.display_page_greeting(page_config["greeting"], username)
        st.session_state['page_loaded'] = True

    # Display chat messages
    for message in st.session_state.get("messages", []):
        app_st_session_utils.display_chat_message(message["role"], message["content"])

    # Handle user prompt
    prompt = st.chat_input(page_config["greeting"])
    if prompt:
        st.chat_message("user").write(prompt)
        with st.spinner("Processing request..."):
            if db_retriever:
                formatted_response = app_prompt.query_llm(prompt, retriever=db_retriever(search_type="similarity", search_kwargs={"k": 5}), message_store=message_store, use_retrieval_chain=True)
                st.chat_message("assistant").markdown(formatted_response, unsafe_allow_html=True)
                app_st_session_utils.add_message_to_session("user", prompt)
                app_st_session_utils.add_message_to_session("assistant", formatted_response)
                app_logger.info(f"Processed user prompt: {prompt}")
            else:
                st.error("Unable to initialize the database. Please try again later.")

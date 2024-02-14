import streamlit as st
from modules import app_logger, app_page_definitions, common_utils, app_to_vectorstore, app_prompt, app_constants, app_st_session_utils

# Use the logger from app_config
app_logger = app_logger.app_logger

def app(message_store, current_page="nav_playbooks",use_retrieval_chain=True):
    app_logger.info(f"Starting Streamlit app - {current_page}")

    # Fetch page configuration from app_page_definitions
    page_config = app_page_definitions.PAGE_CONFIG.get(current_page, app_page_definitions.PAGE_CONFIG["default"])

    # Use configurations for title, caption, and greeting from page_config
    st.title(page_config["title"])
    st.caption(page_config["caption"])

    # Initialize or update session state variables
    app_st_session_utils.initialize_session_state('current_page', current_page)
    app_st_session_utils.initialize_session_state('page_loaded', False)
    app_st_session_utils.initialize_session_state('message_store', message_store)

    # Use the persistent database path from page_config, or default to LOCAL_PERSISTANT_DB
    persistent_db = page_config.get("persistent_db", app_constants.LOCAL_PERSISTANT_DB)
    persistent_db = app_constants.LOCAL_PERSISTANT_DB+current_page+'_chroma_db'

    with st.expander("Upload Documents"):
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt', 'html'])
        if uploaded_file is not None:
            with st.spinner("Indexing your file..."):
                file_path = common_utils.save_uploaded_file(uploaded_file)
                if not common_utils.is_file_processed(file_path):
                    app_logger.info(f"Processing new file: {uploaded_file.name}")
                    db, status = app_to_vectorstore.get_chroma_index(file_path,current_page=current_page)
                    app_logger.info(f"File processed: {uploaded_file.name} to {db}. Status: {status}")
                else:
                    app_logger.info(f"File already processed: {uploaded_file.name}")
                    st.info(f"File '{uploaded_file.name}' has already been processed.")

    # Initialize or retrieve the database
    db_retriever_playbooks = app_st_session_utils.initialize_or_retrieve_db(persistent_db)

    message_store = st.session_state['message_store']
    username = st.session_state.get('username', '')

    # Manage message history
    app_st_session_utils.manage_message_history(current_page)

    # Display page greeting message
    if not st.session_state['page_loaded']:
        app_st_session_utils.display_page_greeting(st.session_state['current_page'], username)
        st.session_state['page_loaded'] = True

    # Display chat messages
    for message in st.session_state.get("messages", []):
        app_st_session_utils.display_chat_message(message["role"], message["content"])

    # Handle user prompt
    prompt = st.chat_input("Let's talk! Upload your playbooks or docs using expander option above.")
    if prompt:
        st.chat_message("user").write(prompt)
        with st.spinner("Processing request..."):
            if db_retriever_playbooks:
                formatted_response = app_prompt.query_llm(prompt, retriever=db_retriever_playbooks.as_retriever(search_type="similarity", search_kwargs={"k": app_constants.RAG_K}), message_store=message_store,use_retrieval_chain=use_retrieval_chain)
                st.chat_message("assistant").markdown(formatted_response, unsafe_allow_html=True)
                app_st_session_utils.add_message_to_session("user", prompt)
                app_st_session_utils.add_message_to_session("assistant", formatted_response)
                app_logger.info(f"Processed user prompt: {prompt}")
            else:
                st.error("Unable to initialize the database. Please try again later.")

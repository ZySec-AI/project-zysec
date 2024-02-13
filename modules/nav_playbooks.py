import streamlit as st
from modules import app_logger, common_utils, app_to_vectorstore,app_prompt, app_constants, app_st_session_utils


# Use the logger from app_config
app_logger = app_logger.app_logger
persistant_db = app_constants.LOCAL_PERSISTANT_DB

def app(message_store):
    app_logger.info("Starting Streamlit app - Playbook page")
    st.title("🔍 Your Playbooks")
    current_page = "nav_playbook"

    # Initialize or update session state variables
    app_st_session_utils.initialize_session_state('current_page', current_page)
    app_st_session_utils.initialize_session_state('page_loaded', False)
    app_st_session_utils.initialize_session_state('message_store', message_store)

    app_logger.info("Initialized session state variables for Playbook page")

    st.caption("🎯 Use ZySec 7B Model AI to find specific answers in playbooks or documents by uploading them below.")
    with st.expander("Upload Playbooks or documents"):
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt', 'html'])
        if uploaded_file is not None:
            file_path = common_utils.save_uploaded_file(uploaded_file)
            if not common_utils.is_file_processed(file_path):
                app_logger.info(f"Processing new file: {uploaded_file.name}")
                db, status = app_to_vectorstore.get_chroma_index(file_path)
                app_logger.info(f"File processed: {uploaded_file.name} to {db}. Status: {status}")
            else:
                app_logger.info(f"File already processed: {uploaded_file.name}")
                st.info(f"File '{uploaded_file.name}' has already been processed.")

    # Initialize or retrieve the database
    db_retriever = app_st_session_utils.initialize_or_retrieve_db(persistant_db)

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
        with st.spinner("Processing your request..."):
            if db_retriever:
                formatted_response = app_prompt.query_llm(prompt, retriever=db_retriever, message_store=message_store)
                st.chat_message("assistant").markdown(formatted_response, unsafe_allow_html=True)
                app_st_session_utils.add_message_to_session("user", prompt)
                app_st_session_utils.add_message_to_session("assistant", formatted_response)
                app_logger.info(f"Processed user prompt: {prompt}")
            else:
                st.error("Unable to initialize the database. Please try again later.")

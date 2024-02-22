import streamlit as st
from modules import app_prompt, app_researcher, app_logger, database_utils, app_to_vectorstore, app_page_definitions
from . import common_utils
from . import app_st_session_utils,app_constants  # Importing the session utilities module

# Use the logger from app_config
app_logger = app_logger.app_logger

def app(message_store):
    app_logger.info("Navigating to nav_researcher page")

    # Fetch page configuration from app_page_definitions
    current_page = "nav_researcher"
    page_config = app_page_definitions.PAGE_CONFIG.get(current_page)

    st.title(page_config["title"])

    # Initialize or update session state variables using session utilities
    app_st_session_utils.initialize_session_state('current_page', current_page)
    app_st_session_utils.initialize_session_state('page_loaded', False)
    app_st_session_utils.initialize_session_state('message_store', message_store)

    st.caption(page_config["caption"])

    topic = st.text_input("Enter Topic for Research", "Threat Management")
    research_button = st.button("Go Research on Internet")

    if research_button and topic:
        with st.spinner('Searching...'):
            try:
                research_notes = app_researcher.explore_url_on_internet(topic, count=app_constants.SEARCH_COUNT)
                app_to_vectorstore.get_chroma_index(research_notes, is_persistent=False)
                app_logger.info("Internet research completed successfully")
                st.success("Internet research completed")
                st.session_state['research_done'] = True
            except Exception as e:
                app_logger.error(f"Error during internet research: {e}")
                st.error(f"Error during internet research: {e}")

    TEMP_DIR = app_constants.WORKSPACE_DIRECTORY + "tmp"
    db_files = database_utils.get_chroma_db_files(TEMP_DIR)
    
    # Create a mapping of formatted names to actual file names
    formatted_db_names = [database_utils.format_db_name(db) for db in db_files]
    name_to_file_map = dict(zip(formatted_db_names, db_files))

    # Display formatted names in the dropdown and use the selection to get the actual file name
    selected_db_formatted = st.selectbox("Pick Researched topic from drop-down and start chatting!", formatted_db_names)
    selected_db_actual = name_to_file_map[selected_db_formatted]
    research_notes = TEMP_DIR + '/' + selected_db_actual

    # Initialize or retrieve the database using the new function
    db_retriever = app_st_session_utils.initialize_or_retrieve_db(research_notes)

    app_st_session_utils.manage_message_history(current_page)
    
    greeting_message = common_utils.get_page_greeting(st.session_state['current_page'], st.session_state.get('username', ''))
    st.chat_message("assistant").markdown(greeting_message, unsafe_allow_html=True)
    app_st_session_utils.update_session_state('page_loaded', True)


    # Displaying chat messages
    for message in st.session_state.get("messages", []):
        app_st_session_utils.display_chat_message(message["role"], message["content"])

    # Handling user prompt
    prompt = st.chat_input("Let's Talk! Conversation secure and private!")
    if prompt:
        st.chat_message("user").write(prompt)
        with st.spinner("Processing your request..."):
            if db_retriever:
                formatted_response = app_prompt.query_llm(prompt,page=current_page, retriever=db_retriever.as_retriever(search_type="similarity", search_kwargs={"k": app_constants.RAG_K}), message_store=st.session_state['message_store'],use_retrieval_chain=True)
                st.chat_message("assistant").markdown(formatted_response, unsafe_allow_html=True)
                app_st_session_utils.add_message_to_session("user", prompt)
                app_st_session_utils.add_message_to_session("assistant", formatted_response)
                app_logger.info(f"Processed user prompt: {prompt}")
            else:
                st.error("Unable to initialize the database. Please try again later.")

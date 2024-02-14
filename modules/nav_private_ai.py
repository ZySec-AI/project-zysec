import streamlit as st
from . import app_prompt, app_st_session_utils
from modules import app_logger
# Use the logger from app_config
app_logger = app_logger.app_logger

def app(message_store):
    app_logger.info("Starting Streamlit app - Private AI page")
    st.title("🤖 Private AI")
    current_page = "nav_private_ai" 

    # Initialize or update session state variables
    app_st_session_utils.initialize_session_state('current_page', current_page)
    app_st_session_utils.initialize_session_state('page_loaded', False)
    app_st_session_utils.initialize_session_state('message_store', message_store)

    app_logger.info("Initialized session state variables for Private AI page")

    st.caption("🔒 AttackIO App's ZySec 7B Model, expert in cybersecurity domain crafted for helping security experts with privacy!")
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
    prompt = st.chat_input("Let's Talk! Conversation secure and private!")
    if prompt:
        st.chat_message("user").write(prompt)
        with st.spinner("Processing your request..."):
            formatted_response = app_prompt.query_llm(prompt, message_store=message_store,retriever=False)
            st.chat_message("assistant").markdown(formatted_response, unsafe_allow_html=True)
            app_st_session_utils.add_message_to_session("user", prompt)
            app_st_session_utils.add_message_to_session("assistant", formatted_response)
            app_logger.info(f"Processed user prompt: {prompt}")

import streamlit as st
from streamlit_option_menu import option_menu
# Import your page modules
from modules import nav_about, nav_private_ai, nav_query_docs, nav_researcher, nav_summarizer 
from modules import app_constants, app_logger, common_utils
from modules.message_store import MessageStore

app_logger = app_logger.app_logger
WORKSPACE_DIRECTORY = app_constants.WORKSPACE_DIRECTORY

# Page configuration
st.set_page_config(page_title="ZySec AI", page_icon=":sparkles:", layout="wide")

# Initialize MessageStore in the session state
if 'message_store' not in st.session_state:
    st.session_state['message_store'] = MessageStore()
def request_username():
    st.title("Welcome to ZySec AI")
    app_logger.info("App started")
    username = st.text_input("How do you want me to call you?",value="Security Ninja" ,placeholder="Enter your name")
    submit_button = st.button('Submit')

    if submit_button and username:
        st.session_state['username'] = username
        return True  # Indicates that a username was submitted
    return False

def main():
    common_utils.setup_initial_folders()
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    if 'username' not in st.session_state or not st.session_state['username']:
        if request_username():
            st.rerun()
        return

    # Sidebar navigation
    with st.sidebar:
        selected = option_menu(
            "ZySec AI", 
            ["Private AI", "Playbooks", "Standards", "Policies", "Summarizer", "Researcher", "About"], 
            icons=["shield-lock", "book-half", "file-earmark-ruled", "journal-bookmark", "file-text", "search", "info-circle"], 
            default_index=0, 
            menu_icon="cast", 
            styles={}
        )
    st.markdown("---")


    try:
        message_store = st.session_state['message_store']


        if selected == "Private AI":
            nav_private_ai.app(message_store)
        elif selected == "Playbooks":
            nav_query_docs.app(message_store)
        elif selected == "Standards":
            nav_query_docs.app(message_store,current_page="nav_standards")
        elif selected == "Policies":
            nav_query_docs.app(message_store,current_page="nav_policies")
        elif selected == "Researcher":
            nav_researcher.app(message_store)
        elif selected == "Summarizer":
            nav_summarizer.app()
        elif selected == "About":
            nav_about.app()
        else:
            pass

    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
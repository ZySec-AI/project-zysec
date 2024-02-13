import streamlit as st
from modules import app_logger, app_prompt
import streamlit.components.v1 as components
from modules import database_utils,common_utils
import datetime

# Use the logger from app_config
app_logger = app_logger.app_logger
def initialize_session_state(key, default_value):
    """
    Initialize a session state variable with a default value if it doesn't exist.

    Args:
    key (str): The key of the session state variable.
    default_value (Any): The default value to initialize the session state variable with.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value

def update_session_state(key, value):
    """Update a session state variable."""
    st.session_state[key] = value

def setup_page_session_state(current_page):
    initialize_session_state('current_page', current_page)
    initialize_session_state('page_loaded', False)
    initialize_session_state('message_store', app_prompt.MessageStore())

def log_session_info(message):
    """Log session-related information."""
    try:
        app_logger.info(message)
    except Exception as e:
        print(f"Logging error: {e}")

def display_page_greeting(page_key, username):
    """Display a greeting message for a specific page."""
    try:
        greeting_message = common_utils.page_greetings(page_key, username)
        st.chat_message("assistant").markdown(greeting_message, unsafe_allow_html=True)
        log_session_info("Displayed greeting message")
    except Exception as e:
        log_session_info(f"Error displaying greeting message: {e}")

def manage_message_history(current_page):
    """Manage the history of messages for the current page."""
    try:
        message_store = st.session_state['message_store']
        if st.session_state['current_page'] != current_page:
            message_store.set_history(st.session_state['current_page'], st.session_state["messages"])
            st.session_state["messages"] = message_store.get_history(current_page)
            st.session_state['current_page'] = current_page
            log_session_info(f"Updated message history for page: {current_page}")
    except Exception as e:
        log_session_info(f"Error managing message history: {e}")

def display_chat_message(role, content):
    """Display a chat message based on the role."""
    if role in ['user', 'assistant']:
        st.chat_message(role).write(content)
    else:
        log_session_info(f"Invalid role '{role}' in display_chat_message")

def reset_session_state():
    """Reset the session state to its initial values."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Reinitialize variables if necessary here

def get_session_data(key, default=None):
    """Retrieve data stored in the session state."""
    return st.session_state.get(key, default)

def reload_page():
    js = "window.location.reload();"
    components.html(f"<script>{js}</script>", height=0, width=0)

def initialize_or_retrieve_db(db_path):
    """
    Initialize the database if not already initialized or if the database path has changed.
    Retrieve the database from the session state if already initialized.

    Args:
    db_path (str): The file path to the database.

    Returns:
    The initialized or retrieved database object.
    """
    print("initializing db", db_path)
    if 'db_retriever' not in st.session_state or st.session_state['db_path'] != db_path:
        # Database not initialized or path has changed
        db_retriever = database_utils.initialize_chroma_db(db_path)
        if db_retriever is not None:
            st.session_state['db_retriever'] = db_retriever
            st.session_state['db_path'] = db_path
            app_logger.info(f"Database initialized at {db_path}")
        else:
            app_logger.error(f"Failed to initialize database at {db_path}")
            return None
    return st.session_state['db_retriever']

# Function to format the response
def format_response(response):
    return response.replace('\r\n', '\n').replace('\r', '\n').strip()

# Add a message to the session state
def add_message_to_session(role, content, add_to_history=True):
    timestamp = datetime.datetime.now()
    message = {"role": role, "content": content, "timestamp": timestamp}
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if add_to_history and role in ["user", "assistant"]:
        st.session_state["messages"].append(message)
        # Update message_store with the new message
        if 'message_store' in st.session_state:
            current_page = st.session_state.get('current_page', 'default_page')
            st.session_state['message_store'].update_message(current_page, 'history', message)


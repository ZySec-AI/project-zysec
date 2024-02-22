import os
from modules import app_constants,app_page_definitions
from modules import app_logger
# Use the logger from app_config
app_logger = app_logger.app_logger
work_dir = app_constants.WORKSPACE_DIRECTORY

def get_system_role(page, message_store):
    system_role = app_page_definitions.PAGE_CONFIG.get(page, {}).get("system_role", "Default system role message")
    message_store.update_message(page, "system", system_role)

def get_page_greeting(page_key, username="", files_indexed=[]):
    """Return a greeting message for a specific page, including a list of indexed files."""
    try:
        # Define the default greeting
        default_greeting = "Hello! How can I assist you today?"
        # Fetch the greeting from page configuration or use the default
        greeting = app_page_definitions.PAGE_CONFIG.get(page_key, {}).get("greeting", default_greeting)

        # Personalize greeting if username is provided
        if username:
            greeting = greeting.replace("Hello", f"Hello {username}")

        # Format the indexed files into a list
        if files_indexed:
            files_list = "\n".join([f"{i+1}. {file}" for i, file in enumerate(files_indexed)])
            additional_message = f"I'm familiar with the following documents:\n{files_list}"
            # Append the file list to the greeting message
            greeting = f"{greeting}\n\n{additional_message}"

        return greeting
    except Exception as e:
        # Handle any exceptions and return a default error message
        return f"Error generating greeting message: {e}"

def setup_initial_folders():
    docs_path = os.path.join(work_dir, "docs")
    db_path = os.path.join(work_dir, "db")
    tmp_path = os.path.join(work_dir, "tmp")
    os.makedirs(docs_path, exist_ok=True)
    os.makedirs(db_path, exist_ok=True)
    os.makedirs(tmp_path, exist_ok=True)

def construct_messages_to_send(page, message_store, prompt):
    """
    Construct a list of messages to send to the language model.

    Args:
    page (str): The current page identifier.
    message_store (MessageStore): The message store instance containing message histories.
    prompt (str): The current user prompt.

    Returns:
    List[Dict[str, str]]: A list of messages structured for the language model.
    """
    messages_to_send = []

    # Retrieve the system and greeting messages if available
    system_message_content = message_store.get_message(page, "system")
    greeting_message_content = message_store.get_message(page, "greeting")
    if system_message_content:
        messages_to_send.append({"role": "system", "content": system_message_content})
    if greeting_message_content:
        messages_to_send.append({"role": "assistant", "content": greeting_message_content})

    # Include recent user and assistant messages from the message history
    history_messages = message_store.get_history(page)

    # Check if there are enough messages in the history, if not, adjust the slicing
    num_messages_to_include = 4  # Include last two pairs (user and assistant)
    if len(history_messages) < num_messages_to_include:
        num_messages_to_include = len(history_messages)

    recent_history = history_messages[-num_messages_to_include:]
    for msg in recent_history:
        messages_to_send.append({"role": msg["role"], "content": msg["content"]})

    # Append the current user prompt
    messages_to_send.append({"role": "user", "content": prompt})

    return messages_to_send


def get_content_mapping_to_module(content_type):
    content_type_lower = content_type.lower()
    # Iterate through each page in PAGE_CONFIG
    for page, config in app_page_definitions.PAGE_CONFIG.items():
        # Check if 'content' key exists
        if 'content' in config:
            # Convert all content types in the list to lowercase for comparison
            content_list_lower = [ct.lower() for ct in config['content']]
            # Check if content_type_lower is in the list
            if content_type_lower in content_list_lower:
                return page
    # Default return if no match is found
    return "nav_playbooks"

import hashlib
import re
import json
import os
from modules import app_constants,app_page_definitions
from modules import app_logger, app_st_session_utils
import subprocess
# Use the logger from app_config
app_logger = app_logger.app_logger
processed_files_record = os.path.join(app_constants.WORKSPACE_DIRECTORY, app_constants.VECTORSTORE_PROCESSED_RECORDS)
work_dir = app_constants.WORKSPACE_DIRECTORY

def compute_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        app_logger.error(f"Error computing MD5 for {file_path}: {e}")
        return None

def sanitize_filename(filename):
    """Sanitize the filename by removing or replacing invalid characters."""
    filename = filename.lower().replace(' ', '_')
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def is_file_processed(file_md5):
    try:
        if os.path.exists(processed_files_record):
            with open(processed_files_record, 'r') as file:
                records = json.load(file)
            return file_md5 in records
        else:
            return False
    except Exception as e:
        app_logger.error(f"Error checking processed files record: {e}")
        return False

def delete_files(work_dir=work_dir):
    for root, dirs, files in os.walk(work_dir, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                os.unlink(file_path)
                app_logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                app_logger.error(f"Failed to delete {file_path}. Reason: {e}")

        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                os.rmdir(dir_path)
                app_logger.info(f"Deleted directory: {dir_path}")
            except Exception as e:
                app_logger.error(f"Failed to delete {dir_path}. Reason: {e}")

def save_uploaded_file(uploaded_file, uploads_path=work_dir+'docs'):
    file_path = os.path.join(uploads_path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    app_logger.info(f"File '{uploaded_file.name}' uploaded to {uploads_path}")
    return file_path

def manage_model_control(command):
    """
    Manage the model control based on the given command, utilizing session utilities.

    Args:
    command (str): A command that can be 'start', 'stop', or 'reload'.
    """
    server_process_key = 'server_process'
    server_running_key = 'server_running'

    if command == 'start':
        if not app_st_session_utils.get_session_data(server_running_key, False):
            # Start the model
            cmd = ["python3", "-m", "llama_cpp.server", "--model", "./models/Attackio/ZySec-7b_q8_0.gguf", "--n_batch", "4", "--n_ctx", "8196", "--n_batch", "200", "--n_gpu_layers", "50", "--chat_format", "zephyr"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            app_st_session_utils.update_session_state(server_process_key, process)
            app_st_session_utils.update_session_state(server_running_key, True)

    elif command == 'stop':
        if app_st_session_utils.get_session_data(server_running_key, False):
            # Stop the model
            process = app_st_session_utils.get_session_data(server_process_key)
            if process is not None:
                process.kill()
                app_st_session_utils.update_session_state(server_process_key, None)
            app_st_session_utils.update_session_state(server_running_key, False)

    elif command == 'reload':
        # Reload the model (stop and start)
        manage_model_control('stop')
        manage_model_control('start')

def get_system_role(page, message_store):
    system_role = app_page_definitions.PAGE_CONFIG.get(page, {}).get("system_role", "Default system role message")
    message_store.update_message(page, "system", system_role)

def page_greetings(page, username=""):
    default_greeting = "Hello! How can I assist you today?"
    greeting = app_page_definitions.PAGE_CONFIG.get(page, {}).get("greeting", default_greeting)
    if username:
        greeting = greeting.replace("Hello", f"Hello {username}")
    return greeting


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



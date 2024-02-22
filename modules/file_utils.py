#file utils.py
import os
from modules import app_constants, app_to_vectorstore,app_page_definitions,common_utils
from modules import app_logger
import json
import requests
import hashlib
import re, csv

# Use the logger from app_config
app_logger = app_logger.app_logger
work_dir = app_constants.WORKSPACE_DIRECTORY
system_content_file = metadata_path=app_constants.SYSTEM_CONTENT_DATA

def download_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        sanitized_filename = sanitize_filename(url.split('/')[-1])
        sanitized_local_path = os.path.join(app_constants.WORKSPACE_DIRECTORY+"/docs/", sanitized_filename)
        with open(sanitized_local_path, 'wb') as f:
            f.write(response.content)
        app_logger.info(f"File downloaded successfully: {sanitized_local_path}")
        return True
    except Exception as e:
        app_logger.error(f"Failed to download file from {url}. Error: {e}")
        return False

def index_file(local_path, module):
    try:
        status = app_to_vectorstore.get_chroma_index(local_path,module,True)
        app_logger.info(f"File indexed successfully: {local_path}")
    except Exception as e:
        app_logger.error(f"Failed to index file. Error: {e}")
        db.persist()
        db = None
    return status
    
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
    """Sanitize the filename by removing or replacing invalid characters and handling URLs."""

    # Extract filename from URL or file path
    filename = os.path.basename(filename)

    # Make the filename lowercase and replace spaces with underscores
    sanitized = filename.lower().replace(' ', '_')

    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^\w\-_\.]', '_', sanitized)

    # Shorten the filename if it's too long
    max_length = 255  # Max length can be adjusted
    if len(sanitized) > max_length:
        # Keep the file extension if present
        file_parts = os.path.splitext(sanitized)
        ext = file_parts[1]
        sanitized = sanitized[:max_length - len(ext)] + ext
    return sanitized

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
    remove_local_uploads()

def save_uploaded_file(uploaded_file, uploads_path, sanitized_filename=None):
    if sanitized_filename is None:
        sanitized_filename = sanitize_filename(uploaded_file.name)
    file_path = os.path.join(uploads_path, sanitized_filename)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    app_logger.info(f"File '{sanitized_filename}' uploaded to {uploads_path}")
    return file_path

def perform_file_operation(resource, operation):
    url = resource.get("url", "")
    content_type = resource.get("content_type", "")
    file_name = work_dir+"docs/" +sanitize_filename(url)
    if operation == "download":
        #print(file_name)
        if url:
            download_success = download_file(url)
            if download_success:
                app_logger.info(f"File {resource['name']} downloaded successfully.")
            else:
                app_logger.error(f"Failed to download file {resource['name']}.")
    elif operation == "learn":
        module = common_utils.get_content_mapping_to_module(content_type)
        # Handle 'learn' operation here if needed
        index_file(file_name, module)
    else:
        app_logger.error(f"Unknown operation: {operation}")


def get_indexed_files_for_page(page_id):
    try:
        filtered_files = []

        # Open and read the CSV file
        with open(os.path.join(work_dir, app_constants.PROCESSED_DOCS), mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                # Check if the second item in the row matches the page_id
                if len(row) > 2 and row[1].lower() == page_id.lower():
                    # Extract just the file name from the full path (third item in the row)
                    file_name = os.path.basename(row[2])
                    filtered_files.append(file_name)

        return filtered_files
    except Exception as e:
        return []

def update_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def load_json_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)
    
def handle_content_update(uploaded_file=None, manual_name="", manual_url="", selected_content_type=""):
    system_content_file = app_constants.SYSTEM_CONTENT_DATA  # Define before use
    uploads_directory = os.path.join(work_dir, "docs")  # Define before use
    file_data = load_json_data(system_content_file)

    if uploaded_file:
        filename = sanitize_filename(uploaded_file.name if uploaded_file else manual_name) 
        file_path = save_file(uploaded_file, filename, uploads_directory)
    else:
        filename = sanitize_filename(manual_url)
        file_path = save_file(uploaded_file, filename, uploads_directory) if uploaded_file else manual_url

    new_entry = {"name": filename, "url": file_path, "content_type": selected_content_type}
    file_data.append(new_entry)
    update_json_file(file_data, system_content_file)

def save_file(uploaded_file, filename, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, filename)
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return file_path

def remove_local_uploads(file_path=app_constants.SYSTEM_CONTENT_DATA):
    # Read the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)
    # Filter out entries where the 'url' points to a local file
    filtered_data = [entry for entry in data if not entry['url'].startswith('./')]
    # Write the filtered data back to the file
    with open(file_path, 'w') as file:
        json.dump(filtered_data, file, indent=4)
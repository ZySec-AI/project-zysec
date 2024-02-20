#file utils.py
import os
from modules import app_constants,common_utils, app_to_vectorstore
from modules import app_logger
import json
import requests
import hashlib
import re

# Use the logger from app_config
app_logger = app_logger.app_logger
work_dir = app_constants.WORKSPACE_DIRECTORY
processed_files_record = os.path.join(app_constants.WORKSPACE_DIRECTORY, app_constants.VECTORSTORE_PROCESSED_RECORDS)
system_content_file = metadata_path=app_constants.SYSTEM_CONTENT_DATA

def list_huggingface_models():
    models_dir = './models'
    models = []
    if not os.path.exists(models_dir):
        app_logger.warning(f"Directory not found: {models_dir}")
        return models

    for orgname in os.listdir(models_dir):
        org_path = os.path.join(models_dir, orgname)
        if os.path.isdir(org_path):
            for item in os.listdir(org_path):
                item_path = os.path.join(org_path, item)
                if os.path.isdir(item_path) or os.path.isfile(item_path):
                    models.append(f"{orgname}/{item}")

    return models

def download_file(url, local_path, metadata_path=system_content_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
        #print(url,local_path,metadata_path)
        # Extract and sanitize the filename from the URL
        sanitized_filename = sanitize_filename(url.split('/')[-1])
        sanitized_local_path = os.path.join(os.path.dirname(local_path), sanitized_filename)
        #print(sanitized_local_path)
        with open(sanitized_local_path, 'wb') as f:
            f.write(response.content)
        app_logger.info(f"File downloaded successfully: {sanitized_local_path}")

        # Update download status in metadata
        update_file_status_in_metadata(sanitized_local_path, 'downloaded_status', True, metadata_path)
        return True
    except Exception as e:
        app_logger.error(f"Failed to download file from {url}. Error: {e}")
        return False

def save_file_metadata(metadata, metadata_path=system_content_file):
    try:
        with open(metadata_path, 'w') as file:
            json.dump(metadata, file, indent=4)
        app_logger.info(f"Metadata saved successfully: {metadata_path}")
    except Exception as e:
        app_logger.error(f"Failed to save metadata. Error: {e}")

def load_file_metadata(metadata_path=system_content_file):
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as file:
                return json.load(file)
        else:
            return {}
    except Exception as e:
        app_logger.error(f"Failed to load metadata. Error: {e}")
        return {}

def index_file(local_path, module):
    # Implement the indexing logic here
    # For example, it could involve parsing the PDF and extracting relevant data
    # Return True if indexing is successful, False otherwise
    try:
        db,status = app_to_vectorstore.get_chroma_index(local_path,module,True)
        update_file_status_in_metadata(local_path, 'indexed_status', True, app_constants.SYSTEM_CONTENT_DATA)
        app_logger.info(f"File indexed successfully: {local_path}")
        return True
    except Exception as e:
        app_logger.error(f"Failed to index file. Error: {e}")
        return False
    
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

def save_uploaded_file(uploaded_file, uploads_path, sanitized_filename=None):
    if sanitized_filename is None:
        sanitized_filename = sanitize_filename(uploaded_file.name)
    file_path = os.path.join(uploads_path, sanitized_filename)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    app_logger.info(f"File '{sanitized_filename}' uploaded to {uploads_path}")
    return file_path

def update_file_status_in_metadata(file_path, status_key, status_value, metadata_path=app_constants.SYSTEM_CONTENT_DATA):
    metadata = load_file_metadata(metadata_path)
    for file in metadata:
        if file['local_path'] == file_path:
            file[status_key] = status_value
            save_file_metadata(metadata, metadata_path)
            break

def delete_specific_file(file_name, metadata_path=system_content_file):
    try:
        file_path = os.path.join(work_dir, 'docs', file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            app_logger.info(f"File '{file_name}' deleted successfully.")

            # Update metadata
            update_file_status_in_metadata(file_path, 'downloaded_status', False, metadata_path)
            update_file_status_in_metadata(file_path, 'indexed_status', False, metadata_path)
        else:
            app_logger.warning(f"File '{file_name}' not found.")
    except Exception as e:
        app_logger.error(f"Error deleting file '{file_name}'. Error: {e}")

def update_file_statuses(file_data):
    status_updated = False
    for file_entry in file_data:
        # Extract the sanitized filename from the local_path
        sanitized_filename = os.path.basename(file_entry["local_path"])
        # Construct the file path using the sanitized filename
        file_path = os.path.join(work_dir, 'docs', sanitized_filename)
        file_exists = os.path.exists(file_path)

        if file_exists != file_entry.get("downloaded_status", False):
            file_entry["downloaded_status"] = file_exists
            status_updated = True

    if status_updated:
        save_file_metadata(file_data)

#operation not used now, but will use in future.
def perform_file_operation(filename, operation):
    # Load the JSON file data
    try:
        with open(app_constants.SYSTEM_CONTENT_DATA, 'r') as file:
            file_data = json.load(file)
    except Exception as e:
        print(f"Error loading file data: {e}")
        return
    # Find the file with the matching filename and perform the operation
    for file_entry in file_data:
        if file_entry.get("local_path") == filename:
                current_page = common_utils.get_content_mapping_to_module(file_entry.get('content_type'))
                index_file(filename,current_page)
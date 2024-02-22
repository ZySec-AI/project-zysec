
#app_to_vectorstore.py

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from modules import common_utils,file_utils
from modules import app_logger
# Assuming all necessary loader classes are imported

from modules import app_constants

app_logger = app_logger.app_logger

TEMP_DIR = app_constants.WORKSPACE_DIRECTORY + "tmp"
DB_DIR = app_constants.WORKSPACE_DIRECTORY + "db"

processed_files_record = os.path.join(app_constants.WORKSPACE_DIRECTORY, app_constants.PROCESSED_DOCS)

def load_documents_from_jsonl(file_path, loader_class):
    try:
        loader = loader_class(file_path, json_lines=True, text_content=False, jq_schema='.')
        return loader.load()
    except Exception as e:
        app_logger.error(f"Error loading documents from JSONL file {file_path}: {e}")
        return None

def update_processed_files_record(file_md5,module, file_path):
    try:
        with open(processed_files_record, 'a') as file:  # 'a' mode will create the file if it doesn't exist
            file.write(f"{file_md5},{module},{file_path}\n")
    except Exception as e:
        app_logger.error(f"Error updating processed files record: {e}")

def is_file_processed(file_md5):
    if os.path.exists(processed_files_record):
        with open(processed_files_record, 'r') as file:
            for line in file:
                md5, _ = line.strip().split(',', 1)
                if md5 == file_md5:
                    return True
    return False

def get_chroma_index(file_path, current_page="nav_playbooks", is_persistent=True):
    app_logger.info(f"Starting get_chroma_index for {file_path}")
    file_md5 = file_utils.compute_md5(file_path)
    if is_file_processed(file_md5):
        app_logger.info(f"File {file_path} has already been processed. Skipping.")
        db = None
        return False
    
    _, file_extension = os.path.splitext(file_path)
    loader_class = app_constants.DOCUMENT_MAP.get(file_extension.lower(), None)

    if not loader_class:
        app_logger.error(f"No suitable loader found for file type {file_extension}")
        return None, False

    embedding_model = app_constants.EMBEDDING_MODEL_NAME
    chunk_size = app_constants.CHUNK_SIZE
    chunk_overlap = app_constants.CHUNK_OVERLAP

    storage_dir = DB_DIR if is_persistent else TEMP_DIR

    base_filename = f"{current_page}_chroma_db" if is_persistent else f"{os.path.splitext(os.path.basename(file_path))[0]}_chroma_db"
    sanitized_base_filename = file_utils.sanitize_filename(base_filename)
    chroma_persist_directory = os.path.join(storage_dir, sanitized_base_filename)


    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    try:
        if file_extension.lower() == '.jsonl':
            documents = load_documents_from_jsonl(file_path, loader_class)
        else:
            loader = loader_class(file_path)
            documents = loader.load()

        if not documents:
            app_logger.error(f"No documents loaded from {file_path}.")
            db = None
            return False

        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)

        if not docs:
            app_logger.error(f"No documents to process after splitting from {file_path}.")
            db = None
            return False

        db = Chroma.from_documents(docs, embeddings, persist_directory=chroma_persist_directory, client_settings=app_constants.CHROMA_SETTINGS)
        update_processed_files_record(file_md5,current_page, file_path)
        app_logger.info("Created index and saved to disk")
        db.persist()
    except Exception as e:
        app_logger.error(f"Error in get_chroma_index for {file_path}: {e}")
        db = None
        return False
    app_logger.info("Completed get_chroma_index operation")
    db = None
    return True
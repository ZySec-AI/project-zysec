# database_utils.py
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from modules import app_constants, app_logger

DB_DIR = "./workspace/db/local_chroma_db"


def initialize_chroma_db(file_path):
    if not os.path.exists(file_path):
        app_logger.error(f"Chroma database not found at {file_path}")
        return None
    embeddings = HuggingFaceEmbeddings(model_name=app_constants.EMBEDDING_MODEL_NAME)
    db = Chroma(persist_directory=file_path, embedding_function=embeddings,client_settings=app_constants.CHROMA_SETTINGS)
    retriever = db.as_retriever()
    return retriever


def get_chroma_db_files(directory):
    """Retrieve files ending with 'chroma_db' from the given directory."""
    return [f for f in os.listdir(directory) if f.endswith('chroma_db')]

def format_db_name(db_name):
    """Format the database name to a more readable form."""
    return db_name.replace('_', ' ').replace('chroma db', '').title().strip()
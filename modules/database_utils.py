# database_utils.py
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from modules import app_constants, app_logger

app_logger = app_logger.app_logger

DB_DIR = "./workspace/db/local_chroma_db"


def initialize_chroma_db(file_path):
    """
    Initializes or creates a new Chroma database.

    :param file_path: Path to the Chroma database file
    :return: A retriever object if initialization is successful, None otherwise
    """
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=app_constants.EMBEDDING_MODEL_NAME)

    # Initialize Chroma database
    try:
        if os.path.exists(file_path):
            app_logger.info(f"Using existing Chroma database at {file_path}.")
        else:
            app_logger.info(f"Chroma database not found at {file_path}. Creating a new one.")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        db = Chroma(persist_directory=file_path, embedding_function=embeddings, client_settings=app_constants.CHROMA_SETTINGS)
    except Exception as e:
        app_logger.error(f"Failed to initialize Chroma database at {file_path}. Reason: {e}")
        return None

    # Create a retriever from the Chroma database
    #retriever = db.as_retriever()
    return db



def get_chroma_db_files(directory):
    """Retrieve files ending with 'chroma_db' from the given directory."""
    return [f for f in os.listdir(directory) if f.endswith('chroma_db')]

def format_db_name(db_name):
    """Format the database name to a more readable form."""
    return db_name.replace('_', ' ').replace('chroma db', '').title().strip()
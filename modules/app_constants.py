import os
from langchain_community.document_loaders import (CSVLoader, TextLoader, UnstructuredExcelLoader, Docx2txtLoader,
                                                   UnstructuredFileLoader, UnstructuredMarkdownLoader, UnstructuredHTMLLoader, JSONLoader)
from chromadb.config import Settings

from modules import app_logger

app_logger = app_logger.app_logger
# Use shared_variable in this module
openai_api_key = os.environ.get("OPENAI_API_KEY", "NONE")

# Set default values if environment variables are not found
#mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
local_model_uri = os.environ.get("LOCAL_OPENAI_URI", "http://localhost:8000/v1")
#local_model_uri = os.environ.get("LOCAL_OPENAI_URI", None)
DOCUMENT_MAP = {
    ".html": UnstructuredHTMLLoader,
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
    ".py": TextLoader,
    ".json": JSONLoader,
    ".jsonl": JSONLoader,
    ".pdf": UnstructuredFileLoader,
    ".csv": CSVLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
}
MODELS_PATH = "./models"
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
MODEL_NAME = 'gpt-3.5-turbo'
# Constants
WORKSPACE_DIRECTORY = './workspace/'


CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)
INGEST_THREADS = os.cpu_count() or 8

CHUNK_SIZE = 880
CHUNK_OVERLAP = 200
VECTORSTORE_PROCESSED_RECORDS = 'processed_log.json'
SEARCH_COUNT = 5
MESSAGE_HISTORY = 4
RAG_K = 3
RAG_TECHNIQUE = 'refine'
SUMMARIZER_BATCH = 4
MAX_FILE_SIZE = 10
LOCAL_PERSISTANT_DB = WORKSPACE_DIRECTORY + "db/"
CONTENT_TYPE = ["Select Type","Policies", "Playbooks", "Standards", "Breaches", "Other"]
SYSTEM_CONTENT_DATA = "app-content.json"
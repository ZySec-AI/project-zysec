import os
import subprocess
import time
from huggingface_hub import hf_hub_download
from modules import app_constants
from modules import app_logger

# Use the logger from app_config
app_logger = app_logger.app_logger

def download_model(repo_id, filename):
    app_logger.info("Downloading model...")
    org_name = repo_id.split('/')[0]
    save_path = os.path.join('models', org_name, filename)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=os.path.dirname(save_path))
    app_logger.info(f"File downloaded and saved to {save_path}")

def check_and_download_model(repo_id, filename):
    org_name = repo_id.split('/')[0]
    model_path = os.path.join('models', org_name, filename)

    if not os.path.exists(model_path):
        app_logger.info(f"Model file {filename} not found. Downloading from Hugging Face...")
        download_model(repo_id, filename)
    else:
        app_logger.info(f"Model file {filename} already exists at {model_path}")

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

def run_model(model_path, run=True):
    process = None

    if run:
        cmd = ["python3", "-m", "llama_cpp.server", "--model", model_path,
               "--n_batch", "4", "--n_ctx", "8196", "--n_batch", "200",
               "--n_gpu_layers", "50", "--chat_format", "zephyr"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        app_logger.info("Model is running...")
    else:
        if process:
            process.kill()
            process = None
        app_logger.info("Model has been terminated.")

    if process:
        try:
            while True:
                output = process.stdout.readline()
                if output == '':
                    if process.poll() is not None:
                        break
                else:
                    app_logger.info(output.strip())
                time.sleep(0.1)
        finally:
            if process:
                process.kill()
    
    return process
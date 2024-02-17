#!/bin/bash

# Define the model directory and file name
model_dir="models/aihub-app"
model_file="ZySec-7B-v1.Q4_K_M.gguf"
model_path="$model_dir/$model_file"

# Check for curl dependency
if ! command -v curl &> /dev/null
then
    echo "curl could not be found, please install it."
    exit 1
fi

# Check if the directory exists and create it if it does not
if [ ! -d "$model_dir" ]; then
  echo "Directory $model_dir does not exist. Creating now."
  mkdir -p "$model_dir" && echo "Directory created." || { echo "Failed to create directory."; exit 1; }
fi

# Check if the model file already exists
if [ ! -f "$model_path" ]; then
  echo "Model file $model_file does not exist. Downloading now."

  # Navigate to the /models/aihub-app directory
  cd "$model_dir" || { echo "Failed to navigate to $model_dir"; exit 1; }

  # Download the file using curl
  curl -L -o "$model_file" "https://huggingface.co/aihub-app/ZySec-7B-v1-GGUF/resolve/main/$model_file?download=true" && echo "Download completed." || { echo "Failed to download model."; exit 1; }
else
  echo "Model file $model_file already exists. Skipping download."
fi

# Run the LLAMA.CPP server command
echo "Starting LLAMA.CPP server with $model_file..."
python3 -m llama_cpp.server --model "./$model_path" --n_batch 4 --n_ctx 8196 --n_batch 200 --verbose true --n_gpu_layers 50 --chat_format zephyr

#!/bin/bash

# Define model directory and file
model_dir="models/aihub-app"
model_file="ZySec-7B-v1.Q4_K_M.gguf"
model_path="$model_dir/$model_file"

# Function to handle SIGINT (Ctrl+C)
handle_sigint() {
  echo "SIGINT received, stopping the server and exiting..."
  kill $server_pid
  exit
}

# Trap SIGINT (Ctrl+C) and execute the handle_sigint function
trap handle_sigint SIGINT

# Step 2: Check for curl and download model file if it doesn't exist
if ! command -v curl &> /dev/null
then
    echo "curl could not be found, please install it."
    exit 1
fi

if [ ! -d "$model_dir" ]; then
    echo "Directory $model_dir does not exist. Creating now."
    mkdir -p "$model_dir" && echo "Directory created." || { echo "Failed to create directory."; exit 1; }
fi

if [ ! -f "$model_path" ]; then
    echo "Model file $model_file does not exist. Downloading now."
    cd "$model_dir" || { echo "Failed to navigate to $model_dir"; exit 1; }
    curl -L -o "$model_file" "https://huggingface.co/aihub-app/ZySec-7B-v1-GGUF/resolve/main/$model_file?download=true" && echo "Download completed." || { echo "Failed to download model."; exit 1; }
else
    echo "Model file $model_file already exists. Skipping download."
fi

# Function to start or restart the model server
start_model_server() {
    # Check if port 8000 is already in use
    if lsof -i:8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port 8000 is already in use. Assuming the model server is running."
        return
    fi

    echo "Starting model server..."
    python3 -m llama_cpp.server --model "./$model_path" --n_batch 4 --n_ctx 8196 --n_batch 200 --verbose true --n_gpu_layers 50 --chat_format zephyr &
    server_pid=$!
    wait $server_pid

    echo "Model server stopped. Exiting."
    exit 1
}

# Step 4: Start model server in the background
start_model_server &
wait

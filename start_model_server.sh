#!/bin/bash

set -e

# Define model directory and file

#ZySec-7B-v1.Q2_K.gguf - MISTRAL
#ZySec-7B-v1.Q4_K_M.gguf - MISTRAL
#ZySec-7B-v1.Q8_0.gguf - MISTRAL

#ZySec-7B-v2.Q2_K.gguf - GEMMA
#ZySec-7B-v2.Q4_K_M.gguf - GEMMA
#ZySec-7B-v2.Q8_0.gguf - GEMMA

model_dir="$PWD/models/ZySec-AI"
model_file="ZySec-7B-v1.Q2_K.gguf"
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
    curl -L -o "$model_file" "https://huggingface.co/ZySec-AI/ZySec-7B-GGUF/resolve/main/$model_file?download=true" && echo "Download completed." || { echo "Failed to download model."; exit 1; }
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
    python3 -m llama_cpp.server --model "$model_path" --n_batch 4 --n_ctx 8196 --n_batch 200 --verbose true --n_gpu_layers 50 --chat_format zephyr &
    server_pid=$!

    echo "Checking if model server is ready..."
    # Loop until curl command gets either 200 or 404 response
    MAX_ATTEMPTS=5
    attempt_num=1
    while : ; do
        echo "Attempt $attempt_num of $MAX_ATTEMPTS to check server health..."
        # Use curl to get the HTTP status code
        status_code=$(curl --write-out '%{http_code}' --silent --output /dev/null http://localhost:8000/health)

        # Check for 200 or 404 status code
        if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 404 ]; then
            echo "Model server is up and running (received status code: $status_code)."
            break
        else
            if [ $attempt_num -eq $MAX_ATTEMPTS ]; then
            echo "Model server failed to start or respond correctly after $MAX_ATTEMPTS attempts (last received status code: $status_code)."
            exit 1
        fi
        fi
       ((attempt_num++))
     sleep 5 # Wait for 5 seconds before retrying
    done
}

# Step 4: Start model server in the background
start_model_server &
wait

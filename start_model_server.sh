#!/bin/bash

# Define the model directory and file name
model_dir="models/aihub-app"
model_file="ZySec-7B-v1.Q2_K.gguf"
model_path="$model_dir/$model_file"

# Check if the directory exists and create it if it does not
if [ ! -d "$model_dir" ]; then
  echo "Directory $model_dir does not exist. Creating now."
  mkdir -p "$model_dir"
  echo "Directory created."
fi

# Check if the model file already exists
if [ ! -f "$model_path" ]; then
  echo "Model file $model_file does not exist. Downloading now."

  # Navigate to the /models/aihub-app directory
  cd "$model_dir"

  # Download the file using wget and specify the output filename
  wget -O "$model_file" "https://huggingface.co/aihub-app/ZySec-7B-v1-GGUF/resolve/main/$model_file?download=true"

  echo "Download completed."
else
  echo "Model file $model_file already exists. Skipping download."
fi

# Run the LLAMA.CPP server command
echo "Starting LLAMA.CPP server with $model_file..."
python3 -m llama_cpp.server --model "./$model_path" --n_batch 4 --n_ctx 8196 --n_batch 200 --verbose true --n_gpu_layers 50 --chat_format zephyr

#!/bin/bash

source "$PWD/config.cfg"

# set degub mode
if [ "$SCRIPT_DEBUG_MODE" = "on" ]; then
  echo "INFO: Debugging mode is enabled in config file, script will run in debug mode"
  set -x
else 
  set +x
fi

model_dir="$PWD/models/ZySec-AI"
model_path="$model_dir/$MODEL_FILE"
venv_path="$PWD/zysec"

# Create virtual environment
create_venv() {
    if [ ! -d "$venv_path" ]; then
        echo "INFO: Creating virtual environment 'ZySec'..."
        python3 -m venv "$venv_path" > /dev/null 2>&1
    fi
}

# Download model
download_model() {
    # Check for curl
    if ! command -v curl &> /dev/null; then
        echo "ERROR: curl could not be found, please install it."
        exit 1
    fi

    # Check if model directory exists, if not create it
    if [ ! -d "$model_dir" ]; then
        echo "INFO: Directory $model_dir does not exist. Creating now."
        mkdir -p "$model_dir" > /dev/null 2>&1 && echo "INFO: Directory created." || { echo "ERROR: Failed to create directory."; exit 1; }
    fi

    if [ ! -f "$model_path" ]; then
        echo "INFO: Model file $MODEL_FILE does not exist. Downloading now."
        cd "$model_dir" || { echo "ERROR: Failed to navigate to $model_dir"; exit 1; }
        if curl -L -o "$MODEL_FILE" "https://huggingface.co/ZySec-AI/ZySec-7B-GGUF/resolve/main/$MODEL_FILE?download=true"; then
            echo "INFO: Download completed."
        else
        echo "ERROR: Failed to download the model. Run the script in debug mode by setting SCRIPT_DEBUG_MODE=yes in the config.cfg"
        exit 1
        fi
    else
        echo "INFO: Model file $MODEL_FILE already exists. Skipping download."
    fi
}

check_api_server_connection() {
    local url=$1
    local key=$2
    local max_attempts=5
    local attempt_num=1

    if [[ ! "$url" =~ ^http(s)?://[^/]+ ]]; then
        echo "ERROR: The URL '$url' is not valid, please check the config file"
        return 1 
    fi

    local curl_error_file="/tmp/curl_error_$$.txt"
    
    echo "INFO: Checking if model server is ready..."

    while : ; do
        echo "INFO: Attempt $attempt_num of $max_attempts to check server"

        # Use curl to get the HTTP status code and redirect error output to a temporary file
        status_code=$(curl --write-out '%{http_code}' --silent --output /dev/null -H "Authorization: Bearer $key" "$url/models" 2>"$curl_error_file")
        curl_exit_code=$?

        if [[ "$status_code" -eq 200 ]]; then
            echo "INFO: Model server is up and running (received status code: $status_code)."
            rm -f "$curl_error_file"
            return 0
        elif [[ "$curl_exit_code" -ne 0 ]]; then
            curl_error=$(<"$curl_error_file")
            echo "ERROR: Curl encountered a network error (exit code: $curl_exit_code, error message: $curl_error)."
            if [[ "$attempt_num" -eq "$max_attempts" ]]; then
                rm -f "$curl_error_file"
                return 1
            fi
        else
            if [[ "$attempt_num" -eq "$max_attempts" ]]; then
                echo "ERROR: Model server failed to start or respond correctly after $max_attempts attempts (last received status code: $status_code)."
                rm -f "$curl_error_file"
                return 1
            fi
        fi

        ((attempt_num++))
        sleep 5
    done

    rm -f "$curl_error_file"
}


start_local_model_server() {
    echo "INFO: Activating virtual environment 'ZySec'..."
    source $venv_path/bin/activate

    if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == *"$venv_path" ]]; then
        echo "INFO: successfuly actiavted 'ZySec' virtual environment."
        echo "INFO: upgrading pip, setuptools and wheel"
        python3 -m pip install --quiet --upgrade pip
        pip install --quiet --upgrade pip setuptools wheel

        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "INFO: The script is running on macOS, cheking if apple metal is supported"
            metal_info=$(system_profiler SPDisplaysDataType | grep "Metal")
            if [[ ! -z "$metal_info" ]]; then
                echo "INFO: The current device supports Metal, enabling metal on llama-cpp-python[server]"
                export CMAKE_ARGS="-DLLAMA_METAL_EMBED_LIBRARY=ON -DLLAMA_METAL=on"
                export FORCE_CMAKE=1
                pip install --quiet llama-cpp-python[server] --no-cache-dir
            fi
        else
            echo "INFO: Not running on macOS"
            pip install --quiet llama-cpp-python[server] --no-cache-dir
        fi

        echo "INFO: Starting model server with model file at $model_path"
        # In start_local_model_server function, after starting the server with nohup:
        if [ "$ENABLE_MODEL_SERVER_LOG" == "yes" ]; then
            nohup python3 -m llama_cpp.server --model "$model_path" --n_batch $BATCH_SIZE --n_ctx $CONTEXT_LENGTH --verbose true --n_gpu_layers $GPU_LAYERS --chat_format zephyr > ./server.log 2>&1 &
        else
            nohup python3 -m llama_cpp.server --model "$model_path" --n_batch $BATCH_SIZE --n_ctx $CONTEXT_LENGTH --verbose true --n_gpu_layers $GPU_LAYERS --chat_format zephyr > /dev/null 2>&1 &
        fi
        MODEL_SERVER_PID=$!
        export MODEL_SERVER_PID  # Export the PID to an environment variable
        echo "INFO: Model server started with PID $MODEL_SERVER_PID."
        sleep 5
        check_api_server_connection $LOCAL_BASE_URL $LOCAL_API_KEY
        result=$?
        if [ "$result" -eq 0 ]; then
            echo "INFO: Connection to model server was successful."
        else
            echo "EROR: Failed to connect to the model server, please enable server log to degug"
            exit 1
        fi
    else
        echo "ERROR: Failed to activate 'ZySec' virtual environment. Exiting."
        exit 1
    fi

}

stop_model_server() {
    if [ -n "$MODEL_SERVER_PID" ]; then
        echo "INFO: Stopping model server with PID $MODEL_SERVER_PID..."
        kill "$MODEL_SERVER_PID"
        unset MODEL_SERVER_PID  # Unset the variable after stopping the server
        echo "INFO: Model server stopped."
    else
        echo "WARNING: Model server PID is not set. The server may not have been started or it was already stopped."
    fi
}
trap stop_model_server SIGINT SIGTERM


# Modified check_start_local_model_server function to include USE_LOCAL_SERVER check
check_start_local_model_server() 
{   
    if [ "$USE_LOCAL_SERVER" = "yes" ]; then
        export LOCAL_BASE_URL=$LOCAL_BASE_URL
        export LOCAL_API_KEY=$LOCAL_API_KEY
        # Check if port is already in use
        port=$(echo $LOCAL_BASE_URL | awk -F'[:/]' '{print $5}')
        pid=$(lsof -i:$port -sTCP:LISTEN -t 2>/dev/null) # Suppress system messages

        if [[ ! -z "$pid" ]]; then
            if ps -f -p $pid 2>/dev/null | grep -q "llama_cpp.server"; then
                echo "INFO: Model server is already running with process $pid"
                return
            else
                echo "ERROR: Port $port is in use by another application, please change the port in the config file and try again."
                exit 1
            fi
        else
            start_local_model_server
        fi
    fi
}

start_app_server () {
# for now pull the latest changes to run locally, in future it will be replaced by releases
echo "INFO: Pulling latest changes from Git repository..."
git pull origin main > /dev/null 2>&1

echo "INFO: Activating virtual environment 'ZySec'..."
source $venv_path/bin/activate 2>/dev/null

# Check if we are in the right virtual environment
if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == *"$venv_path" ]]; then
    echo "INFO: Succesfully activated 'ZySec' virtual environment."
    # upgrade pip
    echo "INFO: uprgading pip"
    python3 -m pip install --upgrade pip > /dev/null 2>&1
    echo "INFO: installing necessary python packages"
    # Install requirements
    pip install -r requirements.txt > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      echo "INFO: starting streamlit app..."
      streamlit run app.py
    else
      echo "ERROR: pip failed to install packages, run the script in debug mode by setting SCRIPT_DEBUG_MODE=yes in the config.cfg"
      exit 1
    fi
else
    echo "ERROR: Failed to activate 'ZySec' virtual environment, run the script in debug mode by setting SCRIPT_DEBUG_MODE=yes in the config.cfg"
    exit 1
fi


}

start_app_with_remote_server() {
    check_api_server_connection $REMOTE_BASE_URL $REMOTE_API_KEY
    result=$?
    if [ "$result" -eq 0 ]; then
        echo "INFO: connection to model server was successful."
        echo "INFO: starting the application"
        start_app_server
    else
        echo "ERROR: Failed to connect to the model server, please check the server connectivity."
        exit 1
    fi
}

# create virtual envrionment
create_venv

# Main execution logic
if [ "$USE_LOCAL_SERVER" = "yes" ]; then
    # Download model and start local model server if USE_LOCAL_SERVER is set to yes
    download_model
    check_start_local_model_server
else
    echo "INFO: Skipping local model server setup as USE_LOCAL_SERVER is set to no."
fi
start_app_server
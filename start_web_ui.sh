#!/bin/bash

# Step 1: Git pull
echo "Pulling latest changes from Git repository..."
git pull

# Step 3: Setup and activate virtual environment
venv_path="zysec"
if [ ! -d "$venv_path" ]; then
    echo "Creating virtual environment 'ZySec'..."
    python3 -m venv $venv_path
fi

echo "Activating virtual environment 'ZySec'..."
source $venv_path/bin/activate

# Check if we are in the right virtual environment
if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == *"$venv_path" ]]; then
    echo "Now in the 'ZySec' virtual environment."
    # Install requirements
    pip3 install -r requirements.txt -q
else
    echo "Failed to activate 'ZySec' virtual environment. Exiting."
    exit 1
fi

# Step 5: Start the Streamlit app
echo "Assuming model instance is running.. you can start it or review settings in about section to connect to remote instance."
echo "Starting Streamlit app..."
streamlit run app.py


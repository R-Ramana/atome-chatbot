#!/bin/bash

set -e

VENV_DIR="atome-chatbot"
SCRIPT_NAME="your_script.py"
REQUIREMENTS="requirements.txt"

echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
if [ -f "$REQUIREMENTS" ]; then
    pip install -r "$REQUIREMENTS"
else
    echo "No requirements.txt found, skipping installation."
fi

echo "Running the scripts..."
uvicorn bot:app --reload &
streamlit run admin_ui.py &
streamlit run chat_ui.py &

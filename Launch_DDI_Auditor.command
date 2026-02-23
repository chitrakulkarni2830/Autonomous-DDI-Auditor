#!/bin/bash

# Navigate to the project directory
cd "/Users/chitrakulkarni/Desktop/Data Analyst Projects/AutonomousDDI-Agent"

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found! Please ensure 'venv' exists in the project root."
    read -p "Press enter to exit..."
    exit 1
fi

echo "🚀 Starting Autonomous DDI Auditor..."

# Run the Streamlit app using the venv python
./venv/bin/python3 -m streamlit run scripts/app.py

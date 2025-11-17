#!/bin/bash
# Run FileSeekr application

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
python3 main.py

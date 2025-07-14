#!/bin/bash
# Activate virtual environment and launch FastAPI app with Uvicorn

# Activate the virtual environment
source .venv/bin/activate

# Launch the FastAPI app
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

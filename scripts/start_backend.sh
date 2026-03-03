#!/bin/bash

# Start Backend (FastAPI)
echo "Starting FastAPI Backend..."
./.venv/bin/python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

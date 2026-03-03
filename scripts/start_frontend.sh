#!/bin/bash

# Start Frontend (Streamlit)
echo "Starting Streamlit Frontend..."
./.venv/bin/streamlit run frontend/app.py --server.port 8501

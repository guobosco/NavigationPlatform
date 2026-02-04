#!/bin/bash
set -e

echo "Initializing Database..."
python -m backend.init_db

echo "Starting Server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000

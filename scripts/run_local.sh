#!/usr/bin/env bash
set -euo pipefail

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT

API_URL="${API_URL:-http://127.0.0.1:8000}" streamlit run frontend/streamlit_app.py

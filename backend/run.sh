#!/bin/bash
set -e
cd /home/sprite/vuurkorf/backend
mkdir -p /tmp/uploads /tmp/outputs
pip install -r requirements.txt -q
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

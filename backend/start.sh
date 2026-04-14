#!/bin/bash
cd /home/sprite/vuurkorf/backend
pip install -r requirements.txt --quiet 2>&1
mkdir -p /tmp/uploads /tmp/outputs
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

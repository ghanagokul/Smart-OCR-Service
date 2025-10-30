#!/bin/bash
set -e
echo "Starting Flask API..."
exec gunicorn -b 0.0.0.0:8080 app:app --workers 2 --threads 4 --timeout 180
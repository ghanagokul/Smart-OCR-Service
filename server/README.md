# 1. Configure .env

cp .env.example .env

# edit GCP_BUCKET, PROJECT_ID, etc.

# 2. Build and start

docker compose up --build

# Flask API → http://localhost:8080

# React UI → http://localhost:5173

docker run -d --name redis -p 6379:6379 redis:7-alpine

from root: docker compose up --build
from server: docker build -t smart-ocr-server .

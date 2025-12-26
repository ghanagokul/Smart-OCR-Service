
# Smart OCR Service

Smart OCR Service is a Dockerized full-stack application for uploading documents, extracting text asynchronously, and enabling search and chat over document content.

---

## Features
- Document upload & OCR processing
- Asynchronous background jobs (Celery + Redis)
- Job status tracking
- Semantic search using vector embeddings
- Chat over document content (RAG-style)
- React frontend with stable error handling

---

## Tech Stack
- **Backend:** Flask, Celery, Redis, PostgreSQL, Qdrant
- **Frontend:** React (Vite)
- **Infra:** Docker, OpenAI API

---

## Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/ghanagokul/Smart-OCR-Service.git
cd Smart-OCR-Service
````

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set required values (database, Redis, OpenAI key, storage config).

> Do not commit `.env`.

### 3. Start the application

```bash
docker compose up --build
```

Backend services and workers will start automatically.

## API Endpoints

* `POST /api/upload` – Upload document
* `GET /api/status/{id}` – Job status
* `GET /api/result/{id}` – OCR result
* `GET /api/search?q=` – Search documents
* `POST /api/chat/{id}` – Chat with document

---

## Author

**Ghana Gokul Gabburi**
GitHub: [https://github.com/ghanagokul](https://github.com/ghanagokul)



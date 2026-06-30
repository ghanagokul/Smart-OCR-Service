# Smart OCR Service

Smart OCR Service is an intelligent document management platform—similar to Google Docs—that turns static files (like scanned PDFs, receipts, or images) into interactive digital knowledge. Unlike traditional folders that only let you search by a file's title, this system reads the actual text inside your documents using **OCR (Optical Character Recognition)**. It then uses **NLP (Natural Language Processing)** to understand the deeper meaning of your files. This means you can search your library based on concepts and context, and even open up an integrated AI chatbot to ask questions and have a conversation directly with a document without ever needing to download it.

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

## API Endpoints

* `POST /api/upload` – Upload document
* `GET /api/status/{id}` – Job status
* `GET /api/result/{id}` – OCR result
* `GET /api/search?q=` – Search documents
* `POST /api/chat/{id}` – Chat with document

import json
from sqlalchemy import select, inspect
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

from status_store import StatusStore
from storage import upload_file, generate_signed_url
from tasks import process_document
from db import Base, engine, get_session
from models import Document

# OpenAI for embeddings + chat
from openai import OpenAI
client = OpenAI()

# Qdrant client
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "ocr_documents")

qclient = QdrantClient(url=QDRANT_URL)

app = Flask(__name__)
CORS(app, origins="*")

STATUS = StatusStore()


# --------------------------
# DB Init
# --------------------------
def init_db():
    """Initialize database tables. Safe for concurrent calls."""
    try:
        inspector = inspect(engine)
        if 'documents' not in inspector.get_table_names():
            Base.metadata.create_all(bind=engine)
    except Exception as e:
        msg = str(e).lower()
        if "already exists" not in msg and "duplicate" not in msg:
            raise


with app.app_context():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True}


# --------------------------
# UPLOAD  ✅ FIXED RESPONSE
# --------------------------
@app.post("/api/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(f.filename)
    job_id = STATUS.new_job(filename)

    # Create DB record
    with get_session() as s:
        doc = Document(
            id=job_id,
            filename=filename,
            mime=f.mimetype or "",
            gcs_uri="",
            status="UPLOADING",
            text="",
            entities_json="[]",
            tags_json="[]"
        )
        s.add(doc)
        s.commit()

    STATUS.update(job_id, status="UPLOADING", progress=20, stage="Uploading to GCS")

    # Upload file
    dest = f"uploads/{job_id}/{filename}"
    gcs_uri = upload_file(f, dest, content_type=f.mimetype)

    with get_session() as s:
        d = s.get(Document, job_id)
        d.gcs_uri = gcs_uri
        d.status = "QUEUED"
        s.commit()

    STATUS.update(job_id, status="QUEUED", progress=40, stage="Queued", gcs_uri=gcs_uri)

    # Queue worker
    process_document.delay(job_id, gcs_uri, filename)

    # ✅ CRITICAL FIX: frontend-safe response
    return jsonify({
        "job_id": job_id,
        "document_id": job_id,
        "status": "QUEUED"
    }), 200


# --------------------------
# STATUS
# --------------------------
@app.get("/api/status/<job_id>")
def status(job_id):
    data = STATUS.get(job_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    return jsonify(data)


# --------------------------
# RESULT
# --------------------------
@app.get("/api/result/<job_id>")
def result(job_id):
    data = STATUS.get(job_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    if data.get("status") != "COMPLETED":
        return jsonify({"error": "not ready"}), 409

    return jsonify({
        "text": data.get("text", ""),
        "entities": data.get("entities", "[]")
    })


# --------------------------
# SEARCH (Postgres only)
# --------------------------
@app.get("/api/search")
def search():
    q = request.args.get("q", "").lower()
    if not q:
        return jsonify({"results": []})

    results = []
    with get_session() as s:
        docs = s.execute(select(Document)).scalars().all()

        for d in docs:
            blob = " ".join([
                d.filename.lower(),
                (d.text or "").lower(),
                " ".join(json.loads(d.tags_json or "[]")).lower(),
                (d.entities_json or "").lower()
            ])

            if q in blob:
                results.append({
                    "id": d.id,
                    "filename": d.filename,
                    "status": d.status,
                    "tags": json.loads(d.tags_json or "[]"),
                    "previewUrl": generate_signed_url(d.gcs_uri, minutes=20)
                })

    return jsonify({"results": results})


# --------------------------
# DOWNLOAD
# --------------------------
@app.get("/api/download/<job_id>")
def download_url(job_id):
    with get_session() as s:
        d = s.get(Document, job_id)
        if not d or not d.gcs_uri:
            return {"error": "not found"}, 404
        return {"url": generate_signed_url(d.gcs_uri, minutes=30)}


# --------------------------
# RAG CHAT
# --------------------------
@app.post("/api/chat/<doc_id>")
def chat(doc_id):
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Empty question"}), 400

    q_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    hits = qclient.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=q_emb,
        limit=5,
        query_filter=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=doc_id))]
        )
    )

    chunks = [hit.payload["text"] for hit in hits]

    if not chunks:
        return jsonify({"answer": "No relevant content found."})

    context = "\n\n---\n".join(chunks)

    prompt = f"""
Answer the question using ONLY the document text below.

DOCUMENT:
{context}

QUESTION:
{question}

ANSWER:
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    return jsonify({
        "answer": resp.choices[0].message.content.strip(),
        "chunks": chunks
    })

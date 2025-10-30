import json
from sqlalchemy.orm import Session
from sqlalchemy import select, inspect
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from status_store import StatusStore
from storage import upload_file, generate_signed_url
from tasks import process_document
from db import Base, engine, get_session
from models import Document

inspector = inspect(engine)
if "documents" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app, origins=os.environ.get("CORS_ORIGINS", "*").split(","))

STATUS = StatusStore()


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(f.filename)
    job_id = STATUS.new_job(filename)
    session = get_session()
    doc = Document(
        id=job_id,
        filename=filename,
        mime=f.mimetype or "",
        gcs_uri="",  # set after upload
        status="UPLOADING",
    )
    session.add(doc)
    session.commit()
    session.close()
    STATUS.update(job_id, status="UPLOADING",
                  progress=20, stage="Uploading to GCS")

    # destination path in bucket: uploads/<job>/<filename>
    dest = f"uploads/{job_id}/{filename}"
    gcs_uri = upload_file(f, dest, content_type=f.mimetype)

    STATUS.update(job_id, status="QUEUED", progress=40,
                  stage="Queued for OCR", gcs_uri=gcs_uri)

    # enqueue celery task
    process_document.delay(job_id, gcs_uri, filename)

    return jsonify({"job_id": job_id})


@app.get("/api/status/<job_id>")
def status(job_id):
    data = STATUS.get(job_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    # entities may be a JSON string; keep as‑is for client
    return jsonify(data)


@app.get("/api/result/<job_id>")
def result(job_id):
    data = STATUS.get(job_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    if data.get("status") != "COMPLETED":
        return jsonify({"error": "not ready", "status": data.get("status")}), 409
    return jsonify({
        "text": data.get("text", ""),
        "entities": data.get("entities", "[]"),
    })


@app.get("/api/doc/<job_id>")
def get_doc(job_id):
    with get_session() as s:
        d = s.get(Document, job_id)
        if not d:
            return jsonify({"error": "not found"}), 404
        return jsonify({
            "id": d.id,
            "filename": d.filename,
            "mime": d.mime,
            "gcs_uri": d.gcs_uri,
            "status": d.status,
            "tags": json.loads(d.tags_json or "[]"),
        })


@app.get("/api/download/<job_id>")
def download_link(job_id):
    with get_session() as s:
        d = s.get(Document, job_id)
        if not d:
            return jsonify({"error": "not found"}), 404
        if not d.gcs_uri:
            return jsonify({"error": "no file"}), 400
        url = generate_signed_url(d.gcs_uri, minutes=30)
        return jsonify({"url": url})


@app.get("/api/search")
def search():
    """
    Simple search over tags + filename + entities + text (prefix/substring).
    For scale, you'd move to full-text index (PG trigram/tsvector or Elastic).
    """
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify({"results": []})

    # naive search
    results = []
    with get_session() as s:
        docs = s.execute(select(Document)).scalars().all()
        for d in docs:
            hay = " ".join([
                d.filename or "",
                (d.text or "")[:5000].lower(),
                " ".join(json.loads(d.tags_json or "[]")).lower(),
                (d.entities_json or "").lower(),
            ])
            if q in hay:
                results.append({
                    "id": d.id,
                    "filename": d.filename,
                    "status": d.status,
                    "tags": json.loads(d.tags_json or "[]"),
                })
    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(host=os.environ.get("API_HOST", "0.0.0.0"),
            port=int(os.environ.get("API_PORT", 8080)))

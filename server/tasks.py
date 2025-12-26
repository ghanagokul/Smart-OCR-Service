import os
import json
import re
import tempfile
import uuid
from collections import Counter

from celery import Celery
import spacy
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

from storage import download_to_path
from status_store import StatusStore
from db import get_session
from models import Document

# ------------- OpenAI -------------
from openai import OpenAI
client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dims

# ------------- Qdrant -------------
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams
)

# ---- FIXED: Use same collection everywhere ----
QDRANT_COLLECTION = "ocr_documents"

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
qclient = QdrantClient(url=QDRANT_URL)


# ===== Ensure Qdrant collection exists =====
def ensure_qdrant_collection():
    try:
        collections = qclient.get_collections().collections
        if any(c.name == QDRANT_COLLECTION for c in collections):
            print(f"✓ Qdrant collection '{QDRANT_COLLECTION}' already exists")
            return

        print(f"Creating Qdrant collection '{QDRANT_COLLECTION}'...")
        qclient.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print(f"✓ Created Qdrant collection '{QDRANT_COLLECTION}'")

    except Exception as e:
        if "already exists" in str(e):
            print(f"✓ Collection '{QDRANT_COLLECTION}' already exists")
        else:
            raise


ensure_qdrant_collection()

# Celery
celery_app = Celery("smart-ocr")
celery_app.config_from_object("celeryconfig")

STATUS = StatusStore()
NLP = spacy.load("en_core_web_sm")


# ============================================================
# Helper: OpenAI Embedding
# ============================================================
def embed(text: str) -> list[float]:
    clean = text.strip()
    if not clean:
        return [0.0] * 1536

    resp = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=clean[:8000]
    )
    return resp.data[0].embedding


# ============================================================
# Helper: OCR
# ============================================================
def extract_text_from_pdf(path: str) -> str:
    pages = convert_from_path(path, dpi=200)
    text_pages = [pytesseract.image_to_string(img) for img in pages]
    return "\n".join(text_pages)


def extract_text_from_image(path: str) -> str:
    return pytesseract.image_to_string(Image.open(path))


def detect_type(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        return "image"
    if lower.endswith((".txt", ".text")):
        return "text"
    return "other"


# ============================================================
# Helper: Tags
# ============================================================
STOPWORDS = set("""
a an and are as at be but by for if in into is it no not of on or such that the
their then there these they this to was were will with you your from
""".split())


def extract_tags(text: str, entities: list, k: int = 20) -> list[str]:
    tags = set()

    # Named entities
    for e in entities:
        t = e.get("text")
        if t:
            tags.add(t)

    # Noun chunks
    try:
        doc = NLP(text)
        for nc in doc.noun_chunks:
            t = re.sub(r"[^A-Za-z0-9\- ]+", "", nc.text).strip()
            if t and t.lower() not in STOPWORDS:
                tags.add(t)
    except:
        pass

    # Frequent words
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9\-]{3,}", text)]
    words = [w for w in words if w not in STOPWORDS]
    freq = Counter(words).most_common(k)

    for w, _ in freq:
        tags.add(w)

    return list(tags)[:50]


# ============================================================
# Helper: Chunking
# ============================================================
def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        chunk = text[i:i+size]
        chunks.append(chunk)
        i += size - overlap
    return chunks


# ============================================================
# Main Worker
# ============================================================
@celery_app.task(queue="ocr")
def process_document(job_id: str, gcs_uri: str, filename: str):
    try:
        STATUS.update(job_id, status="OCR_IN_PROGRESS", progress=60)

        # ---- Download ----
        with tempfile.TemporaryDirectory() as td:
            local_path = os.path.join(td, filename)
            download_to_path(gcs_uri, local_path)

            filetype = detect_type(local_path)
            if filetype == "pdf":
                text = extract_text_from_pdf(local_path)
            elif filetype == "image":
                text = extract_text_from_image(local_path)
            elif filetype == "text":
                with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            else:
                text = ""

        # ---- NLP ----
        STATUS.update(job_id, status="NLP_IN_PROGRESS", progress=80)

        doc = NLP(text)
        entities = [{"text": e.text, "label": e.label_} for e in doc.ents]
        tags = extract_tags(text, entities)

        # ---- Chunk + Embeddings ----
        chunks = chunk_text(text)
        points = []

        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            emb = embed(chunk)
            point_id = str(uuid.uuid4())

            points.append(
                PointStruct(
                    id=point_id,
                    vector=emb,
                    payload={
                        "document_id": job_id,
                        "chunk_index": idx,
                        "text": chunk,
                    }
                )
            )

        if points:
            qclient.upsert(collection_name=QDRANT_COLLECTION, points=points)
            print(f"✓ Inserted {len(points)} chunks for {job_id}")

        # ---- Update database ----
        with get_session() as s:
            d = s.get(Document, job_id)
            if d:
                d.status = "COMPLETED"
                d.text = text[:100000]
                d.entities_json = json.dumps(entities)
                d.tags_json = json.dumps(tags)
                s.commit()

        STATUS.update(job_id, status="COMPLETED", progress=100)

    except Exception as e:
        STATUS.update(job_id, status="FAILED", stage=str(e))
        raise

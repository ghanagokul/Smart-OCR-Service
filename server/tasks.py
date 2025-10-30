from storage import download_to_path
from status_store import StatusStore
from db import get_session
from models import Document
import spacy
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from celery import Celery
import tempfile
import json
import os
import re
from collections import Counter

celery_app = Celery("smart-ocr")
celery_app.config_from_object("celeryconfig")

STATUS = StatusStore()

# Load spaCy model once in worker (loaded only once per worker process)
NLP = spacy.load("en_core_web_sm")

# ------------------------------
# Helper Functions
# ------------------------------


def extract_text_from_pdf(pdf_path: str) -> str:
    texts = []
    images = convert_from_path(pdf_path, dpi=200)
    for img in images:
        text = pytesseract.image_to_string(img)
        texts.append(text)
    return "\n".join(texts)


def extract_text_from_image(img_path: str) -> str:
    img = Image.open(img_path)
    return pytesseract.image_to_string(img)


def simple_detect_type(local_path: str) -> str:
    lower = local_path.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    elif any(lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]):
        return "image"
    return "binary"


# ------------------------------
# Tag / Keyword Extraction
# ------------------------------

STOPWORDS = set("""
a an and are as at be but by for if in into is it no not of on or such that the their then there these they this to was were will with you your from
""".split())


def extract_tags(text: str, entities: list[dict], k: int = 15) -> list[str]:
    tags = set()

    # 1️⃣ Add named entities
    for e in entities:
        token = e.get("text", "").strip()
        if token:
            tags.add(token)

    # 2️⃣ Add noun chunks
    try:
        doc = NLP(text)
        for nc in doc.noun_chunks:
            t = re.sub(r"[^A-Za-z0-9\- ]+", "", nc.text).strip()
            if t and t.lower() not in STOPWORDS and len(t) > 2:
                tags.add(t)
    except Exception:
        pass

    # 3️⃣ Add top frequent words
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9\-]{3,}", text)]
    words = [w for w in words if w not in STOPWORDS]
    freq = Counter(words).most_common(50)
    for w, _ in freq[:k]:
        tags.add(w)

    # Deduplicate and trim
    cleaned = []
    for t in tags:
        t2 = t.strip()
        if t2 and t2 not in cleaned:
            cleaned.append(t2)
    return cleaned[:50]


# ------------------------------
# Celery Task: process_document
# ------------------------------

@celery_app.task(queue="ocr")
def process_document(job_id: str, gcs_uri: str, filename: str):
    """Performs OCR + NER + Tag extraction + DB persistence."""
    try:
        STATUS.update(job_id, status="OCR_IN_PROGRESS",
                      progress=60, stage="Downloading & OCR")

        # ---- 1. Download and OCR ----
        with tempfile.TemporaryDirectory() as td:
            local_path = os.path.join(td, filename)
            download_to_path(gcs_uri, local_path)

            ftype = simple_detect_type(local_path)
            if ftype == "pdf":
                text = extract_text_from_pdf(local_path)
            elif ftype == "image":
                text = extract_text_from_image(local_path)
            else:
                text = ""  # Unsupported file type

        # ---- 2. NLP (NER + Tagging) ----
        STATUS.update(job_id, status="NLP_IN_PROGRESS",
                      progress=80, stage="Extracting entities & tags")
        doc = NLP(text)
        entities = [
            {"text": ent.text, "label": ent.label_,
                "start": ent.start_char, "end": ent.end_char}
            for ent in doc.ents
        ]
        tags = extract_tags(text, entities)

        # ---- 3. Persist to DB ----
        with get_session() as s:
            d = s.get(Document, job_id)
            if d:
                d.status = "COMPLETED"
                d.text = text[:100000]                 # limit large text
                d.entities_json = json.dumps(entities)
                d.tags_json = json.dumps(tags)
                s.add(d)
                s.commit()

        # ---- 4. Update in-memory Status ----
        STATUS.update(
            job_id,
            status="COMPLETED",
            progress=100,
            stage="Done",
            text=text[:20000],
            entities=json.dumps(entities),
        )

    except Exception as e:
        STATUS.update(job_id, status="FAILED", stage=f"Error: {e}")

        # Reflect failure in DB as well
        with get_session() as s:
            d = s.get(Document, job_id)
            if d:
                d.status = "FAILED"
                s.add(d)
                s.commit()

        raise

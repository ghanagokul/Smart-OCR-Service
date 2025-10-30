# ---------- Base image ----------
FROM python:3.11-slim

# ---------- Install system dependencies ----------
# poppler-utils → required for pdf2image (converts PDF → images)
# tesseract-ocr → OCR engine
# libgl1 → required for Pillow image rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# ---------- Set workdir ----------
WORKDIR /app

# ---------- Copy requirements ----------
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Download and link spaCy model ----------
# This ensures your worker has the English NER model ready at runtime
RUN python -m spacy download en_core_web_sm

# ---------- Copy application code ----------
COPY . /app

# ---------- Permissions & env settings ----------
RUN chmod +x /app/entrypoint.sh
ENV PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# ---------- Default command (Gunicorn for Flask API) ----------
CMD ["/bin/bash", "/app/entrypoint.sh"]
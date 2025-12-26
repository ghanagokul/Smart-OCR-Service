# ---------- Base ----------
    FROM python:3.11-slim

    # ---------- System Dependencies ----------
    RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        poppler-utils \
        libgl1 \
        && rm -rf /var/lib/apt/lists/*
    
    WORKDIR /app
    
    # ---------- Python Dependencies ----------
    COPY requirements.txt /app/
    RUN pip install --no-cache-dir -r requirements.txt
    
    # spaCy model
    RUN python -m spacy download en_core_web_sm
    
    # ---------- Copy App ----------
    COPY . /app
    
    RUN chmod +x /app/entrypoint.sh
    
    ENV PYTHONUNBUFFERED=1 \
        PATH="/root/.local/bin:$PATH"
    
    CMD ["/bin/bash", "/app/entrypoint.sh"]
    
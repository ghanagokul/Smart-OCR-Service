# vector_store.py (renamed from qdrant_client.py to avoid naming conflict)
import os
from typing import List
from server.vector_store import QdrantClient
from qdrant_client.http import models as qmodels

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION", "document_chunks")
DIM = 1536  # OpenAI text-embedding-3-small

# ---------------------------------------------------------
# CREATE CLIENT
# ---------------------------------------------------------
client = QdrantClient(url=QDRANT_URL)

# ---------------------------------------------------------
# CREATE COLLECTION IF NOT EXISTS
# ---------------------------------------------------------
def ensure_qdrant_collection():
    try:
        collections = qclient.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if QDRANT_COLLECTION_NAME not in collection_names:
            qclient.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            print(f"Created Qdrant collection: {QDRANT_COLLECTION_NAME}")
        else:
            print(f"Qdrant collection already exists: {QDRANT_COLLECTION_NAME}")
    except Exception as e:
        # If collection already exists (race condition), ignore
        if "already exists" in str(e):
            print(f"Collection {QDRANT_COLLECTION_NAME} already exists (concurrent creation)")
        else:
            raise

# ---------------------------------------------------------
# INSERT CHUNKS
# ---------------------------------------------------------
def upsert_chunks(doc_id: str, chunks: List[str], embeddings: List[List[float]]):
    """
    Upserts text chunks into Qdrant under a single document_id.
    Each chunk is one vector record with:
      - id: unique integer
      - payload.document_id
      - payload.chunk_index
      - payload.text
      - vector: embedding
    """
    ensure_collection()
    points = []
    for idx, (text, emb) in enumerate(zip(chunks, embeddings)):
        points.append(
            qmodels.PointStruct(
                id=f"{doc_id}-{idx}",
                vector=emb,
                payload={
                    "document_id": doc_id,
                    "chunk_index": idx,
                    "text": text,
                },
            )
        )
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )
    print(f"[QDRANT] Inserted {len(points)} chunks for document {doc_id}")

# ---------------------------------------------------------
# SEMANTIC SEARCH
# ---------------------------------------------------------
def semantic_search(doc_id: str, query_emb: List[float], limit: int = 5) -> List[str]:
    """
    Searches inside a single document using semantic vector search.
    Returns the chunk text pieces.
    """
    ensure_collection()
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_emb,
        limit=limit,
        filter=qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchValue(value=doc_id),
                )
            ]
        ),
    )
    return [hit.payload.get("text", "") for hit in hits]
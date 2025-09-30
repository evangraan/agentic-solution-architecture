import os
import sys
import pdfplumber
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer

# --- Configuration ---
PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else "example_design_standards.pdf"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "example_design_standards")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = 500  # characters per chunk

# --- Initialize clients ---
qdrant = QdrantClient(url=QDRANT_URL)
embedder = SentenceTransformer(EMBED_MODEL)

# --- Create collection if not exists ---
if QDRANT_COLLECTION not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.recreate_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config={"size": embedder.get_sentence_embedding_dimension(), "distance": "Cosine"}
    )

# --- Extract and chunk PDF ---
chunks = []
with pdfplumber.open(PDF_PATH) as pdf:
    for page in pdf.pages:
        text = page.extract_text() or ""
        # Simple chunking by character count
        for i in range(0, len(text), CHUNK_SIZE):
            chunk = text[i:i+CHUNK_SIZE].strip()
            if chunk:
                chunks.append(chunk)

print(f"Extracted {len(chunks)} chunks from {PDF_PATH}")

# --- Embed and upsert to Qdrant ---
embeddings = embedder.encode(chunks)
points = [
    PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": chunks[i]})
    for i in range(len(chunks))
]
qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
print(f"Upserted {len(points)} points to Qdrant collection '{QDRANT_COLLECTION}'")

from fastapi import FastAPI, Path, Body
from fastapi import Request, Response
from pydantic import BaseModel

import httpx
import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Qdrant and embedding model setup
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "example_design_standards")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

qdrant_client = QdrantClient(url=QDRANT_URL)
embedder = SentenceTransformer(EMBED_MODEL)

MODEL_MAP = {
    "meta.llama3-8b-instruct-v1:0": "llama3:8b",
    "mistral.mistral-7b-instruct-v0:2": "mistral",
}

def to_ollama_model(model_id: str) -> str:
    if model_id.startswith("ollama."):
        return model_id.split("ollama.", 1)[1]
    return MODEL_MAP.get(model_id, model_id)

app = FastAPI(title="Bedrock proxy (Ollama)")


# AWS Bedrock 'invoke_model' compatibility endpoint
@app.post("/model/{model_id}/invoke")
async def invoke_model(request: Request, model_id: str = Path(...)):
    # Parse the incoming AWS payload
    payload = await request.json()
    # AWS expects {"input": "..."} or {"input": {...}}
    input_data = payload.get("input")
    if isinstance(input_data, dict):
        # If input is a dict, try to extract text
        text = input_data.get("text", str(input_data))
    else:
        text = str(input_data)

    

    # --- Read Augmentation ---
    # 1. Embed the prompt
    query_vec = embedder.encode([text])[0].tolist()
    # 2. Query Qdrant for top-3 relevant chunks
    hits = qdrant_client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vec,
        limit=3
    )
    # 3. Concatenate retrieved context
    context = "\n".join([hit.payload.get("text", "") for hit in hits if hit.payload])
    augmented_prompt = f"Company Standards:\n{context}\n\nUser Request:\n{text}"

    # Map to Ollama chat format
    ollama_model = to_ollama_model(model_id)
    body = {
        "model": ollama_model,
        "messages": [{"role": "user", "content": augmented_prompt}],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json=body)
        r.raise_for_status()
        data = r.json()

    reply = (data.get("message") or {}).get("content", "")
    from fastapi.responses import Response
    return Response(
        content=reply,
        media_type="application/json"
    )


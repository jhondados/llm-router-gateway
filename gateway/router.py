"""Intelligent LLM router with semantic caching."""
from fastapi import FastAPI
import redis.asyncio as redis
from langchain_google_vertexai import ChatVertexAI
from sentence_transformers import SentenceTransformer
import numpy as np, json, hashlib
from typing import Optional

app = FastAPI(title="LLM Gateway")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

MODELS = {
    "flash": ChatVertexAI(model_name="gemini-1.5-flash-002"),
    "pro":   ChatVertexAI(model_name="gemini-1.5-pro-002"),
}

async def semantic_cache_lookup(redis_client, query: str, threshold: float = 0.95) -> Optional[str]:
    emb = embedder.encode(query).tolist()
    cached_keys = await redis_client.keys("llm_cache:*")
    for key in cached_keys[:100]:
        entry = json.loads(await redis_client.get(key) or "{}")
        if "embedding" in entry:
            sim = np.dot(emb, entry["embedding"]) / (np.linalg.norm(emb) * np.linalg.norm(entry["embedding"]))
            if sim >= threshold:
                return entry["response"]
    return None

def classify_complexity(query: str) -> str:
    tokens = len(query.split())
    if tokens < 20: return "flash"
    if tokens < 100: return "pro"
    return "pro"

@app.post("/v1/chat")
async def chat(query: str, force_model: str = None):
    r = await redis.from_url("redis://localhost:6379")
    cached = await semantic_cache_lookup(r, query)
    if cached: return {"response": cached, "cached": True, "cost": 0.0}
    model_key = force_model or classify_complexity(query)
    response = MODELS[model_key].invoke(query).content
    emb = embedder.encode(query).tolist()
    cache_key = f"llm_cache:{hashlib.md5(query.encode()).hexdigest()}"
    await r.setex(cache_key, 3600, json.dumps({"response": response, "embedding": emb}))
    return {"response": response, "cached": False, "model": model_key}

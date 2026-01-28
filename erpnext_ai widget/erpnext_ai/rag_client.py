import os
import requests

# Base URL of FastAPI (Agent) service
# Ensure this matches your actual FastAPI IP
RAG_URL = os.getenv("TRITECH_RAG_URL", "http://172.16.19.232:8000").rstrip("/")

def rag_health(timeout: int = 5):
    try:
        r = requests.get(f"{RAG_URL}/", timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "offline", "error": str(e)}

def rag_chat(message: str, timeout: int = 120):
    """
    Connects to the FastAPI /chat endpoint.
    Payload matches class ChatRequest(BaseModel): query: str
    """
    payload = {
        "query": message
    }
    
    # We point to /chat because that is what we defined in main.py
    r = requests.post(
        f"{RAG_URL}/chat",
        json=payload,
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()

# Alias for compatibility if needed, but we route both to rag_chat
def rag_assist(message: str, top_k: int = 5, timeout: int = 600):
    return rag_chat(message, timeout)
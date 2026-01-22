from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.agent import run_agent

app = FastAPI(title="ERPNext AI Agent")

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    """
    Send a natural language query.
    Example: "How many customers do we have?"
    """
    try:
        answer = run_agent(request.query)
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
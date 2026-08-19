from fastapi import FastAPI

app = FastAPI(
    title="Multi Model RAG",
    version="0.1.0",
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "API is running",
    }

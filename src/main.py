# from fastapi import FastAPI

from src.api.v1.auth import router as users_router
from src.api.v1.documents import router
from fastapi import FastAPI
from src.core.config import create_qdrant_collection
from src.models.user import User
from src.api.v1.knowledge import router as knowledge_router
from src.db.init_db import create_tables

app = FastAPI(
    title="Multi Model RAG API",
    version="1.0.0",
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://multi-model-rag-frontend.netlify.app",
        "https://6a8956d3719b09000854b6e4--multi-model-rag-frontend.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():

    create_qdrant_collection()


create_tables()

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    router,
    prefix="/api/v1",
)

app.include_router(
    knowledge_router,
    prefix="/api/v1",
)

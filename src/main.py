from fastapi import FastAPI

from src.api.v1.users import router as users_router

from fastapi import FastAPI

from src.models.user import User

from src.db.init_db import create_tables

app = FastAPI(
    title="Multi Model RAG API",
    version="1.0.0",
)

create_tables()

app.include_router(
    users_router,
    prefix="/api/v1",
)
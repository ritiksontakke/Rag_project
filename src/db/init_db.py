from src.db.base import Base
from src.db.database import engine
from src.models.user import User


def create_tables():
    Base.metadata.create_all(
        bind=engine
    )
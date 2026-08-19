import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    f"?sslmode=require"
)


engine = create_engine(DATABASE_URL)

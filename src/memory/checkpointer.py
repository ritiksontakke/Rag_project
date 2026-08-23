from langgraph.checkpoint.postgres import PostgresSaver

from src.db.database import (
    USER,
    PASSWORD,
    HOST,
    PORT,
    DBNAME,
)


POSTGRES_CHECKPOINT_URL = (
    f"postgresql://"
    f"{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    f"?sslmode=require"
)


checkpointer_context = PostgresSaver.from_conn_string(
    POSTGRES_CHECKPOINT_URL
)

checkpointer = checkpointer_context.__enter__()

checkpointer.setup()
from langgraph.checkpoint.postgres import PostgresSaver

from src.db.database import DATABASE_URL


checkpointer = PostgresSaver.from_conn_string(
    DATABASE_URL
)

checkpointer.setup()
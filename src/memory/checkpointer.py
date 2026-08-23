from langgraph.checkpoint.postgres import PostgresSaver

from src.db.database import DATABASE_URL


checkpointer_context = PostgresSaver.from_conn_string(
    DATABASE_URL
)

checkpointer = checkpointer_context.__enter__()

checkpointer.setup()
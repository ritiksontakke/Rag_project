from langchain.tools import tool

from src.rag.ingestion.pipeline import (
    ingestion_pipeline,
)


@tool("upload_document")
def upload_document(
    file_path: str,
    department: str,
    uploaded_by: str,
):
    """
    Upload and ingest a PDF document
    into the RAG knowledge base.
    """

    return ingestion_pipeline(
        file_path=file_path,
        department=department,
        uploaded_by=uploaded_by,
    )
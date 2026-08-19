from src.rag.ingestion.loader import load_pdf
from src.rag.ingestion.chunker import chunk_documents
from src.rag.ingestion.embedder import create_embeddings
from src.rag.ingestion.qdrant_store import (
    store_chunks,
)


def ingestion_pipeline(
    file_path: str,
    department: str,
    uploaded_by: str,
):

    # 1. Read PDF
    documents = load_pdf(
        file_path
    )

    # 2. Create chunks
    chunks = chunk_documents(
        documents
    )

    # 3. Create embeddings
    vectors = create_embeddings(
        chunks
    )

    # 4. Store in Qdrant
    result = store_chunks(
        chunks=chunks,
        vectors=vectors,
        department=department,
        uploaded_by=uploaded_by,
    )

    return {
        "status": "success",
        "message": "Document ingested successfully.",
        "department": department,
        "chunks": result["chunks_uploaded"],
    }
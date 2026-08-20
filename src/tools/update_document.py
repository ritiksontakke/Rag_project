from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.core.config import (
    qdrant_client,
    COLLECTION_NAME,
)
from src.rag.ingestion.pipeline import ingestion_pipeline


@tool("update_document")
def update_document(
    source: str,
    file_path: str,
    department: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Replace an existing document with a new PDF.
    """

    # -----------------------------
    # ROLE CHECK
    # -----------------------------

    if runtime.context.role not in {
        "admin",
        "manager",
    }:
        return {
            "status": "error",
            "message": (
                "Permission denied. Only administrators "
                "and managers can update documents."
            ),
        }

    # -----------------------------
    # DEPARTMENT CHECK
    # -----------------------------

    if (
        runtime.context.department.lower()
        != department.lower()
    ):
        return {
            "status": "error",
            "message": (
                "Permission denied. You can only "
                "update documents in your department."
            ),
        }

    try:

        # -----------------------------
        # DELETE OLD DOCUMENT
        # -----------------------------

        qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "source",
                            "match": {
                                "value": source,
                            },
                        },
                        {
                            "key": "department",
                            "match": {
                                "value": department,
                            },
                        },
                    ]
                }
            },
        )

        # -----------------------------
        # INGEST NEW DOCUMENT
        # -----------------------------

        result = ingestion_pipeline(
            file_path=file_path,
            department=department,
            uploaded_by=str(
                runtime.context.id
            ),
        )

        return {
            "status": "success",
            "message": (
                f"Document '{source}' "
                "updated successfully."
            ),
            "result": result,
        }

    except Exception as e:

        return {
            "status": "error",
            "message": (
                "Failed to update document."
            ),
            "error": str(e),
        }
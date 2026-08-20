from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.rag.ingestion.pipeline import ingestion_pipeline


@tool("upload_document")
def upload_document(
    file_path: str,
    department: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Upload and ingest a PDF document
    into the company knowledge base.
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
                "and managers can upload documents."
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
                "upload documents for your department."
            ),
        }

    # -----------------------------
    # INGESTION
    # -----------------------------

    try:

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
                "Document uploaded and "
                "ingested successfully."
            ),
            "result": result,
        }

    except Exception as e:

        return {
            "status": "error",
            "message": "Document ingestion failed.",
            "error": str(e),
        }
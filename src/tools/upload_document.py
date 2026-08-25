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

    if runtime.context.role.lower() not in {
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
    # DEPARTMENT NORMALIZATION
    # -----------------------------

    user_department = (
        runtime.context.department.strip().lower()
    )

    upload_department = (
        department.strip().lower()
    )

    # -----------------------------
    # DEPARTMENT CHECK
    # -----------------------------

    if user_department != upload_department:
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
            department=upload_department,
            uploaded_by=str(runtime.context.id),
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

        print("\n❌ DOCUMENT INGESTION ERROR")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))

        return {
            "status": "error",
            "message": "Document ingestion failed.",
            "error": str(e),
        }
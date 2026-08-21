from langchain.tools import tool, ToolRuntime

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

from src.schemas.user_schemas import UserContext
from src.core.config import (
    qdrant_client,
    COLLECTION_NAME,
)


@tool("delete_document")
def delete_document(
    source: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Delete a document from the vector database.

    Administrators and managers are allowed to delete documents.
    The document must belong to the authenticated user's department.
    """

    print("\n🔥🔥 DELETE DOCUMENT TOOL CALLED 🔥🔥")
    print("SOURCE:", source)
    print("ROLE:", runtime.context.role)
    print("DEPARTMENT:", runtime.context.department)

    # -----------------------------
    # ROLE CHECK
    # -----------------------------

    if runtime.context.role not in {"admin", "manager"}:
        return {
            "status": "error",
            "message": (
                "Access denied. You do not have sufficient privileges "
                "to delete documents."
            ),
        }

    try:

        # -----------------------------
        # DELETE
        # -----------------------------

        qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(
                            value=source
                        ),
                    ),
                    FieldCondition(
                        key="department",
                        match=MatchValue(
                            value=runtime.context.department
                        ),
                    ),
                ]
            ),
        )

        print("✅ DOCUMENT DELETE REQUEST SUCCESSFUL")

        return {
            "status": "success",
            "message": (
                f"Document '{source}' was deleted successfully."
            ),
        }

    except Exception as e:

        print("\n❌ DELETE DOCUMENT ERROR")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))

        return {
            "status": "error",
            "message": (
                f"Unable to delete document '{source}'. "
                "An unexpected error occurred while processing "
                "the deletion request."
            ),
            "error": str(e),
        }
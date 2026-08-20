from langchain.tools import tool, ToolRuntime

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

    Access Control:
    - Administrators and managers are authorized to delete documents.
    - Employees are not authorized to delete documents.

    The document is deleted only when its `source` and `department`
    match the authenticated user's department.

    Args:
        source: The source identifier or filename of the document
                to delete.
        runtime: Runtime context containing the authenticated user's
                 role and department.

    Returns:
        A success response when the document is deleted.
        A professional permission-denied error when the user does not
        have sufficient privileges.
        An error response if the deletion operation fails.
    """

    # -----------------------------
    # ROLE CHECK
    # -----------------------------

    if runtime.context.role not in {"admin", "manager"}:
        return {
            "status": "error",
            "message": (
                "Access denied. You do not have sufficient privileges "
                "to delete documents. Document deletion is restricted "
                "to administrators and managers."
            ),
        }

    try:
        # -----------------------------
        # DELETE
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
                                "value": runtime.context.department,
                            },
                        },
                    ]
                }
            },
        )

        return {
            "status": "success",
            "message": (
                f"Document '{source}' was deleted successfully."
            ),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": (
                f"Unable to delete document '{source}'. "
                "An unexpected error occurred while processing "
                "the deletion request."
            ),
            "error": str(e),
        }
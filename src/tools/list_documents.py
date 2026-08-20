from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.core.config import (
    qdrant_client,
    COLLECTION_NAME,
)


@tool("list_documents")
def list_documents(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """
    List documents from the authenticated user's department
    knowledge base based on the user's query.

    Access Control:
    - Only administrators and managers are authorized to use this tool.
    - Employees and other roles are not permitted to list or search
      department documents.

    Query Requirement:
    - A meaningful query is required before listing documents.
    - If the user does not provide a query, do not execute the tool.
      Instead, respond naturally and ask the user what they would like
      to find or search for.
    - Do not assume or invent a query on behalf of the user.

    Department Access:
    - Only documents belonging to the authenticated user's department
      may be returned.
    - Never expose documents from another department.

    Document Grouping:
    - Documents may be stored as multiple vector chunks in Qdrant.
    - Group chunks by their `source` so that each document appears only
      once in the final response.
    - Include useful metadata such as source, department, uploaded_by,
      and the number of chunks.

    Permission Denied Behavior:
    - If the authenticated user's role is not `admin` or `manager`,
      do not access the knowledge base.
    - Return a professional, human-friendly message explaining that
      document listing is restricted to administrators and managers.

    Args:
        query:
            The user's search request describing which documents they
            want to find or list.

        runtime:
            Runtime context containing the authenticated user's role
            and department.

    Returns:
        A successful response containing the matching documents and
        total document count, or a professional error response when
        the user is unauthorized or the operation fails.
    """

    # -----------------------------
    # ROLE CHECK
    # -----------------------------

    if runtime.context.role not in {"admin", "manager"}:
        return {
            "status": "error",
            "message": (
                "Access denied. I’m sorry, but only administrators "
                "and managers can view the department's document list."
            ),
        }

    # -----------------------------
    # QUERY CHECK
    # -----------------------------

    if not query or not query.strip():
        return {
            "status": "error",
            "message": (
                "Could you tell me what documents you’re looking for? "
                "Please provide a search query."
            ),
        }

    try:
        # -----------------------------
        # DOCUMENT RETRIEVAL
        # -----------------------------

        results = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={
                "must": [
                    {
                        "key": "department",
                        "match": {
                            "value": runtime.context.department,
                        },
                    }
                ]
            },
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )

        points = results[0]

        if not points:
            return {
                "status": "success",
                "documents": [],
                "total_documents": 0,
                "message": (
                    "I couldn't find any documents in your "
                    "department's knowledge base."
                ),
            }

        documents = {}

        for point in points:
            payload = point.payload or {}

            source = payload.get("source")

            if not source:
                continue

            if source not in documents:
                documents[source] = {
                    "source": source,
                    "department": payload.get("department"),
                    "uploaded_by": payload.get("uploaded_by"),
                    "chunks": 0,
                }

            documents[source]["chunks"] += 1

        document_list = list(documents.values())

        return {
            "status": "success",
            "documents": document_list,
            "total_documents": len(document_list),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": (
                "I’m sorry, but I couldn’t retrieve the documents "
                "right now. Please try again."
            ),
            "error": str(e),
        }
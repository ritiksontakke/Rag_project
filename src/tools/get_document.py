from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.core.config import (
    qdrant_client,
    COLLECTION_NAME,
)


@tool("get_document")
def get_document(
    source: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Get an existing document from the company knowledge base.

    IMPORTANT:
    This tool is ONLY for retrieving an existing document.

    Use this tool when the user asks:
    - get a document
    - show a document
    - retrieve a document
    - open a document
    - get document information
    - get a document by filename or source path

    Do NOT use this tool for uploading documents.

    Args:
        source:
            The exact source/path of the existing document.

            Example:
            /tmp/tmprphko54l.pdf

        runtime:
            Authenticated user context containing role and department.

    Returns:
        Information and chunks belonging to the requested document.
    """
    print("\n🔥🔥 GET DOCUMENT TOOL CALLED 🔥🔥")
    print("SOURCE:", source)
    print("ROLE:", runtime.context.role)
    print("DEPARTMENT:", runtime.context.department)

    try:

        results = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={
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
                            "value": (
                                runtime.context.department
                            ),
                        },
                    },
                ]
            },
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )
        print("🔥 QDRANT RESULT TYPE:", type(results))
        print("🔥 POINT COUNT:", len(results[0]))

        points = results[0]

        if not points:
            return {
                "status": "not_found",
                "message": (
                    f"Document '{source}' not found."
                ),
            }

        chunks = []

        for point in points:

            payload = point.payload or {}

            chunks.append(
                {
                    "content": payload.get(
                        "content",
                        "",
                    ),
                    "page": payload.get(
                        "page",
                        0,
                    ),
                    "chunk_index": payload.get(
                        "chunk_index",
                        0,
                    ),
                    "source": payload.get(
                        "source",
                    ),
                    "department": payload.get(
                        "department",
                    ),
                    "uploaded_by": payload.get(
                        "uploaded_by",
                    ),
                }
            )
            print("✅ GET DOCUMENT SUCCESS")
            print("TOTAL CHUNKS:", len(chunks))

        return {
            "status": "success",
            "document": source,
            "chunks": chunks,
            "total_chunks": len(chunks),
        }

    except Exception as e:
        print("\n❌ GET DOCUMENT ERROR")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))


        return {
            "status": "error",
            "message": "Failed to get document.",
            "error": str(e),
        }
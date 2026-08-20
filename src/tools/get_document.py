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
    Get information about a specific document
    from the company knowledge base.
    """

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
            limit=100,
            with_payload=True,
            with_vectors=False,
        )

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

        return {
            "status": "success",
            "document": source,
            "chunks": chunks,
            "total_chunks": len(chunks),
        }

    except Exception as e:

        return {
            "status": "error",
            "message": "Failed to get document.",
            "error": str(e),
        }
from langchain_core.tools import tool


@tool
def reindex_document(
    document_id: str,
):
    """
    Re-index an existing document.
    """

    return {
        "status": "success",
        "message": "Re-index tool called",
    }
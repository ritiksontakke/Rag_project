from langchain_core.tools import tool


@tool
def get_document(
    document_id: str,
):
    """
    Get document information.
    """

    return {
        "status": "success",
        "message": "Get document tool called",
    }
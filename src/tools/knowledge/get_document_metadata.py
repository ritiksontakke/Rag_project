from langchain_core.tools import tool


@tool
def get_document_metadata(
    document_id: str,
):
    """
    Get document metadata.
    """

    return {
        "status": "success",
        "message": "Metadata tool called",
    }
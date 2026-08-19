from langchain_core.tools import tool

@tool
def delete_document(
    document_id: str,
):
    """
    Delete a document from the knowledge base.
    """

    return {
        "status": "success",
        "message": "Delete tool called",
    }
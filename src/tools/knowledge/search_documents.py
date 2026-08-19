from langchain_core.tools import tool


@tool
def search_documents(
    query: str,
):
    """
    Search the knowledge base.
    """

    return {
        "status": "success",
        "message": "Search tool called",
    }
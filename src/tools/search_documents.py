from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.rag.retrieval.pipeline import retrieval_pipeline


@tool("search_documents")
def search_documents(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Search the company knowledge base for information relevant to the
    user's query and return the most relevant document content.

    Access Control:
    - This tool is available to all authenticated user roles, including
      administrators, managers, and employees.
    - There is no role-based restriction on searching documents.
    - Search results must always be restricted to the authenticated
      user's department.

    Search Behavior:
    - Use this tool when the user asks a question that may be answered
      using information stored in the company knowledge base.
    - Search the knowledge base using the user's query and retrieve the
      most relevant document chunks.
    - Do not invent, assume, or fabricate information that is not found
      in the retrieved documents.
    - The retrieved content should be used to provide an accurate,
      concise answer to the user's question.
    - Include relevant document metadata such as source, page, and
      relevance score when available.

    Department Isolation:
    - Only search and return information belonging to the user's
      authenticated department.
    - Never retrieve or expose information from another department.

    Query Requirement:
    - The query should contain the user's actual question or information
      they are looking for.
    - Pass the user's question directly or convert it into a clear
      search query when necessary.

    No Results:
    - If no relevant information is found, clearly inform the user that
      no relevant information was found in their department's knowledge
      base.
    - Do not fabricate an answer when the knowledge base does not contain
      sufficient information.

    Error Handling:
    - If the knowledge base search fails, return a clear and
      professional error message without exposing unnecessary internal
      implementation details.

    Args:
        query:
            The user's question or search request. This is used to find
            relevant information in the company knowledge base.

        runtime:
            Runtime context containing the authenticated user's
            department. The department is used to ensure that search
            results remain isolated to the user's department.

    Returns:
        A response containing the most relevant document chunks found
        in the user's department, including their content and available
        metadata such as source, page, and relevance score.
    """

    print("\n🔥 SEARCH_DOCUMENTS TOOL CALLED")
    print("QUERY:", query)
    print(
        "DEPARTMENT:",
        runtime.context.department,
    )

    try:

        results = retrieval_pipeline(
            query=query,
            department=runtime.context.department,
            limit=5,
        )

        print(
            "🔥 RETRIEVAL RESULTS:",
            len(results),
        )

        documents = []

        for result in results:

            documents.append(
                {
                    "content": result.get(
                        "content",
                        "",
                    ),
                    "page": result.get(
                        "page",
                        0,
                    ),
                    "source": result.get(
                        "source",
                    ),
                    "score": result.get(
                        "score",
                    ),
                }
            )

        if not documents:

            return {
                "status": "not_found",
                "message": (
                    "No relevant documents were found "
                    "in your department's knowledge base."
                ),
                "results": [],
            }

        return {
            "status": "success",
            "results": documents,
        }

    except Exception as e:

        # IMPORTANT: temporary debugging
        print("\n❌ SEARCH DOCUMENTS ERROR")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))

        return {
            "status": "error",
            "message": "Unable to search the knowledge base.",
            "results": [],
            "error": str(e),
        }
from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.rag.retrieval.pipeline import retrieval_pipeline


@tool("search_documents")
def search_documents(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Search the authenticated user's department-specific company
    knowledge base for information relevant to the user's query.

    The search must be meaning-based and tolerant of normal user input
    errors.

    QUERY UNDERSTANDING:
    - The user may make spelling mistakes, typing mistakes, incomplete
      words, missing characters, grammatical mistakes, abbreviations,
      singular/plural variations, or informal phrasing.
    - Do not require an exact spelling match.
    - Do not require an exact phrase match.
    - Interpret the user's intended meaning from the complete query.
    - Important words and concepts should be considered independently
      as well as in combination.
    - The retrieval system should find semantically similar and
      contextually relevant document content even when the wording in
      the document differs from the user's wording.
    - Obvious spelling or typing errors should not prevent relevant
      documents from being retrieved.
    - Do not expose internal query correction or normalization details
      to the user.

    RETRIEVAL:
    - Search the company knowledge base first.
    - Retrieve multiple potentially relevant document chunks.
    - Rank results by relevance.
    - Do not discard a potentially relevant result only because the
      wording or spelling differs from the query.
    - Prefer content that matches the user's intended meaning.
    - Search only within the authenticated user's department.

    COMPANY DATA:
    - Company documents are the authoritative source for
      company-specific policies, procedures, benefits, employment
      information, compensation, leave, hiring, termination, and
      other internal information.
    - Never invent or assume company-specific information.
    - Never use external knowledge inside this tool.
    - If relevant company information cannot be found, return no
      relevant results so the knowledge agent can handle the
      missing-information case.

    ACCESS CONTROL:
    - Results must always be restricted to the authenticated user's
      department.
    - Never return documents belonging to another department.

    ERROR HANDLING:
    - If the search fails, return a clear error response without
      exposing unnecessary internal implementation details.

    Args:
        query:
            The user's original question or search request. The search
            system should interpret the intended meaning of the query
            and retrieve semantically or contextually relevant company
            documents.

        runtime:
            Runtime context containing the authenticated user's
            department.

    Returns:
        A response containing relevant company document chunks and
        available metadata such as source, page, department, and
        relevance score.
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
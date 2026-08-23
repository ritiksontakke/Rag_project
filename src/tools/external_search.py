from langchain.tools import tool
from langchain_tavily import TavilySearch


tavily_search = TavilySearch(
    max_results=5,
)


@tool("external_search")
def external_search(query: str):
    """
    Search external web sources using Tavily.

    This tool must only be used after the user has
    explicitly given permission for external search.
    """

    print("\n" + "=" * 60)
    print(" EXTERNAL SEARCH TOOL CALLED")
    print("QUERY:", query)
    print("=" * 60)

    try:
        result = tavily_search.invoke({
            "query": query
        })

        print("\n EXTERNAL SEARCH RESULT:")
        print(result)

        return result

    except Exception as e:

        print("\n EXTERNAL SEARCH ERROR")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))

        return {
            "status": "error",
            "message": "Unable to search external sources.",
        }
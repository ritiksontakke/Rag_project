from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.utils.model import get_model , getKnowledsubagent
from src.access_control.permission_manager import get_allowed_tools
from src.tools.external_search import external_search

@tool("knowledgeBaseAgent")
def knowledgeAgent(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Knowledge Base Agent.

    Uses the company knowledge base to answer user questions.
    The agent must call search_documents before answering.
    """

    role = runtime.context.role

    tools = get_allowed_tools(role)
    if runtime.context.external_search_allowed:
        tools = tools + [external_search]

    if runtime.context.external_search_allowed:

        print("\n========== EXTERNAL SEARCH FLOW ==========")
        print("EXTERNAL QUERY:", query)

        try:
            result = external_search.invoke({
                "query": query
            })

            print("\nEXTERNAL SEARCH RESULT:")
            print(result)

            return str(result)

        except Exception as e:

            print("\nEXTERNAL SEARCH ERROR:")
            print(repr(e))

            return "Unable to search external sources."

    print(
        "\n========== KNOWLEDGE AGENT =========="
    )

    if not tools:
            return f"Permission denied. No tools are available for role '{role}'."

    knowled_system_prompt = getKnowledsubagent(
        "KnowledgeAgent"
    )

    knowledgebase_agent = create_agent(
        model=get_model(),
        tools=tools,
        context_schema=UserContext,
        system_prompt=knowled_system_prompt,
    )

    result = knowledgebase_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        },
        context=runtime.context,
    )

    print(
        "\n========== AGENT MESSAGES =========="
    )

    for message in result["messages"]:

        print(
            "\nTYPE:",
            type(message).__name__,
        )

        print(
            "CONTENT:",
            getattr(
                message,
                "content",
                None,
            ),
        )

        print(
            "TOOL CALLS:",
            getattr(
                message,
                "tool_calls",
                None,
            ),
        )

    return result["messages"][-1].content
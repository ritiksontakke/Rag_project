from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.utils.model import get_model , getKnowledsubagent
from src.tools.search_documents import search_documents
from src.access_control.permission_manager import get_allowed_tools


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
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

from src.schemas.user_schemas import UserContext
from src.utils.model import get_model, getKnowledsubagent
from src.access_control.permission_manager import get_allowed_tools


@tool("knowledgeBaseAgent")
def knowledgeAgent(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Knowledge Base Agent.

    Searches the company's internal knowledge base first.

    If relevant company information is found:
    - Answer using company documents only.
    - Do not use external sources.

    If relevant company information is not found:
    - Do not search external sources automatically.
    - Ask the user for permission to search external sources.

    External searching is handled separately by externalSearchAgent.
    """

    role = runtime.context.role

    tools = get_allowed_tools(role)

    print("\n========== KNOWLEDGE AGENT ==========")
    print("QUERY:", query)

    if not tools:
        return (
            f"Permission denied. No tools are available "
            f"for role '{role}'."
        )

    knowledge_system_prompt = getKnowledsubagent(
        "KnowledgeAgent"
    )

    knowledgebase_agent = create_agent(
        model=get_model(),
        tools=tools,
        context_schema=UserContext,
        system_prompt=knowledge_system_prompt,
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

    messages = result.get("messages", [])

    if not messages:
        return (
            "I couldn't find relevant information "
            "in the company documents."
        )

    return messages[-1].content
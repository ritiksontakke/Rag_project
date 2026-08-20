from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.agents.middleware import ModelCallLimitMiddleware

from src.schemas.user_schemas import UserContext
from src.utils.model import get_model
from src.tools.search_documents import search_documents


@tool("knowledgeBaseAgent")
def knowledgeAgent(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Knowledge Base Agent.

    Uses the company knowledge base to answer user questions.

    The agent MUST call search_documents before generating
    the final answer.
    """

    context = runtime.context

    # -----------------------------------------
    # ONLY knowledge-base search tool
    # -----------------------------------------

    knowledge_tools = [
        search_documents,
    ]

    print(
        "\n========== KNOWLEDGE AGENT =========="
    )

    print(
        "TOOLS:",
        [tool.name for tool in knowledge_tools],
    )

    # -----------------------------------------
    # System prompt
    # -----------------------------------------

    system_prompt = """
You are the Company Knowledge Base Agent.

You answer questions ONLY from the company's
internal knowledge base.

MANDATORY WORKFLOW:

STEP 1:
For EVERY user question, you MUST call the
search_documents tool.

DO NOT answer before calling the tool.

STEP 2:
Read the complete result returned by
search_documents.

STEP 3:
If relevant information exists in the returned
documents, answer using ONLY that information.

STEP 4:
If the returned documents do not contain enough
information to answer the question, say:

"I could not find relevant information in your
department's knowledge base."

IMPORTANT:

- Never answer from your general knowledge.
- Never guess.
- Never invent information.
- Never ask unnecessary clarification questions.
- Never use information that was not returned by
  search_documents.
- The retrieved company documents are the only
  source of truth.

Do not mention tools, Qdrant, embeddings, retrieval,
agents, or internal implementation details.

Return only the final answer.
"""

    # -----------------------------------------
    # Create agent
    # -----------------------------------------

    knowledgebase_agent = create_agent(
        model=get_model(),
        tools=knowledge_tools,
        middleware=[
            ModelCallLimitMiddleware(
                thread_limit=10,
                run_limit=5,
            ),
        ],
        context_schema=UserContext,
        system_prompt=system_prompt,
    )

    # -----------------------------------------
    # Invoke
    # -----------------------------------------

    result = knowledgebase_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        },
        context=context,
    )

    # -----------------------------------------
    # DEBUG
    # -----------------------------------------

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
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

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
    The agent must call search_documents before answering.
    """

    context = runtime.context

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

    system_prompt = """
You are the Company Knowledge Base Agent.

You answer questions ONLY using information returned
by the search_documents tool.

MANDATORY WORKFLOW:

1. For EVERY user question, call search_documents first.
2. Read the complete tool result.
3. Identify the retrieved content directly relevant
   to the user's question.
4. Answer ONLY from the relevant retrieved content.
5. If the retrieved content does not contain enough
   information, respond exactly:

"I could not find relevant information in your department's knowledge base."

KNOWLEDGE BASE RULES:

- The retrieved company documents are the only source of truth.
- Never use your general knowledge.
- Never guess.
- Never invent information.
- Do not combine unrelated retrieved chunks.
- Ignore chunks that discuss a different topic.
- Prefer the highest-scoring retrieved result that directly answers the question.
- If multiple relevant chunks provide complementary information,
  they may be combined.
- If relevant chunks conflict, clearly state that the documents
  contain conflicting information.
- Keep the final answer concise.

STRICT SOURCE RULES:

- Do not add explanations that are not explicitly present in the retrieved content.
- Do not expand abbreviations unless the expansion appears in the retrieved content.
- Do not add definitions in parentheses.
- Do not add examples from general knowledge.
- Do not add technical details that are not present in the retrieved content.
- Do not infer additional meaning from the retrieved content.
- If the retrieved document contains a direct answer, stay as close as possible to that answer.
- You may remove unrelated information, but you must not add new information.

SOURCE LANGUAGE RULES:

- Preserve the language of the relevant retrieved content.
- If the relevant content is Marathi, answer in Marathi.
- If the relevant content is Hindi, answer in Hindi.
- If the relevant content is English, answer in English.
- If the relevant content is mixed-language, preserve the natural mixed-language style.
- Do not translate unless explicitly asked.

Do not mention tools, Qdrant, embeddings, retrieval,
agents, or internal implementation details.

Return ONLY the final answer.
"""

    knowledgebase_agent = create_agent(
        model=get_model(),
        tools=knowledge_tools,
        context_schema=UserContext,
        system_prompt=system_prompt,
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
        context=context,
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
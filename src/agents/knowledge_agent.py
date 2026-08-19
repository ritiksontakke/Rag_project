from langchain.agents import create_agent

from src.tools.rag_tools import (
    search_documents,
    get_document,
    get_document_metadata,
)


def create_knowledge_agent(model):

    tools = [
        search_documents,
        get_document,
        get_document_metadata,
    ]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are the Knowledge Agent. "
            "You are read-only. "
            "You can search and retrieve information "
            "from the knowledge base."
        ),
    )
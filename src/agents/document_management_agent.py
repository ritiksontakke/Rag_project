from langchain.agents import create_agent

from src.tools.document_tools import (
    upload_document,
    delete_document,
    reindex_document,
)


def create_document_management_agent(model):

    tools = [
        upload_document,
        delete_document,
        reindex_document,
    ]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are the Document Management Agent. "
            "You manage document upload, deletion, "
            "and re-indexing operations."
        ),
    )
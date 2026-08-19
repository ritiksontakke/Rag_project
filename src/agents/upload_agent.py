from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
)

from src.schemas.user_schemas import UserContext
from src.utils.model import get_model
from src.access_control.permission_manager import (
    get_allowed_tools,
)


def get_document_upload_agent(
    context: UserContext,
):
    """
    Create the Document Upload Agent.

    Only managers and administrators can
    access the upload_document tool.
    """

    role = context.role

    # Get tools allowed for this role
    tools = get_allowed_tools(role)

    # Only upload_document tool
    upload_tools = [
        current_tool
        for current_tool in tools
        if current_tool.name == "upload_document"
    ]

    # Second layer RBAC
    if not upload_tools:
        raise PermissionError(
            "Document upload is available only "
            "to managers and administrators."
        )

    document_agent = create_agent(
        model=get_model(),
        tools=upload_tools,
        middleware=[
            ModelCallLimitMiddleware(
                thread_limit=10,
                run_limit=5,
            ),
        ],
        context_schema=UserContext,
        system_prompt=(
            "You are the Document Upload Agent. "
            "Your responsibility is to upload and "
            "ingest PDF documents. "
            "Use the upload_document tool."
        ),
    )

    return document_agent
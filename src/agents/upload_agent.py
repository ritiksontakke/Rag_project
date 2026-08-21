from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
)

from src.schemas.user_schemas import UserContext
from src.utils.model import get_model, getuploadsubagent
from src.access_control.permission_manager import (
    get_allowed_tools,
)


@tool("uploadDocumentAgent")
def uploadDocumentAgent(
    query: str,
    runtime: ToolRuntime[UserContext],
):
    """
    Document Upload Agent.

    Acts as the document-upload sub-agent of the
    main orchestrator agent.

    Responsibilities:
    - Handle document upload requests.
    - Verify that the authenticated user's role
      permits document uploads.
    - Select the upload_document tool allowed for
      the user's role.
    - Delegate PDF ingestion to the upload_document tool.
    - Return the result of the document ingestion process.

    Access Control:
    - Only users with the manager or admin role can
      upload documents.
    - Role-based access control is checked before
      the upload tool is exposed to the agent.
    - A second permission check ensures that the
      upload_document tool is actually available.

    Args:
        query:
            Natural-language document upload request.

        runtime:
            LangChain runtime containing the authenticated
            user's UserContext.

    Returns:
        str:
            Result returned by the document upload agent,
            or a permission-denied message.
    """

    context = runtime.context

    role = context.role

    # -----------------------------------------
    # Get tools allowed for the user's role
    # -----------------------------------------

    tools = get_allowed_tools(role)

    if not tools:
        return (
            f"Permission denied. "
            f"No tools are available for role '{role}'."
        )

    # -----------------------------------------
    # Select ONLY upload_document tool
    # -----------------------------------------


    upload_tools = [
        current_tool
        for current_tool in tools
        if current_tool.name == "upload_document"
    ]

    # -----------------------------------------
    # Second-layer RBAC
    # -----------------------------------------

    if not upload_tools:
        return (
            "Permission denied. Document upload is "
            "available only to managers and administrators."
        )

    # -----------------------------------------
    # Create upload sub-agent
    # -----------------------------------------
    upload_system_prompt = getuploadsubagent(
        "UploadDocumentAgent"
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

        system_prompt =upload_system_prompt
    )

    # -----------------------------------------
    # Execute sub-agent
    # -----------------------------------------

    result = document_agent.invoke(
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

    print("\n========== UPLOAD AGENT MESSAGES ==========")

    for message in result["messages"]:
        print("\nTYPE:", type(message).__name__)
        print("CONTENT:", getattr(message, "content", None))
        print("TOOL CALLS:", getattr(message, "tool_calls", None))

    return result["messages"][-1].content
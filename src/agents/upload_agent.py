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
from src.tools.upload_document import upload_document
from src.memory.checkpointer import checkpointer

def uploadDocumentAgent(context: UserContext):

    # =====================================
    # ROLE BASED ACCESS
    # =====================================

    if context.role not in {"admin", "manager"}:
        raise PermissionError(
            "Document upload is restricted to "
            "administrators and managers."
        )

    return create_agent(
        model=get_model(),
        tools=[upload_document],
        system_prompt= getuploadsubagent("UploadDocumentAgent"),
        checkpointer=checkpointer,
    )
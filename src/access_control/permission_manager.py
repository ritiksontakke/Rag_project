from src.access_control.permission import ROLE_TOOLS
from src.access_control.tool_registry import ALL_TOOLS


def get_allowed_tools(role: str):
    """
    Returns the list of tools allowed for the given role.
    """

    tool_names = ROLE_TOOLS.get(role.lower(), [])
    print("Allowed tool names:", tool_names)
    return [
        ALL_TOOLS[name]
        for name in tool_names
        if name in ALL_TOOLS
    ]


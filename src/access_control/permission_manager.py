from src.access_control.permission import ROLE_TOOLS
from src.access_control.tool_registry import ALL_TOOLS


def get_allowed_tools(role: str):

    tool_names = ROLE_TOOLS.get(
        role.lower(),
        [],
    )

    return [
        ALL_TOOLS[name]
        for name in tool_names
        if name in ALL_TOOLS
    ]


def has_tool_access(
    role: str,
    tool_name: str,
) -> bool:

    tool_names = ROLE_TOOLS.get(
        role.lower(),
        [],
    )

    return tool_name in tool_names
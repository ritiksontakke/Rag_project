from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.schemas.user_schemas import (
    KnowledgeRequest,
    UserContext,
)

from src.auth.oauth import get_current_user
from src.utils.model import langfuse_handler
from src.agents.Orchestrator_Agent import (
    orchestratorAgent,
)


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


@router.post("/ask")
async def ask_knowledge(
    request: KnowledgeRequest,
    current_user=Depends(get_current_user),
):

    try:

        query = request.query.strip()

        # -----------------------------------------
        # Get thread ID
        # -----------------------------------------

        thread_id = current_user["thread_id"]

        # -----------------------------------------
        # Create orchestrator
        # -----------------------------------------

        agent = orchestratorAgent()

        # -----------------------------------------
        # Thread configuration
        # -----------------------------------------

        config = {
            "configurable": {
                "thread_id": thread_id,
            },
            "callbacks": [langfuse_handler],
        }

        # -----------------------------------------
        # Check previous conversation
        # -----------------------------------------

        state = agent.get_state(config)

        previous_messages = []

        if state:
            previous_messages = state.values.get(
                "messages",
                [],
            )

        # -----------------------------------------
        # Check YES permission
        # -----------------------------------------

        is_yes = query.lower() in {
            "yes",
            "y",
            "haan",
            "ha",
            "yes please",
            "sure",
            "okay",
            "ok",
            "go ahead",
            "search externally",
            "search the web",
        }

        external_search_allowed = False

        original_query = query

        if is_yes and previous_messages:

            # Check whether previous assistant
            # asked for external search permission

            previous_answer = ""

            for message in reversed(previous_messages):

                message_type = getattr(
                    message,
                    "type",
                    None,
                )

                if message_type == "ai":

                    previous_answer = getattr(
                        message,
                        "content",
                        "",
                    )

                    break

            waiting_for_external = (
                isinstance(previous_answer, str)
                and
                "would you like me to search external sources"
                in previous_answer.lower()
            )

            if waiting_for_external:

                external_search_allowed = True

                # Find original unanswered question
                for message in reversed(previous_messages):

                    message_type = getattr(
                        message,
                        "type",
                        None,
                    )

                    if message_type == "human":

                        original_query = message.content

                        break

        # -----------------------------------------
        # Build user context
        # -----------------------------------------

        context = UserContext(
            id=current_user["id"],
            full_name=current_user["full_name"],
            email=current_user["email"],
            role=current_user["role"],
            department=current_user["department"],
            external_search_allowed=(
                external_search_allowed
            ),
        )

        # -----------------------------------------
        # Debug
        # -----------------------------------------

        print(
            "\n========== KNOWLEDGE REQUEST =========="
        )

        print("USER QUERY:", query)

        print("THREAD ID:", thread_id)

        print(
            "EXTERNAL SEARCH ALLOWED:",
            external_search_allowed,
        )

        print(
            "ORIGINAL QUERY:",
            original_query,
        )

        # -----------------------------------------
        # Invoke orchestrator
        # -----------------------------------------

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": original_query,
                    }
                ]
            },
            context=context,
            config=config,
        )

        # -----------------------------------------
        # Debug messages
        # -----------------------------------------

        print(
            "\n========== ORCHESTRATOR MESSAGES =========="
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

        # -----------------------------------------
        # Final response
        # -----------------------------------------

        return {
            "answer": result["messages"][-1].content,
            "department": context.department,
        }

    except Exception as e:

        print(
            "Knowledge endpoint error:",
            repr(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
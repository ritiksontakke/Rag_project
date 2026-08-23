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
from src.tools.external_search import external_search


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


# =========================================================
# YES / NO
# =========================================================

YES_WORDS = {
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

NO_WORDS = {
    "no",
    "n",
    "nahi",
    "nah",
    "no thanks",
    "not now",
    "cancel",
}


# =========================================================
# KNOWLEDGE ASK
# =========================================================

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

            previous_messages = (
                state.values.get(
                    "messages",
                    [],
                )
                or []
            )

        # -----------------------------------------
        # Normalize query
        # -----------------------------------------

        normalized_query = query.lower().strip()

        is_yes = normalized_query in YES_WORDS

        is_no = normalized_query in NO_WORDS

        # -----------------------------------------
        # Find previous assistant message
        # -----------------------------------------

        previous_answer = ""

        for message in reversed(previous_messages):

            message_type = getattr(
                message,
                "type",
                None,
            )

            if message_type == "ai":

                content = getattr(
                    message,
                    "content",
                    "",
                )

                if isinstance(content, str):
                    previous_answer = content

                break

        # -----------------------------------------
        # Check whether external search
        # confirmation is pending
        # -----------------------------------------

        waiting_for_external = (
            isinstance(previous_answer, str)
            and
            "would you like me to search external sources"
            in previous_answer.lower()
        )

        # =================================================
        # YES
        # =================================================

        if is_yes and waiting_for_external:

            # -----------------------------------------
            # Find ORIGINAL USER QUESTION
            # -----------------------------------------

            original_query = None

            for message in reversed(previous_messages):

                message_type = getattr(
                    message,
                    "type",
                    None,
                )

                if message_type == "human":

                    content = getattr(
                        message,
                        "content",
                        "",
                    )

                    if (
                        isinstance(content, str)
                        and content.strip().lower()
                        not in YES_WORDS
                        and content.strip().lower()
                        not in NO_WORDS
                    ):
                        original_query = content.strip()
                        break

            # -----------------------------------------
            # Safety check
            # -----------------------------------------

            if not original_query:

                return {
                    "answer": (
                        "I couldn't determine which question "
                        "you want me to search externally. "
                        "Please ask your question again."
                    ),
                    "department": current_user["department"],
                }

            # -----------------------------------------
            # DIRECT EXTERNAL SEARCH
            #
            # IMPORTANT:
            # DO NOT CALL ORCHESTRATOR HERE
            # -----------------------------------------

            print(
                "\n========== EXTERNAL SEARCH CONFIRMED =========="
            )

            print(
                "USER QUERY:",
                query,
            )

            print(
                "ORIGINAL QUERY:",
                original_query,
            )

            try:

                result = external_search.invoke(
                    {
                        "query": original_query
                    }
                )

                print(
                    "\n========== EXTERNAL SEARCH RESULT =========="
                )

                print(result)

                return {
                    "answer": str(result),
                    "department": current_user["department"],
                }

            except Exception as e:

                print(
                    "\n========== EXTERNAL SEARCH ERROR =========="
                )

                print(
                    repr(e)
                )

                return {
                    "answer": (
                        "I’m unable to search external sources "
                        "right now. Please try again later."
                    ),
                    "department": current_user["department"],
                }

        # =================================================
        # NO
        # =================================================

        if is_no and waiting_for_external:

            print(
                "\n========== EXTERNAL SEARCH DECLINED =========="
            )

            return {
                "answer": (
                    "Understood. I’ll continue using only the "
                    "available company documents. "
                    "Please feel free to ask another question."
                ),
                "department": current_user["department"],
            }

        # =================================================
        # OTHER MESSAGE WHILE WAITING FOR YES / NO
        # =================================================

        if (
            waiting_for_external
            and not is_yes
            and not is_no
        ):

            return {
                "answer": (
                    "I’m still waiting for your confirmation "
                    "to search external sources. "
                    "Please reply Yes or No."
                ),
                "department": current_user["department"],
            }

        # =================================================
        # NORMAL KNOWLEDGE FLOW
        # =================================================

        print(
            "\n========== NORMAL KNOWLEDGE FLOW =========="
        )

        print(
            "USER QUERY:",
            query,
        )

        # -----------------------------------------
        # Build context
        # -----------------------------------------

        context = UserContext(
            id=current_user["id"],
            full_name=current_user["full_name"],
            email=current_user["email"],
            role=current_user["role"],
            department=current_user["department"],
            external_search_allowed=False,
        )

        # -----------------------------------------
        # Invoke orchestrator ONLY for normal query
        # -----------------------------------------

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query,
                    }
                ]
            },
            context=context,
            config=config,
        )

        # -----------------------------------------
        # Debug
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
        # Final answer
        # -----------------------------------------

        answer = result["messages"][-1].content

        return {
            "answer": answer,
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
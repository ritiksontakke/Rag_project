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

        # -----------------------------------------
        # Build typed user context
        # -----------------------------------------

        context = UserContext(
            id=current_user["id"],
            full_name=current_user["full_name"],
            email=current_user["email"],
            role=current_user["role"],
            department=current_user["department"],
        )

        # -----------------------------------------
        # Create orchestrator
        # -----------------------------------------

        agent = orchestratorAgent()

        # -----------------------------------------
        # Invoke orchestrator
        # -----------------------------------------

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request.query,
                    }
                ]
            },
            context=context,
            config={
                "callbacks": [langfuse_handler],
            }
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
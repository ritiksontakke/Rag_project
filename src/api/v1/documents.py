import os
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from src.auth.oauth import get_current_user
from src.agents.upload_agent import uploadDocumentAgent
from src.schemas.user_schemas import UserContext
from src.utils.model import langfuse_handler
import uuid

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    department: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):

    # =====================================
    # SECURITY LAYER 1 — AUTHORIZATION
    # =====================================

    role = current_user.get("role")

    if role not in {"admin", "manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "UPLOAD_NOT_ALLOWED",
                "message": (
                    "Document upload is restricted "
                    "to administrators and managers."
                ),
            },
        )

    # =====================================
    # FILE VALIDATION
    # =====================================

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": "Only PDF files are allowed.",
            },
        )

    # =====================================
    # DEPARTMENT SECURITY
    # =====================================

    user_department = current_user.get(
        "department"
    )

    if not user_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "DEPARTMENT_MISSING",
                "message": (
                    "User department is not available."
                ),
            },
        )

    if (
        department.strip().lower()
        != user_department.strip().lower()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "DEPARTMENT_ACCESS_DENIED",
                "message": (
                    "You can upload documents only "
                    "for your assigned department."
                ),
            },
        )

    # =====================================
    # USER CONTEXT
    # =====================================

    try:

        context = UserContext(
            id=current_user["id"],
            full_name=current_user["full_name"],
            email=current_user["email"],
            role=current_user["role"],
            department=current_user["department"],
        )

    except KeyError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_USER_CONTEXT",
                "message": (
                    "Authenticated user information "
                    "is incomplete."
                ),
            },
        ) from e

    # =====================================
    # TEMPORARY FILE
    # =====================================

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp_file:

        temp_file.write(
            await file.read()
        )

        temp_file_path = temp_file.name

    try:

        # =====================================
        # MAIN ORCHESTRATOR
        # =====================================

        agent = uploadDocumentAgent(context)

        # =====================================
        # SEND REQUEST TO MAIN AGENT
        # =====================================
        thread_id = f"document-upload-{current_user['id']}-{uuid.uuid4()}"

        print("🔥 UPLOAD THREAD:", thread_id)

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Upload this PDF document.\n\n"
                            f"File path: {temp_file_path}\n"
                            f"Department: {user_department}\n"
                            f"File name: {file.filename}"
                        ),
                    }
                ]
            },
            context=context,
            config={
                "configurable": {
                    "thread_id": thread_id,
                },
                "callbacks": [langfuse_handler],
            }
        )

        # =====================================
        # FINAL AGENT RESPONSE
        # =====================================

        # answer = result[
        #     "messages"
        # ][-1].content

        return {
            "status": "success",
            "message": "Document uploaded successfully.",
        }

    except PermissionError as e:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "UPLOAD_PERMISSION_DENIED",
                "message": str(e),
            },
        ) from e

    except Exception as e:
        import traceback

        print("\n🔥🔥 DOCUMENT UPLOAD FAILED 🔥🔥")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        traceback.print_exc()
        print("🔥🔥 END UPLOAD ERROR 🔥🔥\n")

        # Log e internally in production.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DOCUMENT_UPLOAD_FAILED",
                "message": (
                    "Unable to process the document "
                    "upload."
                ),
            },
        ) from e

    finally:

        # =====================================
        # CLEAN TEMP FILE
        # =====================================

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
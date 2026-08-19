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
from src.agents.upload_agent import get_document_upload_agent
from src.schemas.user_schemas import UserContext


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
            detail=(
                "Document upload is restricted "
                "to administrators and managers."
            ),
        )

    # =====================================
    # FILE VALIDATION
    # =====================================

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    # =====================================
    # DEPARTMENT SECURITY
    # =====================================

    user_department = current_user.get("department")

    if not user_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User department is not available.",
        )

    if department.lower() != user_department.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can upload documents only for "
                "your assigned department."
            ),
        )

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
        # USER CONTEXT
        # =====================================

        context = UserContext(
            id=current_user["id"],
            full_name=current_user["full_name"],
            email=current_user["email"],
            role=current_user["role"],
            department=current_user["department"],
        )

        # =====================================
        # DOCUMENT UPLOAD AGENT
        # =====================================

        document_agent = get_document_upload_agent(
            context=context,
        )

        # =====================================
        # RUN AGENT
        # =====================================

        result = document_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Upload this PDF file: "
                            f"{temp_file_path}. "
                            f"Department: "
                            f"{user_department}"
                        ),
                    }
                ]
            },
            context=context,
        )

        return {
            "message": (
                "Document uploaded and "
                "ingestion started successfully."
            ),
            "file_name": file.filename,
            "department": user_department,
            "result": result["messages"][-1].content,
        }

    finally:

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
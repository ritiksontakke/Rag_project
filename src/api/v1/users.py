from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.user_schemas import (
    UserLogin,
    UserResponse,
    UserSignup,
)
from src.services.auth_service import AuthService
from src.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    try:
        return service.register_user(
            user_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.post(
    "/login",
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    try:
        return service.login_user(
            user_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )
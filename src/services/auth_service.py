from sqlalchemy.orm import Session

from src.auth.auth_handler import create_access_token
from src.repositories.user_repository import UserRepository
from src.schemas.user_schemas import UserLogin
from src.utils.password import verify_password


class AuthService:

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def login_user(
        self,
        user_data: UserLogin,
    ) -> dict:

        user = self.user_repository.get_by_email(
            user_data.email
        )

        if not user:
            raise ValueError(
                "Invalid email or password"
            )

        if not verify_password(
            user_data.password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid email or password"
            )

        token_data = {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "department": user.department,
        }

        access_token = create_access_token(
            token_data
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
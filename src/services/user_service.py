from sqlalchemy.orm import Session

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user_schemas import UserSignup
from src.utils.password import hash_password


class UserService:

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register_user(
        self,
        user_data: UserSignup,
    ) -> User:

        existing_user = (
            self.user_repository.get_by_email(
                user_data.email
            )
        )

        if existing_user:
            raise ValueError(
                "Email already registered"
            )

        hashed_password = hash_password(
            user_data.password
        )

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=hashed_password,
            role="employee",
            department=user_data.department,
        )

        return self.user_repository.create(user)
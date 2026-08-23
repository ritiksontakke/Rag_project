from pydantic import BaseModel, EmailStr, Field, model_validator
from uuid import UUID
from dataclasses import dataclass

class UserSignup(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=128,
    )

    department: str = Field(
        min_length=2,
        max_length=100,
    )

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

        return self

class UserContext(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str
    department: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str
    department: str

class KnowledgeRequest(BaseModel):
    query: str

class UserContext(BaseModel):

    id: UUID

    full_name: str

    email: EmailStr

    role: str

    department: str

    file_path: str | None = None

    external_search_allowed:bool = False

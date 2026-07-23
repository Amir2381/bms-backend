from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr


class UserLogin(BaseModel):
    email: str
    password: str = Field(min_length=8)


class UserCreate(UserBase):
    password: str = Field(min_length=3)


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

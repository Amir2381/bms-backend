from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserLogin(BaseModel):
    email: str
    password: str = Field(min_length=3)


class UserCreate(UserBase):
    password: str = Field(min_length=3)


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

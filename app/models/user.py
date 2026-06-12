from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=3)


class UserCreate(UserBase):
    password: str = Field(min_length=3)


class UserResponse(UserBase):
    pass

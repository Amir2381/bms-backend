from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=3)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=3)


class UserResponse(BaseModel):
    username: str
    email: EmailStr

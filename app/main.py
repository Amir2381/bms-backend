from fastapi import FastAPI
from models.user import UserResponse, UserCreate

app = FastAPI()


@app.post("/user/register", response_model=UserResponse)
def register_user(user: UserCreate):
    return UserResponse(email=user.email, username=user.username)

from pydantic import BaseModel, Field


class Student(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    age = int
    major = str

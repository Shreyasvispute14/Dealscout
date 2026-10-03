from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: str
    name: str
    email: str
    role: str = "student"


class LoginResponse(BaseModel):
    user: User
    message: str
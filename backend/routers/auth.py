import secrets

from fastapi import APIRouter, Cookie, HTTPException, Response

from models.auth import LoginRequest, LoginResponse, User

router = APIRouter()

DEMO_USER = User(id="student-demo-001", name="SPPU Student", email="student@sppu-project.local")
DEMO_PASSWORD = "demo123"
SESSION_COOKIE = "sppudeal_session"
sessions: dict[str, User] = {}


@router.post("/login", response_model=LoginResponse)
async def login(input: LoginRequest, response: Response):
    if input.email.lower().strip() != DEMO_USER.email or input.password != DEMO_PASSWORD:
        raise HTTPException(status_code=401, detail="Use the demo credentials shown on the login page")
    token = secrets.token_urlsafe(24)
    sessions[token] = DEMO_USER
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", max_age=60 * 60 * 8)
    return LoginResponse(user=DEMO_USER, message="Welcome back")


@router.get("/me", response_model=User | None)
async def current_user(sppudeal_session: str | None = Cookie(default=None)):
    user = sessions.get(sppudeal_session or "")
    return user


@router.post("/logout")
async def logout(response: Response, sppudeal_session: str | None = Cookie(default=None)):
    if sppudeal_session:
        sessions.pop(sppudeal_session, None)
    response.delete_cookie(SESSION_COOKIE)
    return {"message": "Logged out"}
from fastapi import APIRouter
from fastapi import Request, Response, Depends
from fastapi.encoders import jsonable_encoder
from schemas import UserBody, UserInfo, SuccessMsg, Csrf
from database import db_signup, db_login
from auth_utils import AuthJwtCsrf
from fastapi_csrf_protect import CsrfProtect


router = APIRouter()
auth = AuthJwtCsrf()


@router.get("/api/csrftoken", response_model=Csrf)
async def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    res = {"csrf_token": csrf_token}
    return res


@router.post("/api/register", response_model=UserInfo)
async def signup(
    request: Request, data: UserBody, csrf_protect: CsrfProtect = Depends()
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
    user = jsonable_encoder(data)
    new_user = await db_signup(user)
    return new_user


@router.post("/api/login", response_model=SuccessMsg)
async def login(
    request: Request,
    response: Response,
    data: UserBody,
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
    user = jsonable_encoder(data)
    token = await db_login(user)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="none",
        secure=True,
    )
    return {"message": "Successfully logged-in"}

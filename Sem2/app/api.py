from app.schemas import AddUser
from sqlalchemy.orm import Session
from app.db import get_db
from fastapi import Depends, APIRouter, Response, Request
from authx import AuthX, AuthXConfig
import bcrypt
salt = bcrypt.gensalt()
config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
security = AuthX(config=config)




router = APIRouter()

# @router.get("/check_user/")
# def check_user():
#     from cruds import getUsers
#     return getUsers()

@router.post("/sign-up/")
def sign_up(user: AddUser, response: Response, session: Session = Depends(get_db)):
    from app.cruds import setUser
    return setUser(user, response, session)

@router.post("/login/")
def login(user: AddUser, response: Response, session: Session = Depends(get_db)):
    from app.cruds import loginUser
    return loginUser(user, response, session)

@router.get("/users/me/", dependencies=[Depends(security.access_token_required)])
def check(request: Request, session: Session = Depends(get_db)):
    from app.cruds import checkUser
    return checkUser(request, session)

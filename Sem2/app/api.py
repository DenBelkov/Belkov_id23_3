from app.schemas import AddUser
from sqlalchemy.orm import Session
from app.db import get_db
from fastapi import Depends, APIRouter#Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from authx import AuthX, AuthXConfig
from typing import Annotated
from app.services import findShortestPath
from app.schemas import GraphRequest
import bcrypt
salt = bcrypt.gensalt()
# config = AuthXConfig()
# config.JWT_SECRET_KEY = "SECRET_KEY"
# config.JWT_ACCESS_COOKIE_NAME = "auth_token"
# config.JWT_TOKEN_LOCATION = ["cookies"]
# security = AuthX(config=config)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



router = APIRouter()

# @router.get("/check_user/")
# def check_user():
#     from cruds import getUsers
#     return getUsers()

@router.post("/sign-up/")
def sign_up(user: AddUser, session: Session = Depends(get_db)):
    from app.cruds import setUser
    return setUser(user, session)

# @router.post("/login/")
# def login(user: AddUser, session: Session = Depends(get_db)):
#     from app.cruds import loginUser
#     return loginUser(user, session)

@router.post("/login")
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_db)):
    from app.cruds import token
    return token(form_data, session)
@router.get("/users/me/")
def check(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_db)):
    from app.cruds import checkUser
    return checkUser(token, session)

@router.post("/shortest-path/")
async def shortPath(graph: GraphRequest, token: Annotated[str, Depends(oauth2_scheme)]):
    task = findShortestPath.delay(graph.model_dump())
    result = task.get(timeout=100)
    return result

from schemas import AddUser, GetUser, GraphRequest, PathResult
from sqlalchemy import create_engine
from typing import Annotated
from models import Base
from fastapi import Depends, FastAPI, APIRouter, Response, Request
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from authx import AuthX, AuthXConfig
import bcrypt

salt = bcrypt.gensalt()
config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
security = AuthX(config=config)

engine = create_engine("sqlite:///auth1.db")
conn = engine.connect()
Base.metadata.create_all(engine)


# engine = create_async_engine("sqlite+aiosqlite:///mydb.db", echo=True)
#
# new_async_session = async_sessionmaker(engine, expire_on_commit=False)
#
#
# async def get_session():
#     async with new_async_session() as session:
#         yield session
#SessionDep = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter()

# @router.get("/check_user/")
# def check_user():
#     from cruds import getUsers
#     return getUsers()

@router.post("/sign-up/")
def sign_up(user: AddUser, response: Response):
    from cruds import setUser
    return setUser(user, response)

@router.post("/login/")
def login(user: AddUser, response: Response):
    from cruds import loginUser
    return loginUser(user, response)

@router.get("/check", dependencies=[Depends(security.access_token_required)])
def check(request: Request):
    from cruds import checkUser
    return checkUser(request)

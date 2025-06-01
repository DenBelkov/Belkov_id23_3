from app.api import salt #security, config,
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User
from app.schemas import Token
#from fastapi import Response Request
import bcrypt
from app.schemas import GetUser, AddUser
import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def getUsers(session: Session):
    query = select(User)
    users = session.execute(query).scalars().all()
    return users


def get_user_by_email(email: str, session: Session):
    return (session.query(User).filter_by(email=email)).scalar()

def verify_password(password: str, hashed: bytes):
    return bcrypt.checkpw(password.encode(), hashed)

def create_access_token(data:dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# def loginUser(user: AddUser, session: Session):
#     userdata = get_user_by_email(user.email, session)
#     if bool(userdata):
#         if verify_password(user.password, userdata.password):
#             #token = create_access_token(uid=str(userdata.id))
#             #security.set_access_cookies(response=response, token=token)
#             #response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
#             access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#             token = create_access_token(
#                 data={"sub": str(userdata.id)}, expires_delta=access_token_expires
#             )
#             return GetUser(id=userdata.id, email=user.email, token=Token(access_token=token, token_type="bearer"))
#         else: return "password incorrect"
#     else:
#         return "email not in base"

def token(form_data, session: Session):
    userdata = get_user_by_email(form_data.username, session)
    if bool(userdata):
        if verify_password(form_data.password, userdata.password):
            # token = create_access_token(uid=str(userdata.id))
            # security.set_access_cookies(response=response, token=token)
            # response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = create_access_token(
                data={"sub": str(userdata.id)}, expires_delta=access_token_expires
            )
            return Token(access_token=token, token_type="bearer")
        else: return "password incorrect"
    else:
        return "email not in base"

def setUser(user: AddUser, session: Session):
    if not(bool(get_user_by_email(user.email, session))):
        newUser = User(
            #id = max(session.execute(db.select(User.id)).scalar().all()) + 1,
            #id = session.execute(db.select(db.func.max(User.id))).scalar() + 1,
            #id = session.query(db.func.max(User.id)).scalar() + 1,
            email = user.email,
            password = bcrypt.hashpw(user.password.encode(), salt)
        )
        session.add(newUser)
        session.commit()
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": newUser.id}, expires_delta=access_token_expires
        )
        #response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        #security.set_access_cookies(response=response, token=token)
        return GetUser(id = newUser.id, email= newUser.email, token=Token(access_token=token, token_type="bearer"))
    else:
        return "email already in base"

def checkUser(token , session: Session):
    id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    return {"id": id,
            "email": session.query(User.email).filter_by(id=id).scalar()}


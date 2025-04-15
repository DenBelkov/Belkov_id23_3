from app.api import security, config, salt
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User
from fastapi import Response, Request, Depends
import bcrypt
from app.schemas import GetUser, AddUser




def getUsers(session: Session):
    query = select(User)
    users = session.execute(query).scalars().all()
    return users


def get_user_by_email(email: str, session: Session):
    return (session.query(User).filter_by(email=email)).scalar()

def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed)

def loginUser(user: AddUser, response: Response, session: Session):
    userdata = get_user_by_email(user.email, session)
    if bool(userdata):
        if verify_password(user.password, userdata.password):
            token = security.create_access_token(uid=str(userdata.id))
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            return GetUser(id = userdata.id, email= userdata.email, token= token)
        else: return "password incorrect"
    else:
        return "email not in base"

def setUser(user: AddUser, response: Response, session: Session):
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
        token = security.create_access_token(uid=str(newUser.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return GetUser(id = newUser.id, email= newUser.email, token= token)
    else:
        return "email already in base"

def checkUser(request: Request, session: Session):
    id = security._decode_token(request.cookies.get("my_access_token")).sub
    return {"id": id,
            "email": session.query(User.email).filter_by(id=id).scalar()}


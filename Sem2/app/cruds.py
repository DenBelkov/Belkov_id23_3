from api import security, config, salt, engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import User
from fastapi import Response, Request
import bcrypt
from schemas import GetUser, AddUser, GraphRequest, PathResult




def getUsers():
    query = select(User)
    session = Session(engine)
    users = session.execute(query).scalars().all()
    return users


def get_user_by_email(email: str):
    session = Session(engine)
    return (session.query(User).filter_by(email=email)).scalar()

def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed)

def loginUser(user: AddUser, response: Response):
    session = Session(engine)
    userdata = (session.query(User).filter_by(email=user.email)).scalar()
    if bool(userdata):
        if verify_password(user.password, userdata.password):
            token = security.create_access_token(uid=str(userdata.id))
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            return GetUser(id = userdata.id, email= userdata.email, token= token)
        else: return "password incorrect"
    else:
        return "email not in base"

def setUser(user: AddUser, response: Response):
    session = Session(engine)
    if not(bool(get_user_by_email(user.email))):
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

def checkUser(request: Request):
    session = Session(engine)
    id = security._decode_token(request.cookies.get("my_access_token")).sub
    return {"id": id,
            "email": session.query(User.email).filter_by(id=id).scalar()}

def branch_and_bound_tsp(distance_matrix):
    n = len(distance_matrix)
    min_distance = float('inf')
    best_route = None
    def tsp(node, visited, cost, path):
        nonlocal min_distance, best_route
        if len(path) == n:
            cost += distance_matrix[node][0]
            if cost < min_distance:
                min_distance = cost
                best_route = path + [0]
            return
        for next_node in range(n):
            if next_node not in visited:
                tsp(next_node, visited | {next_node}, cost + distance_matrix[node][next_node], path + [next_node])
    tsp(0, {0}, 0, [0])
    return best_route, min_distance

def findShortestPath(graphR: GraphRequest) -> PathResult:
    graph = graphR.graph
    distance_matrix = [[10000000] * len(graph.nodes) for _ in range(len(graph.nodes))]
    for row in graph.edges:
        distance_matrix[row[0] - 1][row[1] - 1] = 1
        distance_matrix[row[1] - 1][row[0] - 1] = 1
    for i in range(len(graph.nodes)):
        distance_matrix[i][i] = 0
    ans = branch_and_bound_tsp(distance_matrix)
    return PathResult(path = list(map(lambda x: x+1, ans[0][:-1])), total_distance = float(ans[1]))
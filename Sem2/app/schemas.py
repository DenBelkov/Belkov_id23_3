from pydantic import BaseModel


class AddUser(BaseModel):
    email: str
    password: str

class Graph(BaseModel):
    nodes:list[int]
    edges:list[list[int]]


class PathResult(BaseModel):
    path: list[int]
    total_distance: float


class GraphRequest(BaseModel):
    graph: Graph

class Token(BaseModel):
    access_token: str
    token_type: str

class GetUser(BaseModel):
    id: int
    email: str
    token: Token
from fastapi import FastAPI
from app.api import router
from app.services import findShortestPath
from app.schemas import GraphRequest, PathResult
app = FastAPI()


@app.post("/shortest-path/")
def shortPath(graph: GraphRequest):
    return findShortestPath(graph)
app.include_router(router)
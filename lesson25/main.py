from fastapi import FastAPI, HTTPException
from typing import List

import database
import  models
from models import  Movies,MovieCreate

app = FastAPI()

@app.get("/")
def read_root():
    return {"message":"Welcome to the movies Crud API"}

@app.post("/movies/",response_model=Movies)
def create_movie(movie: MovieCreate):
    movie_id = database.create_movie(movie)
    return  models.Movie(id=movie_id, **movie.dict())

@app.get("/movies/",response_model=List[Movies])
def read_movies():
    return database.read_movie()

@app.put("/movies/{movie_id}",response_model=Movies)
def update_movie(movie_id: int,movie:MovieCreate):
    updated = database.update_movie(movie_id, movie)
    if not  updated:
        raise  HTTPException(status_code=404, detail="Movie not found")
    return models.(id=movie_id, **movie.dict())


@app.delete("/movies/{movie_id}",response_model=dict)
def delete_movie(movie_id: int):
    deleted = database.delete_movie(movie_id)
    if not  deleted:
        raise  HTTPException(status_code=404, detail="Movie not found")
    return {"message":"movie deleted successfully"}

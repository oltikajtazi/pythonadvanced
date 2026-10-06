from http.client import responses

from fastapi import FastAPI, HTTPException
from typing import List

import database
import models
from models import Movies,MovieCreate


app = FastAPI()
@app.get ("/")
def read_root():
    return {"message":"Welcome to the movies Crud API"}

@app.post("/movies",responses_model=Movies)
def create_movies(movie: MovieCreate):
    movie_id = database.create_movie()
    return models.Movie(id=movie_id, **movie.dict())
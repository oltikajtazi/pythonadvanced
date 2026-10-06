from pydantic import BaseModel


class MovieCreate(BaseModel):
    title:str
    director:str



class Movies(MovieCreate):
    id:int
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI



class User(BaseModel):
    id:int
    name:str
    age:int
    email:str

class Person(BaseModel):
    name:str
    age:int

class personResponse(BaseModel):
    message:str



@app.post("/users/")
async def creat_useer(user:User):
    return user
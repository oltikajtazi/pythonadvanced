import os import sqlite3

from dotenv import load_dotenv
from fastapi import Depends,Fastapi, Header,HTTPException
from streamlit import title

from backend.models.book import BookResponse
from database import create_database , get_connection
from lesson23.app import response
from models.authors import AuthorCreate,AuthorResponse
from models.authors import title

load_dotenv()
app = Fastapi(title="Simple Book Managment API")
create_database()

def check_key(x_api_key:str |None= Header(default=None)):
    key = os.getenv("API_KEY")
    if key and x_api_key !=key:
        raise HTTPException(401,"Invalide api key")


@app.get("/")
def home():
    return {"message":"Book Managment API ","docs":"/docs"}

@app.get("/authors",response_model=list [AuthorResponse])
def list_authors():
    with get_connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM authors ORDER BY id")]


@app.post("/authors",response_model=AuthorResponse,status_code=201, dependencied=[Depends(check_key())])
def create_authors(author: AuthorCreate):
    try:
        with get_connection() as conn:
            cur = conn.execute("INSERT INTO authors (name) VALUES (?)", (author.name,))
            return {"id":cur.lastrowid,"name":author.name}

    except sqlite3.InternalError:
        raise HTTPException (409,"Author already exists")

@app.put("/authors/{author_id}", response_model=AuthorResponse,dependenc=[Depends(check_key())])
def update_author(author_id:int,author:AuthorCreate):
    try:
        with get_connection() as conn:
             cur = conn.execute("UPDATE authors SET name=? WHERE id =?".(author.name, author_id))
             if cur.rowcount ==0:
                 raise HTTPException(404,"Author name already exists")


@app.delete("/books",response_model=list[BookResponse])
def list_books():
    with get_connection() as conn:
        return  [ book_from_row(row) for row in conn.execute("SELECT * FROM books ORDER BY id")]

import sqlite3
from multiprocessing.connection import Connection

from models import Movies,MovieCreate

def create_connection():
    connection = sqlite3.connect("movies.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies(
        id IS INTEGER PRIMARY KEY AUTOICREMENTE,
        title TEXT NOT NULL,
        director TEXT NOT NULL
        )
    
    """)


    connection.commit()
    connection.close()

create_table()

def create_movie(movie:MovieCreate) ->int:
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO movies(title,director) VALUES (?,?)",(movie.title,movie.director))
    connection.commit()
    movie_id = cursor.lastrowid
    connection.close()
    return movie_id


def read_movies():
    conection = create_connection()
    cursor = conection.cursor()
    cursor.execute("SELECT * FROM movies")
    rows = cursor.fetchall()
    conection.close()
    movies = [Movies(id=row[0],title=row[1],director = row[2]) for row in rows]
    return movies


def read_movies(movies_id:int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM movies WHERE id=?",(movies_id,))
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    return Movies(id=row["id"],title = row["title"],director=row["director"])



































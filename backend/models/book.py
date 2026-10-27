from pydantic import BaseModel

class BookBase(BaseModel):
    title :str
    author_id:int
    book_link:str = ""
    genres: list[str] = []
    average_rating: float | int | None = None
    published_year:int | None = None


class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id:int

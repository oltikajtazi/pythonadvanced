from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str = ""
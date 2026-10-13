from pydantic import BaseModel, Field


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    ingredients: str = Field(min_length=1)
    instructions: str = Field(min_length=1)
    cooking_time: int = Field(default=0, ge=0)
    category_id: int | None = None


class RecipeUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    ingredients: str = Field(min_length=1)
    instructions: str = Field(min_length=1)
    cooking_time: int = Field(default=0, ge=0)
    category_id: int | None = None


class RecipeResponse(BaseModel):
    id: int
    title: str
    ingredients: str
    instructions: str
    cooking_time: int
    category_id: int | None = None
    category_name: str | None = None
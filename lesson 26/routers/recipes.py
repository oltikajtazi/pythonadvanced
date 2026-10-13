from fastapi import APIRouter, HTTPException, status

from database import get_db
from models.recipe import RecipeCreate, RecipeUpdate

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


def recipe_query():
    return """
        SELECT
            r.id,
            r.title,
            r.ingredients,
            r.instructions,
            r.cooking_time,
            r.category_id,
            c.name AS category_name
        FROM recipes r
        LEFT JOIN categories c
            ON r.category_id = c.id
    """


def validate_category(db, category_id):
    if category_id is not None:
        category = db.execute(
            "SELECT id FROM categories WHERE id = ?",
            (category_id,)
        ).fetchone()

        if category is None:
            raise HTTPException(
                status_code=400,
                detail="Category does not exist"
            )


@router.get("/")
def get_recipes():
    with get_db() as db:
        rows = db.execute(
            recipe_query() + " ORDER BY r.title"
        ).fetchall()

        return [dict(row) for row in rows]


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int):
    with get_db() as db:
        row = db.execute(
            recipe_query() + " WHERE r.id = ?",
            (recipe_id,)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found"
            )

        return dict(row)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate):
    title = recipe.title.strip()
    ingredients = recipe.ingredients.strip()
    instructions = recipe.instructions.strip()

    if not title or not ingredients or not instructions:
        raise HTTPException(
            status_code=422,
            detail="Title, ingredients, and instructions are required"
        )

    with get_db() as db:
        validate_category(db, recipe.category_id)

        cursor = db.execute(
            """
            INSERT INTO recipes (
                title,
                ingredients,
                instructions,
                cooking_time,
                category_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                ingredients,
                instructions,
                recipe.cooking_time,
                recipe.category_id
            )
        )

        row = db.execute(
            recipe_query() + " WHERE r.id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return dict(row)


@router.put("/{recipe_id}")
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate
):
    title = recipe.title.strip()
    ingredients = recipe.ingredients.strip()
    instructions = recipe.instructions.strip()

    if not title or not ingredients or not instructions:
        raise HTTPException(
            status_code=422,
            detail="Title, ingredients, and instructions are required"
        )

    with get_db() as db:
        existing = db.execute(
            "SELECT id FROM recipes WHERE id = ?",
            (recipe_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found"
            )

        validate_category(db, recipe.category_id)

        db.execute(
            """
            UPDATE recipes
            SET title = ?,
                ingredients = ?,
                instructions = ?,
                cooking_time = ?,
                category_id = ?
            WHERE id = ?
            """,
            (
                title,
                ingredients,
                instructions,
                recipe.cooking_time,
                recipe.category_id,
                recipe_id
            )
        )

        row = db.execute(
            recipe_query() + " WHERE r.id = ?",
            (recipe_id,)
        ).fetchone()

        return dict(row)


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int):
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM recipes WHERE id = ?",
            (recipe_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found"
            )

        return {
            "message": "Recipe deleted successfully"
        }
import sqlite3

from fastapi import APIRouter, HTTPException, status

from database import get_db
from models.category import CategoryCreate, CategoryUpdate

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("/")
def get_categories():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM categories ORDER BY name"
        ).fetchall()

        return [dict(row) for row in rows]


@router.get("/{category_id}")
def get_category(category_id: int):
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM categories WHERE id = ?",
            (category_id,)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return dict(row)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate):
    name = category.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Category name cannot be empty"
        )

    try:
        with get_db() as db:
            cursor = db.execute(
                """
                INSERT INTO categories (name, description)
                VALUES (?, ?)
                """,
                (name, category.description.strip())
            )

            row = db.execute(
                "SELECT * FROM categories WHERE id = ?",
                (cursor.lastrowid,)
            ).fetchone()

            return dict(row)

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )


@router.put("/{category_id}")
def update_category(
    category_id: int,
    category: CategoryUpdate
):
    name = category.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Category name cannot be empty"
        )

    try:
        with get_db() as db:
            cursor = db.execute(
                """
                UPDATE categories
                SET name = ?, description = ?
                WHERE id = ?
                """,
                (name, category.description.strip(), category_id)
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Category not found"
                )

            row = db.execute(
                "SELECT * FROM categories WHERE id = ?",
                (category_id,)
            ).fetchone()

            return dict(row)

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Category name already exists"
        )


@router.delete("/{category_id}")
def delete_category(category_id: int):
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM categories WHERE id = ?",
            (category_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return {
            "message": "Category deleted successfully"
        }
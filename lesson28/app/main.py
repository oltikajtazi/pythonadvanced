
import os
import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Database configuration
DB_PATH = Path(__file__).parent / "database.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()


# Initialize database when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Items API",
    version="1.0.0",
    lifespan=lifespan,
)

# API key authentication
api_key_header = APIKeyHeader(
    name="api-key",
    auto_error=False,
)


def check_key(key: Optional[str] = Depends(api_key_header)):
    allowed_keys = [
        value.strip()
        for value in os.getenv("API_KEYS", "").split(",")
        if value.strip()
    ]

    if not key or key not in allowed_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


# Item models
class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None, min_length=1, max_length=200
    )
    description: Optional[str] = None


# Create an item
@app.post(
    "/items/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_key)],
)
def create_item(item: Item):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO items (name, description) VALUES (?, ?)",
            (item.name, item.description),
        )
        conn.commit()

        return {
            "id": cursor.lastrowid,
            **item.model_dump(),
        }
    finally:
        conn.close()


# Get all items
@app.get("/items/", dependencies=[Depends(check_key)])
def get_items():
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, name, description FROM items ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


# Get one item by ID
@app.get("/items/{item_id}", dependencies=[Depends(check_key)])
def get_item(item_id: int):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, name, description FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        return dict(row)
    finally:
        conn.close()


# Update an item
@app.patch("/items/{item_id}", dependencies=[Depends(check_key)])
def update_item(item_id: int, item: ItemUpdate):
    updates = item.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    allowed_fields = {"name", "description"}
    if not set(updates).issubset(allowed_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid fields",
        )

    fields = list(updates.keys())
    set_clause = ", ".join(f"{field} = ?" for field in fields)
    values = [updates[field] for field in fields]

    conn = get_db()
    try:
        cursor = conn.execute(
            f"UPDATE items SET {set_clause} WHERE id = ?",
            values + [item_id],
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        row = conn.execute(
            "SELECT id, name, description FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()

        return dict(row)
    finally:
        conn.close()


# Delete an item
@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_key)],
)
def delete_item(item_id: int):
    conn = get_db()
    try:
        cursor = conn.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
    finally:
        conn.close()

    return None

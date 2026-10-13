from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import categories, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Online Recipe Book",
    description="API for managing recipes and categories",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(categories.router)
app.include_router(recipes.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Online Recipe Book API",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
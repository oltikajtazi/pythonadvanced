"""Signbridge server. Run with:  python server.py  ->  http://127.0.0.1:8000"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import database as db
import model

STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_):
    db.init()
    model.load()
    yield


app = FastAPI(title="Signbridge", lifespan=lifespan)


class Frame(BaseModel):
    landmarks: list[list[float]] = Field(min_length=21, max_length=21)
    hand: str = "Right"


class SampleBatch(BaseModel):
    label: str = Field(min_length=1, max_length=40)
    frames: list[Frame] = Field(min_length=1, max_length=500)


class Entry(BaseModel):
    source: Literal["sign", "speech"]
    text: str = Field(min_length=1, max_length=500)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status():
    return {"labels": db.label_counts(), "model": db.latest_model(), "min_per_label": model.MIN_PER_LABEL}


@app.post("/api/samples")
def add_samples(batch: SampleBatch):
    try:
        rows = [model.normalize(f.landmarks, f.hand).tolist() for f in batch.frames]
    except ValueError:
        raise HTTPException(422, "Each landmark needs x, y, z.")
    db.add_samples(batch.label.strip(), rows)
    return {"saved": len(rows)}


@app.delete("/api/labels/{label:path}")
def delete_label(label: str):
    return {"deleted": db.delete_label(label)}


@app.post("/api/train")
def train():
    try:
        return model.train()
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/sign/{label:path}")
def sign(label: str):
    features = db.mean_sample(label)
    if features is None:
        raise HTTPException(404, "Unknown sign.")
    return {"label": label, "features": features}


@app.get("/api/history")
def history():
    return db.history()


@app.post("/api/history")
def add_history(entry: Entry):
    db.add_translation(entry.source, entry.text.strip())
    return {"ok": True}


@app.websocket("/ws")
async def live(socket: WebSocket):
    """The browser sends one hand per message; we answer with the predicted sign."""
    await socket.accept()
    try:
        while True:
            data = await socket.receive_json()
            if not model.is_ready():
                await socket.send_json({"trained": False})
                continue
            try:
                frame = Frame(**data)
                label, confidence = model.predict(frame.landmarks, frame.hand)
                await socket.send_json({"trained": True, "label": label, "confidence": confidence})
            except Exception:
                await socket.send_json({"trained": True, "label": None, "confidence": 0})
    except WebSocketDisconnect:
        pass


app.mount("/static", StaticFiles(directory=STATIC), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

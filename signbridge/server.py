"""Signbridge server. Run with:  python server.py  ->  http://127.0.0.1:8000"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

import database as db
import model

STATIC = Path(__file__).parent / "static"
STATIC.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(_):
    db.init()
    model.load()
    yield


app = FastAPI(title="Signbridge", lifespan=lifespan)


class Frame(BaseModel):
    landmarks: list[list[float]] = Field(min_length=21, max_length=21)
    hand: str = "Right"

    @field_validator("hand", mode="before")
    @classmethod
    def _hand(cls, v):
        return "Left" if str(v).strip().lower() == "left" else "Right"


class SampleBatch(BaseModel):
    label: str = Field(min_length=1, max_length=40)

    @field_validator("label", mode="after")
    @classmethod
    def _label(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Label can't be blank.")
        return v

    frames: list[Frame] = Field(min_length=1, max_length=500)


class Entry(BaseModel):
    source: Literal["sign", "speech"]
    text: str = Field(min_length=1, max_length=500)


@app.get("/")
def index():
    page = STATIC / "index.html"
    if not page.exists():
        raise HTTPException(404, "static/index.html is missing. Add the web interface files to the static/ folder.")
    return FileResponse(page)


@app.get("/api/status")
def status():
    latest = db.latest_model()
    if latest:
        latest.pop("path", None)  # don't leak server file paths
    return {"labels": db.label_counts(), "model": latest, "min_per_label": model.MIN_PER_LABEL}


@app.post("/api/samples")
def add_samples(batch: SampleBatch):
    try:
        rows = [model.normalize(f.landmarks, f.hand).tolist() for f in batch.frames]
    except ValueError:
        raise HTTPException(422, "Each landmark needs x, y, z.")
    db.add_samples(batch.label, rows)
    return {"saved": len(rows)}


@app.delete("/api/labels/{label:path}")
def delete_label(label: str):
    deleted = db.delete_label(label)
    reset = False
    latest = db.latest_model()
    if deleted and latest and label in latest["labels"]:
        model.reset()  # the model still knows this sign; force a retrain
        reset = True
    return {"deleted": deleted, "model_reset": reset}


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
            try:
                data = await socket.receive_json()
            except (ValueError, KeyError):  # bad JSON or a non-text message
                await socket.send_json({"error": "Invalid message."})
                continue
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

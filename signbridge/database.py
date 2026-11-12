"""SQLite storage for Signbridge: recorded samples, trained models, translation history."""
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "signbridge.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS samples (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    label      TEXT NOT NULL,
    features   TEXT NOT NULL,          -- JSON list of 63 normalised floats
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_samples_label ON samples(label);

CREATE TABLE IF NOT EXISTS models (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm  TEXT NOT NULL,
    accuracy   REAL NOT NULL,          -- cross-validated accuracy, 0..1
    n_samples  INTEGER NOT NULL,
    labels     TEXT NOT NULL,          -- JSON list
    scores     TEXT NOT NULL,          -- JSON {algorithm: accuracy} for every candidate
    path       TEXT NOT NULL,          -- joblib file
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS translations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source     TEXT NOT NULL,          -- 'sign' or 'speech'
    text       TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init():
    with conn() as c:
        c.executescript(SCHEMA)


# ---- samples ---------------------------------------------------------------
def add_samples(label, rows):
    now = time.time()
    with conn() as c:
        c.executemany(
            "INSERT INTO samples (label, features, created_at) VALUES (?, ?, ?)",
            [(label, json.dumps(r), now) for r in rows],
        )


def label_counts():
    with conn() as c:
        rows = c.execute(
            "SELECT label, COUNT(*) AS count FROM samples GROUP BY label ORDER BY label"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_label(label):
    with conn() as c:
        return c.execute("DELETE FROM samples WHERE label = ?", (label,)).rowcount


def load_samples():
    with conn() as c:
        rows = c.execute("SELECT label, features FROM samples").fetchall()
    if not rows:
        return np.empty((0, 63), dtype=np.float32), np.array([])
    X = np.array([json.loads(r["features"]) for r in rows], dtype=np.float32)
    y = np.array([r["label"] for r in rows])
    return X, y


def mean_sample(label):
    """Average pose of a sign, used to draw its picture."""
    with conn() as c:
        rows = c.execute("SELECT features FROM samples WHERE label = ?", (label,)).fetchall()
    if not rows:
        return None
    return np.mean([json.loads(r["features"]) for r in rows], axis=0).tolist()


# ---- models ----------------------------------------------------------------
def save_model(algorithm, accuracy, n_samples, labels, scores, path):
    with conn() as c:
        c.execute(
            "INSERT INTO models (algorithm, accuracy, n_samples, labels, scores, path, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (algorithm, accuracy, n_samples, json.dumps(labels), json.dumps(scores), path, time.time()),
        )


def latest_model():
    with conn() as c:
        r = c.execute("SELECT * FROM models ORDER BY id DESC LIMIT 1").fetchone()
    if not r:
        return None
    m = dict(r)
    m["labels"] = json.loads(m["labels"])
    m["scores"] = json.loads(m["scores"])
    return m


# ---- history ---------------------------------------------------------------
def add_translation(source, text):
    with conn() as c:
        c.execute(
            "INSERT INTO translations (source, text, created_at) VALUES (?, ?, ?)",
            (source, text, time.time()),
        )


def history(limit=8):
    with conn() as c:
        rows = c.execute(
            "SELECT source, text, created_at FROM translations ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]

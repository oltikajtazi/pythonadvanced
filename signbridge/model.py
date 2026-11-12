"""Hand-sign classifier: normalise landmarks, train several models, keep the best one."""
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import database as db

MIN_PER_LABEL = 8

# Every candidate is trained and cross-validated; the best one is saved.
CANDIDATES = {
    "mlp": lambda: make_pipeline(
        StandardScaler(), MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=800, random_state=1)
    ),
    "random_forest": lambda: RandomForestClassifier(n_estimators=200, random_state=1),
    "knn": lambda: make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
}

_clf = None


def normalize(landmarks, hand="Right"):
    """21 x (x, y, z) -> 63 features.

    Wrist-centred, scale-invariant, and left hands are mirrored so one model
    handles both hands and any distance from the camera.
    """
    pts = np.asarray(landmarks, dtype=np.float32).reshape(21, 3)
    pts = pts - pts[0]
    if hand == "Left":
        pts[:, 0] *= -1
    scale = float(np.abs(pts).max()) or 1.0
    return (pts / scale).flatten()


def train():
    X, y = db.load_samples()
    labels, counts = np.unique(y, return_counts=True)
    if len(labels) < 2:
        raise ValueError("Record at least 2 different signs first.")
    low = [str(l) for l, n in zip(labels, counts) if n < MIN_PER_LABEL]
    if low:
        raise ValueError(f"Need at least {MIN_PER_LABEL} samples for: {', '.join(low)}.")

    cv = int(min(5, counts.min()))
    scores = {name: float(cross_val_score(make(), X, y, cv=cv).mean()) for name, make in CANDIDATES.items()}
    best = max(scores, key=scores.get)

    clf = CANDIDATES[best]().fit(X, y)
    path = db.DATA_DIR / f"model_{int(time.time())}.joblib"
    joblib.dump(clf, path)
    db.save_model(best, scores[best], len(y), [str(l) for l in labels], scores, str(path))
    load()
    return {"algorithm": best, "accuracy": scores[best], "scores": scores}


def load():
    global _clf
    m = db.latest_model()
    _clf = joblib.load(m["path"]) if m and Path(m["path"]).exists() else None
    return _clf is not None


def is_ready():
    return _clf is not None


def predict(landmarks, hand="Right"):
    x = normalize(landmarks, hand).reshape(1, -1)
    proba = _clf.predict_proba(x)[0]
    i = int(proba.argmax())
    return str(_clf.classes_[i]), float(proba[i])

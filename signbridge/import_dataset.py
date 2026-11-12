"""Import a hand-landmark CSV (for example an ASL alphabet dataset) and train on it.

    python import_dataset.py landmarks.csv
    python import_dataset.py landmarks.csv --max-per-label 300 --skip nothing,del,space

The CSV needs a header row, one label column and the 21 MediaPipe hand points as
x, y, z columns (63 numbers; 42 if there is no z). Stop the server first, run this,
then start the server again. Run it once per dataset: running it twice adds the
samples twice.
"""
import argparse
import csv
import math
import random
import re
from collections import defaultdict

import numpy as np

import database as db
import model

LABEL_COLUMNS = ("label", "class", "letter", "sign", "target", "character", "y")
AXIS_FIRST = re.compile(r"^([xyz])\D*(\d+)$")      # x0, x_0, y12
INDEX_FIRST = re.compile(r"^\D*?(\d+)\D*([xyz])$")  # 0_x, lm0_x, landmark_12_z


def parse_name(name):
    m = AXIS_FIRST.match(name)
    if m:
        return int(m.group(2)), m.group(1)
    m = INDEX_FIRST.match(name)
    if m:
        return int(m.group(1)), m.group(2)
    return None


def layout(header, label_name=None):
    """Return (label column, 63 feature columns in x0,y0,z0,x1,... order; None = no z)."""
    low = [h.strip().lower() for h in header]
    if label_name:
        if label_name.strip().lower() not in low:
            raise SystemExit(f"No column named '{label_name}'. First columns: {header[:6]}")
        label_col = low.index(label_name.strip().lower())
    else:
        label_col = next((i for i, h in enumerate(low) if h in LABEL_COLUMNS), 0)

    named = {}
    for i, h in enumerate(low):
        p = parse_name(h) if i != label_col else None
        if p:
            named[p] = i
    if named:
        base = min(k[0] for k in named)
        cols = [named.get((base + i, axis)) for i in range(21) for axis in "xyz"]
        if base not in (0, 1) or any(cols[j] is None for j in range(63) if j % 3 != 2):
            raise SystemExit("Could not find x and y columns for all 21 landmarks.")
        return label_col, cols

    feats = [i for i in range(len(header)) if i != label_col]
    if len(feats) == 63:
        return label_col, feats
    if len(feats) == 42:
        return label_col, [c for k in range(21) for c in (feats[2 * k], feats[2 * k + 1], None)]
    raise SystemExit(f"Expected 63 (x,y,z) or 42 (x,y) landmark columns, found {len(feats)}.")


def read(path, label_name=None):
    by_label = defaultdict(list)
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        label_col, cols = layout(header, label_name)
        for row in reader:
            try:
                label = row[label_col].strip()
                vals = [float(row[c]) if c is not None else 0.0 for c in cols]
            except (ValueError, IndexError):
                continue
            if label and all(math.isfinite(v) for v in vals):
                by_label[label].append(vals)
    return by_label


def main():
    ap = argparse.ArgumentParser(description="Import a landmark CSV and train on it.")
    ap.add_argument("csv")
    ap.add_argument("--label-col", help="name of the label column if it is not detected")
    ap.add_argument("--max-per-label", type=int, default=300, help="samples kept per sign (default 300)")
    ap.add_argument("--skip", default="nothing", help="comma-separated labels to ignore")
    ap.add_argument("--no-train", action="store_true", help="import only, do not train")
    a = ap.parse_args()

    db.init()
    skip = {s.strip().lower() for s in a.skip.split(",") if s.strip()}
    data = read(a.csv, a.label_col)
    rng = random.Random(1)
    total = 0
    for label, rows in sorted(data.items()):
        if label.lower() in skip:
            continue
        rng.shuffle(rows)
        feats = []
        for r in rows[: a.max_per_label]:
            f = model.normalize(r, "Right")
            mirrored = f.copy()
            mirrored[0::3] *= -1  # also store the mirror image so either hand works
            feats += [f.tolist(), mirrored.tolist()]
        db.add_samples(label, feats)
        total += len(feats)
        print(f"  {label}: {len(feats)} samples")
    print(f"Imported {total} samples.")
    if not a.no_train and total:
        print("Training three models, this can take a few minutes...")
        try:
            print(model.train())
        except ValueError as e:
            print("Could not train:", e)


if __name__ == "__main__":
    main()

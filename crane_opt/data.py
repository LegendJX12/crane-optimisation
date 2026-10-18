"""
data.py - Load the precast components and (optionally) stack them into storeys.

The CSV has one row per PPVC module on ONE typical floor:
    id, x, y, width, length, height, weight_t, type
x, y      = centre of the module on plan (m)
width/length = plan size (m), height = module height (m)
weight_t  = module weight (tonnes). In the sample file it is ASSUMED as
            0.6 t per m2 of floor area - replace with values from the
            precast shop drawings (e.g. 327B PPVC details P-3..P-8).
type      = 'large' / 'small' (used to send modules to different pickup bays)
"""
import numpy as np
import pandas as pd

REQUIRED = ["x", "y", "width", "length", "height", "weight_t"]


def load_components(path, storeys=1, floor_height=2.8):
    """Read the CSV and repeat the floor `storeys` times.

    Returns a DataFrame sorted storey by storey (lower floors first),
    which is the default installation order (same as v1 for storeys=1).
    """
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Component file {path} is missing columns: {missing}")
    if df[REQUIRED].isnull().any().any():
        bad = df[df[REQUIRED].isnull().any(axis=1)]["id"].tolist()
        raise ValueError(f"Empty values in component rows: {bad}")
    if "type" not in df.columns:
        df["type"] = "module"
    if "id" not in df.columns:
        df["id"] = np.arange(1, len(df) + 1)

    floors = []
    for s in range(storeys):
        f = df.copy()
        f["storey"] = s + 1
        f["z_level"] = s * floor_height          # slab level of this storey
        f["label"] = f["id"].astype(str) if storeys == 1 else \
            f"L{s+1}-" + f["id"].astype(str)
        floors.append(f)
    out = pd.concat(floors, ignore_index=True)
    return out

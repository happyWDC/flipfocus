"""Shared utilities for the Phone Flip Ritual analysis pipeline."""

import json
import pandas as pd
import numpy as np
from pathlib import Path

CONDITION_LABELS = {
    "A_主动翻转": "Active Flip",
    "B_面朝上": "Face Up",
    "C_无手机": "No Phone",
    "D_被动翻转": "Passive Flip",
}

# Shorter keys for analysis code
COND_SHORT = {
    "A_主动翻转": "A",
    "B_面朝上": "B",
    "C_无手机": "C",
    "D_被动翻转": "D",
}

TRANSITION_WINDOW_MS = 5000  # exclude 5s around flip events


def load_sensor_csv(filepath: str) -> pd.DataFrame:
    """Load a FlipFocus sensors.csv. Columns: timestamp_ms, acc_z, light_lux, proximity."""
    df = pd.read_csv(filepath)
    return df


def load_meta_json(filepath: str) -> dict:
    """Load a FlipFocus meta.json."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def load_bundle_json(filepath: str) -> dict:
    """Load a FlipFocus _bundle.json file (new single-file export format)."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def load_all_sessions(data_dir: str) -> pd.DataFrame:
    """Walk data/ directory, load all sensor data.
    Supports both legacy format (*_sensors.csv + *_meta.json) and new format (*_bundle.json)."""
    rows = []
    data_path = Path(data_dir)

    # ── New format: _bundle.json ──
    bundle_files = list(data_path.rglob("*_bundle.json"))
    for bf in sorted(bundle_files):
        bundle = load_bundle_json(str(bf))
        meta = bundle.get("meta", {})
        sensors = bundle.get("sensors", [])

        if not sensors:
            continue

        sensor_df = pd.DataFrame(sensors)
        # Normalize column names: ts → timestamp_ms
        if "ts" in sensor_df.columns:
            sensor_df.rename(columns={"ts": "timestamp_ms"}, inplace=True)
        if "face_down" not in sensor_df.columns:
            sensor_df["face_down"] = 0

        sensor_df["subject_id"] = meta.get("participant", "?")
        sensor_df["condition_id"] = meta.get("condition", "?")
        sensor_df["repetition"] = meta.get("repetition", 1)
        rows.append(sensor_df)

    # ── Legacy format: _sensors.csv + _meta.json ──
    for sensor_file in sorted(data_path.rglob("*_sensors.csv")):
        # Skip if already covered by a bundle
        prefix = sensor_file.name.replace("_sensors.csv", "")
        bundle_file = sensor_file.parent / f"{prefix}_bundle.json"
        if bundle_file.exists():
            continue  # already loaded via bundle

        meta_file = sensor_file.parent / f"{prefix}_meta.json"
        sensor_df = load_sensor_csv(str(sensor_file))

        if meta_file.exists():
            meta = load_meta_json(str(meta_file))
            sensor_df["subject_id"] = meta["participant"]
            sensor_df["condition_id"] = meta["condition"]
            sensor_df["repetition"] = meta["repetition"]
        else:
            parts = prefix.split("_")
            sensor_df["subject_id"] = parts[0] if len(parts) > 0 else "?"
            sensor_df["condition_id"] = "_".join(parts[1:-1]) if len(parts) > 2 else "?"
            sensor_df["repetition"] = int(parts[-2].replace("R", "")) if len(parts) > 2 else 1

        rows.append(sensor_df)

    if not rows:
        raise FileNotFoundError(f"No *_bundle.json or *_sensors.csv files found under {data_dir}")

    df = pd.concat(rows, ignore_index=True)
    df["condition_short"] = df["condition_id"].map(COND_SHORT)
    return df


def compute_focus_score(row: pd.Series) -> float:
    """Compute focus score from 5 self-report items (Q1-Q5).
    Q2 (mind-wandering) and Q5 (distraction) are reverse-scored: 6 - raw."""
    q1 = row["q1_focus"]
    q2 = 6 - row["q2_mind_wandering"]
    q3 = row["q3_engagement"]
    q4 = row["q4_time_perception"]
    q5 = 6 - row["q5_distraction"]
    return q1 + q2 + q3 + q4 + q5  # range 5–25


def cohens_d(x: np.ndarray, y: np.ndarray) -> tuple:
    """Cohen's d + 95% CI using pooled SD. Suitable for exploratory n=4."""
    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        return np.nan, np.nan, np.nan
    s1, s2 = np.std(x, ddof=1), np.std(y, ddof=1)
    sp = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    if sp == 0:
        return np.nan, np.nan, np.nan
    d = (np.mean(x) - np.mean(y)) / sp
    se = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
    return d, d - 1.96 * se, d + 1.96 * se

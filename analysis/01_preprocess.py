"""
01_preprocess.py — Load FlipFocus sensor CSVs, filter transitional periods, merge with questionnaire.

Input:   ../data/ (contains P1/, P2/, P3/, P4/ subdirs with *_sensors.csv, *_flips.csv, *_meta.json)
         ../data/questionnaire.csv (self-report + accuracy)
Output:  ../data/processed/merged_data.csv

Usage:   python 01_preprocess.py --data-dir ../data/ --questionnaire ../data/questionnaire.csv
"""

import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np
from utils import load_all_sessions, load_meta_json, compute_focus_score, TRANSITION_WINDOW_MS


def load_flip_events(data_dir: str) -> pd.DataFrame:
    """Load all flip events from bundles (new format) or CSVs (legacy)."""
    rows = []

    # ── New format: _bundle.json ──
    for bf in sorted(Path(data_dir).rglob("*_bundle.json")):
        with open(bf, encoding="utf-8") as f:
            bundle = json.load(f)
        meta = bundle.get("meta", {})
        flips = bundle.get("flips", [])
        if not flips:
            continue
        df = pd.DataFrame(flips)
        df["subject_id"] = meta.get("participant", "?")
        df["condition_id"] = meta.get("condition", "?")
        df["repetition"] = meta.get("repetition", 1)
        rows.append(df)

    # ── Legacy format: _flips.csv ──
    for f in sorted(Path(data_dir).rglob("*_flips.csv")):
        prefix = f.name.replace("_flips.csv", "")
        # Skip if bundle already covers it
        if Path(f.parent, f"{prefix}_bundle.json").exists():
            continue
        df = pd.read_csv(f)
        parts = prefix.split("_")
        df["subject_id"] = parts[0] if len(parts) > 0 else "?"
        df["condition_id"] = "_".join(parts[1:-1]) if len(parts) > 2 else "?"
        df["repetition"] = int(parts[-2].replace("R", "")) if len(parts) > 2 else 1
        rows.append(df)

    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def remove_transitions(sensor: pd.DataFrame, flip_events: pd.DataFrame) -> pd.DataFrame:
    """Remove sensor rows within ±5s of each FLIP_DOWN/FLIP_UP event."""
    if flip_events.empty:
        return sensor.copy()

    mask = pd.Series(True, index=sensor.index)
    for _, evt in flip_events.iterrows():
        t = pd.to_datetime(evt["time"]).timestamp() * 1000
        # Only apply to matching session
        subj = evt.get("subject_id", "?")
        cond = evt.get("condition_id", "?")
        rep = evt.get("repetition", 1)

        in_session = (
            (sensor["subject_id"] == subj)
            & (sensor["condition_id"] == cond)
            & (sensor["repetition"] == rep)
        )
        in_window = (sensor["timestamp_ms"] >= t - TRANSITION_WINDOW_MS) & (
            sensor["timestamp_ms"] <= t + TRANSITION_WINDOW_MS
        )
        mask = mask & ~(in_session & in_window)

    return sensor[mask].copy()


def main():
    p = argparse.ArgumentParser(description="Preprocess FlipFocus sensor data")
    p.add_argument("--data-dir", default="../data/")
    p.add_argument("--questionnaire", default="../data/questionnaire.csv")
    p.add_argument("--out-dir", default="../data/processed/")
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load sensors
    print("Loading sensor data...")
    sensor = load_all_sessions(args.data_dir)
    print(f"  {len(sensor):,} rows from {sensor['subject_id'].nunique()} subjects")

    # Load flip events
    flips = load_flip_events(args.data_dir)
    print(f"  {len(flips)} flip events")

    # Remove transitional periods
    clean = remove_transitions(sensor, flips)
    print(f"  After removing ±5s transitions: {len(clean):,} rows ({len(sensor)-len(clean):,} removed)")

    # Merge questionnaire if available
    qpath = Path(args.questionnaire)
    if qpath.exists():
        quest = pd.read_csv(qpath)
        quest["focus_score"] = quest.apply(compute_focus_score, axis=1)
        print(f"  Loaded {len(quest)} questionnaire entries")

        # Aggregate sensor data to session level for merge
        session_agg = (
            clean.groupby(["subject_id", "condition_id", "repetition"])
            .agg(
                total_face_down_ms=("proximity", lambda x: (x == 1).sum() * 100),  # rough estimate
                sensor_rows=("timestamp_ms", "count"),
            )
            .reset_index()
        )

        merged = quest.merge(session_agg, on=["subject_id", "condition_id", "repetition"], how="left")
        merged.to_csv(out / "merged_data.csv", index=False)
        print(f"  Merged: {len(merged)} sessions saved")
    else:
        print(f"  NOTE: {qpath} not found — skipping questionnaire merge")
        clean.to_csv(out / "sensor_clean.csv", index=False)

    print(f"\nDone. Output → {out}/")


if __name__ == "__main__":
    main()

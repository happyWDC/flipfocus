"""
04_validate.py — Self-report validity and robustness checks.

1. Pearson r: focus_score × accuracy (r > 0.5 = acceptable proxy)
2. Cronbach's α for 5-item self-report scale
3. Order effect: does repetition predict performance?
4. Per-subject × per-condition summary table

Usage:  python 04_validate.py --merged-data ../data/processed/merged_data.csv
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from utils import COND_SHORT


def pearson_r(df: pd.DataFrame) -> dict:
    r, p = stats.pearsonr(df["focus_score"], df["accuracy"])
    return {"r": round(r, 3), "p": round(p, 4), "n": len(df), "valid": r > 0.5}


def cronbach_alpha(df: pd.DataFrame) -> float:
    items = ["q1_focus", "q2_mind_wandering", "q3_engagement",
             "q4_time_perception", "q5_distraction"]
    scores = df[items].copy()
    scores["q2_mind_wandering"] = 6 - scores["q2_mind_wandering"]
    scores["q5_distraction"] = 6 - scores["q5_distraction"]
    k = len(items)
    item_vars = scores.var(ddof=1)
    total_var = scores.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var) if total_var > 0 else np.nan


def order_effects(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in ["focus_score", "accuracy"]:
        r, p = stats.pearsonr(df["repetition"], df[metric])
        rows.append({"metric": metric, "r": round(r, 3), "p": round(p, 4)})
    return pd.DataFrame(rows)


def subject_summary(df: pd.DataFrame) -> pd.DataFrame:
    df["cond"] = df["condition_id"].map(COND_SHORT)
    return df.groupby(["subject_id", "cond"]).agg(
        focus_mean=("focus_score", "mean"), focus_sd=("focus_score", "std"),
        acc_mean=("accuracy", "mean"), acc_sd=("accuracy", "std"),
        n=("repetition", "nunique"),
    ).round(2).reset_index()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--merged-data", default="../data/processed/merged_data.csv")
    p.add_argument("--out-dir", default="../results/")
    args = p.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.merged_data)
    print(f"Data: {len(df)} sessions")

    # 1. Pearson
    print("\n=== Self-Report Validation ===")
    v = pearson_r(df)
    print(f"  r={v['r']}, p={v['p']}, n={v['n']}")
    print(f"  r>0.5: {'PASS' if v['valid'] else 'FAIL'}")
    pd.DataFrame([v]).to_csv(out / "validation.csv", index=False)

    # 2. Cronbach's α
    try:
        a = cronbach_alpha(df)
        print(f"\n=== Cronbach's α = {a:.3f} ===")
        print(f"  {'OK' if a >= 0.7 else 'Low — note in limitations'}")
    except Exception as e:
        print(f"  α skipped: {e}")

    # 3. Order effects
    print("\n=== Order Effects ===")
    oe = order_effects(df)
    print(oe.to_string(index=False))
    oe.to_csv(out / "order_effects.csv", index=False)

    # 4. Subject summary
    print("\n=== Per-Subject × Per-Condition ===")
    ss = subject_summary(df)
    print(ss.to_string(index=False))
    ss.to_csv(out / "subject_summary.csv", index=False)

    print(f"\nResults → {out}/")


if __name__ == "__main__":
    main()

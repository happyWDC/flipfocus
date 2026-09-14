"""
02_analysis.py — LME model + Cohen's d for FlipFocus experiment.

Primary contrast: A (active flip) vs D (passive flip) — tests agency hypothesis.
Exploratory n=4 → report Cohen's d + 95% CI, effect direction, not p-values.

Usage:  python 02_analysis.py --merged-data ../data/processed/merged_data.csv
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from utils import cohens_d, COND_SHORT

COND_ORDER = ["A", "B", "C", "D"]
COND_LABELS = {
    "A": "Active Flip", "B": "Face Up",
    "C": "No Phone", "D": "Passive Flip",
}


def run_lme(df: pd.DataFrame):
    """Linear mixed-effects: focus_score ~ condition + (1|subject_id)."""
    import statsmodels.formula.api as smf

    df["cond"] = df["condition_id"].map(COND_SHORT)
    model = smf.mixedlm("focus_score ~ C(cond)", df, groups=df["subject_id"])
    result = model.fit(reml=True)
    return result


def compute_all_cohens_d(df: pd.DataFrame) -> pd.DataFrame:
    """Pairwise Cohen's d on focus_score and accuracy."""
    df["cond"] = df["condition_id"].map(COND_SHORT)
    rows = []
    for i, c1 in enumerate(COND_ORDER):
        for c2 in COND_ORDER[i + 1 :]:
            x = df[df["cond"] == c1]["focus_score"].values
            y = df[df["cond"] == c2]["focus_score"].values
            xa = df[df["cond"] == c1]["accuracy"].values
            ya = df[df["cond"] == c2]["accuracy"].values

            d_f, cl_f, ch_f = cohens_d(x, y)
            d_a, cl_a, ch_a = cohens_d(xa, ya)

            rows.append({
                "comparison": f"{c1} vs {c2}",
                "label": f"{COND_LABELS[c1]} vs {COND_LABELS[c2]}",
                "d_focus": round(d_f, 3) if not np.isnan(d_f) else "N/A",
                "ci_focus": f"[{cl_f:.2f}, {ch_f:.2f}]" if not np.isnan(d_f) else "N/A",
                "d_accuracy": round(d_a, 3) if not np.isnan(d_a) else "N/A",
                "ci_accuracy": f"[{cl_a:.2f}, {ch_a:.2f}]" if not np.isnan(d_a) else "N/A",
                "mean_c1": round(np.mean(x), 1),
                "mean_c2": round(np.mean(y), 1),
            })
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--merged-data", default="../data/processed/merged_data.csv")
    p.add_argument("--out-dir", default="../results/")
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.merged_data)

    df["cond"] = df["condition_id"].map(COND_SHORT)
    print(f"Data: {len(df)} sessions, {df['subject_id'].nunique()} subjects")

    # Descriptives
    print("\n=== Per-Condition Means ===")
    desc = df.groupby("cond").agg(
        focus_mean=("focus_score", "mean"),
        focus_sd=("focus_score", "std"),
        acc_mean=("accuracy", "mean"),
        acc_sd=("accuracy", "std"),
        n=("focus_score", "count"),
    ).round(2)
    print(desc)
    desc.to_csv(out / "descriptive_stats.csv")

    # LME
    print("\n=== LME Model ===")
    try:
        lme = run_lme(df)
        print(lme.summary())
        with open(out / "lme_summary.txt", "w", encoding="utf-8") as f:
            f.write(str(lme.summary()))
    except Exception as e:
        print(f"  LME unavailable: {e}")

    # Cohen's d
    print("\n=== Cohen's d (95% CI) ===")
    d_all = compute_all_cohens_d(df)
    print(d_all.to_string(index=False))
    d_all.to_csv(out / "cohens_d.csv", index=False)

    # Primary: A vs D
    ad = d_all[d_all["comparison"] == "A vs D"]
    if len(ad) > 0:
        r = ad.iloc[0]
        print(f"\n=== Primary Contrast (A vs D) ===")
        print(f"  Focus: d={r['d_focus']} {r['ci_focus']}")
        print(f"  Accuracy: d={r['d_accuracy']} {r['ci_accuracy']}")
        try:
            d_val = float(r["d_focus"])
            if abs(d_val) > 0.8:
                print("  → Large effect")
            elif abs(d_val) > 0.5:
                print("  → Medium effect")
            else:
                print("  → Small/inconclusive — be honest in Discussion")
        except ValueError:
            pass

    print(f"\nResults → {out}/")


if __name__ == "__main__":
    main()

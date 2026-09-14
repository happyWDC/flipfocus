"""
03_visualize.py — Figures for the Teenager Show paper.

Generates:
  1. Focus boxplot (4 conditions)
  2. Individual differences (4 subjects × 4 conditions)
  3. Self-report × accuracy validation scatter

Usage:  python 03_visualize.py --merged-data ../data/processed/merged_data.csv
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from utils import COND_SHORT

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 12,
    "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
})

COND_ORDER = ["A", "B", "C", "D"]
COND_LABELS = {"A": "Active Flip", "B": "Face Up", "C": "No Phone", "D": "Passive Flip"}
COLORS = {"A": "#2ECC71", "B": "#4F8EF7", "C": "#6B7280", "D": "#E74C3C"}


def plot_boxplot(df: pd.DataFrame, out_path: str):
    """Boxplot of focus scores across 4 conditions."""
    fig, ax = plt.subplots(figsize=(6, 4.5))

    data = [df[df["cond"] == c]["focus_score"].values for c in COND_ORDER]
    bp = ax.boxplot(data, labels=[COND_LABELS[c] for c in COND_ORDER],
                     patch_artist=True, widths=0.5,
                     medianprops={"color": "black", "linewidth": 1.5})

    for patch, c in zip(bp["boxes"], COND_ORDER):
        patch.set_facecolor(COLORS[c]); patch.set_alpha(0.7)

    for i, c in enumerate(COND_ORDER):
        y = df[df["cond"] == c]["focus_score"].values
        x = np.random.normal(i + 1, 0.05, len(y))
        ax.scatter(x, y, color="black", s=30, alpha=0.6, zorder=3)

    ax.set_ylabel("Focus Score (5–25)"); ax.set_xlabel("Condition")
    ax.set_ylim(4, 26); ax.set_title("Self-Reported Focus by Condition")
    fig.tight_layout(); fig.savefig(out_path); plt.close()
    print(f"  Saved {out_path}")


def plot_individual(df: pd.DataFrame, out_path: str):
    """Individual subject trajectories."""
    subjects = sorted(df["subject_id"].unique())
    n = len(subjects)
    fig, axes = plt.subplots(1, n, figsize=(3 * n, 3.5), sharey=True)

    for ax, subj in zip([axes] if n == 1 else axes, subjects):
        sdf = df[df["subject_id"] == subj]
        means = []
        for c in COND_ORDER:
            vals = sdf[sdf["cond"] == c]["focus_score"].values
            means.append(np.mean(vals) if len(vals) else np.nan)
            ax.scatter([COND_ORDER.index(c) + 1] * len(vals), vals, color=COLORS[c], s=40)
        ax.plot(range(1, 5), means, "k-", lw=1, alpha=0.4)
        ax.set_title(f"Subject {subj}"); ax.set_xticks(range(1, 5))
        ax.set_xticklabels(COND_ORDER, fontsize=9); ax.set_ylim(4, 26)
        if ax == (axes[0] if n > 1 else axes): ax.set_ylabel("Focus Score")

    fig.suptitle("Individual Differences", y=1.02)
    fig.tight_layout(); fig.savefig(out_path); plt.close()
    print(f"  Saved {out_path}")


def plot_validation(df: pd.DataFrame, out_path: str):
    """Self-report focus vs accuracy scatter."""
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    x, y = df["focus_score"], df["accuracy"]
    r, p = stats.pearsonr(x, y)

    for c in COND_ORDER:
        cd = df[df["cond"] == c]
        ax.scatter(cd["focus_score"], cd["accuracy"], color=COLORS[c],
                   label=COND_LABELS[c], s=50, alpha=0.7)

    m, b = np.polyfit(x, y, 1)
    xr = np.linspace(x.min() - 1, x.max() + 1, 100)
    ax.plot(xr, m * xr + b, "k--", lw=1, alpha=0.5)

    ax.set_xlabel("Self-Reported Focus"); ax.set_ylabel("Accuracy")
    ax.set_title("Validation: Focus vs Accuracy")
    ax.legend(fontsize=8)
    ax.text(0.05, 0.95, f"r = {r:.2f}, p = {p:.3f}\n{'VALID' if r > 0.5 else 'WEAK'} (r>0.5)",
            transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    fig.tight_layout(); fig.savefig(out_path); plt.close()
    print(f"  Saved {out_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--merged-data", default="../data/processed/merged_data.csv")
    p.add_argument("--out-dir", default="../results/figures/")
    args = p.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.merged_data)
    df["cond"] = df["condition_id"].map(COND_SHORT)
    print(f"Data: {len(df)} sessions")

    plot_boxplot(df, str(out / "fig1_boxplot.png"))
    plot_individual(df, str(out / "fig2_individual.png"))
    plot_validation(df, str(out / "fig3_validation.png"))
    print(f"\nAll figures → {out}/")


if __name__ == "__main__":
    main()

"""
fig2_individual_nature.py — Nature-style individual subject trajectories.
Small multiples: one panel per subject, shared y-axis, Morandi condition colours.
"""
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path

DATA_PATH = Path(r"F:\Claude project\ubicomp_teenager\data\processed\merged_data.csv")
OUT_DIR   = Path(r"F:\Claude project\ubicomp_teenager\results\figures")

COND_ORDER = ["A", "B", "C", "D"]
COND_LABELS = {"A": "Active\nFlip", "B": "Face\nUp", "C": "No\nPhone", "D": "Passive\nFlip"}
# Morandi palette — same as Fig 1 condition colours (muted, low saturation)
COND_COLORS = {"A": "#7B8FA1", "B": "#B8978A", "C": "#8FA894", "D": "#9B8EAB"}
COND_SHORT  = {"A_主动翻转": "A", "B_面朝上": "B", "C_无手机": "C", "D_被动翻转": "D"}

df = pd.read_csv(DATA_PATH)
df["cond_short"] = df["condition_id"].map(COND_SHORT)
subjects = sorted(df["subject_id"].unique())

# ═══════════════════════════════════════════════════════════════
# Nature-style rcParams (matching Fig 1)
# ═══════════════════════════════════════════════════════════════
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.9,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
})

# ═══════════════════════════════════════════════════════════════
# Small multiples: 1 row × 4 columns
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 4, figsize=(9.0, 3.2), sharey=True)

for ax_idx, (ax, subj) in enumerate(zip(axes, subjects)):
    sdf = df[df["subject_id"] == subj]

    # Per-condition scatter + mean line
    for ci, c in enumerate(COND_ORDER):
        vals = sdf[sdf["cond_short"] == c]["focus_score"].values
        x_jitter = np.random.RandomState(42 + ci).uniform(-0.08, 0.08, len(vals))
        ax.scatter(
            np.full(len(vals), ci + 1) + x_jitter, vals,
            color=COND_COLORS[c], s=22, alpha=0.80, zorder=3,
            edgecolors="white", linewidth=0.3,
        )
        # Mean bar
        mean_val = np.mean(vals)
        ax.hlines(mean_val, ci + 0.75, ci + 1.25,
                  color="#333333", linewidth=1.2, zorder=4)

    # Connect per-condition means with a line
    means = [np.mean(sdf[sdf["cond_short"] == c]["focus_score"].values) for c in COND_ORDER]
    ax.plot(range(1, 5), means, "-", color="#555555", linewidth=0.8, alpha=0.6, zorder=2)

    ax.set_title(f"Subject {subj}", fontweight="bold", color="#333333", pad=4)
    ax.set_xticks(range(1, 5))
    ax.set_xticklabels([COND_LABELS[c] for c in COND_ORDER], fontsize=10, linespacing=1.1)
    ax.set_ylim(4, 26)
    ax.tick_params(axis="both", which="both", direction="in",
                   top=False, right=False, labeltop=False, labelright=False)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.yaxis.grid(True, which="major", color="#E8E8E8", linewidth=0.3, alpha=0.6)
    ax.set_axisbelow(True)

    if ax_idx == 0:
        ax.set_ylabel("Focus score")

# ── Condition legend below all subplots ──
legend_elements = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=COND_COLORS[c],
               markersize=6, label=COND_LABELS[c].replace("\n", " "))
    for c in COND_ORDER
]
leg = fig.legend(
    handles=legend_elements,
    loc="lower center",
    ncol=4,
    fontsize=10,
    frameon=False,                     # no box — clean Nature style
    handletextpad=0.5,
    columnspacing=1.0,
    borderaxespad=0.0,
    title="Condition",
    title_fontsize=10,
    bbox_to_anchor=(0.5, -0.08),
)
# Title styling to match figure
leg.get_title().set_fontweight("normal")
leg.get_title().set_color("#555555")

fig.subplots_adjust(bottom=0.18)

# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════
OUT_DIR.mkdir(parents=True, exist_ok=True)
base = OUT_DIR / "fig2_individual"
for fmt, dpi in [("svg", None), ("pdf", None), ("tiff", 600)]:
    kw = {"dpi": dpi} if dpi else {}
    fig.savefig(str(base) + f".{fmt}", bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)

print(f"Fig 2 saved: {base}.svg | .pdf | .tiff")
print("Caption: Figure 2 | Individual subject focus scores across four conditions.")
print("Coloured points show 3 repetitions per condition; horizontal bars mark")
print("per-condition means; grey line connects means within each subject.")
print("All subjects show lowest focus in Face Up (B) condition.")

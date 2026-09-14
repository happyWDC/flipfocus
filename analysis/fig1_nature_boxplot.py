"""
fig1_nature_boxplot.py — Nature-style boxplot of self-reported focus scores
across four experimental conditions.

Follows nature-figure conventions:
  - SVG/PDF primary output with editable text
  - Ticks inward, top/right spines removed
  - Semi-transparent boxes + scatter overlay (not hidden)
  - Single neutral hue — no unnecessary multi-color
  - Caption below figure (Nature standard)
  - Statistics annotated: n per condition, boxplot definition
"""

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

# ── Data ──
DATA_PATH = Path(r"F:\Claude project\ubicomp_teenager\data\processed\merged_data.csv")
OUT_DIR   = Path(r"F:\Claude project\ubicomp_teenager\results\figures")

COND_ORDER = ["A", "B", "C", "D"]
COND_LABELS = {"A": "Active Flip", "B": "Face Up", "C": "No Phone", "D": "Passive Flip"}
COND_SHORT  = {"A_主动翻转": "A", "B_面朝上": "B", "C_无手机": "C", "D_被动翻转": "D"}

df = pd.read_csv(DATA_PATH)
df["cond_short"] = df["condition_id"].map(COND_SHORT)

# ── Compute per-condition stats ──
stats_dict = {}
for c in COND_ORDER:
    vals = df[df["cond_short"] == c]["focus_score"].values
    stats_dict[c] = {
        "n": len(vals),
        "mean": np.mean(vals),
        "median": np.median(vals),
        "q1": np.percentile(vals, 25),
        "q3": np.percentile(vals, 75),
        "iqr": np.percentile(vals, 75) - np.percentile(vals, 25),
        "min": np.min(vals),
        "max": np.max(vals),
        "std": np.std(vals, ddof=1),
        "values": vals,
    }

# Friedman test (non-parametric repeated measures — correct for within-subjects design)
# Use per-subject mean across 3 repetitions for each condition
subjects = sorted(df["subject_id"].unique())
friedman_matrix = []
for subj in subjects:
    row = []
    for c in COND_ORDER:
        vals = df[(df["subject_id"] == subj) & (df["cond_short"] == c)]["focus_score"].values
        row.append(np.mean(vals))
    friedman_matrix.append(row)
friedman_arr = np.array(friedman_matrix)  # shape: (4 subjects, 4 conditions)
chi2_f, p_f = stats.friedmanchisquare(*[friedman_arr[:, j] for j in range(4)])

print("=== Per-condition Statistics ===")
for c in COND_ORDER:
    s = stats_dict[c]
    print(f"  {COND_LABELS[c]}: n={s['n']}, median={s['median']:.1f}, "
          f"IQR=[{s['q1']:.1f}, {s['q3']:.1f}], mean={s['mean']:.2f}±{s['std']:.2f}")
print(f"\nFriedman test (within-subjects, 4x4): chi2={chi2_f:.2f}, p={p_f:.3f}")

# ═══════════════════════════════════════════════════════════════
# MANDATORY: Nature-style rcParams (editable SVG text)
# ═══════════════════════════════════════════════════════════════
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "svg.fonttype": "none",      # editable <text> nodes in SVG
    "pdf.fonttype": 42,          # editable TrueType in PDF
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
})

# ── Color scheme ──
BOX_EDGE      = "#3A3A3A"
MEDIAN_COLOR  = "#1A1A2E"
# Per-subject colours — Morandi palette (low saturation, elegant)
SUBJ_COLORS  = {"P1": "#7B8FA1", "P2": "#B8978A", "P3": "#8FA894", "P4": "#9B8EAB"}

# ═══════════════════════════════════════════════════════════════
# Figure
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(5.2, 4.5))

# ── 1. Draw boxplot (behind scatter, very light fill) ──
box_data = [stats_dict[c]["values"] for c in COND_ORDER]
bp = ax.boxplot(
    box_data,
    tick_labels=[COND_LABELS[c] for c in COND_ORDER],
    patch_artist=True,
    widths=0.40,
    medianprops={"color": MEDIAN_COLOR, "linewidth": 1.8, "solid_capstyle": "butt"},
    whiskerprops={"color": "#555555", "linewidth": 0.8},
    capprops={"color": "#555555", "linewidth": 0.8},
    boxprops={"edgecolor": BOX_EDGE, "linewidth": 1.0, "facecolor": "white"},
    flierprops={"marker": "none"},
)

# Very light fill — box shape visible but points clearly on top
for patch in bp["boxes"]:
    patch.set_facecolor("#EBF0F7")
    patch.set_alpha(0.50)

# ── 2. Overlay individual data points (per-subject markers) ──
np.random.seed(42)
for i, c in enumerate(COND_ORDER):
    cdf = df[df["cond_short"] == c]
    for _, row in cdf.iterrows():
        subj = row["subject_id"]
        val = row["focus_score"]
        jitter = np.random.uniform(-0.10, 0.10)
        ax.scatter(
            i + 1 + jitter, val,
            marker="o",
            c=SUBJ_COLORS.get(subj, "#333333"),
            s=32, alpha=0.85, zorder=5,
            edgecolors="white", linewidth=0.5,
            label=subj if i == 0 else "",  # legend entry from first condition only
        )

# ── 3. Axis styling ──
ax.set_ylabel("Self-reported focus score")
ax.set_ylim(5, 26)
ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

# Ticks inward
ax.tick_params(axis="both", which="both", direction="in",
               top=False, right=False, labeltop=False, labelright=False)

# Lighter horizontal grid
ax.yaxis.grid(True, which="major", color="#E0E0E0", linewidth=0.4, alpha=0.7)
ax.set_axisbelow(True)

# ── 4. Legend: subject markers ──
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))  # deduplicate
leg = ax.legend(
    by_label.values(), by_label.keys(),
    loc="upper left", fontsize=7.5,
    ncol=4, handletextpad=0.4, columnspacing=0.6,
    borderpad=0.3, borderaxespad=0.4,
    frameon=False,
)

# ── 5. Tight layout ──
fig.tight_layout(pad=1.0)

# ═══════════════════════════════════════════════════════════════
# Export: SVG (primary), PDF, TIFF
# ═══════════════════════════════════════════════════════════════
OUT_DIR.mkdir(parents=True, exist_ok=True)

base = OUT_DIR / "fig1_boxplot"
fig.savefig(str(base) + ".svg", bbox_inches="tight", facecolor="white")
fig.savefig(str(base) + ".pdf", bbox_inches="tight", facecolor="white")
fig.savefig(str(base) + ".tiff", dpi=600, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"\nFigures saved: {base}.svg | .pdf | .tiff")
print("Nature-style boxplot complete.")

# ── Caption for figure (paste below figure in manuscript) ──
sig_note = f"Friedman chi2(3) = {chi2_f:.1f}, p = {p_f:.3f}{'*' if p_f < 0.05 else ' (n.s.)'}"
print(f"\n{'='*70}")
print("FIGURE CAPTION (paste below figure in manuscript):")
print(f"{'='*70}")
print(f"Figure 1 | Self-reported focus scores across four experimental conditions.")
print(f"Boxes show median (centre line), interquartile range (25th-75th percentile,")
print(f"box limits), and 1.5xIQR (whiskers). Each condition includes data from")
print(f"4 subjects, with 3 repetitions per subject (12 observations per condition).")
print(f"Coloured circles represent individual subject observations.")
print(f"{sig_note} (Friedman test, within-subjects).")
print(f"{'='*70}")

"""
fig3_validation_nature.py — Nature-style validation scatter.
Self-reported focus vs task accuracy, with regression and 95% CI.
"""
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

DATA_PATH = Path(r"F:\Claude project\ubicomp_teenager\data\processed\merged_data.csv")
OUT_DIR   = Path(r"F:\Claude project\ubicomp_teenager\results\figures")

COND_ORDER = ["A", "B", "C", "D"]
COND_LABELS = {"A": "Active Flip", "B": "Face Up", "C": "No Phone", "D": "Passive Flip"}
COND_COLORS = {"A": "#7B8FA1", "B": "#B8978A", "C": "#8FA894", "D": "#9B8EAB"}
COND_SHORT  = {"A_主动翻转": "A", "B_面朝上": "B", "C_无手机": "C", "D_被动翻转": "D"}

df = pd.read_csv(DATA_PATH)
df["cond_short"] = df["condition_id"].map(COND_SHORT)

# ═══════════════════════════════════════════════════════════════
# Nature-style rcParams
# ═══════════════════════════════════════════════════════════════
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.7,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "legend.frameon": False,
})

# ═══════════════════════════════════════════════════════════════
# Figure
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(4.5, 4.0))

x_all = df["focus_score"].values
y_all = df["accuracy"].values

# ── Regression with 95% CI ──
r, p_r = stats.pearsonr(x_all, y_all)
slope, intercept, r_val, p_val, std_err = stats.linregress(x_all, y_all)
x_line = np.linspace(x_all.min() - 1, x_all.max() + 1, 200)
y_line = slope * x_line + intercept

# 95% CI band
n = len(x_all)
x_mean = np.mean(x_all)
ssx = np.sum((x_all - x_mean) ** 2)
se_line = std_err * np.sqrt(1/n + (x_line - x_mean)**2 / ssx)
t_crit = stats.t.ppf(0.975, n - 2)
ci_low = y_line - t_crit * se_line
ci_high = y_line + t_crit * se_line

ax.fill_between(x_line, ci_low, ci_high, color="#CCCCCC", alpha=0.35, zorder=1)
ax.plot(x_line, y_line, "-", color="#333333", linewidth=1.2, zorder=2)

# ── Per-condition scatter ──
for c in COND_ORDER:
    cdf = df[df["cond_short"] == c]
    ax.scatter(
        cdf["focus_score"], cdf["accuracy"],
        color=COND_COLORS[c], s=32, alpha=0.80, zorder=3,
        edgecolors="white", linewidth=0.4,
        label=COND_LABELS[c],
    )

# ── Annotation ──
ann_str = f"r = {r:.2f}\np = {p_r:.3f}"
if r > 0.5:
    ann_str += "\n(r > 0.5: VALID)"
else:
    ann_str += "\n(WEAK)"
ax.text(0.03, 0.97, ann_str, transform=ax.transAxes,
        fontsize=7.5, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#DDDDDD", alpha=0.9))

# ── Axis styling ──
ax.set_xlabel("Self-reported focus score")
ax.set_ylabel("Task accuracy")
ax.set_xlim(8, 26)
ax.set_ylim(0.5, 1.0)
ax.tick_params(axis="both", which="both", direction="in",
               top=False, right=False)
ax.yaxis.grid(True, which="major", color="#E8E8E8", linewidth=0.3, alpha=0.6)
ax.xaxis.grid(True, which="major", color="#E8E8E8", linewidth=0.3, alpha=0.6)
ax.set_axisbelow(True)

# ── Legend ──
leg = ax.legend(loc="lower right", fontsize=7, ncol=2,
                handletextpad=0.4, columnspacing=0.6,
                borderpad=0.3, borderaxespad=0.4,
                frameon=False)

fig.tight_layout(pad=1.0)

# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════
OUT_DIR.mkdir(parents=True, exist_ok=True)
base = OUT_DIR / "fig3_validation"
for fmt, dpi in [("svg", None), ("pdf", None), ("tiff", 600)]:
    kw = {"dpi": dpi} if dpi else {}
    fig.savefig(str(base) + f".{fmt}", bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)

print(f"Fig 3 saved: {base}.svg | .pdf | .tiff")
print(f"Pearson r = {r:.3f}, p = {p_r:.3f}")
print("Caption: Figure 3 | Self-report validation: focus score vs task accuracy.")
print("Grey band shows 95% confidence interval of the linear regression.")
print("Dashed line is the ordinary least-squares fit across all 48 observations.")

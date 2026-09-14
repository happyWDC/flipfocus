"""
fig4_sensor_nature.py — Clean-room rewrite. Two independent panels,
explicit identical axes, no shared-axis surprises. No Chinese text.
"""
import json
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(r"F:\Claude project\ubicomp_teenager\data")
OUT_DIR  = Path(r"F:\Claude project\ubicomp_teenager\results\figures")

# ── Data file config ──
FILES = [
    ("P1_A_主动翻转_R1_1781095889754_bundle.json", "P1: Active Flip",     "#7B8FA1", "a"),
    ("P2_B_面朝上_R1_1781097673383_bundle.json",   "P2: Face-Up Control", "#B8978A", "b"),
]

THRESH_COLOR = "#8B6914"
DOWN_COLOR   = "#9B6E6E"
UP_COLOR     = "#6E8B7A"
ZERO_COLOR   = "#BEBEBE"
GRID_COLOR   = "#EDEDED"

# ═══════════════════════════════════════════════════════════════
# rcParams — every text element Arial, ticks inward, no top/right spines
# ═══════════════════════════════════════════════════════════════
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 8,
    "axes.labelsize": 9,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.9,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "legend.frameon": False,
})

# ═══════════════════════════════════════════════════════════════
# Load
# ═══════════════════════════════════════════════════════════════
sessions = []
for fname, legend_label, color, panel_id in FILES:
    with open(DATA_DIR / fname, encoding="utf-8") as f:
        b = json.load(f)
    sensors = b["sensors"]
    ts  = np.array([s["ts"] for s in sensors])
    acc = np.array([s["acc_z"] for s in sensors])
    fd  = np.array([s.get("face_down", 0) for s in sensors])
    t0  = ts[0]
    t_min = (ts - t0) / 1000.0 / 60.0
    dur_min = t_min[-1]

    flips_parsed = []
    for ev in b["flips"]:
        try:
            dt = datetime.fromisoformat(ev["time"].replace("Z", "+00:00"))
            ft = (dt.timestamp() * 1000 - t0) / 1000.0 / 60.0
            flips_parsed.append((ft, ev["type"]))
        except Exception:
            pass

    m = b["meta"]
    sessions.append({
        "t_min": t_min, "acc_z": acc, "face_down": fd,
        "flips": flips_parsed,
        "flip_count": m["flip_count"],
        "face_down_sec": float(m["total_face_down_sec"]),
        "data_points": m["data_points"],
        "duration_min": dur_min,
        "hz": m["data_points"] / (dur_min * 60) if dur_min > 0 else 0,
        "legend": legend_label, "color": color, "panel": panel_id,
    })

# ═══════════════════════════════════════════════════════════════
# Figure — TWO INDEPENDENT axes (no sharex/sharey surprises)
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 1, figsize=(6.0, 4.5))
fig.subplots_adjust(hspace=0.25, bottom=0.28, top=0.96, left=0.12, right=0.98)

Y_LIM   = (-2.4, 2.4)
Y_TICKS = [-2, -1, 0, 1, 2]

for ax_idx, (ax, dat) in enumerate(zip(axes, sessions)):
    # ── Face-down shading (zorder=0) ──
    fd_arr = dat["face_down"]
    tm = dat["t_min"]
    in_fd, si = False, None
    for i, v in enumerate(fd_arr):
        if v and not in_fd:
            si = i; in_fd = True
        elif not v and in_fd:
            ax.axvspan(tm[si], tm[i], alpha=0.10,
                       facecolor=dat["color"], edgecolor="none", zorder=0)
            in_fd = False
    if in_fd:
        ax.axvspan(tm[si], tm[-1], alpha=0.10,
                   facecolor=dat["color"], edgecolor="none", zorder=0)

    # ── Reference lines ──
    ax.axhline(y=0,    color=ZERO_COLOR,   linewidth=0.5, linestyle="-",  zorder=1)
    ax.axhline(y=-0.75, color=THRESH_COLOR, linewidth=0.8, linestyle="--",
               alpha=0.80, zorder=1)

    # ── ACC_Z TRACE (zorder=5) ──
    ax.plot(tm, dat["acc_z"], color=dat["color"],
            linewidth=0.5, alpha=0.93, zorder=5)

    # ── D/U markers ──
    for ft, fl in dat["flips"]:
        is_down = "DOWN" in fl
        c = DOWN_COLOR if is_down else UP_COLOR
        sym = "D" if is_down else "U"
        y_top    =  2.55   # outside plot
        y_bottom = -2.55   # outside plot
        y_anchor = y_bottom if is_down else y_top
        y_end    = -1.1 if is_down else 1.1
        # Guide line
        ax.plot([ft, ft], [y_anchor, y_end],
                color=c, linewidth=0.4, alpha=0.45, linestyle="-", zorder=3,
                clip_on=False)
        # Symbol
        ax.text(ft, y_anchor, sym, fontsize=5.5, color=c, fontweight="bold",
                ha="center", va="center", zorder=6, clip_on=False,
                bbox=dict(boxstyle="round,pad=0.06", facecolor="white",
                          edgecolor="none", alpha=0.75))

    # ── Axis — IDENTICAL for both panels (manually set, no sharey) ──
    ax.set_ylim(Y_LIM)
    ax.set_yticks(Y_TICKS)
    ax.set_xlim(0, None)
    ax.tick_params(axis="both", which="major", direction="in",
                   top=False, right=False, labeltop=False, labelright=False,
                   labelsize=7.5, pad=2, length=4, width=0.5)
    ax.yaxis.grid(True, which="major", color=GRID_COLOR, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)

    # ── Y-axis label: panel a ONLY ──
    if ax_idx == 0:
        ax.set_ylabel("acc_z (g)")
    # panel b gets NO ylabel — but keeps its ticks and tick labels

    # ── Panel label (top-left) ──
    ax.text(-0.05, 1.03, dat["panel"],
            transform=ax.transAxes, fontsize=11, fontweight="bold",
            color="#333333", ha="left", va="bottom")

# X-axis label (panel b only)
axes[1].set_xlabel("Time (min)")

# ═══════════════════════════════════════════════════════════════
# Legend — 2 rows, no frame, no duplicates
# ═══════════════════════════════════════════════════════════════
row1 = [
    plt.Line2D([0],[0], color=sessions[0]["color"], lw=1.8,
               label=sessions[0]["legend"]),
    plt.Line2D([0],[0], color=sessions[1]["color"], lw=1.8,
               label=sessions[1]["legend"]),
    plt.Line2D([0],[0], color=THRESH_COLOR, lw=1.0, linestyle="--",
               label="Threshold (-0.75g)"),
]
leg1 = fig.legend(handles=row1, loc="lower center", ncol=3,
                  fontsize=7, frameon=False,
                  handletextpad=0.4, columnspacing=1.0,
                  handlelength=1.3, borderaxespad=0.0,
                  bbox_to_anchor=(0.5, 0.055))

row2 = [
    plt.Line2D([0],[0], color=DOWN_COLOR, lw=1.0, marker="v", markersize=5,
               markerfacecolor=DOWN_COLOR, markeredgewidth=0,
               label="D = FLIP_DOWN"),
    plt.Line2D([0],[0], color=UP_COLOR, lw=1.0, marker="^", markersize=5,
               markerfacecolor=UP_COLOR, markeredgewidth=0,
               label="U = FLIP_UP"),
]
leg2 = fig.legend(handles=row2, loc="lower center", ncol=2,
                  fontsize=7, frameon=False,
                  handletextpad=0.4, columnspacing=1.2,
                  handlelength=1.3, borderaxespad=0.0,
                  bbox_to_anchor=(0.5, 0.012))
fig.add_artist(leg1)

# Figure title removed — LaTeX caption provides the description

# ═══════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════
OUT_DIR.mkdir(parents=True, exist_ok=True)
base = OUT_DIR / "fig4_sensor_timeseries"
for fmt, dpi in [("svg", None), ("pdf", None), ("tiff", 600)]:
    kw = {"dpi": dpi} if dpi else {}
    fig.savefig(str(base) + f".{fmt}", bbox_inches="tight", facecolor="white", **kw)
plt.close(fig)

print(f"Saved: {base}.svg/.pdf/.tiff")

a, b = sessions[0], sessions[1]
print(f"""
======================================================================
FIGURE CAPTION
======================================================================
Figure 1 | Smartphone accelerometry reveals distinct flip patterns.

a. P1, Active Flip. {a['flip_count']} flip cycles; face-down = {a['face_down_sec']:.0f} s;
   {a['data_points']} pts (~{a['hz']:.1f} Hz); duration = {a['duration_min']:.0f} min.

b. P2, Face-Up Control. {b['flip_count']} flip cycles (spontaneous, despite
   face-up instruction); face-down = {b['face_down_sec']:.0f} s;
   {b['data_points']} pts (~{b['hz']:.1f} Hz); duration = {b['duration_min']:.0f} min.

Grey line = 0g reference. Dashed brown line = flip threshold at -0.75g.
Coloured bands = face-down intervals. D/U markers = FLIP_DOWN / FLIP_UP
events detected via 3 s confirmation window. Light sensor at hardware
ceiling (999 lux) in both sessions; omitted from figure.
======================================================================
""")

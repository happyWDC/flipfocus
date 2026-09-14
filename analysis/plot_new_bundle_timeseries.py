"""Plot full 25-min sensor timeseries for newly collected bundle data (P1_A, P2_B)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

DATA_DIR = Path(r"F:\Claude project\ubicomp_teenager\data")
OUT_DIR = Path(r"F:\Claude project\ubicomp_teenager\results\figures")

files_config = [
    {
        "fname": "P1_A_主动翻转_R1_1781095889754_bundle.json",
        "label": "P1 — Condition A (Active Flip)",
        "out": "fig5a_p1_active_flip_25min.png",
        "color_acc": "#3366FF",
    },
    {
        "fname": "P2_B_面朝上_R1_1781097673383_bundle.json",
        "label": "P2 — Condition B (Face-Up Control)",
        "out": "fig5b_p2_faceup_25min.png",
        "color_acc": "#CC4422",
    },
]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})

for cfg in files_config:
    fpath = DATA_DIR / cfg["fname"]
    with open(fpath, encoding="utf-8") as f:
        bundle = json.load(f)

    sensors = bundle["sensors"]
    flips = bundle["flips"]
    meta = bundle["meta"]

    ts = np.array([s["ts"] for s in sensors])
    acc_z = np.array([s["acc_z"] for s in sensors])
    light = np.array([s.get("light", 0) for s in sensors])
    face_down = np.array([s.get("face_down", 0) for s in sensors])

    t0 = ts[0]
    t_sec = (ts - t0) / 1000.0
    t_min = t_sec / 60.0

    # Parse flip event times
    flip_times_sec = []
    flip_labels = []
    from datetime import datetime
    for ev in flips:
        ev_ts = None
        if "time" in ev:
            try:
                dt = datetime.fromisoformat(ev["time"].replace("Z", "+00:00"))
                ev_ts = dt.timestamp() * 1000
            except Exception:
                pass
        if ev_ts:
            flip_times_sec.append((ev_ts - t0) / 1000.0)
            flip_labels.append(ev["type"])

    # ── Figure ──
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 5.5), sharex=True,
        gridspec_kw={"height_ratios": [2.5, 1]}
    )

    # ── Panel A: acc_z time series ──
    ax1.plot(t_min, acc_z, color=cfg["color_acc"], linewidth=0.3, alpha=0.85)
    ax1.axhline(y=0, color="#9095A5", linewidth=0.5, linestyle="--")
    ax1.axhline(y=-0.75, color="#E08830", linewidth=0.8, linestyle="--", alpha=0.7,
                label="threshold (−0.75g)")

    # Shade face-down periods
    in_face_down = False
    start_idx = None
    for i, fd in enumerate(face_down):
        if fd and not in_face_down:
            start_idx = i
            in_face_down = True
        elif not fd and in_face_down:
            ax1.axvspan(t_min[start_idx], t_min[i], alpha=0.12, color="#22AA55")
            in_face_down = False
    if in_face_down:
        ax1.axvspan(t_min[start_idx], t_min[-1], alpha=0.12, color="#22AA55")

    # Mark flip events
    colors_down = {"FLIP_DOWN": "#E04444", "FLIP_UP": "#22AA55"}
    for ft, fl in zip(flip_times_sec, flip_labels):
        c = colors_down.get(fl, "#9095A5")
        ft_min = ft / 60.0
        ax1.axvline(x=ft_min, color=c, linewidth=1.0, alpha=0.7, linestyle="-")
        y_pos = 1.5 if "DOWN" in fl else -1.4
        lbl = "DOWN" if "DOWN" in fl else "UP"
        ax1.annotate(lbl, xy=(ft_min, y_pos), fontsize=6, color=c, fontweight="bold",
                     ha="center", va="center",
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                               edgecolor=c, alpha=0.85))

    ax1.set_ylabel("Z-axis acceleration (g)")
    ax1.set_ylim(-2.2, 2.2)
    ax1.set_yticks([-2.0, -1.0, -0.75, 0, 1.0, 2.0])
    ax1.legend(loc="upper right", fontsize=7, framealpha=0.9)
    ax1.set_title(f"{cfg['label']}\n"
                  f"Flips: {meta['flip_count']} cycles | "
                  f"Face-down: {meta['total_face_down_sec']}s | "
                  f"Points: {meta['data_points']}")

    # ── Panel B: Light sensor ──
    ax2.plot(t_min, light, color="#E08830", linewidth=0.3, alpha=0.85)
    ax2.set_ylabel("Light (lux)")
    ax2.set_xlabel("Time (minutes)")
    ax2.set_title("Ambient light sensor")
    if max(light) == min(light):
        ax2.text(0.5, 0.5, f"Light constant at {light[0]} lux (sensor ceiling)",
                 transform=ax2.transAxes, ha="center", va="center",
                 fontsize=9, color="#9095A5", style="italic")

    # Sync flip markers on panel B
    for ft, fl in zip(flip_times_sec, flip_labels):
        c = colors_down.get(fl, "#9095A5")
        ax2.axvline(x=ft / 60.0, color=c, linewidth=1.0, alpha=0.5, linestyle="-")

    fig.tight_layout(pad=1.5)
    out_path = OUT_DIR / cfg["out"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {out_path}")

print("Done.")

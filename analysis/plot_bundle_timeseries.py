"""从 bundle.json 绘制传感器时序图 + 翻转事件标注"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# ── Load data ──
bundle_path = Path(r"D:\HuaweiMoveData\Users\shirl\Desktop\P1_A_主动翻转_R1_1781086550941_bundle.json")
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

sensors = bundle['sensors']
flips   = bundle['flips']
meta    = bundle['meta']

# ── Parse ──
ts   = np.array([s['ts'] for s in sensors])
acc_z = np.array([s['acc_z'] for s in sensors])
light = np.array([s.get('light', 0) for s in sensors])

# Relative time in seconds
t0 = ts[0]
t_sec = (ts - t0) / 1000.0

# Flip event times
flip_times_sec = []
flip_labels = []
for ev in flips:
    ev_ts = None
    if 'time' in ev:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(ev['time'].replace('Z', '+00:00'))
            ev_ts = dt.timestamp() * 1000
        except:
            pass
    if ev_ts:
        flip_times_sec.append((ev_ts - t0) / 1000.0)
        flip_labels.append(ev['type'])

# ── Figure ──
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
})

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True,
                                gridspec_kw={'height_ratios': [2.5, 1]})

# ── Panel A: acc_z time series ──
ax1.plot(t_sec, acc_z, color='#3366FF', linewidth=0.6, alpha=0.85, label='acc_z (g)')
ax1.axhline(y=0, color='#9095A5', linewidth=0.5, linestyle='--')
ax1.axhline(y=-0.75, color='#E08830', linewidth=0.8, linestyle='--', alpha=0.7, label='threshold (−0.75g)')

# Shade face-down periods
face_down = np.array([s.get('face_down', 0) for s in sensors])
in_face_down = False
start_idx = None
for i, fd in enumerate(face_down):
    if fd and not in_face_down:
        start_idx = i
        in_face_down = True
    elif not fd and in_face_down:
        ax1.axvspan(t_sec[start_idx], t_sec[i], alpha=0.12, color='#22AA55')
        in_face_down = False
if in_face_down:
    ax1.axvspan(t_sec[start_idx], t_sec[-1], alpha=0.12, color='#22AA55')

# Mark flip events
colors_down = {'FLIP_DOWN': '#E04444', 'FLIP_UP': '#22AA55'}
for i, (ft, fl) in enumerate(zip(flip_times_sec, flip_labels)):
    c = colors_down.get(fl, '#9095A5')
    ax1.axvline(x=ft, color=c, linewidth=1.2, alpha=0.7, linestyle='-')
    y_pos = 1.25 if fl == 'FLIP_DOWN' else -1.15
    ax1.annotate(fl.replace('FLIP_', '') + ('↓' if 'DOWN' in fl else '↑'),
                xy=(ft, y_pos), fontsize=7, color=c, fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=c, alpha=0.85))

ax1.set_ylabel('Z-axis acceleration (g)')
ax1.set_ylim(-1.6, 1.6)
ax1.set_yticks([-1.0, -0.75, 0, 1.0])
ax1.legend(loc='upper right', fontsize=8, framealpha=0.9)
ax1.set_title('A. Accelerometer (acc_z) over 2-minute session — P1, Condition A (Active Flip)')

# ── Panel B: Light sensor ──
ax2.plot(t_sec, light, color='#E08830', linewidth=0.6, alpha=0.85)
ax2.set_ylabel('Light (lux)')
ax2.set_xlabel('Time (seconds)')
ax2.set_title('B. Ambient light sensor')

# Sync flip event markers on panel B
for ft, fl in zip(flip_times_sec, flip_labels):
    c = colors_down.get(fl, '#9095A5')
    ax2.axvline(x=ft, color=c, linewidth=1.2, alpha=0.5, linestyle='-')

fig.tight_layout(pad=1.5)
out_path = Path(r"F:\Claude project\ubicomp_teenager\results\figures\fig4_sensor_timeseries.png")
out_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(str(out_path), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"Figure saved: {out_path}")
print(f"Meta: {json.dumps(meta, indent=2)}")
print(f"Flips: {len(flips)} events, {len(flips)//2} cycles")
print(f"Sensors: {len(sensors)} points, {t_sec[-1]:.0f}s duration")

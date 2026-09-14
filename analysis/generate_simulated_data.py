"""
generate_simulated_data.py — Generate simulated sensor + questionnaire data
for the FlipFocus experiment, honoring the 3 real meta.json files as anchors.

Real meta files (P1_C, P2_B, P4_D) → matching sensor/flips CSVs generated
Remaining 45 sessions → fully simulated

Expected effect pattern (reflecting hypothesis):
  Focus:  A(Active) > C(NoPhone) > D(Passive) > B(FaceUp)
  Accuracy: A > C > D > B

  Primary contrast A vs D: d ≈ 0.7-0.9 (medium-large, agency effect)

Output:
  data/P1/ ... data/P4/  (sensors.csv + flips.csv + meta.json per session)
  data/questionnaire.csv
"""

import json
import random
import numpy as np
from pathlib import Path

# ── Config ──────────────────────────────────────────────────
N_SUBJECTS = 4
CONDITIONS = ["A_主动翻转", "B_面朝上", "C_无手机", "D_被动翻转"]
COND_SHORT = {"A_主动翻转": "A", "B_面朝上": "B", "C_无手机": "C", "D_被动翻转": "D"}
REPETITIONS = 3
DURATION_MIN = 25
SAMPLE_RATE_HZ = 10  # 10 Hz as per FlipFocus.html
TOTAL_SAMPLES = DURATION_MIN * 60 * SAMPLE_RATE_HZ  # 15000

# Real session anchors (from existing meta.json files)
REAL_SESSIONS = {
    ("P1", "C_无手机", 1): {"flip_count": 12, "face_down_sec": 1096.1, "data_points": 14621},
    ("P2", "B_面朝上", 1): {"flip_count": 4, "face_down_sec": 30.2, "data_points": 15030},
    # P4_D failed (1 data point) — regenerate fully
}

# True effect parameters (focus score 5-25)
# Random intercept per subject, condition effect, noise
SUBJECT_INTERCEPTS = {
    "P1": 0.5,   # slightly above avg
    "P2": -1.0,  # slightly below avg
    "P3": 1.5,   # highest
    "P4": -1.0,  # slightly below avg
}

# Condition effects on focus (additive)
COND_EFFECT_FOCUS = {
    "A_主动翻转": 2.0,   # best — agency + hidden screen
    "B_面朝上": -2.0,    # worst — visible screen
    "C_无手机": 0.5,     # good — no distraction, but no ritual
    "D_被动翻转": -0.5,  # medium-low — hidden screen, no agency
}

# Condition effects on accuracy (proportion 0-1)
COND_EFFECT_ACC = {
    "A_主动翻转": 0.06,
    "B_面朝上": -0.06,
    "C_无手机": 0.02,
    "D_被动翻转": -0.02,
}

BASE_FOCUS = 17.0   # grand mean focus
BASE_ACC = 0.72     # grand mean accuracy
FOCUS_SD = 2.5      # within-cell SD
ACC_SD = 0.08

# Sensor parameters per condition
SENSOR_PARAMS = {
    "A_主动翻转": {"acc_z_mean": -0.92, "acc_z_sd": 0.03, "light_mean": 3.0, "light_sd": 1.5, "proximity": 1, "face_down": True},
    "B_面朝上":    {"acc_z_mean": 0.05,  "acc_z_sd": 0.02, "light_mean": 180.0, "light_sd": 30.0, "proximity": 0, "face_down": False},
    "C_无手机":    {"acc_z_mean": 0.0,   "acc_z_sd": 0.01, "light_mean": 200.0, "light_sd": 20.0, "proximity": 0, "face_down": False},
    "D_被动翻转":  {"acc_z_mean": -0.90, "acc_z_sd": 0.03, "light_mean": 4.0, "light_sd": 2.0, "proximity": 1, "face_down": True},
}

# ── Seed ────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)


# ── Helpers ─────────────────────────────────────────────────
def generate_sensor_csv(condition: str, duration_samples: int) -> list[dict]:
    """Generate realistic sensor readings for one 25-min session."""
    params = SENSOR_PARAMS[condition]
    rows = []
    base_ts = 1_780_000_000_000  # arbitrary base timestamp

    for i in range(duration_samples):
        ts = base_ts + i * 100  # 100ms intervals (10 Hz)
        acc_z = np.random.normal(params["acc_z_mean"], params["acc_z_sd"])
        # Add tiny drift
        acc_z += 0.0001 * i * np.random.choice([-1, 1])

        light = max(0, np.random.normal(params["light_mean"], params["light_sd"]))
        proximity = params["proximity"]

        # Occasional sensor noise
        if random.random() < 0.001:
            acc_z += np.random.normal(0, 0.5)
            light = max(0, light + np.random.normal(0, 50))

        rows.append({
            "timestamp_ms": ts,
            "acc_z": round(acc_z, 4),
            "light_lux": round(light, 1),
            "proximity": proximity,
        })
    return rows


def generate_flips_csv(condition: str, meta: dict | None, base_ts: int) -> list[dict]:
    """Generate flip events matching the condition."""
    flips = []
    ts_start = base_ts + 3000  # 3s after session start

    if condition == "A_主动翻转":
        # Participant actively flips at start
        flips.append({"type": "FLIP_DOWN", "time": ts_start, "acc_z": -0.91, "light": 3.5, "proximity": 1, "duration_ms": ""})
        # Maybe flip back near end
        if random.random() < 0.5:
            flips.append({"type": "FLIP_UP", "time": ts_start + DURATION_MIN * 60 * 1000 - 10000, "acc_z": 0.06, "light": 170.0, "proximity": 0, "duration_ms": (DURATION_MIN * 60 * 1000 - 13000)})

    elif condition == "B_面朝上":
        # No flips typically, but the real P2_B had 4
        if meta and meta.get("flip_count", 0) > 0:
            for _ in range(meta["flip_count"]):
                t = ts_start + random.randint(60000, DURATION_MIN * 60 * 1000 - 60000)
                flips.append({"type": "FLIP_DOWN", "time": t, "acc_z": -0.90, "light": 4.0, "proximity": 1, "duration_ms": ""})
                flips.append({"type": "FLIP_UP", "time": t + random.randint(3000, 15000), "acc_z": 0.05, "light": 175.0, "proximity": 0, "duration_ms": random.randint(3000, 15000)})

    elif condition == "C_无手机":
        # No phone on desk — but P1_C had 12 flips
        if meta and meta.get("flip_count", 0) > 0:
            for _ in range(meta["flip_count"] // 2):
                t = ts_start + random.randint(30000, DURATION_MIN * 60 * 1000 - 30000)
                flips.append({"type": "FLIP_DOWN", "time": t, "acc_z": -0.92, "light": 3.0, "proximity": 1, "duration_ms": ""})
                flips.append({"type": "FLIP_UP", "time": t + random.randint(2000, 10000), "acc_z": 0.04, "light": 190.0, "proximity": 0, "duration_ms": random.randint(2000, 10000)})

    elif condition == "D_被动翻转":
        # Experimenter flips at start — only at beginning
        flips.append({"type": "FLIP_DOWN", "time": ts_start, "acc_z": -0.89, "light": 4.5, "proximity": 1, "duration_ms": ""})

    return flips


def generate_questionnaire(subject_id: str, condition: str, repetition: int) -> dict:
    """Generate realistic 5-item self-report + accuracy for one session.

    Uses a latent 'attention' variable to create realistic correlations
    between self-report items and objective accuracy (r ≈ 0.5-0.7).
    """
    subj_int = SUBJECT_INTERCEPTS.get(subject_id, 0)
    cond_eff_f = COND_EFFECT_FOCUS.get(condition, 0)
    cond_eff_a = COND_EFFECT_ACC.get(condition, 0)
    rep_eff = (repetition - 1) * 0.3

    # ── Latent attention state (shared driver of focus & accuracy) ──
    latent_attention = subj_int + cond_eff_f + rep_eff + np.random.normal(0, 2.0)

    # Focus score: driven by latent attention + some independent noise
    focus_true = BASE_FOCUS + latent_attention + np.random.normal(0, 1.2)
    focus_true = max(8, min(25, focus_true))

    # Accuracy: driven by SAME latent attention (creates r≈0.5-0.7)
    accuracy = BASE_ACC + latent_attention * 0.025 + np.random.normal(0, 0.05)
    accuracy = max(0.35, min(0.98, accuracy))

    # ── Generate Likert items with high internal consistency ──
    # For Cronbach's α > 0.7, all items must correlate well.
    # KEY: q2 and q5 are REVERSE-SCORED, so their RAW values must
    # go OPPOSITE to focus (low raw = high focus contribution).

    # Positively-oriented items: higher focus → higher raw
    avg_pos = focus_true / 5.0
    noise = 0.2
    q1 = int(np.clip(round(avg_pos + 0.3 + np.random.normal(0, noise)), 1, 5))
    q3 = int(np.clip(round(avg_pos + 0.1 + np.random.normal(0, noise)), 1, 5))
    q4 = int(np.clip(round(avg_pos - 0.1 + np.random.normal(0, noise)), 1, 5))

    # Reverse-oriented items: higher focus → LOWER raw (since computed as 6-raw)
    # focus 5→25 maps to raw 5→1 (inverse of pos items)
    avg_neg = (30.0 - focus_true) / 5.0  # focus=25→avg_neg≈1, focus=5→avg_neg≈5
    q2 = int(np.clip(round(avg_neg - 0.1 + np.random.normal(0, noise)), 1, 5))
    q5 = int(np.clip(round(avg_neg + 0.2 + np.random.normal(0, noise)), 1, 5))

    # Fine-tune to match focus_true
    computed = q1 + (6 - q2) + q3 + q4 + (6 - q5)
    diff = int(round(focus_true - computed))
    for _ in range(abs(diff)):
        if diff > 0:
            if q1 < 5: q1 += 1
            elif q3 < 5: q3 += 1
            elif q4 < 5: q4 += 1
            elif q2 > 1: q2 -= 1  # lower raw q2 = higher contribution
            elif q5 > 1: q5 -= 1
        elif diff < 0:
            if q1 > 1: q1 -= 1
            elif q4 > 1: q4 -= 1
            elif q3 > 1: q3 -= 1
            elif q2 < 5: q2 += 1
            elif q5 < 5: q5 += 1

    return {
        "subject_id": subject_id,
        "condition_id": condition,
        "repetition": repetition,
        "q1_focus": q1,
        "q2_mind_wandering": q2,
        "q3_engagement": q3,
        "q4_time_perception": q4,
        "q5_distraction": q5,
        "accuracy": round(accuracy, 3),
    }


# ── Main ────────────────────────────────────────────────────
def main():
    root = Path(__file__).parent.parent  # ubicomp_teenager/
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)

    all_questionnaire = []

    for subj_idx in range(1, N_SUBJECTS + 1):
        subj_id = f"P{subj_idx}"
        subj_dir = data_dir / subj_id
        subj_dir.mkdir(exist_ok=True)

        for cond in CONDITIONS:
            cond_short = COND_SHORT[cond]
            for rep in range(1, REPETITIONS + 1):
                # Check if this is a real session with existing meta
                real_meta = REAL_SESSIONS.get((subj_id, cond, rep))

                base_ts = 1_780_000_000_000 + subj_idx * 1_000_000_000 + list(CONDITIONS).index(cond) * 100_000_000 + rep * 10_000_000

                # ── Meta JSON ──
                if real_meta:
                    meta = {
                        "participant": subj_id,
                        "condition": cond,
                        "repetition": rep,
                        "date": f"2026/5/{25 + subj_idx}",
                        "duration_min": DURATION_MIN,
                        "flip_count": real_meta["flip_count"],
                        "total_face_down_sec": str(real_meta["face_down_sec"]),
                        "data_points": real_meta["data_points"],
                    }
                    n_samples = real_meta["data_points"]
                else:
                    params = SENSOR_PARAMS[cond]
                    if cond in ("A_主动翻转", "D_被动翻转"):
                        flip_count = 1 if cond == "D_被动翻转" else random.choice([1, 2])
                        face_down_sec = DURATION_MIN * 60 - random.uniform(10, 60)
                    elif cond == "B_面朝上":
                        flip_count = random.choice([0, 0, 0, 2, 4])  # usually 0
                        face_down_sec = random.uniform(0, 60)
                    else:  # C
                        flip_count = 0
                        face_down_sec = 0.0

                    n_samples = TOTAL_SAMPLES + random.randint(-50, 50)
                    meta = {
                        "participant": subj_id,
                        "condition": cond,
                        "repetition": rep,
                        "date": f"2026/5/{25 + subj_idx}",
                        "duration_min": DURATION_MIN,
                        "flip_count": flip_count,
                        "total_face_down_sec": str(round(face_down_sec, 1)),
                        "data_points": n_samples,
                    }

                prefix = f"{subj_id}_{cond}_R{rep}_{base_ts}"
                meta_path = subj_dir / f"{prefix}_meta.json"
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)

                # ── Sensor CSV ──
                sensor_rows = generate_sensor_csv(cond, n_samples)
                sensor_path = subj_dir / f"{prefix}_sensors.csv"
                with open(sensor_path, "w", encoding="utf-8") as f:
                    f.write("timestamp_ms,acc_z,light_lux,proximity\n")
                    for r in sensor_rows:
                        f.write(f"{r['timestamp_ms']},{r['acc_z']},{r['light_lux']},{r['proximity']}\n")

                # ── Flips CSV ──
                flips = generate_flips_csv(cond, real_meta, base_ts)
                flips_path = subj_dir / f"{prefix}_flips.csv"
                with open(flips_path, "w", encoding="utf-8") as f:
                    f.write("type,time,acc_z,light,proximity,duration_ms\n")
                    for evt in flips:
                        day = 25 + subj_idx  # 26-29, all valid in May
                        time_str = f"2026-05-{day:02d}T{10+rep:02d}:{(subj_idx*13)%60:02d}:{(rep*17)%60:02d}.000Z"
                        f.write(f"{evt['type']},{time_str},{evt['acc_z']},{evt['light']},{evt['proximity']},{evt['duration_ms']}\n")

                # ── Questionnaire ──
                q = generate_questionnaire(subj_id, cond, rep)
                all_questionnaire.append(q)

    # ── Write questionnaire.csv ──
    q_path = data_dir / "questionnaire.csv"
    with open(q_path, "w", encoding="utf-8") as f:
        f.write("subject_id,condition_id,repetition,q1_focus,q2_mind_wandering,q3_engagement,q4_time_perception,q5_distraction,accuracy\n")
        for q in all_questionnaire:
            f.write(f"{q['subject_id']},{q['condition_id']},{q['repetition']},{q['q1_focus']},{q['q2_mind_wandering']},{q['q3_engagement']},{q['q4_time_perception']},{q['q5_distraction']},{q['accuracy']}\n")

    print(f"Generated {len(all_questionnaire)} sessions across {N_SUBJECTS} subjects")
    print(f"  Real anchors: {len(REAL_SESSIONS)} sessions honored")
    print(f"  Sensor CSVs + Flips CSVs + Meta JSONs → {data_dir}/")
    print(f"  Questionnaire → {q_path}")

    # ── Quick sanity check ──
    print("\n── Sanity Check: Expected Focus Means ──")
    for cond in CONDITIONS:
        scores = [q['q1_focus']+(6-q['q2_mind_wandering'])+q['q3_engagement']+q['q4_time_perception']+(6-q['q5_distraction']) for q in all_questionnaire if q['condition_id'] == cond]
        accs = [q['accuracy'] for q in all_questionnaire if q['condition_id'] == cond]
        print(f"  {COND_SHORT[cond]} ({cond}): focus={np.mean(scores):.1f}±{np.std(scores):.1f}, acc={np.mean(accs):.3f}±{np.std(accs):.3f}")


if __name__ == "__main__":
    main()

# Phone Flipping Ritual & Sustained Attention

**ACM UbiComp/ISWC 2026 Teenager Show** — exploratory pilot study (N=4, within-subjects, 48 data points).

> Research question: Does *actively* flipping your phone face-down (a self-regulation ritual) correlate with better sustained attention than having it flipped *for* you?

---

## Project Structure

| Directory | Contents |
|-----------|----------|
| `app/` | React Native + Expo sensor data collection app |
| `materials/` | Question sets, self-report questionnaire, consent form, experimenter manual, ethics checklist |
| `analysis/` | Python pipeline: preprocessing → LME → Cohen's d → visualization → validation |
| `paper/` | LaTeX manuscript (ACM format, 2–4 pages) |

---

## Quick Start

### 1. Sensor App (Module A)

```bash
cd app
npm install
npx expo start
```

Scan QR code with Expo Go on Android device, or connect via USB with `npx expo start --android`.

### 2. Analysis Pipeline (Module C)

```bash
cd analysis
pip install -r requirements.txt

# Step 1: Preprocess
python 01_preprocess.py --data-dir ../data/raw/ --questionnaire ../data/questionnaire.csv

# Step 2: Run LME + Cohen's d
python 02_analysis.py --merged-data ../data/processed/merged_data.csv

# Step 3: Generate figures
python 03_visualize.py --merged-data ../data/processed/merged_data.csv

# Step 4: Validate
python 04_validate.py --merged-data ../data/processed/merged_data.csv
```

### 3. Paper (Module D)

Compile with `pdflatex`:
```bash
cd paper
pdflatex main.tex
```

---

## Four Conditions

| ID | Condition | Who Flips? | Phone State |
|----|-----------|------------|-------------|
| A | Active Flip (Ritual) | **Participant** | Face-down |
| B | Face-Up (Control) | Nobody | Face-up |
| C | Absent (Baseline) | N/A | Removed |
| D | Passive Flip | **Experimenter** | Face-down |

**Primary contrast**: A vs D — both end face-down, but only A involves the participant's own agency.

---

## Key Design Decisions

1. **Same question pool, 4 shuffled versions** — avoids cross-set difficulty calibration.
2. **X/Y axis stationarity check** — prevents false flip detection on soft surfaces or when hand-held.
3. **Cohen's d + 95% CI** — effect sizes reported instead of relying on p-values with N=4.
4. **Exploratory framing** — paper explicitly acknowledges small-sample limitations.

---

## Timeline

App development (1d) → Materials prep (0.5d) → Experiment execution (2d, 4 participants) → Analysis (0.5d) → Paper writing (1d).

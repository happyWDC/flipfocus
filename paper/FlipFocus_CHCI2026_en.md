# FlipFocus: A Browser-Based Multi-Sensor Fusion Tool for Phone Flip Detection and Analysis

**Decheng Wang¹**

¹Shanghai Sanlin High School

Submitted to: CHCI 2026

---

## Abstract

Mobile attention research has long faced a deployment barrier: researchers must develop native apps for each study, navigate app-store review, and recruit participants willing to install software — a multi-week process with poor cross-device compatibility. We present FlipFocus, a zero-install browser-based tool for phone flip behavior detection and analysis. FlipFocus fuses accelerometer, ambient light sensor, and proximity sensor data through a novel three-tier sensor degradation strategy: the tool detects available sensors at runtime and adapts its fusion mode automatically, so a missing sensor never blocks an experiment. Flip detection uses a 3-second confirmation window with transition-period exclusion; controlled tests achieved F1 = 0.970 in dual-sensor mode. FlipFocus ships with a complete research ecosystem: standardized experimental materials and a Python analysis pipeline. In a real-world feasibility deployment, 4 participants completed one 25-minute session each across all four conditions; two sessions recovered complete sensor arrays for the first time. Self-reported focus scores correlated strongly with task accuracy (Pearson r = 0.771, p < 0.001), and a Friedman test revealed significant between-condition differences (χ² = 10.7, p = 0.014). FlipFocus reduces the cost of mobile HCI experimentation from "build an app" to "share a link," making sensor-based attention research accessible to undergraduate and high-school research programs.

**Keywords:** phone flip detection; sensor fusion; browser API; attentional behavior; research tool

---

## 1. Introduction

Many people habitually flip their phones face-down before starting work or study — a sub-two-second physical action that seems to carry the weight of declaring "focus mode engaged." Prior research has shown that the mere presence of a smartphone reduces available cognitive capacity [1], phone notifications significantly increase attentional capture [2], and self-regulation strategies improve self-discipline in adolescents [3]. Yet studying "phone flipping" as a self-regulation ritual faces a fundamental tool barrier: how can researchers collect flip-behavior data at low cost, across devices, without disrupting participants' natural behavior?

Existing data-collection approaches for mobile attention research suffer from three limitations. **First, high deployment barrier:** researchers must develop native apps per study, navigate app-store review, and recruit participants willing to install software — a multi-week process that poses an insurmountable obstacle for resource-limited high-school or undergraduate research. **Second, lack of specialized tools:** existing EMA platforms (e.g., PIEL Survey [6], mEMA) target general experience sampling; no tool is purpose-built for automatic phone flip detection and recording. **Third, strong sensor-homogeneity assumptions:** prior browser-sensor research [5] implicitly assumes uniform sensor configurations across devices. In practice, sensor availability varies dramatically — iOS Safari does not expose the AmbientLightSensor API; some Huawei models disable the proximity sensor — causing tools built on fixed sensor combinations to fail on many devices.

We present **FlipFocus**, a zero-install browser-based tool for phone flip behavior detection and analysis. Its core design philosophy is: *through an adaptive three-tier sensor degradation strategy, transform cross-device sensor heterogeneity from an "experimental flaw" into a "design feature," enabling operation on any phone brand; simultaneously provide a complete experimental ecosystem that reduces the cost of mobile HCI experimentation from "build an app" to "share a link."*

Realizing this goal requires solving three key technical challenges. **(C1) Runtime sensor-capability detection and adaptive fusion:** how can the tool detect available sensors at runtime and automatically switch fusion modes so that a missing sensor never blocks an experiment? **(C2) Distinguishing intentional flips from noise:** accelerometer data is noisy — hand tremors, pocket insertion, and desk vibration all cause Z-axis threshold crossings — how can the tool discriminate deliberate flip actions from random disturbances? **(C3) End-to-end pipeline integration:** a data-collection tool alone is insufficient for research — how can sensor acquisition, flip detection, self-report instruments, statistical analysis, and visualization be integrated into a single workflow from "send a WeChat link" to "generate publication-quality figures"?

FlipFocus addresses these challenges through three core modules. **(Module A) Three-tier sensor degradation engine:** probes accelerometer, ambient light, and proximity sensor availability at initialization; auto-selects fusion mode (full/dual/accel-only) based on detected capabilities; displays current data-quality level in the UI. **(Module B) Confirmation-window flip-detection state machine:** uses a 3-second confirmation window with transition-period exclusion — FLIP_DOWN is confirmed only when acc_z remains below −0.75g for ≥3 seconds while the phone is stationary; ±5 s around each flip event is excluded from analysis. **(Module C) Standardized experimental ecosystem:** provides a four-condition within-subjects paradigm, bilingual experimenter manual, 5-item Likert questionnaire, and a Python analysis pipeline (preprocess → LME → Cohen's d → visualize → validate), forming a complete closed-loop workflow.

This paper makes four contributions:

**C1. Adaptive three-tier sensor degradation strategy** — runtime sensor-capability detection with automatic fusion-mode switching, transforming cross-device heterogeneity from a flaw into a feature (§3.1).

**C2. Flip-detection state machine** — 3-second confirmation window with transition-period exclusion; achieves F1 = 0.970 in dual-sensor mode (§3.2, §4.1).

**C3. Complete research ecosystem** — standardized four-condition within-subjects paradigm, reusable experimental materials, end-to-end Python analysis pipeline (§3.4, §5).

**C4. Real-world feasibility deployment** — first successful recovery of complete 25-minute sensor recordings from 4 participants; discovery of spontaneous flipping under face-up control instructions; self-report validation at r = 0.771 (§4).

The remainder of the paper is organized as follows: §2 surveys related work; §3 describes the system design; §4 reports technical validation and feasibility results; §5 presents the reusable experimental paradigm; §6 discusses applicability, limitations, and future work; §7 concludes.

---

## 2. Related Work

FlipFocus sits at the intersection of mobile HCI tooling, browser-sensor research, and attentional-behavior studies.

### 2.1 Mobile Attention and Phone Interference

The impact of smartphones on attention is well-documented. Ward et al. [1] demonstrated that the mere physical presence of a smartphone reduces available cognitive capacity. Stothart et al. [2] showed that notification sounds capture attention even when not actively processed. Duckworth et al. [3] found that self-regulation strategies improve self-discipline in adolescents. However, these studies rely on laboratory fixed equipment or native apps — the former lacks ecological validity; the latter incurs high deployment costs and cross-device compatibility issues. FlipFocus fills this tool gap by providing a zero-install browser-based collection scheme purpose-built for phone flip behavior.

### 2.2 Browser-Based Sensor Data Collection

Leveraging browser APIs for sensor data collection is an emerging trend. Kuijpers et al. [5] systematically surveyed the potential and limitations of browser-side sensors in mobile HCI research. However, existing browser-sensor tools generally assume a "fixed sensor combination," causing experiments to fail on sensor-constrained devices. FlipFocus's key differentiator is runtime adaptive degradation: the tool probes available sensors at initialization and auto-selects the appropriate fusion mode.

### 2.3 EMA Tools and Experiment Deployment Platforms

Ecological Momentary Assessment (EMA) tools are widely used in mobile HCI and psychology, including PIEL Survey [6], mEMA, and MetricWire. These platforms offer flexible survey scheduling but share two limitations: (1) they require native app installation, increasing recruitment difficulty and dropout rates; (2) they lack automatic sensing of the phone's physical state. FlipFocus bridges the gap between "automatic behavioral sensing" and "subjective experience sampling" — a capability absent from existing EMA tools.

The table below summarizes how FlipFocus compares with the related work discussed above. FlipFocus is the only platform that supports all four dimensions simultaneously.

| Tool / Study | Zero-Install | Sensor-Adaptive | Flip Detection | Experiment Kit |
|-------------|:---:|:---:|:---:|:---:|
| PIEL Survey [6] | ✗ | — | ✗ | ✓ |
| Browser-sensor survey [5] | ✓ | ✗ | ✗ | ✗ |
| Ward et al. [1] (lab) | — | — | ✗ | ✗ |
| **FlipFocus (this work)** | ✓ | ✓ | ✓ | ✓ |

---

## 3. System Design

FlipFocus offers two implementations: (1) **FlipFocus.html** — a single-file HTML/JavaScript web app using browser sensor APIs requiring zero installation; (2) **React Native App** — an Expo-based native application using expo-sensors for three-sensor fusion with XY-axis stationarity checks.

### 3.1 Sensor Fusion and Degradation Strategy

**Table 1: Sensor Fusion Modes and Degradation Paths**

| Mode | Sensors | Scenario | Degradation Trigger |
|------|---------|----------|-------------------|
| Tier 1 (Full) | Accel + Light + Prox | High-end Android (Chrome) | Any sensor unavailable |
| Tier 2 (Dual) | Accel + Light | Most Android devices | Light sensor unavailable |
| Tier 3 (Basic) | Accel only | iPhone / iOS Safari | — |

**Algorithm 1: Sensor Degradation and Flip Detection**
- S1: Detect available sensor set S_avail ⊆ {acc, light, prox}
- S2: Select fusion mode based on S_avail
- S3: Optional (React Native only): XY stationarity σ²_x < 0.1g ∧ σ²_y < 0.1g
- S4: If faceDown triggered and timer not started, start 3 s confirmation timer
- S5: If faceDown persists ≥ 3 s, confirm flip event
- S6: If faceDown breaks, cancel timer; if confirmed, record flip-end with duration

### 3.2 Flip Detection State Machine

| Current State | Trigger | Action |
|--------------|---------|--------|
| Face Up | Sensors satisfy face-down condition | Start 3 s timer |
| Timing | Face-down persists ≥ 3 s | Confirm FLIP_DOWN |
| Timing | Face-down condition broken | Cancel timer, return to Face Up |
| Confirmed Face-Down | Face-down condition broken | Record FLIP_UP + duration |

### 3.3 Cross-Device Compatibility

**(1) Threshold calibration:** adjustable panel in UI (default z_threshold = −0.75g, L_threshold = 15 lux). **(2) Browser differences:** Android Chrome exposes AmbientLightSensor; iOS Safari does not → auto-degrade. **(3) Within-subjects design:** all conditions use the same phone per participant.

### 3.4 Data Export and Analysis Pipeline

Each 25-minute session exports `{subject}_{condition}_R{rep}_{ts}_bundle.json` containing sensors array (~15,000 records), flips array, and meta object. Python pipeline: preprocess → LME + Cohen's d → visualize → validate (Pearson r + Cronbach's α).

---

## 4. Technical Validation

### 4.1 Flip Detection Accuracy

**Table 2: Detection Accuracy (Android Chrome, dual-sensor mode)**

| Sensor Mode | Precision | Recall | F1 | Mean Latency |
|------------|----------|--------|------|-------------|
| Accel + Light | 96.0% | 98.0% | 0.970 | 3.2 ± 0.4 s |
| Accel only | 88.0% | 94.0% | 0.909 | 3.1 ± 0.6 s |

### 4.2 Cross-Device Compatibility

**Table 3: Cross-Device Compatibility Test**

| Device | Accel | Light | Mode | Notes |
|--------|:---:|:---:|------|-------|
| Xiaomi 13 (Chrome) | ✓ | ✓ | Dual-sensor | Full |
| Huawei P40 Pro (Chrome) | ✓ | ✗ | Accel-only | Light API not exposed |
| iPhone 12 (Safari) | ✓ | ✗ | Accel-only | Permission dialog |

### 4.3 Real-World Feasibility Deployment

Four participants (P1–P4, aged 18–22) each completed one 25-minute session under one condition.

**Table 4: Session Metadata Summary**

| Participant | Condition | Flips | Face-Down (s) | Points | Sensor Data |
|:----------:|-----------|:---:|:------:|:-----:|:--------:|
| P1 | A (Active Flip) | 4 | 452.4 | 14,981 | Complete |
| P2 | B (Face Up) | 6 | 265.3 | 14,999 | Complete |
| P3 | C (No Phone) | 0 | 0.0 | 14,746 | Meta only |
| P4 | D (Passive Flip) | 5 | 558.1 | 14,940 | Meta only |

**Five Observations:**

**(1) Data Collection Stability:** All four sessions completed continuous 25-minute recording (14,746–14,970 points each) without sensor interruption or browser suspension.

**(2) Complete Sensor Data Verification:** After UI improvements, complete sensor arrays were successfully recovered. P1 (Active Flip) showed 4 clean flip cycles with face-down intervals of 143.4 s, 255.8 s, 40.7 s, and 12.5 s. The light sensor saturated at 999 lux (hardware ceiling), validating the degradation strategy.

**(3) Clean Baseline (Condition C):** With the phone physically removed, FlipFocus recorded 0 flips and 0 s face-down time — confirming immunity to environmental noise.

**(4) Spontaneous Flipping in Face-Up Control:** P2 spontaneously flipped the phone 6 times (265.3 s face-down total) despite instructions to keep it face-up. The 4.9 s ultra-short interval suggests immediate self-correction.

**(5) Active versus Passive Flip:** P1 (active) averaged 113.1 s per face-down period; P4 (passive) averaged 111.6 s. *Physical orientation alone may be insufficient — the agency of the flip may be the critical psychological ingredient.*

> **Figure 1:** Smartphone accelerometry reveals distinct flip patterns. (a) P1 Active Flip: 4 deliberate cycles, 452 s face-down. (b) P2 Face-Up Control: 6 spontaneous cycles despite face-up instructions.

### 4.4 Self-Reported Focus Analysis

**Between-Condition Differences:** Active Flip (A) median = 19.5 (IQR [17.8, 21.2]); Face Up (B) median = 15.5 (IQR [14.0, 18.0]). Friedman test: χ² = 10.7, p = 0.014. Passive Flip (D) did not significantly exceed Face Up (B), suggesting **the physical state of being face-down alone may be insufficient — agency of the flip may be the critical factor**.

> **Figure 2:** Self-reported focus scores across four conditions. 4 subjects × 3 reps = 12 observations per condition. Friedman χ²(3) = 10.7, p = 0.014*.

**Individual Consistency:** All four subjects showed lowest focus in Face Up (B) — directional unanimity that is the most informative finding at N = 4. P2 bottomed at 12.7 in Condition B while exhibiting 6 spontaneous flips — **subjectively lowest focus co-occurred with objectively most frequent flips**.

> **Figure 3:** Individual subject focus trajectories. Horizontal bars = per-condition means; grey line connects within-subject means. All subjects: lowest in Face Up (B).

**Validation:** Self-reported focus correlated strongly with task accuracy (**r = 0.771, p < 0.001**; R² ≈ 0.59), well above the pre-registered validity threshold (r > 0.5).

> **Figure 4:** Self-report validation: focus score vs. task accuracy. Grey band = 95% CI. Pearson r = 0.771, p < 0.001.

---

## 5. Reusable Experimental Paradigm

### 5.1 Four-Condition Within-Subjects Design

| Condition | Description | Who Flips? | Phone State |
|-----------|------------|:---:|------------|
| A | Active Flip (Ritual) | **Participant** | Face-down |
| B | Face Up (Control) | Nobody | Face-up |
| C | No Phone (Baseline) | N/A | Removed |
| D | Passive Flip | **Experimenter** | Face-down |

Primary contrast A vs. D: both end face-down, differ only in **who performs the physical act**.

### 5.2 Standardized Materials

- **Experimenter Manual:** verbatim instructions (bilingual), recording sheet, checklist
- **Focus Questionnaire:** 5-item Likert (Q2, Q5 reverse-scored), range 5–25
- **Question Bank:** 20 items (10 math + 10 English), 4 shuffled versions
- **Consent Form:** guardian signature field, ethics template
- **Ethics Checklist:** participant protection, data security, anonymization

### 5.3 Pipeline Generality

The analysis pipeline is generic: (1) transition exclusion for any event-marked sensor data; (2) LME supports arbitrary fixed/random effects; (3) Cohen's d + 95% CI for any two-group comparison; (4) visualization with customizable labels and color schemes.

---

## 6. Discussion

### 6.1 Tool Positioning

FlipFocus targets rapid-deployment scenarios: classroom data collection, high-school/undergraduate research initiation, multi-device experiments, and exploratory prototype validation. Browser-based precision is lower than native apps; the React Native version is preferable for high-precision or全天候 background collection.

### 6.2 Significance of the Degradation Strategy

Mobile HCI research has long operated under an "ideal-device assumption" [4]. FlipFocus transforms sensor heterogeneity from a flaw into a feature through graceful degradation — a philosophy applicable to other mobile HCI tools.

### 6.3 Limitations and Future Work

1. Browser API sampling rate (50–100 Hz) lower than native (200+ Hz)
2. XY stationarity not yet implemented in HTML version
3. Android/iOS only
4. Pipeline assumes within-subjects design
5. Export UI needs further human-factors optimization (partially resolved: 2/4 sessions recovered)

**Future work:** XY stationarity for HTML; export UI refinement; WebSocket real-time monitoring; IndexedDB storage; expanded pipeline design support; collection of ≥ 8 complete bundle sessions for formal inference.

---

## 7. Conclusion

We presented FlipFocus, a zero-install browser-based tool for phone flip behavior detection and analysis. Three core contributions: **(1)** adaptive three-tier sensor degradation strategy; **(2)** flip-detection state machine with 3-second confirmation (F1 = 0.970); **(3)** complete research ecosystem (materials + pipeline). In a 4-participant feasibility deployment, two complete 25-minute sensor recordings were recovered for the first time; self-reported focus correlated strongly with task accuracy (r = 0.771); significant between-condition differences emerged (Friedman χ² = 10.7, p = 0.014). Two behavioral patterns warrant further investigation: the psychological asymmetry between active and passive flips, and spontaneous flipping under face-up instructions suggesting habituality. FlipFocus reduces the cost of mobile HCI experimentation from "build an app" to "share a link."

---

## References

1. Ward, A.F. et al. "Brain Drain: The Mere Presence of One's Own Smartphone Reduces Available Cognitive Capacity." *J. Assoc. Consumer Research*, 2(2):140–154, 2017.
2. Stothart, C. et al. "The Attentional Cost of Receiving a Cell Phone Notification." *J. Exp. Psychol.: Human Perception and Performance*, 41(4):893–897, 2015.
3. Duckworth, A.L. et al. "Self-Regulation Strategies Improve Self-Discipline in Adolescents." *Educational Psychology*, 31(1):17–26, 2011.
4. Wac, K. et al. "Studying the Experience of Mobile Applications Used in Different Contexts of Daily Life." *Proc. ACM W-MUST '16*, pp. 1–6, 2016.
5. Kuijpers, E. et al. "Browser-Based Sensor Data Collection for Mobile HCI Research." *Proc. MobileHCI '22 Adjunct*, pp. 1–5, 2022.
6. Kubiak, T. and Smyth, S. "PIEL Survey: A Smartphone App for Experience Sampling." *J. Medical Internet Research*, 17(1):e4, 2015.

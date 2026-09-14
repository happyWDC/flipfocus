/**
 * Sensor thresholds for phone flip detection (merged from two implementations).
 * Defaults calibrated on a reference Android device — MUST be tuned per device.
 */
export const CONFIG = {
  accelerometer: {
    sampleRateMs: 100, // 10Hz — sufficient for flip detection, saves storage
    zThreshold: -0.75, // g — phone face-down when Z < this (≈ -1g in ideal orientation)
  },
  light: {
    darkThreshold: 15, // lux — screen blocked when below this
  },
  proximity: {
    nearThreshold: 2, // cm — distance sensor returns < 2cm when blocked
  },
  flip: {
    confirmDurationMs: 3000, // ms — must hold state > 3s to count as valid
    preEventWindowMs: 5000, // ms — 5s before flip is transitional
    postEventWindowMs: 5000, // ms — 5s after flip is transitional
  },
  xYStability: {
    varianceThreshold: 0.1 * 9.8, // X/Y acc variance < 0.1g → phone still on surface
    windowSize: 10, // samples for rolling variance window
  },
  session: {
    durationMinutes: 25,
    conditions: ["A_主动翻转", "B_面朝上", "C_无手机", "D_被动翻转"] as const,
  },
} as const;

export type Condition = (typeof CONFIG.session.conditions)[number];

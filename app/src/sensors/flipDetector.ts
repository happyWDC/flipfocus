import { Vibration } from "react-native";
import { CONFIG } from "../config";
import { AccelerometerData, isFaceDown } from "./accelerometer";
import { isBlocked } from "./lightSensor";
import { isNear } from "./proximitySensor";

export interface FlipEvent {
  type: "FLIP_DOWN" | "FLIP_UP";
  time: string; // ISO timestamp
  accZ: number;
  light: number;
  proximity: number;
  durationMs: number | null; // only for FLIP_UP
}

export interface SensorRecord {
  ts: number;
  acc_z: number;
  light: number;
  proximity: number; // 0 = far, 1 = near
}

export interface SessionMeta {
  participant: string;
  condition: string;
  repetition: number;
  date: string;
  durationMin: number;
  flipCount: number;
  totalFaceDownSec: number;
}

/**
 * Three-sensor fusion flip detector:
 *   face_down = (acc_z < threshold) AND (light < threshold OR proximity near)
 *               AND (X/Y stationary on surface)
 *   Must persist > 3s to count as a valid flip event.
 *   Vibrates on each confirmed flip for tactile feedback.
 */
export class FlipDetector {
  private dataLog: SensorRecord[] = [];
  private flipEvents: FlipEvent[] = [];
  private faceDownSince: number | null = null;
  private flipConfirmTimer: ReturnType<typeof setTimeout> | null = null;
  private recentAcc: AccelerometerData[] = [];
  private totalFaceDownMs = 0;
  private flipCount = 0;
  private lightAvailable = true;
  private proximityAvailable = true;

  setSensorAvailability(light: boolean, proximity: boolean): void {
    this.lightAvailable = light;
    this.proximityAvailable = proximity;
  }

  getSensorMode(): string {
    if (this.lightAvailable && this.proximityAvailable) return '加速度计 + 光线 + 距离';
    if (this.lightAvailable) return '加速度计 + 光线';
    if (this.proximityAvailable) return '加速度计 + 距离';
    return '仅加速度计';
  }

  private isStationary(): boolean {
    if (this.recentAcc.length < CONFIG.xYStability.windowSize) return false;
    const xs = this.recentAcc.map((a) => a.x);
    const ys = this.recentAcc.map((a) => a.y);
    const meanX = xs.reduce((s, v) => s + v, 0) / xs.length;
    const meanY = ys.reduce((s, v) => s + v, 0) / ys.length;
    const varX = xs.reduce((s, v) => s + (v - meanX) ** 2, 0) / xs.length;
    const varY = ys.reduce((s, v) => s + (v - meanY) ** 2, 0) / ys.length;
    return varX < CONFIG.xYStability.varianceThreshold &&
           varY < CONFIG.xYStability.varianceThreshold;
  }

  /** Feed a new fused sensor sample. Returns current face-down state. */
  feed(acc: AccelerometerData, light: number, proximityDistance: number): boolean {
    this.recentAcc.push(acc);
    if (this.recentAcc.length > CONFIG.xYStability.windowSize) this.recentAcc.shift();

    const proximityNear = isNear(proximityDistance);

    let sensorOk = true;
    if (this.lightAvailable && this.proximityAvailable) {
      sensorOk = (light < CONFIG.light.darkThreshold) || proximityNear;
    } else if (this.lightAvailable) {
      sensorOk = (light < CONFIG.light.darkThreshold);
    } else if (this.proximityAvailable) {
      sensorOk = proximityNear;
    }

    const faceDown = isFaceDown(acc.z) && sensorOk && this.isStationary();

    // Log raw data
    this.dataLog.push({
      ts: acc.timestamp,
      acc_z: parseFloat(acc.z.toFixed(4)),
      light: parseFloat(light.toFixed(1)),
      proximity: proximityNear ? 1 : 0,
    });

    // Flip state machine
    if (faceDown && this.faceDownSince === null) {
      this.faceDownSince = acc.timestamp;
      this.flipConfirmTimer = setTimeout(() => {
        // Confirmed: held face-down for > 3s
        this.flipCount++;
        this.flipEvents.push({
          type: "FLIP_DOWN",
          time: new Date().toISOString(),
          accZ: acc.z,
          light,
          proximity: proximityNear ? 1 : 0,
          durationMs: null,
        });
        Vibration.vibrate(100);
      }, CONFIG.flip.confirmDurationMs);

    } else if (!faceDown && this.faceDownSince !== null) {
      clearTimeout(this.flipConfirmTimer!);
      const duration = acc.timestamp - this.faceDownSince;
      if (duration >= CONFIG.flip.confirmDurationMs) {
        this.totalFaceDownMs += duration;
        this.flipEvents.push({
          type: "FLIP_UP",
          time: new Date().toISOString(),
          accZ: acc.z,
          light,
          proximity: proximityNear ? 1 : 0,
          durationMs: duration,
        });
      }
      this.faceDownSince = null;
    }

    return faceDown;
  }

  getDataLog(): SensorRecord[] { return this.dataLog; }
  getFlipEvents(): FlipEvent[] { return this.flipEvents; }
  getFlipCount(): number { return this.flipCount; }
  getTotalFaceDownMs(): number { return this.totalFaceDownMs; }

  getMeta(participant: string, condition: string, repetition: number): SessionMeta {
    return {
      participant,
      condition,
      repetition,
      date: new Date().toLocaleDateString("zh-CN"),
      durationMin: CONFIG.session.durationMinutes,
      flipCount: this.flipCount,
      totalFaceDownSec: parseFloat((this.totalFaceDownMs / 1000).toFixed(1)),
    };
  }

  reset(): void {
    this.dataLog = [];
    this.flipEvents = [];
    this.faceDownSince = null;
    this.totalFaceDownMs = 0;
    this.flipCount = 0;
    this.recentAcc = [];
    if (this.flipConfirmTimer) clearTimeout(this.flipConfirmTimer);
  }
}

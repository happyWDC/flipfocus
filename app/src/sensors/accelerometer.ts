import { Accelerometer } from "expo-sensors";
import { CONFIG } from "../config";

export interface AccelerometerData {
  x: number;
  y: number;
  z: number;
  timestamp: number;
}

type Listener = (data: AccelerometerData) => void;

export function startAccelerometer(listener: Listener): void {
  Accelerometer.setUpdateInterval(CONFIG.accelerometer.sampleRateMs);
  Accelerometer.addListener(({ x, y, z }) => {
    listener({ x, y, z, timestamp: Date.now() });
  });
}

export function stopAccelerometer(): void {
  Accelerometer.removeAllListeners();
}

export function isFaceDown(z: number): boolean {
  return z < CONFIG.accelerometer.zThreshold;
}

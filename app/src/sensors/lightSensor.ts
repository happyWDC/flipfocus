import { LightSensor } from "expo-sensors";
import { CONFIG } from "../config";

export interface LightSensorData {
  illuminance: number;
  timestamp: number;
}

type Listener = (data: LightSensorData) => void;

let hasLight = true;

export function startLightSensor(listener: Listener, onUnavailable?: () => void): void {
  hasLight = true;
  let fired = false;
  try {
    LightSensor.addListener(({ illuminance }) => {
      fired = true;
      listener({ illuminance, timestamp: Date.now() });
    });
    setTimeout(() => {
      if (!fired) {
        hasLight = false;
        onUnavailable?.();
      }
    }, 2000);
  } catch {
    hasLight = false;
    onUnavailable?.();
  }
}

export function stopLightSensor(): void {
  LightSensor.removeAllListeners();
}

export function isLightAvailable(): boolean {
  return hasLight;
}

export function isBlocked(illuminance: number): boolean {
  return illuminance < CONFIG.light.darkThreshold;
}

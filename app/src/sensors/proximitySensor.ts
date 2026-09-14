import { Proximity } from "expo-sensors";
import { CONFIG } from "../config";

export interface ProximityData {
  distance: number; // cm, < 2 means blocked
  near: boolean;
  timestamp: number;
}

type Listener = (data: ProximityData) => void;

let hasProximity = true;

export function startProximitySensor(listener: Listener, onUnavailable?: () => void): void {
  hasProximity = true;
  let fired = false;
  try {
    Proximity.addListener(({ distance }) => {
      fired = true;
      listener({
        distance,
        near: distance < CONFIG.proximity.nearThreshold,
        timestamp: Date.now(),
      });
    });
    setTimeout(() => {
      if (!fired) {
        hasProximity = false;
        onUnavailable?.();
      }
    }, 2000);
  } catch {
    hasProximity = false;
    onUnavailable?.();
  }
}

export function stopProximitySensor(): void {
  try {
    Proximity.removeAllListeners();
  } catch { /* noop */ }
}

export function isProximityAvailable(): boolean {
  return hasProximity;
}

export function isNear(distance: number): boolean {
  return distance < CONFIG.proximity.nearThreshold;
}

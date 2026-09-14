import React, { useEffect, useRef, useState, useCallback } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert, Vibration } from "react-native";
import { activateKeepAwakeAsync, deactivateKeepAwake } from "expo-keep-awake";
import { startAccelerometer, stopAccelerometer } from "../sensors/accelerometer";
import { startLightSensor, stopLightSensor, isLightAvailable } from "../sensors/lightSensor";
import { startProximitySensor, stopProximitySensor, isProximityAvailable } from "../sensors/proximitySensor";
import { FlipDetector } from "../sensors/flipDetector";
import { exportSession, shareFile } from "../storage/csvExport";
import { CONFIG, type Condition } from "../config";

const { durationMinutes, conditions } = CONFIG.session;

interface Props {
  subjectId: string;
  repetition: number;
  condition: Condition;
  onDone: () => void;
}

const C = {
  bg: "#0A0E1A",
  card: "#141927",
  accent: "#4F8EF7",
  accentGreen: "#2ECC71",
  accentRed: "#E74C3C",
  text: "#E8EAF0",
  muted: "#6B7280",
  border: "#1E2A3A",
};

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
};

export default function RecordScreen({ subjectId, repetition, condition, onDone }: Props) {
  const [elapsed, setElapsed] = useState(0);
  const [isFaceDown, setIsFaceDown] = useState(false);
  const [flipCount, setFlipCount] = useState(0);
  const [totalFaceDownMs, setTotalFaceDownMs] = useState(0);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [saved, setSaved] = useState(false);

  // Live sensor values for dashboard
  const [accZ, setAccZ] = useState(0);
  const [light, setLight] = useState(999);
  const [proximityNear, setProximityNear] = useState(false);
  const [sensorMode, setSensorMode] = useState('加速度计 + 光线 + 距离');

  // Internal refs (avoid re-render on every sensor tick)
  const detectorRef = useRef(new FlipDetector());
  const sessionTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const currentAccZ = useRef(0);
  const currentLight = useRef(999);
  const currentProximity = useRef(9);
  const dataPointCount = useRef(0);
  const lightOkRef = useRef(true);
  const proxOkRef = useRef(true);

  // ── Flip detection callback (called on every acc sample) ──
  const checkFaceDown = useCallback(() => {
    const fd = detectorRef.current.feed(
      { x: 0, y: 0, z: currentAccZ.current, timestamp: Date.now() },
      currentLight.current,
      currentProximity.current,
    );
    setIsFaceDown(fd);
    setFlipCount(detectorRef.current.getFlipCount());
    setTotalFaceDownMs(detectorRef.current.getTotalFaceDownMs());
    dataPointCount.current = detectorRef.current.getDataLog().length;
  }, []);

  // ── Update flip detector with current sensor availability ──
  const updateSensorAvailability = useCallback(() => {
    const lightOk = lightOkRef.current;
    const proxOk = proxOkRef.current;
    detectorRef.current.setSensorAvailability(lightOk, proxOk);
    setSensorMode(detectorRef.current.getSensorMode());
  }, []);

  // ── Start sensors ──
  const startSensors = useCallback(() => {
    lightOkRef.current = true;
    proxOkRef.current = true;

    startAccelerometer((acc) => {
      currentAccZ.current = acc.z;
      setAccZ(acc.z);
      checkFaceDown();
    });

    startLightSensor((data) => {
      currentLight.current = data.illuminance;
      setLight(data.illuminance);
    }, () => {
      lightOkRef.current = false;
      updateSensorAvailability();
    });

    startProximitySensor((data) => {
      currentProximity.current = data.distance;
      setProximityNear(data.near);
    }, () => {
      proxOkRef.current = false;
      updateSensorAvailability();
    });
  }, [checkFaceDown, updateSensorAvailability]);

  // ── Stop sensors ──
  const stopSensors = useCallback(() => {
    stopAccelerometer();
    stopLightSensor();
    stopProximitySensor();
  }, []);

  // ── Session timer ──
  useEffect(() => {
    activateKeepAwakeAsync();
    startSensors();

    sessionTimerRef.current = setInterval(() => {
      setElapsed((e) => {
        const next = e + 1;
        if (next >= durationMinutes * 60) {
          stopSensors();
          clearInterval(sessionTimerRef.current!);
          Vibration.vibrate([0, 200, 100, 200]); // end-of-session pattern
          setSessionComplete(true);
        }
        return next;
      });
    }, 1000);

    return () => {
      deactivateKeepAwake();
      stopSensors();
      if (sessionTimerRef.current) clearInterval(sessionTimerRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Export ──
  const handleExport = async () => {
    const detector = detectorRef.current;
    const meta = detector.getMeta(subjectId, condition, String(repetition));

    try {
      const { sensorPath } = await exportSession(
        detector.getDataLog(),
        detector.getFlipEvents(),
        meta,
      );
      await shareFile(sensorPath);
      setSaved(true);
    } catch {
      // Save succeeded but share failed
      setSaved(true);
    }
  };

  // ── Early stop ──
  const handleEarlyStop = () => {
    Alert.alert("提前结束？", "数据将被保留并导出", [
      { text: "继续实验", style: "cancel" },
      {
        text: "结束并导出",
        onPress: () => {
          stopSensors();
          clearInterval(sessionTimerRef.current!);
          setSessionComplete(true);
        },
      },
    ]);
  };

  const remaining = durationMinutes * 60 - elapsed;
  const progress = elapsed / (durationMinutes * 60);

  return (
    <View style={styles.container}>
      {/* ── Status badge ── */}
      <View style={[styles.statusBadge, isFaceDown ? styles.statusDown : styles.statusUp]}>
        <Text style={styles.statusText}>
          {isFaceDown ? "面朝下（专注中）" : "面朝上"}
        </Text>
      </View>

      {/* ── Countdown ── */}
      <Text style={styles.timer}>{formatTime(remaining)}</Text>
      <View style={styles.progressBg}>
        <View style={[styles.progressFill, { width: `${Math.min(progress * 100, 100)}%` }]} />
      </View>

      {/* ── Experiment info ── */}
      <View style={styles.infoRow}>
        <Text style={styles.infoText}>{subjectId}</Text>
        <Text style={styles.infoText}>{condition}</Text>
        <Text style={styles.infoText}>第{repetition}次</Text>
      </View>

      {/* ── Real-time sensor dashboard ── */}
      <View style={styles.sensorCard}>
        <Text style={styles.sensorTitle}>传感器实时值 · {sensorMode}</Text>
        <View style={styles.sensorRow}>
          <View style={styles.sensorItem}>
            <Text style={styles.sensorLabel}>加速度Z</Text>
            <Text style={[styles.sensorValue, accZ < CONFIG.accelerometer.zThreshold && styles.sensorTriggered]}>
              {accZ.toFixed(2)}g
            </Text>
          </View>
          <View style={styles.sensorItem}>
            <Text style={styles.sensorLabel}>光线</Text>
            <Text style={[styles.sensorValue, light < CONFIG.light.darkThreshold && styles.sensorTriggered]}>
              {light.toFixed(0)} lux
            </Text>
          </View>
          <View style={styles.sensorItem}>
            <Text style={styles.sensorLabel}>距离</Text>
            <Text style={[styles.sensorValue, proximityNear && styles.sensorTriggered]}>
              {proximityNear ? "近" : "远"}
            </Text>
          </View>
        </View>
      </View>

      {/* ── Session statistics ── */}
      <View style={styles.statsCard}>
        <View style={styles.statItem}>
          <Text style={styles.statNum}>{flipCount}</Text>
          <Text style={styles.statLabel}>翻转次数</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNum}>{formatTime(Math.floor(totalFaceDownMs / 1000))}</Text>
          <Text style={styles.statLabel}>面朝下时长</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNum}>{dataPointCount.current}</Text>
          <Text style={styles.statLabel}>数据点</Text>
        </View>
      </View>

      {/* ── Action buttons ── */}
      {sessionComplete ? (
        saved ? (
          <TouchableOpacity style={styles.backBtn} onPress={onDone}>
            <Text style={styles.backBtnText}>返回首页</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={styles.exportBtn} onPress={handleExport}>
            <Text style={styles.exportBtnText}>实验完成，导出数据</Text>
          </TouchableOpacity>
        )
      ) : (
        <TouchableOpacity style={styles.stopBtn} onPress={handleEarlyStop}>
          <Text style={styles.stopBtnText}>提前结束</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, backgroundColor: C.bg,
    paddingTop: 50, paddingHorizontal: 20,
  },
  statusBadge: {
    alignSelf: "center", paddingHorizontal: 20, paddingVertical: 10,
    borderRadius: 24, marginBottom: 16,
  },
  statusDown: { backgroundColor: "#1A2E1A", borderWidth: 1, borderColor: C.accentGreen },
  statusUp: { backgroundColor: "#2A1A1A", borderWidth: 1, borderColor: C.accentRed },
  statusText: { color: C.text, fontSize: 15, fontWeight: "700" },
  timer: {
    fontSize: 72, fontWeight: "900", color: C.text,
    textAlign: "center", fontVariant: ["tabular-nums"],
  },
  progressBg: {
    height: 4, backgroundColor: C.border, borderRadius: 2,
    marginVertical: 12, overflow: "hidden",
  },
  progressFill: { height: "100%", backgroundColor: C.accent, borderRadius: 2 },
  infoRow: {
    flexDirection: "row", justifyContent: "space-around", marginBottom: 12,
  },
  infoText: { color: C.muted, fontSize: 13 },
  sensorCard: {
    backgroundColor: C.card, borderRadius: 16,
    padding: 16, marginBottom: 10,
    borderWidth: 1, borderColor: C.border,
  },
  sensorTitle: {
    color: C.muted, fontSize: 11, letterSpacing: 1,
    textTransform: "uppercase", marginBottom: 12,
  },
  sensorRow: { flexDirection: "row", justifyContent: "space-around" },
  sensorItem: { alignItems: "center" },
  sensorLabel: { color: C.muted, fontSize: 11, marginBottom: 4 },
  sensorValue: { color: C.text, fontSize: 20, fontWeight: "700" },
  sensorTriggered: { color: C.accentGreen },
  statsCard: {
    flexDirection: "row", justifyContent: "space-around",
    backgroundColor: C.card, borderRadius: 16,
    padding: 16, marginBottom: 16,
    borderWidth: 1, borderColor: C.border,
  },
  statItem: { alignItems: "center" },
  statNum: { color: C.accent, fontSize: 24, fontWeight: "800" },
  statLabel: { color: C.muted, fontSize: 11, marginTop: 4 },
  exportBtn: {
    backgroundColor: C.accentGreen, borderRadius: 16,
    padding: 18, alignItems: "center",
  },
  exportBtnText: { color: "#fff", fontSize: 16, fontWeight: "800" },
  stopBtn: {
    borderWidth: 1, borderColor: C.border, borderRadius: 16,
    padding: 14, alignItems: "center",
  },
  stopBtnText: { color: C.muted, fontSize: 15 },
  backBtn: {
    borderWidth: 1, borderColor: C.border, borderRadius: 16,
    padding: 14, alignItems: "center",
  },
  backBtnText: { color: C.muted, fontSize: 15 },
});

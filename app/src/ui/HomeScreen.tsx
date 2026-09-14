import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from "react-native";
import { CONFIG, type Condition } from "../config";

const C = {
  bg: "#0A0E1A",
  card: "#141927",
  accent: "#4F8EF7",
  text: "#E8EAF0",
  muted: "#6B7280",
  border: "#1E2A3A",
};

interface Props {
  subjectId: string;
  repetition: number;
  condition: Condition;
  onSubjectChange: (id: string) => void;
  onRepetitionChange: (r: number) => void;
  onConditionChange: (c: Condition) => void;
  onStartRecording: () => void;
  onViewData: () => void;
}

export default function HomeScreen({
  subjectId, repetition, condition,
  onSubjectChange, onRepetitionChange, onConditionChange,
  onStartRecording, onViewData,
}: Props) {
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>FlipFocus</Text>
      <Text style={styles.subtitle}>注意力仪式研究采集工具</Text>

      {/* ── 被试编号 ── */}
      <View style={styles.card}>
        <Text style={styles.label}>被试编号</Text>
        <View style={styles.row}>
          {["P1", "P2", "P3", "P4"].map((p) => (
            <TouchableOpacity
              key={p}
              style={[styles.chip, subjectId === p && styles.chipActive]}
              onPress={() => onSubjectChange(p)}
            >
              <Text style={[styles.chipText, subjectId === p && styles.chipTextActive]}>{p}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* ── 实验条件 ── */}
      <View style={styles.card}>
        <Text style={styles.label}>实验条件</Text>
        {CONFIG.session.conditions.map((c) => (
          <TouchableOpacity
            key={c}
            style={[styles.conditionBtn, condition === c && styles.conditionBtnActive]}
            onPress={() => onConditionChange(c)}
          >
            <Text style={[styles.conditionText, condition === c && styles.conditionTextActive]}>
              {c}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* ── 重复次数 ── */}
      <View style={styles.card}>
        <Text style={styles.label}>重复次数</Text>
        <View style={styles.row}>
          {[1, 2, 3].map((r) => (
            <TouchableOpacity
              key={r}
              style={[styles.chip, repetition === r && styles.chipActive]}
              onPress={() => onRepetitionChange(r)}
            >
              <Text style={[styles.chipText, repetition === r && styles.chipTextActive]}>第{r}次</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* ── 开始 ── */}
      <TouchableOpacity style={styles.startBtn} onPress={onStartRecording}>
        <Text style={styles.startBtnText}>开始采集（25分钟）</Text>
      </TouchableOpacity>

      {/* ── 历史数据 ── */}
      <TouchableOpacity style={styles.dataBtn} onPress={onViewData}>
        <Text style={styles.dataBtnText}>查看历史数据</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.bg, paddingTop: 60, paddingHorizontal: 20 },
  title: { fontSize: 32, fontWeight: "800", color: C.accent, letterSpacing: 2, textAlign: "center" },
  subtitle: { fontSize: 13, color: C.muted, textAlign: "center", marginBottom: 28, marginTop: 4 },
  card: {
    backgroundColor: C.card, borderRadius: 16, padding: 16, marginBottom: 14,
    borderWidth: 1, borderColor: C.border,
  },
  label: { color: C.muted, fontSize: 12, fontWeight: "600", letterSpacing: 1, marginBottom: 10, textTransform: "uppercase" },
  row: { flexDirection: "row", gap: 8 },
  chip: {
    paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20,
    borderWidth: 1, borderColor: C.border, backgroundColor: C.bg,
  },
  chipActive: { backgroundColor: C.accent, borderColor: C.accent },
  chipText: { color: C.muted, fontSize: 14, fontWeight: "600" },
  chipTextActive: { color: "#fff" },
  conditionBtn: {
    paddingVertical: 10, paddingHorizontal: 14, borderRadius: 10,
    borderWidth: 1, borderColor: C.border, marginBottom: 6, backgroundColor: C.bg,
  },
  conditionBtnActive: { backgroundColor: C.accent, borderColor: C.accent },
  conditionText: { color: C.muted, fontSize: 14 },
  conditionTextActive: { color: "#fff", fontWeight: "700" },
  startBtn: { backgroundColor: C.accent, borderRadius: 16, padding: 18, alignItems: "center", marginTop: 8 },
  startBtnText: { color: "#fff", fontSize: 17, fontWeight: "800" },
  dataBtn: { padding: 14, borderRadius: 12, alignItems: "center", marginTop: 8, marginBottom: 40 },
  dataBtnText: { color: C.muted, fontSize: 14 },
});

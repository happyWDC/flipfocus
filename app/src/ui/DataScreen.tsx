import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Alert,
} from "react-native";
import {
  getAllRecordings,
  shareCSV,
  deleteRecording,
} from "../storage/csvExport";

interface Recording {
  name: string;
  path: string;
  size: number;
}

interface Props {
  onBack: () => void;
}

export default function DataScreen({ onBack }: Props) {
  const [recordings, setRecordings] = useState<Recording[]>([]);

  const load = async () => {
    const data = await getAllRecordings();
    setRecordings(data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = (r: Recording) => {
    Alert.alert("删除确认", `确定删除 ${r.name}？`, [
      { text: "取消", style: "cancel" },
      {
        text: "删除",
        style: "destructive",
        onPress: async () => {
          await deleteRecording(r.path);
          load();
        },
      },
    ]);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>历史数据</Text>
      <Text style={styles.subtitle}>{recordings.length} 条记录</Text>

      <FlatList
        data={recordings}
        keyExtractor={(item) => item.path}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={styles.rowLeft}>
              <Text style={styles.fileName} numberOfLines={1}>
                {item.name}
              </Text>
              <Text style={styles.fileSize}>{formatSize(item.size)}</Text>
            </View>
            <View style={styles.rowRight}>
              <TouchableOpacity
                style={styles.shareBtn}
                onPress={() => shareCSV(item.path)}
              >
                <Text style={styles.shareText}>分享</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.deleteBtn}
                onPress={() => handleDelete(item)}
              >
                <Text style={styles.deleteText}>删除</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        ListEmptyComponent={
          <Text style={styles.empty}>暂无数据</Text>
        }
      />

      <TouchableOpacity style={styles.backBtn} onPress={onBack}>
        <Text style={styles.backBtnText}>返回</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#1a1a2e", padding: 20 },
  title: { color: "#e94560", fontSize: 22, fontWeight: "bold", textAlign: "center", marginTop: 40 },
  subtitle: { color: "#888", fontSize: 14, textAlign: "center", marginBottom: 20 },
  row: {
    backgroundColor: "#16213e",
    borderRadius: 8,
    padding: 14,
    marginBottom: 8,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  rowLeft: { flex: 1, marginRight: 10 },
  fileName: { color: "#fff", fontSize: 13 },
  fileSize: { color: "#666", fontSize: 11, marginTop: 2 },
  rowRight: { flexDirection: "row", gap: 8 },
  shareBtn: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: "#4ecca3",
  },
  shareText: { color: "#1a1a2e", fontWeight: "bold", fontSize: 12 },
  deleteBtn: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#e94560",
  },
  deleteText: { color: "#e94560", fontSize: 12 },
  empty: { color: "#888", textAlign: "center", marginTop: 40 },
  backBtn: {
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 10,
    marginBottom: 20,
  },
  backBtnText: { color: "#888", fontSize: 16 },
});

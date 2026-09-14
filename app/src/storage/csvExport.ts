import * as FileSystem from "expo-file-system";
import * as Sharing from "expo-sharing";
import type { SensorRecord, FlipEvent, SessionMeta } from "../sensors/flipDetector";

const SENSOR_HEADER = "timestamp_ms,acc_z,light_lux,proximity";
const FLIP_HEADER = "type,time,acc_z,light,proximity,duration_ms";

export async function exportSession(
  dataLog: SensorRecord[],
  flipEvents: FlipEvent[],
  meta: SessionMeta
): Promise<{ prefix: string; sensorPath: string; flipPath: string; metaPath: string }> {
  const dir = `${FileSystem.documentDirectory}flip_data`;
  const dirInfo = await FileSystem.getInfoAsync(dir);
  if (!dirInfo.exists) {
    await FileSystem.makeDirectoryAsync(dir, { intermediates: true });
  }

  const prefix = `${meta.participant}_${meta.condition}_R${meta.repetition}_${Date.now()}`;

  // 1. Sensor CSV
  const csvRows = dataLog.map(
    (d) => `${d.ts},${d.acc_z},${d.light},${d.proximity}`
  );
  const sensorCSV = [SENSOR_HEADER, ...csvRows].join("\n");
  const sensorPath = `${dir}/${prefix}_sensors.csv`;
  await FileSystem.writeAsStringAsync(sensorPath, sensorCSV, {
    encoding: FileSystem.EncodingType.UTF8,
  });

  // 2. Flip events CSV
  const flipRows = flipEvents.map(
    (e) =>
      `${e.type},${e.time},${e.accZ.toFixed(4)},${e.light},${e.proximity},${e.durationMs ?? ""}`
  );
  const flipCSV = [FLIP_HEADER, ...flipRows].join("\n");
  const flipPath = `${dir}/${prefix}_flips.csv`;
  await FileSystem.writeAsStringAsync(flipPath, flipCSV, {
    encoding: FileSystem.EncodingType.UTF8,
  });

  // 3. Metadata JSON
  const metaPath = `${dir}/${prefix}_meta.json`;
  await FileSystem.writeAsStringAsync(metaPath, JSON.stringify(meta, null, 2), {
    encoding: FileSystem.EncodingType.UTF8,
  });

  return { prefix, sensorPath, flipPath, metaPath };
}

export async function shareFile(filePath: string): Promise<void> {
  const canShare = await Sharing.isAvailableAsync();
  if (canShare) {
    await Sharing.shareAsync(filePath, {
      mimeType: "text/csv",
      dialogTitle: "导出实验数据",
    });
  }
}

export async function getAllRecordings(): Promise<
  { name: string; path: string; size: number }[]
> {
  const dir = `${FileSystem.documentDirectory}flip_data`;
  const dirInfo = await FileSystem.getInfoAsync(dir);
  if (!dirInfo.exists) return [];

  const files = await FileSystem.readDirectoryAsync(dir);
  const results: { name: string; path: string; size: number }[] = [];
  for (const name of files) {
    const info = await FileSystem.getInfoAsync(`${dir}/${name}`);
    if (info.exists && !info.isDirectory) {
      results.push({ name, path: info.uri, size: info.size ?? 0 });
    }
  }
  results.sort((a, b) => b.name.localeCompare(a.name));
  return results;
}

export async function deleteRecording(path: string): Promise<void> {
  await FileSystem.deleteAsync(path, { idempotent: true });
}

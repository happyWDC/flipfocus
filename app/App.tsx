import React, { useState } from "react";
import { StatusBar } from "expo-status-bar";
import HomeScreen from "./src/ui/HomeScreen";
import RecordScreen from "./src/ui/RecordScreen";
import DataScreen from "./src/ui/DataScreen";
import type { Condition } from "./src/config";

type Screen = "home" | "record" | "data";

export default function App() {
  const [screen, setScreen] = useState<Screen>("home");
  const [subjectId, setSubjectId] = useState("P1");
  const [repetition, setRepetition] = useState(1);
  const [condition, setCondition] = useState<Condition>("A_主动翻转");

  if (screen === "record") {
    return (
      <>
        <StatusBar style="light" />
        <RecordScreen
          subjectId={subjectId}
          repetition={repetition}
          condition={condition}
          onDone={() => setScreen("home")}
        />
      </>
    );
  }

  if (screen === "data") {
    return (
      <>
        <StatusBar style="light" />
        <DataScreen onBack={() => setScreen("home")} />
      </>
    );
  }

  return (
    <>
      <StatusBar style="light" />
      <HomeScreen
        subjectId={subjectId}
        repetition={repetition}
        condition={condition}
        onSubjectChange={setSubjectId}
        onRepetitionChange={setRepetition}
        onConditionChange={setCondition}
        onStartRecording={() => setScreen("record")}
        onViewData={() => setScreen("data")}
      />
    </>
  );
}

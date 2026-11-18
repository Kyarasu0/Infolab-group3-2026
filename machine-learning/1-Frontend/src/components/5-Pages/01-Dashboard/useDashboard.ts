import { useCallback, useEffect, useState } from "react";

import {
  changeMode, fetchArchitecture, fetchCurrentJob, fetchMode, fetchResult,
  fetchScenarios, startComparison, startTraining,
} from "../../../functions/api-client";
import type {
  Architecture, JobStatus, Mode, ScenarioResult, ScenarioSummary,
} from "../../../functions/api-types";

const POLLING_INTERVAL_MS = 1000;
const IDLE_JOB: JobStatus = { state: "idle", autoencoder_loss: [] };

export function useDashboard() {
  const [mode, setMode] = useState<Mode>("train");
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [job, setJob] = useState<JobStatus>(IDLE_JOB);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [architecture, setArchitecture] = useState<Architecture | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // 1. APIを呼び、失敗したら画面にエラーを出す
  const run = useCallback(async (action: () => Promise<unknown>) => {
    try {
      setErrorMessage(null);
      await action();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : String(error));
    }
  }, []);

  // 2. 最初に、モードとシナリオ一覧を読む
  const reloadScenarios = useCallback(() => run(async () => setScenarios(await fetchScenarios())), [run]);
  useEffect(() => {
    run(async () => setMode((await fetchMode()).mode));
    reloadScenarios();
  }, [run, reloadScenarios]);

  // 3. 学習中は、進捗を1秒ごとに取得する。終わったら一覧を更新する
  useEffect(() => {
    if (job.state !== "running") return;
    const timer = setInterval(async () => {
      const latest = await fetchCurrentJob().catch(() => null);
      if (!latest) return;
      setJob(latest);
      if (latest.state !== "running") reloadScenarios();
    }, POLLING_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [job.state, reloadScenarios]);

  // 4. 選んだシナリオの結果と構成を読む(未学習なら空にする)
  useEffect(() => {
    setResult(null);
    setArchitecture(null);
    if (!selectedName || !scenarios.find((s) => s.name === selectedName)?.trained) return;
    run(async () => {
      setResult(await fetchResult(selectedName));
      setArchitecture(await fetchArchitecture(selectedName));
    });
  }, [selectedName, scenarios, run]);

  const startJob = (start: () => Promise<unknown>) =>
    run(async () => {
      await start();
      setJob(await fetchCurrentJob());
    });

  return {
    mode, scenarios, job, selectedName, result, architecture, errorMessage,
    isBusy: job.state === "running",
    setErrorMessage,
    refreshJob: async () => setJob(await fetchCurrentJob()),
    select: setSelectedName,
    switchMode: (nextMode: Mode) => run(async () => setMode((await changeMode(nextMode)).mode)),
    train: (name: string) => startJob(() => startTraining(name)),
    compare: () => startJob(() => startComparison()),
  };
}

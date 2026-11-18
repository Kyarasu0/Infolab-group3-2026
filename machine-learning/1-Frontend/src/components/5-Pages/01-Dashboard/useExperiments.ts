import { useCallback, useEffect, useState } from "react";

import {
  fetchEvaluationPlans, fetchParameterDescriptions, fetchParameters, fetchRecord, fetchRecords, runExperiment,
} from "@/functions/api-client";
import type {
  EvaluationPlan, ExperimentRecord, JobStatus, ParameterDescriptions, ParameterSet, RecordSummary,
} from "@/functions/api-types";

type ParameterTexts = Record<string, Record<string, string>>;

// 入力欄の文字を、元の値の型(数値か文字)に戻して、上書き用のパラメータにする
function toParameterSet(texts: ParameterTexts, defaults: ParameterSet): ParameterSet {
  const result: ParameterSet = {};
  for (const [model, values] of Object.entries(texts)) {
    result[model] = {};
    for (const [key, text] of Object.entries(values)) {
      const isNumber = typeof defaults[model][key] === "number";
      if (isNumber && (text.trim() === "" || Number.isNaN(Number(text)))) {
        throw new Error(`数値で入力してください: ${model}.${key}`);
      }
      // 文字の欄では「null」と書くと、値なし(null)になる
      result[model][key] = isNumber ? Number(text) : text.trim() === "null" ? null : text;
    }
  }
  return result;
}

export function useExperiments(
  scenarioNames: string[], job: JobStatus, refreshJob: () => Promise<void>,
  onError: (message: string | null) => void,
) {
  const [plans, setPlans] = useState<EvaluationPlan[]>([]);
  const [descriptions, setDescriptions] = useState<ParameterDescriptions>({});
  const [scenarioName, setScenarioName] = useState("");
  const [planName, setPlanName] = useState("");
  const [defaults, setDefaults] = useState<ParameterSet>({});
  const [parameterTexts, setParameterTexts] = useState<ParameterTexts>({});
  const [note, setNote] = useState("");
  const [records, setRecords] = useState<RecordSummary[]>([]);
  const [existingRecord, setExistingRecord] = useState<RecordSummary | null>(null);
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null);
  const [recordDetail, setRecordDetail] = useState<ExperimentRecord | null>(null);

  // 1. APIを呼び、失敗したら画面にエラーを出す
  const run = useCallback(async (action: () => Promise<unknown>) => {
    try {
      onError(null);
      await action();
    } catch (error) {
      onError(error instanceof Error ? error.message : String(error));
    }
  }, [onError]);

  const reloadRecords = useCallback(() => run(async () => setRecords(await fetchRecords())), [run]);

  // 2. 最初に、評価計画・パラメータの説明・記録を読む。選択の初期値は先頭にする
  useEffect(() => {
    run(async () => {
      const loadedPlans = await fetchEvaluationPlans();
      setPlans(loadedPlans);
      setPlanName((current) => current || loadedPlans[0]?.name || "");
      setDescriptions(await fetchParameterDescriptions());
    });
    reloadRecords();
  }, [run, reloadRecords]);
  useEffect(() => setScenarioName((current) => current || scenarioNames[0] || ""), [scenarioNames]);

  // 3. シナリオを選んだら、そのパラメータを読んで、入力欄に入れる
  useEffect(() => {
    if (!scenarioName) return;
    run(async () => {
      const loaded = await fetchParameters(scenarioName);
      setDefaults(loaded);
      setParameterTexts(Object.fromEntries(Object.entries(loaded).map(([model, values]) => [
        model, Object.fromEntries(Object.entries(values).map(([key, value]) => [key, String(value)])),
      ])));
    });
  }, [scenarioName, run]);

  // 4. 実験が終わったら、記録を読み直す
  useEffect(() => {
    if (job.kind === "experiment" && job.state === "finished") reloadRecords();
  }, [job.kind, job.state, reloadRecords]);

  // 5. 記録を選んだら、詳細を読む
  useEffect(() => {
    setRecordDetail(null);
    if (selectedRecordId) run(async () => setRecordDetail(await fetchRecord(selectedRecordId)));
  }, [selectedRecordId, run]);

  // 6. 実験を実行する。実行済みなら、実行せず通知を出す(force なら、もう一度実行する)
  const startRun = (force: boolean) => run(async () => {
    const response = await runExperiment({
      scenario: scenarioName, evaluation_plan: planName, note, force,
      parameters: toParameterSet(parameterTexts, defaults),
    });
    if (response.status === "exists") {
      setExistingRecord(response.record);
      return;
    }
    setExistingRecord(null);
    await refreshJob();
  });

  return {
    plans, descriptions, scenarioName, planName, parameterTexts, note, records, existingRecord,
    selectedRecordId, recordDetail,
    setScenarioName, setPlanName, setNote, setSelectedRecordId,
    changeParameter: (model: string, key: string, text: string) =>
      setParameterTexts((current) => ({ ...current, [model]: { ...current[model], [key]: text } })),
    runExperiment: () => startRun(false),
    rerunExperiment: () => startRun(true),
    showExistingRecord: () => {
      setSelectedRecordId(existingRecord?.id ?? null);
      setExistingRecord(null);
    },
    closeNotice: () => setExistingRecord(null),
  };
}

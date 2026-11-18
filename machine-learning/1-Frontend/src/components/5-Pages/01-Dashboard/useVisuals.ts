import { useEffect, useState } from "react";

import { fetchDataSummary, fetchErrorDistribution, fetchScatter } from "@/functions/api-client";
import type { DataSummary, ErrorDistribution, JobStatus, ScatterData, ScenarioSummary } from "@/functions/api-types";

// データがあるときだけ見られるグラフの値。取れなかったときは、その理由(メッセージ)を持つ
export interface Visual<T> { data: T | null; message: string | null }
const EMPTY: Visual<never> = { data: null, message: null };

async function loadVisual<T>(load: () => Promise<T>): Promise<Visual<T>> {
  try {
    return { data: await load(), message: null };
  } catch (error) {
    return { data: null, message: error instanceof Error ? error.message : String(error) };
  }
}

export function useVisuals(selectedName: string | null, scenarios: ScenarioSummary[], job: JobStatus) {
  const [scatter, setScatter] = useState<Visual<ScatterData>>(EMPTY);
  const [errorDistribution, setErrorDistribution] = useState<Visual<ErrorDistribution>>(EMPTY);
  const [dataSummary, setDataSummary] = useState<Visual<DataSummary>>(EMPTY);

  // 1. 選んだシナリオが学習済みなら、散布図と誤差の分布を読む(学習し直したら、一覧が変わるので読み直す)
  const isTrained = scenarios.some((scenario) => scenario.name === selectedName && scenario.trained);
  useEffect(() => {
    setScatter(EMPTY);
    setErrorDistribution(EMPTY);
    if (!selectedName || !isTrained) return;
    loadVisual(() => fetchScatter(selectedName)).then(setScatter);
    loadVisual(() => fetchErrorDistribution(selectedName)).then(setErrorDistribution);
  }, [selectedName, isTrained, scenarios]);

  // 2. データの概要は、最初と、処理が終わったときに読む
  useEffect(() => {
    if (job.state !== "running") loadVisual(fetchDataSummary).then(setDataSummary);
  }, [job.state]);

  return { scatter, errorDistribution, dataSummary };
}

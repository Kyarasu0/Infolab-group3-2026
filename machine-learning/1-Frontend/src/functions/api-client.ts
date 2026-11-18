// ==========================================
// functions/api-client.ts
// バックエンド(2-Backend)のAPI呼び出し(描画に関係しない)
// APIのメソッドとパスは、3-Shared/api-list.json から、APIの名前で引く
// (フロントには /api/... を直接書かない)
// ==========================================

import apiList from "../../../3-Shared/api-list.json";
import type {
  Architecture, EvaluationPlan, ExperimentRecord, JobStatus, Mode, ParameterSet,
  RecordSummary, RunExperimentRequest, RunExperimentResponse, ScenarioResult, ScenarioSummary,
} from "./api-types";

// APIの名前から、一覧の項目(メソッドとパス)を探す(なければ例外)
function findApi(apiName: string) {
  const api = apiList.apis.find((entry) => entry.name === apiName);
  if (!api) throw new Error(`APIが一覧にありません: ${apiName}`);
  return api;
}

// パスの {name} などを値で置き換える
export function apiUrl(apiName: string, pathParams: Record<string, string> = {}): string {
  return findApi(apiName).path.replace(/\{(\w+)\}/g, (_, key: string) => {
    if (!(key in pathParams)) throw new Error(`パスの値がありません: ${key}`);
    return encodeURIComponent(pathParams[key]);
  });
}

// APIを名前で呼ぶ(例: callApi("get_scenario_result", { name }))。失敗したら、バックエンドが返した理由を例外にする
export async function callApi<T>(
  apiName: string, pathParams: Record<string, string> = {}, body?: unknown,
): Promise<T> {
  // 1. 一覧のメソッドとパスで、リクエストを送る(本文があればJSONで送る)
  const response = await fetch(apiUrl(apiName, pathParams), {
    method: findApi(apiName).method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  // 2. 失敗したら、バックエンドが返した理由を、エラーにして投げる
  if (!response.ok) {
    const detail = (await response.json().catch(() => ({}))).detail;
    throw new Error(typeof detail === "string" ? detail : `通信に失敗しました(${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const fetchMode = () => callApi<{ mode: Mode }>("get_mode");
export const changeMode = (mode: Mode) => callApi<{ mode: Mode }>("put_mode", {}, { mode });
export const fetchScenarios = () => callApi<ScenarioSummary[]>("get_scenarios");
export const fetchResult = (name: string) => callApi<ScenarioResult>("get_scenario_result", { name });
export const fetchArchitecture = (name: string) => callApi<Architecture>("get_scenario_architecture", { name });
export const fetchParameters = (name: string) => callApi<ParameterSet>("get_scenario_parameters", { name });
export const startTraining = (scenario: string) => callApi("post_train", {}, { scenario });
export const startComparison = () => callApi("post_compare");
export const fetchCurrentJob = () => callApi<JobStatus>("get_current_job");
export const fetchEvaluationPlans = () => callApi<EvaluationPlan[]>("get_evaluation_plans");
export const runExperiment = (request: RunExperimentRequest) =>
  callApi<RunExperimentResponse>("post_experiment_run", {}, request);
export const fetchRecords = () => callApi<RecordSummary[]>("get_experiment_records");
export const fetchRecord = (recordId: string) =>
  callApi<ExperimentRecord>("get_experiment_record", { record_id: recordId });

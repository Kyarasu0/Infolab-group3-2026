import type {
  Architecture, JobStatus, Mode, ScenarioResult, ScenarioSummary,
} from "./api-types";

const API_BASE_URL = "/api";

async function requestJson<T>(path: string, method = "GET", body?: unknown): Promise<T> {
  // 1. バックエンドにリクエストを送る
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  // 2. 失敗したら、バックエンドが返した理由を、エラーにして投げる
  if (!response.ok) {
    const detail = (await response.json().catch(() => ({}))).detail;
    throw new Error(detail ?? `通信に失敗しました(${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const fetchMode = () => requestJson<{ mode: Mode }>("/mode");
export const changeMode = (mode: Mode) => requestJson<{ mode: Mode }>("/mode", "PUT", { mode });
export const fetchScenarios = () => requestJson<ScenarioSummary[]>("/scenarios");
export const fetchResult = (name: string) => requestJson<ScenarioResult>(`/scenarios/${name}/result`);
export const fetchArchitecture = (name: string) =>
  requestJson<Architecture>(`/scenarios/${name}/architecture`);
export const startTraining = (scenario: string) => requestJson("/train", "POST", { scenario });
export const startComparison = () => requestJson("/compare", "POST");
export const fetchCurrentJob = () => requestJson<JobStatus>("/jobs/current");

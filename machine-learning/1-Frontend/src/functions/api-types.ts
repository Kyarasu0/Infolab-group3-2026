// バックエンドAPIの入出力の型
export type Mode = "train" | "predict";

export interface Metrics {
  accuracy: number;
  macro_f1: number;
  anomaly_detection_rate: number;
  normal_false_alarm_rate: number;
  cluster_silhouette: number | null;
}

export interface ScenarioSummary {
  name: string;
  description: string;
  trained: boolean;
  metrics: Metrics | null;
}

export interface JobStatus {
  state: "idle" | "running" | "finished" | "failed";
  kind?: string;
  scenario?: string;
  epoch?: number;
  autoencoder_loss: number[];
  error?: string;
}

export interface LayerDescription {
  layer_number: number;
  part: string;
  type: string;
  parameter_count: number;
  in_features?: number;
  out_features?: number;
  weight?: { shape: number[]; mean: number; std: number; min: number; max: number };
}

export interface Architecture {
  scenario: string;
  input_dim: number;
  autoencoder?: {
    input_dim: number;
    latent_dim: number;
    total_parameters: number;
    layers: LayerDescription[];
  };
  svm?: { total_support_vectors: number; support_vectors_per_class: Record<string, number> };
  clustering: Record<string, { method: string; cluster_count: number }>;
}

export interface ScenarioResult {
  history: { autoencoder_loss: number[] };
  metrics: Metrics;
}

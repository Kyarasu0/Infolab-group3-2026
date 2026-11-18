import type { MetricSummary } from "@/functions/api-types";

// 「平均 ± 標準偏差」の文字にする(値が無ければ「-」)
export function formatMeanStd(summary: MetricSummary, metricName: string): string {
  const value = summary[metricName];
  return value ? `${value.mean.toFixed(3)} ± ${value.std.toFixed(3)}` : "-";
}

export const formatValue = (value: number | null | undefined) =>
  value === null || value === undefined ? "-" : value.toFixed(3);

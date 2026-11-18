import type { RecordSummary } from "@/functions/api-types";
import { BarChart } from "../../2-Molecules/03-BarChart/BarChart";
import { Panel } from "../../1-Atoms/03-Panel/Panel";

interface CompareChartProps {
  records: RecordSummary[];
  planName: string;
}

const SERIES = [
  { name: "正解率", color: "var(--chart-1)" },
  { name: "F1", color: "var(--chart-2)" },
];

// 選んだ評価計画の、シナリオごとの最新の記録を、正解率とF1の平均 ± 標準偏差で並べる
export function CompareChart({ records, planName }: CompareChartProps) {
  // 1. 記録は新しい順なので、シナリオごとに最初に見つかったものが最新
  const latestByScenario = new Map<string, RecordSummary>();
  for (const record of records) {
    if (record.evaluation_plan === planName && !latestByScenario.has(record.scenario)) {
      latestByScenario.set(record.scenario, record);
    }
  }

  // 2. 棒グラフ用の形にする(ラベルは、先頭の番号を除いて短くする)
  const groups = [...latestByScenario.entries()].map(([scenario, record]) => ({
    label: scenario.replace(/^\d+-/, ""),
    bars: ["accuracy", "macro_f1"].map((name) => {
      const value = record.summary[name];
      return value ? { value: value.mean, error: value.std } : null;
    }),
  }));

  return (
    <Panel>
      <BarChart title="シナリオ比較" subtitle={`評価計画: ${planName || "-"}(棒の線は標準偏差)`} series={SERIES} groups={groups} />
    </Panel>
  );
}

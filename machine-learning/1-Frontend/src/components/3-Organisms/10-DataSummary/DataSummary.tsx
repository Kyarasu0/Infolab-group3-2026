import type { DataSummary as DataSummaryData } from "@/functions/api-types";
import { groupColor, groupLabel } from "@/functions/group-style";
import { Panel } from "../../1-Atoms/03-Panel/Panel";
import { LineChart } from "../../2-Molecules/02-LineChart/LineChart";
import styles from "./DataSummary.module.css";

interface DataSummaryProps {
  summary: DataSummaryData | null;
  message: string | null;   // 表示できない理由(データが無いなど)
}

export function DataSummary({ summary, message }: DataSummaryProps) {
  if (!summary) {
    return <Panel><h2>データの概要</h2><p className={styles.muted}>{message ?? "データがありません"}</p></Panel>;
  }
  const groups = Object.keys(summary.features);
  return (
    <Panel>
      <h2>データの概要</h2>
      <p>
        特徴量 {summary.feature_count}個 / 通常 {summary.normal_count}件 / ラベル付き {summary.labeled_count}件
        ({Object.entries(summary.counts).filter(([group]) => group !== "normal")
          .map(([group, count]) => `${groupLabel(group)} ${count}件`).join(", ")})
      </p>
      <LineChart
        title="特徴量ごとの平均(状態別)" subtitle="横軸は特徴量の番号。状態で平均が離れている特徴量が、判定の手がかりになる"
        xLabel="特徴量 "
        series={groups.map((group, index) => ({
          name: groupLabel(group), color: groupColor(group, index), values: summary.features[group].mean,
        }))}
      />
    </Panel>
  );
}

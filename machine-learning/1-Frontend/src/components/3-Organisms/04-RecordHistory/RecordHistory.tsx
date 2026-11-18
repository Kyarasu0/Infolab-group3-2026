import metrics from "../../../../../3-Shared/concept/metrics.json";
import type { ExperimentRecord, RecordSummary } from "../../../functions/api-types";
import { formatMeanStd, formatValue } from "../../../functions/format-metrics";
import styles from "./RecordHistory.module.css";

interface RecordHistoryProps {
  records: RecordSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  detail: ExperimentRecord | null;
}

export function RecordHistory({ records, selectedId, onSelect, detail }: RecordHistoryProps) {
  return (
    <section className={styles.history}>
      <h2 className={styles.title}>実験の記録(平均 ± 標準偏差)</h2>
      {records.length === 0 ? <p className={styles.empty}>まだ記録がありません</p> : (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>日時</th><th>シナリオ</th><th>評価計画</th>
              {metrics.map((metric) => <th key={metric.name}>{metric.label}</th>)}
              <th>メモ</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id} className={record.id === selectedId ? styles.selectedRow : styles.row}
                onClick={() => onSelect(record.id)}>
                <td>{record.created_at.replace("T", " ")}</td>
                <td>{record.scenario}</td>
                <td>{record.evaluation_plan}</td>
                {metrics.map((metric) => <td key={metric.name}>{formatMeanStd(record.summary, metric.name)}</td>)}
                <td>{record.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {detail && (
        <div className={styles.detail}>
          <h3 className={styles.subtitle}>選んだ記録の詳細(学習 {detail.seconds}秒 / commit {detail.git_commit ?? "-"})</h3>
          <table className={styles.table}>
            <thead>
              <tr><th>fold</th>{metrics.map((metric) => <th key={metric.name}>{metric.label}</th>)}</tr>
            </thead>
            <tbody>
              {detail.folds.map((fold) => (
                <tr key={fold.fold}>
                  <td>{fold.fold}</td>
                  {metrics.map((metric) => <td key={metric.name}>{formatValue(fold.metrics[metric.name])}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
          <pre className={styles.parameters}>{JSON.stringify(detail.parameters, null, 2)}</pre>
        </div>
      )}
    </section>
  );
}

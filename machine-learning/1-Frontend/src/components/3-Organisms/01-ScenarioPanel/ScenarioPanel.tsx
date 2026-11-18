import type { Metrics, Mode, ScenarioSummary } from "../../../functions/api-types";
import { Button } from "../../1-Atoms/01-Button/Button";
import { StatusBadge } from "../../1-Atoms/02-StatusBadge/StatusBadge";
import styles from "./ScenarioPanel.module.css";

interface ScenarioPanelProps {
  scenarios: ScenarioSummary[];
  mode: Mode;
  isBusy: boolean;
  selectedName: string | null;
  onSelect: (name: string) => void;
  onTrain: (name: string) => void;
  onCompare: () => void;
}

const formatRate = (value: number | null) => (value === null ? "-" : value.toFixed(3));

function MetricCells({ metrics }: { metrics: Metrics | null }) {
  return (
    <>
      <td>{metrics ? formatRate(metrics.accuracy) : "-"}</td>
      <td>{metrics ? formatRate(metrics.macro_f1) : "-"}</td>
      <td>{metrics ? formatRate(metrics.anomaly_detection_rate) : "-"}</td>
      <td>{metrics ? formatRate(metrics.normal_false_alarm_rate) : "-"}</td>
      <td>{metrics ? formatRate(metrics.cluster_silhouette) : "-"}</td>
    </>
  );
}

export function ScenarioPanel(props: ScenarioPanelProps) {
  const canTrain = props.mode === "train" && !props.isBusy;
  return (
    <section className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>シナリオ比較</h2>
        <Button disabled={!canTrain} onClick={props.onCompare}>全シナリオを比較</Button>
      </div>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>シナリオ</th><th>状態</th><th>正解率</th><th>F1</th>
            <th>乖離検出率</th><th>通常の誤検出率</th><th>サブタイプ分離</th><th></th>
          </tr>
        </thead>
        <tbody>
          {props.scenarios.map((scenario) => (
            <tr
              key={scenario.name}
              className={scenario.name === props.selectedName ? styles.selectedRow : styles.row}
              onClick={() => props.onSelect(scenario.name)}
              title={scenario.description}
            >
              <td>{scenario.name}</td>
              <td><StatusBadge text={scenario.trained ? "学習済み" : "未学習"} tone={scenario.trained ? "success" : "neutral"} /></td>
              <MetricCells metrics={scenario.metrics} />
              <td>
                <Button disabled={!canTrain} onClick={(event) => { event.stopPropagation(); props.onTrain(scenario.name); }}>
                  学習
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

import metrics from "@shared/concept/metrics.json";
import type { Mode, ScenarioSummary } from "@/functions/api-types";
import { formatValue } from "@/functions/format-metrics";
import { Button } from "../../1-Atoms/01-Button/Button";
import { Panel, PanelHead } from "../../1-Atoms/03-Panel/Panel";
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

export function ScenarioPanel(props: ScenarioPanelProps) {
  const canTrain = props.mode === "train" && !props.isBusy;
  return (
    <Panel>
      <PanelHead>
        <h2>シナリオ</h2>
        <Button disabled={!canTrain} onClick={props.onCompare}>全シナリオを比較</Button>
      </PanelHead>
      <p className={styles.note}>
        行を選ぶと、学習曲線とモデルの構成を表示します。「学習」は、データの7割で学習し、残り3割で評価して、予測用モデルを保存します。
      </p>
      <table>
        <thead>
          <tr>
            <th>シナリオ</th><th>状態</th>
            {metrics.map((metric) => <th key={metric.name}>{metric.label}</th>)}
            <th></th>
          </tr>
        </thead>
        <tbody>
          {props.scenarios.map((scenario) => (
            <tr key={scenario.name} title={scenario.description}
              className={scenario.name === props.selectedName ? styles.selectedRow : styles.row}
              onClick={() => props.onSelect(scenario.name)}>
              <td>{scenario.name}<div className={styles.description}>{scenario.description}</div></td>
              <td><StatusBadge text={scenario.trained ? "学習済み" : "未学習"} tone={scenario.trained ? "success" : "neutral"} /></td>
              {metrics.map((metric) => (
                <td key={metric.name}>{formatValue(scenario.metrics?.[metric.name as keyof typeof scenario.metrics])}</td>
              ))}
              <td>
                <Button disabled={!canTrain} onClick={(event) => { event.stopPropagation(); props.onTrain(scenario.name); }}>学習</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}

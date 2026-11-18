import type { ScatterData } from "@/functions/api-types";
import { Panel } from "../../1-Atoms/03-Panel/Panel";
import { ScatterChart } from "../../2-Molecules/06-ScatterChart/ScatterChart";
import styles from "./ScatterPanel.module.css";

interface ScatterPanelProps {
  scenarioName: string | null;
  scatter: ScatterData | null;
  message: string | null;   // 表示できない理由(未学習・データ無しなど)
}

const percent = (ratio: number | undefined) => (ratio === undefined ? "-" : `${(ratio * 100).toFixed(0)}%`);

export function ScatterPanel({ scenarioName, scatter, message }: ScatterPanelProps) {
  if (!scatter) {
    return <Panel><h2>散布図</h2><p className={styles.muted}>{message ?? "学習済みのシナリオを選ぶと、表示します"}</p></Panel>;
  }
  const [first, second] = scatter.explained_variance_ratio;
  return (
    <Panel>
      <ScatterChart
        title={`散布図: ${scenarioName}`}
        subtitle={`入力: ${scatter.input} / 評価用データ ${scatter.shown_points}点`}
        points={scatter.points}
        xLabel={`第1主成分(寄与率 ${percent(first)})`}
        yLabel={`第2主成分(${percent(second)})`}
      />
      <p className={styles.muted}>
        分類器に入る特徴量(上の「入力」)を、主成分分析で2次元にした図。色は状態、形はサブタイプ(○ □ △ ◇)。
        状態の色が分かれて固まっていれば、分類しやすい特徴量といえる。
      </p>
    </Panel>
  );
}

import type { ErrorDistribution } from "@/functions/api-types";
import { groupColor, groupLabel } from "@/functions/group-style";
import { Panel } from "../../1-Atoms/03-Panel/Panel";
import { Histogram } from "../../2-Molecules/07-Histogram/Histogram";
import styles from "./ErrorDistributionPanel.module.css";

interface ErrorDistributionPanelProps {
  scenarioName: string | null;
  distribution: ErrorDistribution | null;
  message: string | null;   // 表示できない理由(未学習・AEを使わないシナリオなど)
}

export function ErrorDistributionPanel({ scenarioName, distribution, message }: ErrorDistributionPanelProps) {
  if (!distribution) {
    return <Panel><h2>誤差の分布</h2><p className={styles.muted}>{message ?? "学習済みのシナリオを選ぶと、表示します"}</p></Panel>;
  }
  const groups = Object.keys(distribution.ratios);
  return (
    <Panel>
      <Histogram
        title={`再構成誤差の分布: ${scenarioName}`}
        subtitle="評価用データ(各グループの割合)"
        edges={distribution.bin_edges}
        threshold={distribution.threshold}
        xLabel="再構成誤差(標準化したスケール。最後の区間は、それ以上を含む)"
        series={groups.map((group, index) => ({
          name: groupLabel(group), color: groupColor(group, index), ratios: distribution.ratios[group],
        }))}
      />
      <p className={styles.muted}>
        通常時のデータは小さい誤差に、ストレス・疲労は大きい誤差に寄るのが理想。閾値(点線)より右が「乖離あり」と判定され、
        重なりが大きいほど、乖離の検出が難しい。
      </p>
    </Panel>
  );
}

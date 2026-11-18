import type { JobStatus } from "@/functions/api-types";
import { Panel } from "../../1-Atoms/03-Panel/Panel";
import { StatusBadge } from "../../1-Atoms/02-StatusBadge/StatusBadge";
import { RadarIndicator } from "../../2-Molecules/05-RadarIndicator/RadarIndicator";
import styles from "./RunStatus.module.css";

const KIND_LABELS: Record<string, string> = { train: "学習", compare: "シナリオ比較", experiment: "実験" };

// 実行中・直近の処理の状況(まだ何も実行していなければ、出さない)
export function RunStatus({ job }: { job: JobStatus }) {
  if (job.state === "idle") return null;
  const kind = KIND_LABELS[job.kind ?? ""] ?? job.kind;
  return (
    <Panel className={styles.status}>
      <RadarIndicator active={job.state === "running"} />
      <div>
        {job.state === "running" && <p>{kind}を実行中: {job.scenario}(エポック {job.epoch})</p>}
        {job.state === "finished" && <p><StatusBadge text="完了" tone="success" /> {kind}: {job.scenario}</p>}
        {job.state === "failed" && <p><StatusBadge text="失敗" tone="danger" /> {kind}: {job.error}</p>}
      </div>
    </Panel>
  );
}

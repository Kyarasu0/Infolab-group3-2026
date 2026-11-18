import type { RecordSummary } from "@/functions/api-types";
import { formatMeanStd } from "@/functions/format-metrics";
import { Button } from "../../1-Atoms/01-Button/Button";
import styles from "./ExistingRecordNotice.module.css";

interface ExistingRecordNoticeProps {
  record: RecordSummary;
  onShowRecord: () => void;
  onRerun: () => void;
  onClose: () => void;
}

export function ExistingRecordNotice({ record, onShowRecord, onRerun, onClose }: ExistingRecordNoticeProps) {
  return (
    <section className={styles.notice}>
      <p>同じ条件の記録があります({record.created_at.replace("T", " ")} / 正解率 {formatMeanStd(record.summary, "accuracy")})。</p>
      <div className={styles.actions}>
        <Button primary onClick={onShowRecord}>過去の結果を表示する</Button>
        <Button onClick={onRerun}>もう一度実行する</Button>
        <Button onClick={onClose}>閉じる</Button>
      </div>
    </section>
  );
}

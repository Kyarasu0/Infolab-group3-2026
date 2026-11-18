// レーダー風の表示: 処理の実行中は、走査線が回る(動きを減らす設定の人には、止めて見せる)
import styles from "./RadarIndicator.module.css";

export function RadarIndicator({ active }: { active: boolean }) {
  return (
    <span className={`${styles.radar} ${active ? styles.active : ""}`} aria-hidden="true">
      <span className={styles.sweep} />
    </span>
  );
}

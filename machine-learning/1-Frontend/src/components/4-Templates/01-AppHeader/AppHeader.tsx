import { Button } from "../../1-Atoms/01-Button/Button";
import { StatusBadge } from "../../1-Atoms/02-StatusBadge/StatusBadge";
import styles from "./AppHeader.module.css";

interface AppHeaderProps {
  modeLabel: string;
  isTrainMode: boolean;
  canSwitch: boolean;
  onSwitch: () => void;
}

export function AppHeader({ modeLabel, isTrainMode, canSwitch, onSwitch }: AppHeaderProps) {
  return (
    <header className={styles.header}>
      <h1 className={styles.title}>疲労・ストレス推定 MLダッシュボード</h1>
      <div className={styles.right}>
        <StatusBadge text={modeLabel} tone={isTrainMode ? "warning" : "success"} />
        <Button disabled={!canSwitch} onClick={onSwitch}>{isTrainMode ? "予測モードにする" : "学習モードにする"}</Button>
      </div>
    </header>
  );
}

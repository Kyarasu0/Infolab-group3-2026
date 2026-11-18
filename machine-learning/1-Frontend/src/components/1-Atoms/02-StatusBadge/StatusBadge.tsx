import styles from "./StatusBadge.module.css";

interface StatusBadgeProps {
  text: string;
  tone: "neutral" | "success" | "warning" | "danger";
}

export function StatusBadge({ text, tone }: StatusBadgeProps) {
  return <span className={`${styles.badge} ${styles[tone]}`}>{text}</span>;
}

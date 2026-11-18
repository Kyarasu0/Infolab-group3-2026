import styles from "./ParameterField.module.css";

interface ParameterFieldProps {
  label: string;          // 日本語の名前(例: 圧縮後の次元数)
  name?: string;          // 設定の名前(例: latent_dim)
  description?: string;   // 何のパラメータかの説明
  text: string;
  onChange: (text: string) => void;
}

export function ParameterField({ label, name, description, text, onChange }: ParameterFieldProps) {
  return (
    <label className={styles.field}>
      <span className={styles.label}>{label}{name && <code className={styles.name}>{name}</code>}</span>
      <input className={styles.input} value={text} onChange={(event) => onChange(event.target.value)} />
      {description && <span className={styles.description}>{description}</span>}
    </label>
  );
}

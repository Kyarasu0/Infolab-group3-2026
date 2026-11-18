import styles from "./ParameterField.module.css";

interface ParameterFieldProps {
  label: string;
  text: string;
  onChange: (text: string) => void;
}

export function ParameterField({ label, text, onChange }: ParameterFieldProps) {
  return (
    <label className={styles.field}>
      <span className={styles.label}>{label}</span>
      <input className={styles.input} value={text} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

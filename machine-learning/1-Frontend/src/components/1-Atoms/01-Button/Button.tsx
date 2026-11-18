import type { ButtonHTMLAttributes } from "react";

import styles from "./Button.module.css";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & { primary?: boolean };

export function Button({ primary, className, ...rest }: ButtonProps) {
  return <button {...rest} className={[styles.button, primary && styles.primary, className].filter(Boolean).join(" ")} />;
}

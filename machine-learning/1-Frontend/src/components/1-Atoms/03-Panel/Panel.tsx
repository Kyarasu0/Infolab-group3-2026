// 枠(ガラスの面): 画面のまとまりを入れる。見出しの行(PanelHead)も一緒に出す
import type { HTMLAttributes } from "react";

import styles from "./Panel.module.css";

const join = (...names: (string | undefined)[]) => names.filter(Boolean).join(" ");

export function Panel({ className, ...rest }: HTMLAttributes<HTMLElement>) {
  return <section className={join(styles.panel, className)} {...rest} />;
}

export function PanelHead({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={join(styles.head, className)} {...rest} />;
}

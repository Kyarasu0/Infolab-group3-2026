// チャートの外枠: 題・凡例・ホバーの吹き出し・データが無いときの表示をまとめる
import { useRef, useState, type ReactNode, type RefObject } from "react";

import { bind } from "@/functions/cx";
import chart from "@/styles/chart.module.css";

const cx = bind(chart);

export interface Legend { name: string; color: string }
export interface TipRow { name?: string; color?: string; value: string }
interface Tip { x: number; y: number; title: string; rows: TipRow[] }

// 吹き出しの位置と中身を持つ(座標は、画面上の位置から、枠の中の位置に直す)
export function useChartTip() {
  const box = useRef<HTMLDivElement>(null);
  const [tip, setTip] = useState<Tip | null>(null);
  const show = (clientX: number, clientY: number, title: string, rows: TipRow[]) => {
    const rect = box.current?.getBoundingClientRect();
    if (rect) setTip({ x: clientX - rect.left, y: clientY - rect.top, title, rows });
  };
  return { box, tip, show, hide: () => setTip(null) };
}

interface ChartFrameProps {
  title: string;
  subtitle?: string;
  legend?: Legend[];
  isEmpty?: boolean;
  box: RefObject<HTMLDivElement | null>;
  tip: Tip | null;
  children: ReactNode;
}

export function ChartFrame({ title, subtitle, legend, isEmpty, box, tip, children }: ChartFrameProps) {
  return (
    <figure className={cx("chart")}>
      <figcaption className={cx("caption")}>
        <strong>{title}</strong>
        {subtitle && <span className={cx("subtitle")}>{subtitle}</span>}
      </figcaption>
      {legend && legend.length > 1 && (
        <div className={cx("legend")}>
          {legend.map((item) => (
            <span key={item.name}><i className={cx("swatch")} style={{ background: item.color }} />{item.name}</span>
          ))}
        </div>
      )}
      <div ref={box}>
        {isEmpty ? <p className={cx("empty")}>データがありません</p> : children}
        {tip && (
          <div className={cx("tip")} style={{ left: tip.x + 12, top: tip.y + 12 }}>
            <div className={cx("tipTitle")}>{tip.title}</div>
            {tip.rows.map((row, index) => (
              <div key={index}>
                {row.color && <i className={cx("swatch")} style={{ background: row.color }} />}
                {row.name ? `${row.name}: ` : ""}{row.value}
              </div>
            ))}
          </div>
        )}
      </div>
    </figure>
  );
}

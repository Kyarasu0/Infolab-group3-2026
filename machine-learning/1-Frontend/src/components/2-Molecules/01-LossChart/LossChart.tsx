import styles from "./LossChart.module.css";

interface LossChartProps {
  title: string;
  values: number[];
}

const CHART_WIDTH = 100;
const CHART_HEIGHT = 40;

// 損失の並びを、折れ線のpoints文字列にする(値が1つなら横線になる)
function toPolylinePoints(values: number[]): string {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  return values
    .map((value, index) => {
      const x = values.length === 1 ? 0 : (index / (values.length - 1)) * CHART_WIDTH;
      const y = CHART_HEIGHT - ((value - min) / range) * CHART_HEIGHT;
      return `${x},${y}`;
    })
    .join(" ");
}

export function LossChart({ title, values }: LossChartProps) {
  const hasValues = values.length > 0;
  return (
    <figure className={styles.chart}>
      <figcaption className={styles.title}>{title}</figcaption>
      {hasValues ? (
        <svg className={styles.svg} viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} preserveAspectRatio="none">
          <polyline className={styles.line} points={toPolylinePoints(values)} vectorEffect="non-scaling-stroke" />
        </svg>
      ) : (
        <p className={styles.empty}>データがありません</p>
      )}
      {hasValues && (
        <p className={styles.summary}>
          {values.length} エポック / 最初 {values[0].toFixed(4)} → 最新 {values[values.length - 1].toFixed(4)}
        </p>
      )}
    </figure>
  );
}

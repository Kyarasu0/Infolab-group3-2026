// ヒストグラム: グループごとの分布(各区間の割合)を、階段状の線で重ねる。閾値の線も引く
import { zeroBaseTicks } from "@/functions/chart-scale";
import { bind } from "@/functions/cx";
import chart from "@/styles/chart.module.css";
import { ChartFrame, useChartTip, type Legend } from "../01-ChartFrame/ChartFrame";

const cx = bind(chart);

export interface HistogramSeries extends Legend { ratios: number[] }

interface HistogramProps {
  title: string;
  subtitle?: string;
  edges: number[];
  series: HistogramSeries[];
  threshold?: number;
  xLabel: string;
}

const W = 720, H = 260, LEFT = 56, RIGHT = 16, TOP = 16, BOTTOM = 40;
const percent = (value: number) => `${(value * 100).toFixed(0)}%`;

export function Histogram({ title, subtitle, edges, series, threshold, xLabel }: HistogramProps) {
  const { box, tip, show, hide } = useChartTip();
  const binCount = edges.length - 1;
  const maxRatio = Math.max(0, ...series.flatMap((s) => s.ratios));

  // 1. 値の範囲から縦軸の目盛りを決め、座標を計算する関数を用意する
  const scale = zeroBaseTicks(maxRatio);
  const plotW = W - LEFT - RIGHT, plotH = H - TOP - BOTTOM;
  const lastEdge = edges[binCount] || 1;
  const x = (value: number) => LEFT + Math.min(1, Math.max(0, value / lastEdge)) * plotW;
  const y = (ratio: number) => TOP + plotH - (ratio / scale.high) * plotH;

  // 2. 階段状の線(各区間の左端から右端まで、同じ高さ)にする
  const stepPath = (ratios: number[]) =>
    ratios.map((ratio, i) => `${i === 0 ? "M" : "L"}${x(edges[i])},${y(ratio)} L${x(edges[i + 1])},${y(ratio)}`).join(" ");

  // 3. ポインタのある区間の割合を、吹き出しに出す
  const onMove = (event: React.PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const svgX = ((event.clientX - rect.left) / rect.width) * W;
    const bin = Math.min(binCount - 1, Math.max(0, Math.floor(((svgX - LEFT) / plotW) * binCount)));
    show(event.clientX, event.clientY, `${edges[bin].toFixed(2)} 〜 ${edges[bin + 1].toFixed(2)}`,
      series.map((s) => ({ name: s.name, color: s.color, value: percent(s.ratios[bin]) })));
  };

  return (
    <ChartFrame title={title} subtitle={subtitle} legend={series} isEmpty={binCount < 1} box={box} tip={tip}>
      <svg className={cx("svg")} viewBox={`0 0 ${W} ${H}`} onPointerMove={onMove} onPointerLeave={hide}>
        {scale.ticks.map((tick) => (
          <g key={tick}>
            <line className={cx("grid")} x1={LEFT} x2={W - RIGHT} y1={y(tick)} y2={y(tick)} />
            <text className={cx("tickText")} x={LEFT - 6} y={y(tick) + 4} textAnchor="end">{percent(tick)}</text>
          </g>
        ))}
        {[0, 0.25, 0.5, 0.75, 1].map((fraction) => (
          <text key={fraction} className={cx("tickText")} x={LEFT + fraction * plotW} y={TOP + plotH + 16} textAnchor="middle">
            {(fraction * lastEdge).toFixed(2)}
          </text>
        ))}
        <text className={cx("tickText")} x={LEFT + plotW / 2} y={H - 6} textAnchor="middle">{xLabel}</text>
        {series.map((s) => (
          <path key={s.name} d={stepPath(s.ratios)} fill="none" strokeWidth={2} style={{ stroke: s.color }} />
        ))}
        {threshold !== undefined && (
          <g>
            <line className={cx("axis")} x1={x(threshold)} x2={x(threshold)} y1={TOP} y2={TOP + plotH} strokeDasharray="5 4" />
            <text className={cx("tickText")} x={x(threshold) + 4} y={TOP + 10}>乖離の閾値 {threshold.toFixed(2)}</text>
          </g>
        )}
        <line className={cx("axis")} x1={LEFT} x2={W - RIGHT} y1={TOP + plotH} y2={TOP + plotH} />
      </svg>
    </ChartFrame>
  );
}

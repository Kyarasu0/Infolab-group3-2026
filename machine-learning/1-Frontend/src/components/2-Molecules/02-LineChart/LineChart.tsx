// 折れ線グラフ: 横軸は 1, 2, 3...(エポックなど)。ポインタに一番近い点で、全系列の値を出す
import { rangeTicks } from "@/functions/chart-scale";
import { bind } from "@/functions/cx";
import chart from "@/styles/chart.module.css";
import { ChartFrame, useChartTip, type Legend } from "../01-ChartFrame/ChartFrame";

const cx = bind(chart);

export interface LineSeries extends Legend { values: (number | null)[] }

interface LineChartProps {
  title: string;
  subtitle?: string;
  series: LineSeries[];
  xLabel?: string;
  format?: (value: number) => string;
}

const W = 720, H = 220, LEFT = 56, RIGHT = 16, TOP = 12, BOTTOM = 28;

export function LineChart({ title, subtitle, series, xLabel = "", format = (v) => v.toFixed(3) }: LineChartProps) {
  const { box, tip, show, hide } = useChartTip();
  const pointCount = Math.max(0, ...series.map((s) => s.values.length));
  const allValues = series.flatMap((s) => s.values).filter((v): v is number => v !== null);

  // 1. 値の範囲から縦軸の目盛りを決め、点の座標を計算する関数を用意する
  const scale = rangeTicks(Math.min(...allValues, Infinity), Math.max(...allValues, -Infinity));
  const plotW = W - LEFT - RIGHT, plotH = H - TOP - BOTTOM;
  const x = (index: number) => LEFT + (pointCount <= 1 ? plotW / 2 : (index / (pointCount - 1)) * plotW);
  const y = (value: number) => TOP + plotH - ((value - scale.low) / (scale.high - scale.low)) * plotH;

  // 2. 値の無い点で切れる線にする
  const pathOf = (values: (number | null)[]) =>
    values.map((v, i) => (v === null ? "" : `${values[i - 1] === null || i === 0 ? "M" : "L"}${x(i)},${y(v)}`)).join(" ");

  // 3. ポインタに一番近い点の値を、吹き出しに出す
  const onMove = (event: React.PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const svgX = ((event.clientX - rect.left) / rect.width) * W;
    const index = Math.min(pointCount - 1, Math.max(0, Math.round(((svgX - LEFT) / plotW) * (pointCount - 1))));
    show(event.clientX, event.clientY, `${xLabel}${index + 1}`,
      series.map((s) => ({ name: s.name, color: s.color, value: s.values[index] == null ? "-" : format(s.values[index]!) })));
  };
  const xTicks = Array.from({ length: Math.min(pointCount, 6) }, (_, i) =>
    Math.round((i * (pointCount - 1)) / Math.max(1, Math.min(pointCount, 6) - 1)));

  return (
    <ChartFrame title={title} subtitle={subtitle} legend={series} isEmpty={pointCount === 0} box={box} tip={tip}>
      <svg className={cx("svg")} viewBox={`0 0 ${W} ${H}`} onPointerMove={onMove} onPointerLeave={hide}>
        {scale.ticks.map((tick) => (
          <g key={tick}>
            <line className={cx("grid")} x1={LEFT} x2={W - RIGHT} y1={y(tick)} y2={y(tick)} />
            <text className={cx("tickText")} x={LEFT - 6} y={y(tick) + 4} textAnchor="end">{format(tick)}</text>
          </g>
        ))}
        <line className={cx("axis")} x1={LEFT} x2={W - RIGHT} y1={TOP + plotH} y2={TOP + plotH} />
        {xTicks.map((index) => (
          <text key={index} className={cx("tickText")} x={x(index)} y={H - 8} textAnchor="middle">{index + 1}</text>
        ))}
        {series.map((s) => (
          <path key={s.name} d={pathOf(s.values)} fill="none" strokeWidth={2} style={{ stroke: s.color }} />
        ))}
      </svg>
    </ChartFrame>
  );
}

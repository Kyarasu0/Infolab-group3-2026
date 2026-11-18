// 散布図: 色 = 状態、形 = サブタイプ(○ □ △ ◇)。ポインタに一番近い点の情報を出す
import type { ScatterPoint } from "@/functions/api-types";
import { rangeTicks } from "@/functions/chart-scale";
import { bind } from "@/functions/cx";
import { groupColor, groupLabel, subtypeLabel } from "@/functions/group-style";
import chart from "@/styles/chart.module.css";
import { ChartFrame, useChartTip } from "../01-ChartFrame/ChartFrame";

const cx = bind(chart);

interface ScatterChartProps {
  title: string;
  subtitle?: string;
  points: ScatterPoint[];
  xLabel: string;
  yLabel: string;
}

const W = 720, H = 360, LEFT = 56, RIGHT = 16, TOP = 12, BOTTOM = 40, R = 4.5, HOVER_DISTANCE = 16;

// サブタイプ番号に応じた形(点の中心 x, y)
function Marker({ x, y, subtype, color }: { x: number; y: number; subtype: number | null; color: string }) {
  const style = { fill: color, fillOpacity: 0.75, stroke: color };
  switch ((subtype ?? 0) % 4) {
    case 1: return <rect x={x - R} y={y - R} width={2 * R} height={2 * R} style={style} />;
    case 2: return <path d={`M${x},${y - R - 1} L${x + R + 1},${y + R} L${x - R - 1},${y + R} Z`} style={style} />;
    case 3: return <path d={`M${x},${y - R - 1} L${x + R + 1},${y} L${x},${y + R + 1} L${x - R - 1},${y} Z`} style={style} />;
    default: return <circle cx={x} cy={y} r={R} style={style} />;
  }
}

export function ScatterChart({ title, subtitle, points, xLabel, yLabel }: ScatterChartProps) {
  const { box, tip, show, hide } = useChartTip();
  const groups = [...new Set(points.map((point) => point.group))];

  // 1. 値の範囲から目盛りを決め、点の座標を計算する関数を用意する
  const xs = rangeTicks(Math.min(...points.map((p) => p.x), Infinity), Math.max(...points.map((p) => p.x), -Infinity));
  const ys = rangeTicks(Math.min(...points.map((p) => p.y), Infinity), Math.max(...points.map((p) => p.y), -Infinity));
  const plotW = W - LEFT - RIGHT, plotH = H - TOP - BOTTOM;
  const px = (value: number) => LEFT + ((value - xs.low) / (xs.high - xs.low)) * plotW;
  const py = (value: number) => TOP + plotH - ((value - ys.low) / (ys.high - ys.low)) * plotH;

  // 2. ポインタに一番近い点(近くに無ければ出さない)の情報を、吹き出しに出す
  const onMove = (event: React.PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const sx = ((event.clientX - rect.left) / rect.width) * W, sy = ((event.clientY - rect.top) / rect.height) * H;
    let nearest: ScatterPoint | null = null, best = HOVER_DISTANCE;
    for (const point of points) {
      const distance = Math.hypot(px(point.x) - sx, py(point.y) - sy);
      if (distance < best) { best = distance; nearest = point; }
    }
    if (!nearest) return hide();
    show(event.clientX, event.clientY, groupLabel(nearest.group), [
      { name: "サブタイプ", value: subtypeLabel(nearest.subtype) },
      { name: xLabel, value: nearest.x.toFixed(3) }, { name: yLabel, value: nearest.y.toFixed(3) },
    ]);
  };

  return (
    <ChartFrame title={title} subtitle={subtitle} isEmpty={points.length === 0} box={box} tip={tip}
      legend={groups.map((group, index) => ({ name: groupLabel(group), color: groupColor(group, index) }))}>
      <svg className={cx("svg")} viewBox={`0 0 ${W} ${H}`} onPointerMove={onMove} onPointerLeave={hide}>
        {xs.ticks.map((tick) => (
          <g key={`x${tick}`}>
            <line className={cx("grid")} x1={px(tick)} x2={px(tick)} y1={TOP} y2={TOP + plotH} />
            <text className={cx("tickText")} x={px(tick)} y={TOP + plotH + 16} textAnchor="middle">{tick.toFixed(1)}</text>
          </g>
        ))}
        {ys.ticks.map((tick) => (
          <g key={`y${tick}`}>
            <line className={cx("grid")} x1={LEFT} x2={W - RIGHT} y1={py(tick)} y2={py(tick)} />
            <text className={cx("tickText")} x={LEFT - 6} y={py(tick) + 4} textAnchor="end">{tick.toFixed(1)}</text>
          </g>
        ))}
        <text className={cx("tickText")} x={LEFT + plotW / 2} y={H - 6} textAnchor="middle">{xLabel}</text>
        <text className={cx("tickText")} x={14} y={TOP + plotH / 2} textAnchor="middle" transform={`rotate(-90 14 ${TOP + plotH / 2})`}>{yLabel}</text>
        {points.map((point, index) => (
          <Marker key={index} x={px(point.x)} y={py(point.y)} subtype={point.subtype}
            color={groupColor(point.group, groups.indexOf(point.group))} />
        ))}
      </svg>
    </ChartFrame>
  );
}

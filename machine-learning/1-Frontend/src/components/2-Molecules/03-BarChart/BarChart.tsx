// 棒グラフ: グループごとに、系列の棒を並べる。誤差(標準偏差)があれば、ひげで示す
import { zeroBaseTicks } from "@/functions/chart-scale";
import { bind } from "@/functions/cx";
import chart from "@/styles/chart.module.css";
import { ChartFrame, useChartTip, type Legend } from "../01-ChartFrame/ChartFrame";

const cx = bind(chart);

export interface Bar { value: number; error?: number }
export interface BarGroup { label: string; bars: (Bar | null)[] }

interface BarChartProps {
  title: string;
  subtitle?: string;
  series: Legend[];
  groups: BarGroup[];
  format?: (value: number) => string;
}

const W = 720, H = 240, LEFT = 56, RIGHT = 16, TOP = 12, BOTTOM = 48;

export function BarChart({ title, subtitle, series, groups, format = (v) => v.toFixed(3) }: BarChartProps) {
  const { box, tip, show, hide } = useChartTip();
  const maxValue = Math.max(0, ...groups.flatMap((g) => g.bars.map((b) => (b ? b.value + (b.error ?? 0) : 0))));

  // 1. 値の範囲から縦軸の目盛りを決め、棒の座標を計算する
  const scale = zeroBaseTicks(maxValue);
  const plotW = W - LEFT - RIGHT, plotH = H - TOP - BOTTOM;
  const y = (value: number) => TOP + plotH - (value / scale.high) * plotH;
  const groupW = plotW / Math.max(1, groups.length);
  const barW = Math.min(36, (groupW * 0.7) / Math.max(1, series.length));

  // 2. ポインタのあるグループの値を、吹き出しに出す
  const onMove = (event: React.PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const svgX = ((event.clientX - rect.left) / rect.width) * W;
    const group = groups[Math.min(groups.length - 1, Math.max(0, Math.floor((svgX - LEFT) / groupW)))];
    show(event.clientX, event.clientY, group.label, series.map((s, i) => ({
      name: s.name, color: s.color,
      value: group.bars[i] ? `${format(group.bars[i]!.value)}${group.bars[i]!.error !== undefined ? ` ± ${format(group.bars[i]!.error!)}` : ""}` : "-",
    })));
  };

  return (
    <ChartFrame title={title} subtitle={subtitle} legend={series} isEmpty={groups.length === 0} box={box} tip={tip}>
      <svg className={cx("svg")} viewBox={`0 0 ${W} ${H}`} onPointerMove={onMove} onPointerLeave={hide}>
        {scale.ticks.map((tick) => (
          <g key={tick}>
            <line className={cx("grid")} x1={LEFT} x2={W - RIGHT} y1={y(tick)} y2={y(tick)} />
            <text className={cx("tickText")} x={LEFT - 6} y={y(tick) + 4} textAnchor="end">{format(tick)}</text>
          </g>
        ))}
        {groups.map((group, groupIndex) => {
          const center = LEFT + groupW * (groupIndex + 0.5);
          return (
            <g key={group.label}>
              {group.bars.map((bar, barIndex) => {
                if (!bar) return null;
                const left = center - (series.length * barW) / 2 + barIndex * barW;
                return (
                  <g key={barIndex}>
                    <rect x={left} y={y(bar.value)} width={barW - 2} height={TOP + plotH - y(bar.value)} style={{ fill: series[barIndex].color }} />
                    {bar.error !== undefined && (
                      <line className={cx("axis")} x1={left + barW / 2 - 1} x2={left + barW / 2 - 1}
                        y1={y(Math.max(0, bar.value - bar.error))} y2={y(bar.value + bar.error)} />
                    )}
                  </g>
                );
              })}
              <text className={cx("tickText")} x={center} y={H - 26} textAnchor="middle">{group.label}</text>
            </g>
          );
        })}
        <line className={cx("axis")} x1={LEFT} x2={W - RIGHT} y1={TOP + plotH} y2={TOP + plotH} />
      </svg>
    </ChartFrame>
  );
}

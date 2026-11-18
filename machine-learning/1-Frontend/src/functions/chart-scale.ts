// チャートの目盛りの計算(軸は「キリのいい数」で区切る)

// キリのいい間隔を選ぶ
function niceStep(rawStep: number): number {
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  return [1, 2, 2.5, 5, 10].map((m) => m * magnitude).find((s) => s >= rawStep) ?? 10 * magnitude;
}

// low〜high を step ごとに区切った目盛り
function ticksBetween(low: number, high: number, step: number): number[] {
  const ticks: number[] = [];
  for (let value = low; value <= high + step / 1000; value += step) ticks.push(Number(value.toFixed(6)));
  return ticks;
}

// min〜max を含む、キリのいい範囲と目盛り(最小と最大が同じなら、少し広げる)
export function rangeTicks(min: number, max: number, count = 4) {
  if (min === max) { min -= 1; max += 1; }
  const step = niceStep((max - min) / count);
  const low = Math.floor(min / step) * step;
  const high = Math.ceil(max / step) * step;
  return { low, high, ticks: ticksBetween(low, high, step) };
}

// 0 から max までの、キリのいい範囲と目盛り(棒グラフ用)
export function zeroBaseTicks(max: number, count = 4) {
  if (max <= 0) return { low: 0, high: 1, ticks: [0, 1] };
  const step = niceStep(max / count);
  const high = Math.ceil(max / step) * step;
  return { low: 0, high, ticks: ticksBetween(0, high, step) };
}

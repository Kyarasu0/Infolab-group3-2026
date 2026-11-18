// 状態(normal / stress / fatigue)ごとの表示名(3-Shared/concept/states.json)と色
import states from "@shared/concept/states.json";

const GROUP_COLORS: Record<string, string> = {
  normal: "var(--chart-2)", stress: "var(--chart-4)", fatigue: "var(--chart-5)",
};
const FALLBACK_COLORS = ["var(--chart-1)", "var(--chart-3)", "var(--chart-6)"];

// 一覧に無い状態にも、順番で色を割り当てる
export function groupColor(group: string, index = 0): string {
  return GROUP_COLORS[group] ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

export const groupLabel = (group: string): string => states.find((state) => state.name === group)?.label ?? group;
export const subtypeLabel = (subtype: number | null): string => (subtype === null ? "-" : `タイプ${subtype + 1}`);

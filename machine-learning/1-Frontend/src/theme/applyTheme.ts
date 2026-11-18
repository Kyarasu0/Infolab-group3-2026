import { colorPalette } from "./ColorPalette";
import { sizeScale } from "./SizeScale";

// パレットと目盛りを、CSS変数として画面全体に設定する
export function applyTheme(): void {
  const variables = { ...colorPalette, ...sizeScale };
  for (const [name, value] of Object.entries(variables)) {
    document.documentElement.style.setProperty(`--${name}`, value);
  }
}

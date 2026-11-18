import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const FRONTEND_DIR = import.meta.dirname;
const SHARED_DIR = path.resolve(import.meta.dirname, "../3-Shared");

// 部品のCSSクラス名を「c + 階層1桁 + 部品2桁 - ファイル名 - クラス名」にする
// 例: 1-Atoms/01-Button/Button.module.css の .button → c101-Button-button
function generateScopedName(className: string, cssFilePath: string): string {
  const componentId = cssFilePath.match(/components\/(\d)-[^/]+\/(\d{2})-/);
  const fileName = path.basename(cssFilePath).replace(".module.css", "");
  const prefix = componentId ? `c${componentId[1]}${componentId[2]}` : "c000";
  return `${prefix}-${fileName}-${className}`;
}

export default defineConfig({
  plugins: [react()],
  css: { modules: { generateScopedName } },
  server: {
    // 3-Shared/(API一覧など)は、フロントの外にあるので、読めるようにする
    fs: { allow: [FRONTEND_DIR, SHARED_DIR] },
    // バックエンド(FastAPI)へ中継して、CORSを意識しなくてよくする(パスは /api/... のまま)
    proxy: { "/api": `http://localhost:${process.env.ML_BACKEND_PORT ?? 8000}` },
  },
});

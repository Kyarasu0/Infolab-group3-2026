import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const FRONTEND_DIR = import.meta.dirname;
const SHARED_DIR = path.resolve(FRONTEND_DIR, "../3-Shared");

// CSSのクラス名を、検証画面から直すファイルが分かる形にする
//   部品: c + 階層1桁 + 部品2桁 - ファイル名 - クラス名(例: c101-Button-button)
//   共通のクラス(styles/): shared-ファイル名-クラス名 / それ以外: app-クラス名
function generateScopedName(className: string, cssFilePath: string): string {
  const fileName = path.basename(cssFilePath).replace(".module.css", "");
  const componentId = cssFilePath.match(/components\/(\d)-[^/]+\/(\d{2})-/);
  if (componentId) return `c${componentId[1]}${componentId[2]}-${fileName}-${className}`;
  if (cssFilePath.includes("/styles/")) return `shared-${fileName}-${className}`;
  return `app-${className}`;
}

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(FRONTEND_DIR, "src"), "@shared": SHARED_DIR },
  },
  css: { modules: { generateScopedName } },
  server: {
    // 3-Shared/(API一覧など)は、フロントの外にあるので、読めるようにする
    fs: { allow: [FRONTEND_DIR, SHARED_DIR] },
    // バックエンド(FastAPI)へ中継して、CORSを意識しなくてよくする(パスは /api/... のまま)
    proxy: { "/api": `http://localhost:${process.env.ML_BACKEND_PORT ?? 8000}` },
  },
});

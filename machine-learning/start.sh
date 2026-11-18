#!/usr/bin/env bash
# 2回目以降用: バックエンド(FastAPI)とフロントエンド(Vite)を、まとめて起動する
# 初回は、先に setup.sh を実行する
#
# 使い方(どこから実行してもよい):
#   machine-learning/start.sh            # 学習モードで起動
#   machine-learning/start.sh predict    # 予測モードで起動
# 止めるときは Ctrl+C(バックエンドも一緒に止まる)
#
# 環境変数: ML_BACKEND_PORT(既定 8000)。そのほかの ML_* は README.md を参照
#
# 【全体の流れ】
# 1. 引数と、作業フォルダ・初回準備の確認
# 2. バックエンドを裏で起動し、動くまで待つ
# 3. フロントエンドを起動する(終了時にバックエンドも止める)

set -euo pipefail

# 1. 引数と、作業フォルダ・初回準備の確認
MODE="${1:-train}"
if [[ "$MODE" != "train" && "$MODE" != "predict" ]]; then
  echo "使い方: start.sh [train|predict]" >&2
  exit 1
fi
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ ! -d .venv || ! -d 1-Frontend/node_modules ]]; then
  echo "[start] 初回の準備が済んでいません。先に machine-learning/setup.sh を実行してください" >&2
  exit 1
fi
export ML_BACKEND_PORT="${ML_BACKEND_PORT:-8000}"   # フロントの中継先(vite.config.ts)も、これを読む

# 2. バックエンドを裏で起動し、動くまで待つ
ML_MODE="$MODE" PYTHONPATH=. .venv/bin/uvicorn server:app --app-dir 2-Backend --port "$ML_BACKEND_PORT" &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  curl -sf "http://localhost:${ML_BACKEND_PORT}/api/health" >/dev/null && break
  sleep 1
done
curl -sf "http://localhost:${ML_BACKEND_PORT}/api/health" >/dev/null \
  || { echo "[start] バックエンドが起動しませんでした" >&2; exit 1; }
echo "[start] バックエンド起動: http://localhost:${ML_BACKEND_PORT}(${MODE}モード)"

# 3. フロントエンドを起動する(http://localhost:5173)
cd 1-Frontend
npm run dev

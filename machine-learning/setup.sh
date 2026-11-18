#!/usr/bin/env bash
# 初回用: Python環境とnpmの依存を用意する(何度実行してもよい)
#
# 使い方(どこから実行してもよい):
#   machine-learning/setup.sh
# 終わったら、起動は start.sh を使う
#
# 【全体の流れ】
# 1. 作業フォルダの確認
# 2. Python環境(.venv)を作り、依存を入れる
# 3. フロントエンドのnpmの依存を入れる
# 4. データの有無を知らせる

set -euo pipefail

# 1. 作業フォルダの確認
cd "$(dirname "${BASH_SOURCE[0]}")"

# 2. Python環境(.venv)を作り、依存を入れる(torchはCPU版。数分かかります)
[[ -d .venv ]] || python3 -m venv .venv
.venv/bin/pip install -q --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
echo "[setup] Python環境: OK"

# 3. フロントエンドのnpmの依存を入れる
(cd 1-Frontend && npm install)
echo "[setup] npmの依存: OK"

# 4. データの有無を知らせる
if [[ ! -f data/training_data.npz ]]; then
  echo "[setup] 注意: data/training_data.npz がありません。学習・実験は、データを置くまでエラーになります(data/README.md)"
fi
echo "[setup] 完了。起動は machine-learning/start.sh"

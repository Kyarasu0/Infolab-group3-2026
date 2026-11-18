"""機械学習バックエンドの入口(フロントエンドと、通知用バックエンドの両方から呼ばれる)

APIの一覧(名前・メソッド・パス・担当のファイル・使えるモード)は、フロントと共有する
3-Shared/api-list.json に書く。各APIの処理は api/ に、1 API = 1 ファイル = 1 関数で置く
(例: api/get-health.py の get_health)。このファイルは、起動と登録だけを持つ。
モードや実行中の処理などの共有する状態は functions/app_state.py に、1か所だけ置く。

起動(machine-learning/ で実行):
    PYTHONPATH=. .venv/bin/uvicorn server:app --app-dir 2-Backend --port 8000

【ファイル全体の流れ】
1. アプリの作成
2. APIの登録(api-list.json の各APIを、api/ の関数に結びつける)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from functions.api_list_loader import load_api_list
from functions.api_registry import register_apis
from functions.backend_settings import ALLOWED_ORIGINS

# 1. アプリの作成
app = FastAPI(title="Typing fatigue/stress ML backend")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])

# 2. APIの登録
register_apis(app, load_api_list())

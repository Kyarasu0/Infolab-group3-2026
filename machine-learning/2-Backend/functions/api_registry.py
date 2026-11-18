"""3-Shared/api-list.json の各APIを、api/ の関数に結びつけて登録する"""
import importlib.util
from pathlib import Path
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException

from functions.app_state import mode_state

API_DIR = Path(__file__).resolve().parents[1] / "api"


def load_api_handler(api: dict) -> Callable:
    """api/ の担当のファイルから、APIの名前と同じ関数を読む(なければ例外)"""
    # 1. ファイル名にハイフンがあるので、パスから直接読み込む
    handler_file = API_DIR / api["handler_file"]
    spec = importlib.util.spec_from_file_location(f"ml_api_{api['name']}", handler_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 2. 名前の関数が無ければ、起動時に止める
    if not hasattr(module, api["name"]):
        raise RuntimeError(f"{handler_file.name} に {api['name']} がありません")
    return getattr(module, api["name"])


def find_unlisted_api_files(apis: list) -> set:
    """一覧に載っていないのに、api/ にあるファイル(あれば、書き忘れ)"""
    listed_files = {api["handler_file"] for api in apis}
    return {path.name for path in API_DIR.glob("*.py")} - listed_files


def _require_mode(required_mode: str):
    # 現在のモードでは使えないAPIを、409で断る
    def check() -> None:
        if mode_state.mode != required_mode:
            raise HTTPException(409, f"このAPIは {required_mode} モードでのみ使えます(現在: {mode_state.mode})")
    return check


def register_apis(target_app: FastAPI, apis: list) -> None:
    """一覧の各APIを、メソッド・パス・使えるモードで登録する(一覧に書いた順)"""
    unlisted = find_unlisted_api_files(apis)
    if unlisted:
        raise RuntimeError(f"api-list.json に載っていないファイルがあります: {sorted(unlisted)}")
    for api in apis:
        dependencies = [] if api["mode"] == "any" else [Depends(_require_mode(api["mode"]))]
        target_app.add_api_route(
            api["path"], load_api_handler(api), methods=[api["method"]],
            status_code=api.get("status_code", 200), summary=api["description"],
            dependencies=dependencies,
        )

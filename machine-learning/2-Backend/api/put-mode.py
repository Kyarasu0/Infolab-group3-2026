"""
モードの切り替え (PUT /api/mode):
モードを切り替える。学習などの実行中は切り替えられない(409)。
"""

from fastapi import HTTPException

from functions.app_state import job_tracker, mode_state
from functions.schemas import ModeRequest


def put_mode(request: ModeRequest) -> dict:
    """モードの切り替え"""
    # 1. 処理の最中は切り替えない
    if job_tracker.is_running():
        raise HTTPException(409, "学習などの実行中は、モードを変えられません")

    # 2. 未知のモードは断る
    try:
        mode_state.change(request.mode)
    except ValueError as error:
        raise HTTPException(422, str(error))
    return {"mode": mode_state.mode}

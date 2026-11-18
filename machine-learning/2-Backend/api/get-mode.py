"""
モードの取得 (GET /api/mode):
現在のモード(学習 / 予測)を返す。
"""

from functions.app_state import mode_state


def get_mode() -> dict:
    """モードの取得"""
    return {"mode": mode_state.mode}

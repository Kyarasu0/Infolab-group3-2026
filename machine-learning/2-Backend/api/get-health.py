"""
ヘルスチェック (GET /api/health):
バックエンドが動いているかと、現在のモードを返す。
"""

from functions.app_state import mode_state


def get_health() -> dict:
    """ヘルスチェック"""
    return {"status": "ok", "mode": mode_state.mode}

"""
処理の進捗の取得 (GET /api/jobs/current):
実行中(または直近)の処理の進捗と、エポックごとの損失を返す。
"""

from functions.app_state import job_tracker


def get_current_job() -> dict:
    """処理の進捗の取得"""
    return job_tracker.status()

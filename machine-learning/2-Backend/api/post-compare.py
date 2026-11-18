"""
全シナリオの比較 (POST /api/compare):
全シナリオを同じデータで学習・評価して比べる(別スレッドで実行)。
"""

from functions import prediction_service, training_service
from functions.app_state import start_job


def post_compare() -> dict:
    """全シナリオの比較"""
    # 1. 全シナリオを比べて保存し、古い予測用モデルを捨てる処理を、別スレッドで始める
    def work(on_epoch):
        results = training_service.compare_all(on_epoch)
        for result in results:
            prediction_service.forget_runner(result["scenario"])
        return results

    return start_job("compare", "all", work)

"""
比較結果の取得 (GET /api/compare/result):
直近のシナリオ比較の結果を返す。
"""

from functions import training_service


def get_compare_result() -> dict:
    """比較結果の取得"""
    return training_service.read_comparison()

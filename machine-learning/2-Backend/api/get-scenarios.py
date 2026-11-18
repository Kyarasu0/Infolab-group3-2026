"""
シナリオ一覧の取得 (GET /api/scenarios):
シナリオの一覧と、学習済みかどうか・最新の指標を返す。
"""

from functions import training_service


def get_scenarios() -> list:
    """シナリオ一覧の取得"""
    return training_service.list_scenarios()

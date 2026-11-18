"""
シナリオの結果ファイルの取得(architecture) (GET /api/scenarios/{name}/architecture):
学習済みシナリオの、層ごとの構成とパラメータ量を返す。未学習なら404。
"""

from fastapi import HTTPException

from functions import training_service


def get_scenario_architecture(name: str) -> dict:
    """学習済みシナリオの層ごとの構成とパラメータ量の取得"""
    try:
        return training_service.read_scenario_file(name, "architecture.json")
    except FileNotFoundError as error:
        raise HTTPException(404, str(error))

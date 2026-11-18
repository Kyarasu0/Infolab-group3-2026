"""
シナリオの結果ファイルの取得(result) (GET /api/scenarios/{name}/result):
学習済みシナリオの、学習曲線と評価指標を返す。未学習なら404。
"""

from fastapi import HTTPException

from functions import training_service


def get_scenario_result(name: str) -> dict:
    """学習済みシナリオの学習曲線と評価指標の取得"""
    try:
        return training_service.read_scenario_file(name, "result.json")
    except FileNotFoundError as error:
        raise HTTPException(404, str(error))

"""
散布図の取得 (GET /api/scenarios/{name}/scatter):
学習済みシナリオの、評価用データを2次元に落とした点を返す(状態ごとの色分けとサブタイプ用)。
"""

from fastapi import HTTPException

from functions import visualization_service


def get_scenario_scatter(name: str) -> dict:
    """散布図の取得"""
    # 1. 失敗の種類を、HTTPのエラーに変える
    try:
        return visualization_service.scenario_scatter(name)
    except KeyError as error:
        raise HTTPException(404, str(error.args[0]))
    except FileNotFoundError as error:
        raise HTTPException(409, str(error))
    except ValueError as error:
        raise HTTPException(400, str(error))

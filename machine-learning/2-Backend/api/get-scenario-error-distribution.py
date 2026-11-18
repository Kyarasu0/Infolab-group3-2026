"""
誤差の分布の取得 (GET /api/scenarios/{name}/error-distribution):
再構成誤差の分布(状態ごとの割合)と、乖離の閾値を返す。オートエンコーダーを使うシナリオのみ。
"""

from fastapi import HTTPException

from functions import visualization_service


def get_scenario_error_distribution(name: str) -> dict:
    """誤差の分布の取得"""
    # 1. 失敗の種類を、HTTPのエラーに変える
    try:
        return visualization_service.scenario_error_distribution(name)
    except KeyError as error:
        raise HTTPException(404, str(error.args[0]))
    except FileNotFoundError as error:
        raise HTTPException(409, str(error))
    except ValueError as error:
        raise HTTPException(400, str(error))

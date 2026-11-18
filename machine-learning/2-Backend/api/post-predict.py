"""
予測 (POST /api/predict):
学習済みモデルで、疲労・ストレスを予測する。通知用バックエンドから呼ばれる(予測モードのみ)。
"""

from fastapi import HTTPException

from functions import prediction_service
from functions.schemas import PredictRequest


def post_predict(request: PredictRequest) -> dict:
    """予測"""
    # 1. 学習済みモデルで予測し、失敗の種類をHTTPのエラーに変える
    try:
        return prediction_service.predict(request.samples, request.scenario)
    except KeyError as error:
        raise HTTPException(404, str(error.args[0]))
    except FileNotFoundError as error:
        raise HTTPException(409, str(error))
    except ValueError as error:
        raise HTTPException(400, str(error))

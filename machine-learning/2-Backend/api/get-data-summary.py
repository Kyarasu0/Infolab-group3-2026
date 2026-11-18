"""
データの概要の取得 (GET /api/data/summary):
学習データの件数と、特徴量ごとの平均・標準偏差を、状態ごとに返す。
"""

from fastapi import HTTPException

from functions import visualization_service


def get_data_summary() -> dict:
    """データの概要の取得"""
    # 1. 失敗の種類を、HTTPのエラーに変える
    try:
        return visualization_service.whole_data_summary()
    except FileNotFoundError as error:
        raise HTTPException(409, str(error))

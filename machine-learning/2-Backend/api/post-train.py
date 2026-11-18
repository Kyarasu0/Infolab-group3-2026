"""
シナリオの学習 (POST /api/train):
全データでシナリオを学習し、予測用モデルを保存する(別スレッドで実行。進捗は get_current_job)。
"""

from functions import prediction_service, training_service
from functions.app_state import start_job
from functions.schemas import TrainRequest


def post_train(request: TrainRequest) -> dict:
    """シナリオの学習"""
    # 1. 学習して保存し、古い予測用モデルを捨てる処理を、別スレッドで始める
    def work(on_epoch):
        result = training_service.train_scenario(request.scenario, on_epoch)
        prediction_service.forget_runner(request.scenario)
        return result

    return start_job("train", request.scenario, work)

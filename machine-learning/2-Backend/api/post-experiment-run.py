"""
実験の実行 (POST /api/experiments/run):
シナリオ・評価計画・パラメータで評価して記録する。同じ条件の記録があれば実行せず、その記録を返す(force で再実行)。
"""

from fastapi import HTTPException

from experiments.recorder import record_reader
from experiments.recorder.experiment_recorder import build_experiment, execute_experiment
from functions import training_service
from functions.app_state import start_job
from functions.schemas import ExperimentRunRequest


def post_experiment_run(request: ExperimentRunRequest) -> dict:
    """実験の実行"""
    # 1. 条件を確かめて、実行キーを作る
    try:
        experiment = build_experiment(request.scenario, request.evaluation_plan,
                                      request.parameters, training_service.TRAINING_DATA_PATH)
    except KeyError as error:
        raise HTTPException(404, str(error.args[0]))
    except FileNotFoundError as error:
        raise HTTPException(409, str(error))
    except ValueError as error:
        raise HTTPException(400, str(error))

    # 2. 同じ条件の記録があれば、force でない限り実行せず、その記録を返す
    existing = record_reader.find_by_run_key(experiment["run_key"])
    if existing and not request.force:
        return {"status": "exists", "record": existing}

    # 3. なければ、別スレッドで評価して記録する
    def work(on_epoch):
        data = training_service.load_training_data()
        record = execute_experiment(experiment, data, request.note, on_epoch)
        return {"record_id": record["id"]}

    return start_job("experiment", request.scenario, work)

"""グラフ用の値を、学習済みモデルと、評価用に分けたデータから作る"""
from scenarios.scenario_loader import list_scenario_names
from scenarios.scenario_runner import ScenarioRunner
from scenarios.training_data import TrainingData
from scenarios.visualization_data import data_summary, error_distribution, scatter_data

from functions import training_service


def _load_runner(name: str) -> ScenarioRunner:
    # 1. 未知のシナリオは KeyError、未学習は FileNotFoundError
    if name not in list_scenario_names():
        raise KeyError(f"未知のシナリオです: {name}")
    if not (training_service.ARTIFACTS_DIR / name / "scenario.json").exists():
        raise FileNotFoundError(f"学習済みモデルがありません: {name}(先に学習してください)")
    return ScenarioRunner.load(training_service.ARTIFACTS_DIR / name)


def _test_data() -> TrainingData:
    # 学習に使わなかった評価用のデータ(学習のときと同じ分け方)
    return training_service.load_training_data().split(training_service.TEST_RATIO, training_service.SPLIT_SEED)[1]


def scenario_scatter(name: str) -> dict:
    return scatter_data(_load_runner(name), _test_data())


def scenario_error_distribution(name: str) -> dict:
    return error_distribution(_load_runner(name), _test_data())


def whole_data_summary() -> dict:
    return data_summary(training_service.load_training_data())

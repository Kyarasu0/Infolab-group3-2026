"""学習済みモデルを読み込んで予測する(読み込んだモデルは使い回す)"""
import threading

from scenarios.scenario_loader import list_scenario_names
from scenarios.scenario_runner import ScenarioRunner

from backend_settings import ARTIFACTS_DIR, DEFAULT_SCENARIO

_runners = {}
_lock = threading.Lock()


def predict(samples, scenario_name: str = None) -> dict:
    # 1. シナリオ名が無ければ、既定のシナリオを使う
    name = scenario_name or DEFAULT_SCENARIO
    if name not in list_scenario_names():
        raise KeyError(f"未知のシナリオです: {name}")

    # 2. 学習済みモデルを読み込み(2回目以降は使い回し)、予測する
    results = _get_runner(name).predict(samples)
    return {"scenario": name, "results": results}


def forget_runner(name: str) -> None:
    # 再学習したときに、古いモデルを捨てる
    with _lock:
        _runners.pop(name, None)


def _get_runner(name: str) -> ScenarioRunner:
    with _lock:
        if name not in _runners:
            if not (ARTIFACTS_DIR / name / "scenario.json").exists():
                raise FileNotFoundError(f"学習済みモデルがありません: {name}(先に学習してください)")
            _runners[name] = ScenarioRunner.load(ARTIFACTS_DIR / name)
        return _runners[name]

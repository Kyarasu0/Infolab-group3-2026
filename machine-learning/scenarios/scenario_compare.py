"""全シナリオを同じデータで学習・評価し、指標を比べる"""
from scenarios.scenario_loader import list_scenario_names, load_scenario
from scenarios.scenario_runner import ScenarioRunner
from scenarios.training_data import TrainingData


def compare_scenarios(data: TrainingData, test_ratio=0.3, seed=0, on_epoch=None) -> list:
    # 1. 全シナリオで、同じ分割の学習用・評価用データを使う
    train, test = data.split(test_ratio, seed)

    # 2. シナリオごとに学習し、評価データで指標を出す
    results = []
    for name in list_scenario_names():
        runner = ScenarioRunner(load_scenario(name))
        runner.fit(train, on_epoch)
        results.append({"scenario": name, "metrics": runner.evaluate(test)})

    # 3. 正解率の高い順に並べて返す
    return sorted(results, key=lambda result: result["metrics"]["accuracy"], reverse=True)

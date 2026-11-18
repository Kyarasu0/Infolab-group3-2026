"""学習・シナリオ比較を行い、結果をartifactsフォルダに保存する"""
from models.common import load_json, save_json
from scenarios.scenario_compare import compare_scenarios
from scenarios.scenario_loader import list_scenario_names, load_scenario
from scenarios.scenario_runner import ScenarioRunner
from scenarios.training_data import TrainingData

from functions.backend_settings import ARTIFACTS_DIR, TRAINING_DATA_PATH

TEST_RATIO = 0.3
SPLIT_SEED = 0


def load_training_data() -> TrainingData:
    # 1. データファイルが無ければ、分かるエラーにする
    if not TRAINING_DATA_PATH.exists():
        raise FileNotFoundError(f"学習データがありません: {TRAINING_DATA_PATH}")
    return TrainingData.from_npz(TRAINING_DATA_PATH)


def train_scenario(name: str, on_epoch=None) -> dict:
    # 1. データを学習用と評価用に分ける
    train, test = load_training_data().split(TEST_RATIO, SPLIT_SEED)

    # 2. シナリオの順にモデルを学習し、評価データで指標を出す
    runner = ScenarioRunner(load_scenario(name))
    history = runner.fit(train, on_epoch)
    metrics = runner.evaluate(test)

    # 3. モデル・構成JSON・学習曲線・指標を保存する
    runner.save(ARTIFACTS_DIR / name)
    save_json({"history": history, "metrics": metrics}, ARTIFACTS_DIR / name / "result.json")
    return {"scenario": name, "metrics": metrics}


def compare_all(on_epoch=None) -> list:
    # 1. 全シナリオを同じデータで比べ、結果を保存する
    results = compare_scenarios(load_training_data(), TEST_RATIO, SPLIT_SEED, on_epoch)
    save_json({"results": results}, ARTIFACTS_DIR / "comparison.json")
    return results


def read_comparison() -> dict:
    path = ARTIFACTS_DIR / "comparison.json"
    return load_json(path) if path.exists() else {"results": []}


def list_scenarios() -> list:
    # 1. シナリオごとに、説明と学習済みかどうかを返す
    summaries = []
    for name in list_scenario_names():
        result_path = ARTIFACTS_DIR / name / "result.json"
        summaries.append({
            "name": name,
            "description": load_scenario(name).get("description", ""),
            "trained": result_path.exists(),
            "metrics": load_json(result_path)["metrics"] if result_path.exists() else None,
        })
    return summaries


def read_scenario_file(name: str, file_name: str) -> dict:
    # 1. 学習済みの結果(result.json / architecture.json)を返す
    path = ARTIFACTS_DIR / name / file_name
    if name not in list_scenario_names() or not path.exists():
        raise FileNotFoundError(f"学習済みの結果がありません: {name}")
    return load_json(path)

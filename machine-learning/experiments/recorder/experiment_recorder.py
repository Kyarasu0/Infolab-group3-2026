"""実験(シナリオ x 評価計画 x パラメータ)を実行して、結果を records/ に記録する"""
import copy
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

from experiments.recorder import record_reader
from experiments.recorder.cross_validator import cross_validate
from experiments.recorder.evaluation_plan import load_plan
from experiments.recorder.run_key import hash_file, make_run_key
from models.common import save_json
from scenarios.scenario_loader import list_scenario_names, load_scenario, merge_parameters
from scenarios.training_data import TrainingData


def apply_overrides(scenario: dict, overrides: dict = None) -> dict:
    """シナリオのparametersに、実行時の上書き値を重ねた、新しいシナリオを返す"""
    # 1. 既定値にある名前だけ、上書きできる
    defaults = merge_parameters(scenario)
    merged = copy.deepcopy(scenario)
    merged["parameters"] = copy.deepcopy(defaults)
    for model, values in (overrides or {}).items():
        for key, value in values.items():
            if model not in defaults or key not in defaults[model]:
                raise ValueError(f"未知のパラメータです: {model}.{key}")
            merged["parameters"][model][key] = value
    return merged


def build_experiment(scenario_name: str, plan_name: str, overrides, data_path) -> dict:
    # 1. シナリオ・評価計画・データを確かめる(無ければ KeyError / FileNotFoundError)
    if scenario_name not in list_scenario_names():
        raise KeyError(f"未知のシナリオです: {scenario_name}")
    if not Path(data_path).exists():
        raise FileNotFoundError(f"学習データがありません: {data_path}")
    scenario = apply_overrides(load_scenario(scenario_name), overrides)
    plan = load_plan(plan_name)

    # 2. 結果を左右する条件から、実行キーを作る
    data_hash = hash_file(data_path)
    run_key = make_run_key(scenario["pipeline"], scenario["parameters"], plan, data_hash)
    return {"scenario": scenario, "plan": plan, "data_hash": data_hash, "run_key": run_key}


def execute_experiment(experiment: dict, data: TrainingData, note: str = "", on_epoch=None) -> dict:
    # 1. 評価計画に沿って、交差検証などで評価する
    scenario = experiment["scenario"]
    result = cross_validate(scenario, experiment["plan"], data, on_epoch)

    # 2. 再現に必要な情報と一緒に、記録を作る
    created_at = datetime.now()
    record_id = f"{created_at:%Y-%m-%d-%H%M%S}-{scenario['name']}-{experiment['run_key'][:8]}"
    record = {
        "id": record_id,
        "created_at": created_at.isoformat(timespec="seconds"),
        "run_key": experiment["run_key"],
        "scenario": scenario["name"],
        "pipeline": scenario["pipeline"],
        "parameters": scenario["parameters"],
        "evaluation_plan": experiment["plan"],
        "data": {
            "sha256": experiment["data_hash"],
            "normal_count": len(data.normal_x),
            "labeled_count": len(data.labeled_x),
            "feature_count": int(data.labeled_x.shape[1]),
            "label_counts": dict(Counter(data.labels.tolist())),
        },
        "git_commit": _current_git_commit(),
        **result,
        "note": note,
    }

    # 3. records/ に1実行1ファイルで保存する
    save_json(record, record_reader.RECORDS_DIR / f"{record_id}.json")
    return record


def _current_git_commit():
    try:
        output = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                                text=True, check=True, cwd=Path(__file__).parent)
        return output.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None

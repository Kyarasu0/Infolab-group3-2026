"""シナリオのJSONを読み込み、パラメータを合成して、内容を検証する"""
from pathlib import Path

from models.common import load_json
from scenarios.feature_sets import AUTOENCODER_FEATURE_NAMES, FEATURE_NAMES

SCENARIOS_DIR = Path(__file__).parent
MODELS_DIR = SCENARIOS_DIR.parent / "models"
DEFAULT_PARAMS_PATHS = {
    "autoencoder": MODELS_DIR / "autoencoder" / "autoencoder.json",
    "svm": MODELS_DIR / "svm" / "svm.json",
    "clustering": MODELS_DIR / "clustering" / "clustering.json",
}


def list_scenario_names() -> list:
    return sorted(path.stem for path in SCENARIOS_DIR.glob("*.json"))


def load_scenario(name: str) -> dict:
    # 1. JSONを読み、内容を検証する
    scenario = load_json(SCENARIOS_DIR / f"{name}.json")
    scenario["name"] = name
    validate_scenario(scenario)
    return scenario


def merge_parameters(scenario: dict) -> dict:
    """モデルごとの既定パラメータに、シナリオの上書き値を重ねる"""
    # 1. 既定のJSONを読み、シナリオの parameters で上書きする
    overrides = scenario.get("parameters", {})
    return {
        model: {**load_json(path), **overrides.get(model, {})}
        for model, path in DEFAULT_PARAMS_PATHS.items()
    }


def load_parameter_descriptions() -> dict:
    """モデルごとの、パラメータの日本語名と説明を返す(models/*/*.descriptions.json)"""
    # 1. 既定のパラメータJSONと同じ場所の、<名前>.descriptions.json を読む
    return {
        model: load_json(path.with_name(f"{path.stem}.descriptions.json"))
        for model, path in DEFAULT_PARAMS_PATHS.items()
    }


def validate_scenario(scenario: dict) -> None:
    seen_models = []
    for stage in scenario["pipeline"]:
        model = stage["model"]
        feature = stage.get("input", "raw")

        # 1. 未知のモデル・特徴量を弾く
        if model not in DEFAULT_PARAMS_PATHS:
            raise ValueError(f"未知のモデルです: {model}")
        if model != "autoencoder" and feature not in FEATURE_NAMES:
            raise ValueError(f"未知の特徴量です: {feature}")

        # 2. 順序の前提を確認する(AEの特徴量はAEの後、サブタイプは状態判定の後)
        if feature in AUTOENCODER_FEATURE_NAMES and "autoencoder" not in seen_models:
            raise ValueError(f"{feature} を使うには、先に autoencoder が必要です")
        if model == "clustering" and "svm" not in seen_models:
            raise ValueError("clustering は、svm の後に置いてください")
        seen_models.append(model)

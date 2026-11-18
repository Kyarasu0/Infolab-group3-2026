"""評価計画(データの分け方・kの値など)のJSONを読み込んで検証する"""
from pathlib import Path

from models.common import load_json

PLANS_DIR = Path(__file__).resolve().parent.parent / "evaluation_plans"
METHODS = ("kfold", "holdout")


def list_plan_names() -> list:
    return sorted(path.stem for path in PLANS_DIR.glob("*.json"))


def load_plan(name: str) -> dict:
    # 1. 計画のJSONを読む(名前が無ければ KeyError)
    if name not in list_plan_names():
        raise KeyError(f"未知の評価計画です: {name}")
    plan = {**load_json(PLANS_DIR / f"{name}.json"), "name": name}

    # 2. 手法ごとの値を検証する
    _validate(plan)
    return plan


def _validate(plan: dict) -> None:
    if plan["method"] not in METHODS:
        raise ValueError(f"未対応の評価方法です: {plan['method']}")
    if plan["method"] == "kfold" and not (isinstance(plan["k"], int) and plan["k"] >= 2):
        raise ValueError("kfold の k は2以上の整数にしてください")
    if plan["method"] == "holdout" and not 0 < plan["test_ratio"] < 1:
        raise ValueError("holdout の test_ratio は0〜1の間にしてください")

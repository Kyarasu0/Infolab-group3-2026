"""APIの入力の形"""
from typing import Any, List, Optional

from pydantic import BaseModel


class ModeRequest(BaseModel):
    mode: str   # 3-Shared/concept/modes.json の名前


class TrainRequest(BaseModel):
    scenario: str


class PredictRequest(BaseModel):
    scenario: Optional[str] = None   # 省略すると、既定のシナリオ
    samples: List[Any]               # 1サンプル=1次元配列。サンプルの配列を渡す(次元数は自由)


class ExperimentRunRequest(BaseModel):
    scenario: str
    evaluation_plan: str
    parameters: Optional[dict] = None   # {モデル名: {パラメータ名: 値}} の上書き
    note: str = ""
    force: bool = False                 # true なら、実行済みでも、もう一度実行する

"""APIの入出力の形"""
from typing import Any, List, Optional

from pydantic import BaseModel


class ModeRequest(BaseModel):
    mode: str   # "train" か "predict"


class TrainRequest(BaseModel):
    scenario: str


class PredictRequest(BaseModel):
    scenario: Optional[str] = None   # 省略すると、既定のシナリオ
    samples: List[Any]               # 1サンプル=1次元配列。サンプルの配列を渡す(次元数は自由)

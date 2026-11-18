"""各モデルで共通して使う補助関数(配列の整形・JSONの読み書き)"""
import json
from pathlib import Path

import numpy as np


def load_json(json_path) -> dict:
    # 1. JSONファイルを読み込んで辞書にする
    with open(json_path, encoding="utf-8") as json_file:
        return json.load(json_file)


def save_json(values: dict, json_path) -> None:
    # 1. 保存先フォルダが無ければ作る
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)

    # 2. 辞書をJSONファイルに書き出す
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(values, json_file, ensure_ascii=False, indent=2)


def as_2d_array(values) -> np.ndarray:
    """どんな次元の入力でも (サンプル数, 特徴量数) の2次元配列にそろえる

    - 1次元: 1サンプル分の特徴量として扱う
    - 3次元以上: サンプルごとに平坦化する(例: 時間窓 x チャンネル)
    """
    # 1. numpy配列にそろえる
    array = np.asarray(values, dtype=np.float64)

    # 2. 次元数に応じて2次元にする
    if array.ndim == 0:
        raise ValueError("スカラーは入力できません。配列を渡してください")
    if array.ndim == 1:
        return array.reshape(1, -1)
    return array.reshape(array.shape[0], -1)

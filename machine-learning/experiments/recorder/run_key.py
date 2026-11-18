"""「同じ条件の実行か」を見分けるための実行キー(ハッシュ)を作る"""
import hashlib
import json
from pathlib import Path


def hash_file(file_path) -> str:
    # 1. データファイルの中身から、ハッシュを作る(データが変われば別の実行になる)
    digest = hashlib.sha256()
    with open(Path(file_path), "rb") as data_file:
        for chunk in iter(lambda: data_file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value):
    """1.0 と 1 のように、同じ値で書き方だけが違うものを、同じ形にそろえる"""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    return value


def make_run_key(pipeline: list, parameters: dict, plan: dict, data_hash: str) -> str:
    # 1. 結果を左右する条件を、順序を固定したJSONにして、ハッシュの先頭16文字を返す
    conditions = _canonical({"pipeline": pipeline, "parameters": parameters, "plan": plan, "data": data_hash})
    text = json.dumps(conditions, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

"""実験の記録(records/のJSON)を読む"""
import os
import re
from pathlib import Path

from models.common import load_json

# 記録の保存先(環境変数 ML_RECORDS_DIR で変えられる)
RECORDS_DIR = Path(os.environ.get("ML_RECORDS_DIR", Path(__file__).resolve().parent.parent / "records"))
RECORD_ID_PATTERN = re.compile(r"^[0-9A-Za-z_.-]+$")


def list_records() -> list:
    # 1. 新しい順(ファイル名の日時順)に、概要だけを返す
    paths = sorted(RECORDS_DIR.glob("*.json"), reverse=True)
    return [_to_summary(load_json(path)) for path in paths]


def get_record(record_id: str) -> dict:
    # 1. IDにパス区切りなどが混ざっていたら、探さずに断る
    path = RECORDS_DIR / f"{record_id}.json"
    if not RECORD_ID_PATTERN.match(record_id) or not path.exists():
        raise KeyError(f"記録がありません: {record_id}")
    return load_json(path)


def find_by_run_key(run_key: str):
    """同じ実行キーの記録のうち、最新の概要を返す(無ければ None)"""
    for summary in list_records():
        if summary["run_key"] == run_key:
            return summary
    return None


def _to_summary(record: dict) -> dict:
    return {
        "id": record["id"],
        "created_at": record["created_at"],
        "run_key": record["run_key"],
        "scenario": record["scenario"],
        "evaluation_plan": record["evaluation_plan"]["name"],
        "summary": record["summary"],
        "note": record["note"],
    }

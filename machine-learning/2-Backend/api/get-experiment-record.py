"""
実験の記録の詳細の取得 (GET /api/experiments/records/{record_id}):
実験の記録1件の詳細(全パラメータ・foldごとの指標)を返す。
"""

from fastapi import HTTPException

from experiments.recorder import record_reader


def get_experiment_record(record_id: str) -> dict:
    """実験の記録の詳細の取得"""
    try:
        return record_reader.get_record(record_id)
    except KeyError as error:
        raise HTTPException(404, str(error.args[0]))

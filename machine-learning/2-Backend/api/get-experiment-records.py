"""
実験の記録の一覧の取得 (GET /api/experiments/records):
実験の記録を、新しい順に一覧する(概要のみ)。
"""

from experiments.recorder import record_reader


def get_experiment_records() -> list:
    """実験の記録の一覧の取得"""
    return record_reader.list_records()

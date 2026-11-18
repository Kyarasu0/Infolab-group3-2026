"""
評価計画の一覧の取得 (GET /api/evaluation-plans):
選べる評価計画(k交差検証・holdoutなど)の一覧を返す。
"""

from experiments.recorder.evaluation_plan import list_plan_names, load_plan


def get_evaluation_plans() -> list:
    """評価計画の一覧の取得"""
    return [load_plan(name) for name in list_plan_names()]

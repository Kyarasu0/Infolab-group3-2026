"""
シナリオのパラメータの取得 (GET /api/scenarios/{name}/parameters):
シナリオで使われる全パラメータ(モデルの既定値+シナリオの上書き)を返す。
"""

from fastapi import HTTPException

from scenarios.scenario_loader import load_scenario, merge_parameters


def get_scenario_parameters(name: str) -> dict:
    """シナリオのパラメータの取得"""
    try:
        return merge_parameters(load_scenario(name))
    except FileNotFoundError:
        raise HTTPException(404, f"未知のシナリオです: {name}")

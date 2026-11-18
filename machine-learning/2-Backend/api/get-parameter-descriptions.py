"""
パラメータの説明の取得 (GET /api/parameter-descriptions):
モデルごとの、パラメータの日本語名と説明を返す(models/*/*.descriptions.json)。
"""

from scenarios.scenario_loader import load_parameter_descriptions


def get_parameter_descriptions() -> dict:
    """パラメータの説明の取得"""
    return load_parameter_descriptions()

"""3-Shared/ のJSON(API一覧・モード)を読み込む"""
from models.common import load_json

from functions.backend_settings import PROJECT_ROOT

SHARED_DIR = PROJECT_ROOT / "3-Shared"


def load_api_list() -> list:
    # 1. API一覧を、ファイルに書いた順に返す
    return load_json(SHARED_DIR / "api-list.json")["apis"]


def load_mode_names() -> list:
    return [mode["name"] for mode in load_json(SHARED_DIR / "concept" / "modes.json")]

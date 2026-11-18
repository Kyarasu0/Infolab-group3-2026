import re

from fastapi import FastAPI

from functions.api_list_loader import SHARED_DIR, load_api_list, load_mode_names
from functions.api_registry import API_DIR, find_unlisted_api_files, load_api_handler, register_apis
from models.common import load_json
from scenarios.evaluation_metrics import compute_metrics


def test_全APIの担当ファイルがあり_名前と同じ関数がある():
    for api in load_api_list():
        assert (API_DIR / api["handler_file"]).exists()
        assert api["handler_file"] == api["name"].replace("_", "-") + ".py"
        assert callable(load_api_handler(api))


def test_api_dirのファイルは全て一覧に載っている():
    assert find_unlisted_api_files(load_api_list()) == set()


def test_全APIに一言の説明と使えるモードがある():
    modes = set(load_mode_names()) | {"any"}
    for api in load_api_list():
        assert api["description"].strip() and api["mode"] in modes


def test_APIの名前とパスとメソッドが重複しない():
    apis = load_api_list()
    assert len({api["name"] for api in apis}) == len(apis)
    assert len({(api["method"], api["path"]) for api in apis}) == len(apis)
    assert all(api["path"].startswith("/api/") for api in apis)


def test_一覧の全APIが実際のルートとして登録される():
    app = FastAPI()
    register_apis(app, load_api_list())
    registered = {(route.path, tuple(route.methods - {"HEAD"})) for route in app.routes if hasattr(route, "methods")}
    for api in load_api_list():
        assert (api["path"], (api["method"],)) in registered


def test_パス引数の名前は小文字とアンダースコアだけ():
    for api in load_api_list():
        assert all(re.fullmatch(r"[a-z_]+", name) for name in re.findall(r"{(.*?)}", api["path"]))


def test_メトリクス定義が評価指標の名前と一致する():
    names = {metric["name"] for metric in load_json(SHARED_DIR / "concept" / "metrics.json")}
    assert names == set(compute_metrics([{"state": "normal"}], ["stress"], [], {}))

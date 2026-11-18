import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

from functions import backend_settings, prediction_service, training_service
from experiments.recorder import record_reader
from tests.synthetic_data import make_training_data


@pytest.fixture
def client(tmp_path, monkeypatch):
    # 合成データと一時フォルダを使い、実データ・実成果物に触れないようにする
    data = make_training_data(6)
    data_path = tmp_path / "training_data.npz"
    np.savez(data_path, normal_x=data.normal_x, labeled_x=data.labeled_x, labels=data.labels)
    for module in (backend_settings, training_service, prediction_service):
        monkeypatch.setattr(module, "ARTIFACTS_DIR", tmp_path / "artifacts", raising=False)
    monkeypatch.setattr(training_service, "TRAINING_DATA_PATH", data_path)
    monkeypatch.setattr(prediction_service, "_runners", {})
    monkeypatch.setattr(record_reader, "RECORDS_DIR", tmp_path / "records")
    from functions import app_state
    import server
    app_state.mode_state.change("train")
    return TestClient(server.app)


def _wait_for_job(client):
    for _ in range(300):
        status = client.get("/api/jobs/current").json()
        if status["state"] != "running":
            return status
        time.sleep(0.1)
    raise TimeoutError


def test_学習モードで学習し_予測モードで予測できる(client):
    # 1. 学習モードで、学習を始めて終わるまで待つ
    assert client.post("/api/train", json={"scenario": "04-raw-svm-baseline"}).status_code == 202
    assert _wait_for_job(client)["state"] == "finished"

    # 2. 構成JSONと一覧に、学習済みとして出る
    assert client.get("/api/scenarios/04-raw-svm-baseline/architecture").json()["svm"]["total_support_vectors"] > 0
    assert any(s["name"] == "04-raw-svm-baseline" and s["trained"] for s in client.get("/api/scenarios").json())

    # 3. 予測モードに切り替えて、予測する
    assert client.put("/api/mode", json={"mode": "predict"}).json()["mode"] == "predict"
    body = {"scenario": "04-raw-svm-baseline", "samples": [[5, 5, 5, 0, 0, 0], [-5, -5, -5, 0, 0, 0]]}
    results = client.post("/api/predict", json=body).json()["results"]
    assert [r["state"] for r in results] == ["stress", "fatigue"]


def test_モードに合わないAPIは409で断る(client):
    assert client.post("/api/predict", json={"samples": [[1, 2, 3]]}).status_code == 409
    client.put("/api/mode", json={"mode": "predict"})
    assert client.post("/api/train", json={"scenario": "04-raw-svm-baseline"}).status_code == 409


def test_次元が違う入力は400_未学習は409(client):
    client.put("/api/mode", json={"mode": "predict"})
    assert client.post("/api/predict", json={"scenario": "04-raw-svm-baseline", "samples": [[1, 2]]}).status_code == 409
    client.put("/api/mode", json={"mode": "train"})
    client.post("/api/train", json={"scenario": "04-raw-svm-baseline"})
    _wait_for_job(client)
    client.put("/api/mode", json={"mode": "predict"})
    assert client.post("/api/predict", json={"scenario": "04-raw-svm-baseline", "samples": [[1, 2]]}).status_code == 400


def test_データが無いと学習は失敗として記録される(client, monkeypatch, tmp_path):
    monkeypatch.setattr(training_service, "TRAINING_DATA_PATH", tmp_path / "none.npz")
    client.post("/api/train", json={"scenario": "04-raw-svm-baseline"})
    status = _wait_for_job(client)
    assert status["state"] == "failed" and "学習データ" in status["error"]


def test_実験は実行され_同じ条件なら過去の記録が返り_forceで再実行できる(client):
    body = {"scenario": "04-raw-svm-baseline", "evaluation_plan": "kfold-5", "note": "初回"}

    # 1. 初回は、実行されて記録される
    assert client.post("/api/experiments/run", json=body).json()["status"] == "started"
    assert _wait_for_job(client)["state"] == "finished"
    records = client.get("/api/experiments/records").json()
    assert len(records) == 1 and records[0]["summary"]["accuracy"]["mean"] > 0.7
    detail = client.get(f"/api/experiments/records/{records[0]['id']}").json()
    assert len(detail["folds"]) == 5 and detail["note"] == "初回"

    # 2. 同じ条件は実行されず、過去の記録が返る
    again = client.post("/api/experiments/run", json=body).json()
    assert again["status"] == "exists" and again["record"]["id"] == records[0]["id"]

    # 3. パラメータを変えれば別の実行になり、force なら同じ条件でも再実行される
    changed = {**body, "parameters": {"svm": {"C": 3.0}}}
    assert client.post("/api/experiments/run", json=changed).json()["status"] == "started"
    _wait_for_job(client)
    assert client.post("/api/experiments/run", json={**body, "force": True}).json()["status"] == "started"
    _wait_for_job(client)
    assert len(client.get("/api/experiments/records").json()) == 3


def test_実験APIの入力エラーと評価計画_パラメータ一覧(client):
    assert client.post("/api/experiments/run", json={"scenario": "nope", "evaluation_plan": "kfold-5"}).status_code == 404
    assert client.post("/api/experiments/run", json={"scenario": "04-raw-svm-baseline", "evaluation_plan": "nope"}).status_code == 404
    bad = {"scenario": "04-raw-svm-baseline", "evaluation_plan": "kfold-5", "parameters": {"svm": {"zzz": 1}}}
    assert client.post("/api/experiments/run", json=bad).status_code == 400
    assert client.get("/api/experiments/records/..%2Fx").status_code == 404
    assert {p["name"] for p in client.get("/api/evaluation-plans").json()} >= {"kfold-5", "holdout-30"}
    assert client.get("/api/scenarios/01-latent-to-svm/parameters").json()["autoencoder"]["latent_dim"] == 4
    client.put("/api/mode", json={"mode": "predict"})
    assert client.post("/api/experiments/run", json={"scenario": "04-raw-svm-baseline", "evaluation_plan": "kfold-5"}).status_code == 409

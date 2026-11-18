import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

import backend_settings
import prediction_service
import training_service
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
    import main
    main.mode_state.change("train")
    return TestClient(main.app)


def _wait_for_job(client):
    for _ in range(300):
        status = client.get("/jobs/current").json()
        if status["state"] != "running":
            return status
        time.sleep(0.1)
    raise TimeoutError


def test_学習モードで学習し_予測モードで予測できる(client):
    # 1. 学習モードで、学習を始めて終わるまで待つ
    assert client.post("/train", json={"scenario": "04-raw-svm-baseline"}).status_code == 202
    assert _wait_for_job(client)["state"] == "finished"

    # 2. 構成JSONと一覧に、学習済みとして出る
    assert client.get("/scenarios/04-raw-svm-baseline/architecture").json()["svm"]["total_support_vectors"] > 0
    assert any(s["name"] == "04-raw-svm-baseline" and s["trained"] for s in client.get("/scenarios").json())

    # 3. 予測モードに切り替えて、予測する
    assert client.put("/mode", json={"mode": "predict"}).json()["mode"] == "predict"
    body = {"scenario": "04-raw-svm-baseline", "samples": [[5, 5, 5, 0, 0, 0], [-5, -5, -5, 0, 0, 0]]}
    results = client.post("/predict", json=body).json()["results"]
    assert [r["state"] for r in results] == ["stress", "fatigue"]


def test_モードに合わないAPIは409で断る(client):
    assert client.post("/predict", json={"samples": [[1, 2, 3]]}).status_code == 409
    client.put("/mode", json={"mode": "predict"})
    assert client.post("/train", json={"scenario": "04-raw-svm-baseline"}).status_code == 409


def test_次元が違う入力は400_未学習は409(client):
    client.put("/mode", json={"mode": "predict"})
    assert client.post("/predict", json={"scenario": "04-raw-svm-baseline", "samples": [[1, 2]]}).status_code == 409
    client.put("/mode", json={"mode": "train"})
    client.post("/train", json={"scenario": "04-raw-svm-baseline"})
    _wait_for_job(client)
    client.put("/mode", json={"mode": "predict"})
    assert client.post("/predict", json={"scenario": "04-raw-svm-baseline", "samples": [[1, 2]]}).status_code == 400


def test_データが無いと学習は失敗として記録される(client, monkeypatch, tmp_path):
    monkeypatch.setattr(training_service, "TRAINING_DATA_PATH", tmp_path / "none.npz")
    client.post("/train", json={"scenario": "04-raw-svm-baseline"})
    status = _wait_for_job(client)
    assert status["state"] == "failed" and "学習データ" in status["error"]

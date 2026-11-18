import numpy as np
import pytest

from experiments.recorder import record_reader
from experiments.recorder.cross_validator import summarize_metrics
from experiments.recorder.data_splitter import split_data
from experiments.recorder.evaluation_plan import list_plan_names, load_plan
from experiments.recorder.experiment_recorder import (
    apply_overrides, build_experiment, execute_experiment,
)
from experiments.recorder.run_key import make_run_key
from scenarios.scenario_loader import load_scenario
from tests.synthetic_data import make_training_data


@pytest.fixture
def records_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(record_reader, "RECORDS_DIR", tmp_path / "records")
    return tmp_path / "records"


@pytest.fixture
def data_path(tmp_path):
    data = make_training_data(6)
    path = tmp_path / "training_data.npz"
    np.savez(path, normal_x=data.normal_x, labeled_x=data.labeled_x, labels=data.labels)
    return path


def test_全評価計画が読み込める():
    assert {"kfold-5", "kfold-10", "holdout-30"} <= set(list_plan_names())
    assert all(load_plan(name)["method"] in ("kfold", "holdout") for name in list_plan_names())


def test_kfoldは全サンプルを1回ずつ評価に使い_ラベルの比率が保たれる():
    data = make_training_data(6)
    pairs = list(split_data(data, load_plan("kfold-5")))
    assert len(pairs) == 5
    assert sum(len(test.labeled_x) for _, test in pairs) == len(data.labeled_x)
    assert sum(len(test.normal_x) for _, test in pairs) == len(data.normal_x)
    for train, test in pairs:
        assert len(train.labeled_x) + len(test.labeled_x) == len(data.labeled_x)
        assert set(test.labels) == {"stress", "fatigue"}


def test_kがラベルの最少数より大きいと弾く():
    data = make_training_data(6)
    with pytest.raises(ValueError):
        list(split_data(data, {"method": "kfold", "k": 500, "stratified": True, "seed": 0}))


def test_holdoutは1組だけ返す():
    assert len(list(split_data(make_training_data(6), load_plan("holdout-30")))) == 1


def test_指標の平均と標準偏差をまとめる():
    summary = summarize_metrics([{"a": 1.0, "b": None}, {"a": 3.0, "b": None}])
    assert summary["a"] == {"mean": 2.0, "std": 1.0} and summary["b"] is None


def test_実行キーは条件が同じなら同じで_違えば変わる():
    base = make_run_key([{"model": "svm"}], {"svm": {"C": 1}}, {"k": 5}, "hash")
    assert base == make_run_key([{"model": "svm"}], {"svm": {"C": 1}}, {"k": 5}, "hash")
    assert base != make_run_key([{"model": "svm"}], {"svm": {"C": 2}}, {"k": 5}, "hash")
    assert base != make_run_key([{"model": "svm"}], {"svm": {"C": 1}}, {"k": 5}, "other-data")


def test_上書きは既定値にある名前だけ許す():
    scenario = load_scenario("01-latent-to-svm")
    assert apply_overrides(scenario, {"svm": {"C": 5}})["parameters"]["svm"]["C"] == 5
    with pytest.raises(ValueError):
        apply_overrides(scenario, {"svm": {"no_such_param": 1}})


def test_実験を実行して記録し_同じキーで見つけられる(records_dir, data_path):
    experiment = build_experiment("04-raw-svm-baseline", "kfold-5", None, data_path)
    assert record_reader.find_by_run_key(experiment["run_key"]) is None

    record = execute_experiment(experiment, make_training_data(6), note="テスト")
    assert len(record["folds"]) == 5 and record["summary"]["accuracy"]["mean"] > 0.7
    assert record["parameters"]["svm"]["C"] == 1.0 and record["data"]["feature_count"] == 6

    assert record_reader.find_by_run_key(experiment["run_key"])["id"] == record["id"]
    assert record_reader.get_record(record["id"])["note"] == "テスト"
    assert [r["id"] for r in record_reader.list_records()] == [record["id"]]


def test_記録IDにパス区切りがあると読まない(records_dir):
    with pytest.raises(KeyError):
        record_reader.get_record("../../secrets")


def test_実行キーは_1と1_0を同じ値として扱う():
    assert make_run_key([], {"svm": {"C": 1}}, {"k": 5}, "h") == make_run_key([], {"svm": {"C": 1.0}}, {"k": 5}, "h")

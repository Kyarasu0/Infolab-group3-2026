import pytest

from models.common import load_json

from scenarios.scenario_compare import compare_scenarios
from scenarios.scenario_loader import list_scenario_names, load_scenario
from scenarios.scenario_runner import ScenarioRunner
from tests.synthetic_data import make_training_data

FAST_AUTOENCODER = {"autoencoder": {"epochs": 20}}


def _fast(scenario: dict) -> dict:
    scenario["parameters"] = {**scenario.get("parameters", {}), **{
        "autoencoder": {**scenario.get("parameters", {}).get("autoencoder", {}), "epochs": 20}}}
    return scenario


@pytest.mark.parametrize("name", list_scenario_names())
def test_全シナリオが学習と予測と評価までできる(name):
    train, test = make_training_data().split(0.3, 0)
    runner = ScenarioRunner(_fast(load_scenario(name)))
    runner.fit(train)
    predictions = runner.predict(test.labeled_x)
    assert len(predictions) == len(test.labeled_x)
    assert {"state", "subtype", "anomaly_score", "state_probabilities"} <= set(predictions[0])
    assert runner.evaluate(test)["accuracy"] > 0.7


def test_保存したシナリオを読み込むと同じ予測になる(tmp_path):
    train, test = make_training_data().split(0.3, 0)
    runner = ScenarioRunner(_fast(load_scenario("01-latent-to-svm")))
    runner.fit(train)
    runner.save(tmp_path)
    loaded = ScenarioRunner.load(tmp_path)
    assert [p["state"] for p in runner.predict(test.labeled_x)] == \
        [p["state"] for p in loaded.predict(test.labeled_x)]


def test_AEより前にAEの特徴量を使うシナリオは弾く():
    scenario = {"pipeline": [{"model": "svm", "input": "latent"}, {"model": "autoencoder"}]}
    with pytest.raises(ValueError):
        ScenarioRunner(scenario)


def test_比較は全シナリオの結果を返す():
    results = compare_scenarios(make_training_data())
    assert {r["scenario"] for r in results} == set(list_scenario_names())


def test_構成JSONに各層のパラメータ量が出る(tmp_path):
    train, _ = make_training_data(8).split(0.3, 0)
    runner = ScenarioRunner(_fast(load_scenario("01-latent-to-svm")))
    runner.fit(train)
    runner.save(tmp_path)
    architecture = load_json(tmp_path / "architecture.json")
    autoencoder = architecture["autoencoder"]
    linear_layers = [layer for layer in autoencoder["layers"] if layer["type"] == "Linear"]
    assert autoencoder["input_dim"] == 8
    assert autoencoder["total_parameters"] == sum(layer["parameter_count"] for layer in linear_layers)
    assert linear_layers[0]["weight"]["shape"] == [linear_layers[0]["out_features"], 8]
    assert architecture["svm"]["total_support_vectors"] > 0
    assert set(architecture["clustering"]) == {"stress", "fatigue"}
    assert "values" in runner.describe_architecture(include_values=True)["autoencoder"]["layers"][0]["weight"]

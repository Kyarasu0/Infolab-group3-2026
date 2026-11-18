"""シナリオJSONの順番どおりにモデルをつなぎ、学習・予測・評価を行う"""
from pathlib import Path

import numpy as np

from models.autoencoder.autoencoder import Autoencoder
from models.clustering.clustering_model import ClusteringModel
from models.common import as_2d_array, load_json, save_json
from models.svm.svm_classifier import SvmClassifier
from scenarios.evaluation_metrics import compute_metrics
from scenarios.feature_sets import build_feature_sets
from scenarios.scenario_loader import merge_parameters, validate_scenario
from scenarios.training_data import TrainingData

NORMAL_STATE = "normal"


class ScenarioRunner:
    def __init__(self, scenario: dict):
        # 1. シナリオを検証し、モデルごとのパラメータを合成する
        validate_scenario(scenario)
        self.scenario = scenario
        self.parameters = merge_parameters(scenario)
        self.autoencoder = None
        self.svm = None
        self.clusterings = {}   # 状態ラベルごとのクラスタリング
        self.input_dim = None   # 学習時の入力次元(予測時の検査に使う)

    def fit(self, data: TrainingData, on_epoch=None) -> dict:
        # 1. 入力次元をそろえて記録する(通常データとラベル付きデータで同じ次元)
        if data.normal_x.shape[1] != data.labeled_x.shape[1]:
            raise ValueError("通常データとラベル付きデータで、特徴量の数が違います")
        self.input_dim = int(data.labeled_x.shape[1])

        # 2. パイプラインの順に、各モデルを学習する
        for stage in self.scenario["pipeline"]:
            model = stage["model"]
            features = build_feature_sets(data.labeled_x, self.autoencoder)

            if model == "autoencoder":
                self.autoencoder = Autoencoder(self.parameters["autoencoder"])
                self.autoencoder.fit(data.normal_x, on_epoch)
            elif model == "svm":
                self.svm = SvmClassifier(self.parameters["svm"])
                self.svm.fit(features[stage.get("input", "raw")], data.labels)
            elif model == "clustering":
                self._fit_clusterings(features[stage.get("input", "raw")], data.labels)

        # 3. 学習曲線を、画面表示用に返す
        loss_history = self.autoencoder.loss_history if self.autoencoder else []
        return {"autoencoder_loss": loss_history}

    def predict(self, x) -> list:
        # 1. 学習時と同じ入力次元か確認する
        x = as_2d_array(x)
        if self.input_dim is not None and x.shape[1] != self.input_dim:
            raise ValueError(
                f"入力の特徴量数が学習時と違います(学習時: {self.input_dim}、今回: {x.shape[1]})"
            )

        # 2. 特徴量を作り、乖離スコアで「通常」を先に除く(ゲート)
        features = build_feature_sets(x, self.autoencoder)
        row_count = len(features["raw"])
        scores = self.autoencoder.reconstruction_error(x) if self.autoencoder else None
        use_gate = self.autoencoder is not None and self.scenario.get("anomaly_gate", True)
        active = self.autoencoder.is_anomalous(x) if use_gate else np.ones(row_count, bool)

        # 3. 乖離のあるサンプルだけ、SVMで状態を判定する
        states = [NORMAL_STATE] * row_count
        probabilities = [None] * row_count
        svm_features = features[self._input_of("svm")]
        if active.any():
            active_features = svm_features[active]
            for row, state, probability in zip(
                np.flatnonzero(active),
                self.svm.predict(active_features),
                self.svm.predict_proba(active_features),
            ):
                states[row] = state
                probabilities[row] = probability

        # 4. 状態ごとのクラスタリングで、サブタイプを決める
        subtypes = self._predict_subtypes(features[self._input_of("clustering")], states)

        return [
            {
                "state": states[row],
                "subtype": subtypes[row],
                "anomaly_score": None if scores is None else float(scores[row]),
                "state_probabilities": probabilities[row],
            }
            for row in range(row_count)
        ]

    def evaluate(self, test_data: TrainingData) -> dict:
        # 1. 評価データと通常データに予測を行う
        predictions = self.predict(test_data.labeled_x)
        normal_predictions = self.predict(test_data.normal_x)

        # 2. 状態ごとに、サブタイプの分かれ具合を測る材料を集める
        features = build_feature_sets(test_data.labeled_x, self.autoencoder)
        cluster_features = features[self._input_of("clustering")]
        cluster_materials = {}
        for label, model in self.clusterings.items():
            rows = test_data.labels == label
            if rows.sum() >= 3:
                cluster_materials[label] = (
                    cluster_features[rows], model.predict(cluster_features[rows])
                )
        return compute_metrics(
            predictions, test_data.labels, normal_predictions, cluster_materials
        )

    def describe_architecture(self, include_values: bool = False) -> dict:
        """シナリオ全体の構成(各モデルの層・パラメータ量)を返す"""
        # 1. 学習済みのモデルだけ、構成を説明する
        architecture = {"scenario": self.scenario.get("name"), "pipeline": self.scenario["pipeline"],
                        "input_dim": self.input_dim}
        if self.autoencoder:
            architecture["autoencoder"] = self.autoencoder.describe(include_values)
        if self.svm:
            architecture["svm"] = self.svm.describe()
        architecture["clustering"] = {
            label: model.describe() for label, model in self.clusterings.items()
        }
        return architecture

    def save(self, directory) -> None:
        # 1. シナリオと、学習済みの各モデルを保存する
        directory = Path(directory)
        save_json(self.scenario, directory / "scenario.json")
        save_json({"input_dim": self.input_dim}, directory / "runner_meta.json")
        save_json(self.describe_architecture(), directory / "architecture.json")
        if self.autoencoder:
            self.autoencoder.save(directory / "autoencoder")
        if self.svm:
            self.svm.save(directory / "svm.joblib")
        for label, model in self.clusterings.items():
            model.save(directory / "clustering" / f"{label}.joblib")

    @classmethod
    def load(cls, directory) -> "ScenarioRunner":
        # 1. 保存したシナリオから、同じ構成を作ってモデルを読み込む
        directory = Path(directory)
        runner = cls(load_json(directory / "scenario.json"))
        runner.input_dim = load_json(directory / "runner_meta.json")["input_dim"]
        if (directory / "autoencoder").exists():
            runner.autoencoder = Autoencoder.load(directory / "autoencoder")
        if (directory / "svm.joblib").exists():
            runner.svm = SvmClassifier.load(directory / "svm.joblib")
        for path in sorted((directory / "clustering").glob("*.joblib")):
            runner.clusterings[path.stem] = ClusteringModel.load(path)
        return runner

    def _input_of(self, model: str) -> str:
        for stage in self.scenario["pipeline"]:
            if stage["model"] == model:
                return stage.get("input", "raw")
        return "raw"

    def _fit_clusterings(self, features, labels) -> None:
        # 状態(stress / fatigue)ごとに、別々にクラスタリングする
        for label in sorted(set(labels)):
            model = ClusteringModel(self.parameters["clustering"])
            model.fit(features[labels == label])
            self.clusterings[str(label)] = model

    def _predict_subtypes(self, features, states: list) -> list:
        subtypes = [None] * len(states)
        for label, model in self.clusterings.items():
            rows = np.array([state == label for state in states])
            if rows.any():
                for row, subtype in zip(np.flatnonzero(rows), model.predict(features[rows])):
                    subtypes[row] = subtype
        return subtypes

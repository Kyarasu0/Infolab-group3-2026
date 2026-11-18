"""ストレス/疲労などの状態を判定するSVM(特徴量の次元数は自動で決まる)"""
from collections import Counter
from pathlib import Path

import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from models.common import as_2d_array, load_json

DEFAULT_PARAMS_PATH = Path(__file__).with_name("svm.json")


class SvmClassifier:
    def __init__(self, params: dict = None):
        # 1. 引数が無ければ、既定のJSONを使う
        self.params = params or load_json(DEFAULT_PARAMS_PATH)
        self.pipeline = None

    def fit(self, features, labels) -> None:
        # 1. 確率を出すため、SVMを確率較正でつつむ(クラス内の最少数でCVの分割数を決める)
        smallest_class_count = min(Counter(labels).values())
        svm = SVC(
            kernel=self.params["kernel"],
            C=self.params["C"],
            gamma=self.params["gamma"],
            class_weight=self.params["class_weight"],
            random_state=self.params["seed"],
        )
        calibrated_svm = CalibratedClassifierCV(
            svm, ensemble=False, cv=max(2, min(5, smallest_class_count))
        )

        # 2. 標準化と合わせて、特徴量とラベルで学習する
        self.pipeline = make_pipeline(StandardScaler(), calibrated_svm)
        self.pipeline.fit(as_2d_array(features), labels)

    def predict(self, features) -> list:
        return [str(label) for label in self.pipeline.predict(as_2d_array(features))]

    def predict_proba(self, features) -> list:
        # 1. クラスごとの確率を、サンプルごとの辞書にして返す
        probabilities = self.pipeline.predict_proba(as_2d_array(features))
        classes = [str(label) for label in self.pipeline.classes_]
        return [
            {label: float(value) for label, value in zip(classes, row)}
            for row in probabilities
        ]

    def describe(self) -> dict:
        """サポートベクターの数など、学習結果の構成を返す"""
        # 1. 較正の中に入っている、学習済みSVMを取り出す
        svm = self.pipeline[-1].calibrated_classifiers_[0].estimator
        classes = [str(label) for label in svm.classes_]
        return {
            "model": "svm",
            "input_dim": int(svm.n_features_in_),
            "classes": classes,
            "support_vectors_per_class": dict(zip(classes, map(int, svm.n_support_))),
            "total_support_vectors": int(svm.support_vectors_.shape[0]),
            "support_vectors_shape": list(svm.support_vectors_.shape),
            "dual_coef_shape": list(svm.dual_coef_.shape),
            "hyperparameters": self.params,
        }

    def save(self, file_path) -> None:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"params": self.params, "pipeline": self.pipeline}, file_path)

    @classmethod
    def load(cls, file_path) -> "SvmClassifier":
        saved = joblib.load(file_path)
        model = cls(saved["params"])
        model.pipeline = saved["pipeline"]
        return model

"""サブタイプ(ストレス・疲労の種類)を分けるクラスタリング(KMeans / GMM)"""
from pathlib import Path

import joblib
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from models.common import as_2d_array, load_json

DEFAULT_PARAMS_PATH = Path(__file__).with_name("clustering.json")


class ClusteringModel:
    def __init__(self, params: dict = None):
        # 1. 引数が無ければ、既定のJSONを使う
        self.params = params or load_json(DEFAULT_PARAMS_PATH)
        self.pipeline = None

    def fit(self, features) -> None:
        # 1. サンプル数より多いクラスタは作れないので、数を収める
        x = as_2d_array(features)
        n_clusters = max(1, min(self.params["n_clusters"], len(x)))

        # 2. 標準化と、選ばれた手法のクラスタリングをまとめて学習する
        if self.params["method"] == "kmeans":
            cluster_model = KMeans(
                n_clusters=n_clusters, n_init=10, random_state=self.params["seed"]
            )
        elif self.params["method"] == "gmm":
            cluster_model = GaussianMixture(
                n_components=n_clusters, random_state=self.params["seed"]
            )
        else:
            raise ValueError(f"未対応の手法です: {self.params['method']}")
        self.pipeline = make_pipeline(StandardScaler(), cluster_model)
        self.pipeline.fit(x)

    def predict(self, features) -> list:
        return [int(label) for label in self.pipeline.predict(as_2d_array(features))]

    def describe(self) -> dict:
        """クラスタ数と、各クラスタの中心の形を返す"""
        # 1. 手法ごとに、中心の持ち方が違う(KMeans: cluster_centers_、GMM: means_)
        cluster_model = self.pipeline[-1]
        centers = getattr(cluster_model, "cluster_centers_", None)
        if centers is None:
            centers = cluster_model.means_
        return {
            "model": "clustering",
            "method": self.params["method"],
            "input_dim": int(centers.shape[1]),
            "cluster_count": int(centers.shape[0]),
            "centers_shape": list(centers.shape),
            "hyperparameters": self.params,
        }

    def save(self, file_path) -> None:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"params": self.params, "pipeline": self.pipeline}, file_path)

    @classmethod
    def load(cls, file_path) -> "ClusteringModel":
        saved = joblib.load(file_path)
        model = cls(saved["params"])
        model.pipeline = saved["pipeline"]
        return model

"""画面のグラフ(散布図・誤差の分布・データの概要)に使う値を作る"""
import numpy as np
from sklearn.decomposition import PCA

from scenarios.feature_sets import build_feature_sets
from scenarios.scenario_runner import NORMAL_STATE, ScenarioRunner
from scenarios.training_data import TrainingData

MAX_POINTS = 600
HISTOGRAM_BINS = 30


def _groups_of(data: TrainingData) -> dict:
    """グループ名(normal と、各ラベル)ごとの入力を返す"""
    groups = {NORMAL_STATE: data.normal_x}
    for label in sorted(set(data.labels)):
        groups[str(label)] = data.labeled_x[data.labels == label]
    return groups


def scatter_data(runner: ScenarioRunner, data: TrainingData, seed: int = 0) -> dict:
    """分類器に入る特徴量を、PCAで2次元にした点を返す(サブタイプは、状態ごとのクラスタ番号)"""
    # 1. グループごとに、分類器が見る特徴量を作る(AEを使うシナリオなら、圧縮後など)
    input_name = runner.input_of("svm")
    features = {group: build_feature_sets(x, runner.autoencoder)[input_name]
                for group, x in _groups_of(data).items()}

    # 2. 全グループをまとめて2次元に落とす(特徴量が1つなら、縦は0)
    stacked = np.vstack(list(features.values()))
    components = min(2, stacked.shape[1])
    pca = PCA(n_components=components).fit(stacked)
    projected = {group: pca.transform(values) for group, values in features.items()}

    # 3. 点にまとめ、多すぎるときは、同じ割合で間引く
    points = []
    for group, values in projected.items():
        subtypes = runner.clusterings[group].predict(features[group]) if group in runner.clusterings else [None] * len(values)
        for coordinates, subtype in zip(values, subtypes):
            points.append({"x": float(coordinates[0]), "y": float(coordinates[1]) if components > 1 else 0.0,
                           "group": group, "subtype": subtype})
    total = len(points)
    if total > MAX_POINTS:
        keep = np.random.default_rng(seed).choice(total, MAX_POINTS, replace=False)
        points = [points[index] for index in sorted(keep)]
    return {
        "input": input_name, "total_points": total, "shown_points": len(points), "points": points,
        "explained_variance_ratio": [float(ratio) for ratio in pca.explained_variance_ratio_],
    }


def error_distribution(runner: ScenarioRunner, data: TrainingData) -> dict:
    """グループごとの再構成誤差の分布(各区間の割合)と、乖離の閾値を返す"""
    # 1. オートエンコーダーを使わないシナリオには、誤差が無い
    if runner.autoencoder is None:
        raise ValueError("このシナリオはオートエンコーダーを使わないため、誤差の分布はありません")

    # 2. グループごとの誤差を出し、外れ値で区間が潰れないよう、上位1%を超える値は最後の区間に入れる
    errors = {group: runner.autoencoder.reconstruction_error(x) for group, x in _groups_of(data).items()}
    upper = float(np.percentile(np.concatenate(list(errors.values())), 99))
    upper = max(upper, runner.autoencoder.anomaly_threshold, 1e-9)
    edges = np.linspace(0, upper, HISTOGRAM_BINS + 1)

    # 3. 区間ごとの割合(グループの件数が違っても比べられるようにする)
    ratios = {}
    for group, values in errors.items():
        counts, _ = np.histogram(np.clip(values, 0, upper), bins=edges)
        ratios[group] = [float(count) / len(values) for count in counts]
    return {"threshold": float(runner.autoencoder.anomaly_threshold),
            "bin_edges": [float(edge) for edge in edges], "ratios": ratios,
            "counts": {group: len(values) for group, values in errors.items()}}


def data_summary(data: TrainingData) -> dict:
    """件数と、特徴量ごとの平均・標準偏差をグループごとに返す(次元数は問わない)"""
    groups = _groups_of(data)
    return {
        "normal_count": len(data.normal_x), "labeled_count": len(data.labeled_x),
        "feature_count": int(data.labeled_x.shape[1]),
        "counts": {group: len(values) for group, values in groups.items()},
        "features": {group: {"mean": values.mean(axis=0).tolist(), "std": values.std(axis=0).tolist()}
                     for group, values in groups.items()},
    }

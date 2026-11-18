"""シナリオの良し悪しを比べるための指標"""
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, silhouette_score


def compute_metrics(predictions: list, test_labels, normal_predictions: list,
                    cluster_features_by_label: dict) -> dict:
    # 1. 状態判定の正解率とF1(「normal」と判定されたものは不正解になる)
    predicted_states = [prediction["state"] for prediction in predictions]
    metrics = {
        "accuracy": float(accuracy_score(test_labels, predicted_states)),
        "macro_f1": float(f1_score(test_labels, predicted_states, average="macro")),
    }

    # 2. 乖離の検出率と、通常時の誤検出率
    metrics["anomaly_detection_rate"] = _rate(
        [prediction["state"] != "normal" for prediction in predictions]
    )
    metrics["normal_false_alarm_rate"] = _rate(
        [prediction["state"] != "normal" for prediction in normal_predictions]
    )

    # 3. サブタイプの分かれ具合(シルエット係数の平均。2クラスタ未満は除く)
    silhouettes = [
        silhouette_score(features, clusters)
        for features, clusters in cluster_features_by_label.values()
        if len(set(clusters)) >= 2
    ]
    metrics["cluster_silhouette"] = float(np.mean(silhouettes)) if silhouettes else None
    return metrics


def _rate(flags: list) -> float:
    return float(np.mean(flags)) if flags else 0.0

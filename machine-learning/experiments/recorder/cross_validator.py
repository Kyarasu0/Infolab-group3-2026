"""分割ごとに学習・評価を行い、指標の平均と標準偏差を出す"""
import time

import numpy as np

from experiments.recorder.data_splitter import split_data
from scenarios.scenario_runner import ScenarioRunner
from scenarios.training_data import TrainingData


def cross_validate(scenario: dict, plan: dict, data: TrainingData, on_epoch=None) -> dict:
    # 1. 分割ごとに、シナリオを学習して評価する
    started_at = time.perf_counter()
    folds = []
    for fold_number, (train, test) in enumerate(split_data(data, plan), start=1):
        runner = ScenarioRunner(scenario)
        runner.fit(train, on_epoch)
        folds.append({"fold": fold_number, "metrics": runner.evaluate(test)})

    # 2. 指標ごとに、平均と標準偏差をまとめる
    return {
        "folds": folds,
        "summary": summarize_metrics([fold["metrics"] for fold in folds]),
        "seconds": round(time.perf_counter() - started_at, 2),
    }


def summarize_metrics(metrics_per_fold: list) -> dict:
    summary = {}
    for name in metrics_per_fold[0]:
        # 値が無い(None)foldは、平均から除く
        values = [metrics[name] for metrics in metrics_per_fold if metrics[name] is not None]
        summary[name] = (
            {"mean": float(np.mean(values)), "std": float(np.std(values))} if values else None
        )
    return summary

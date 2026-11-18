"""評価計画に従って、データを学習用と評価用に分ける

TODO: 人・日ごとのグループ(group_id)を同じfoldに入れる分割は、データ形式が決まってから対応する
"""
from collections import Counter

from sklearn.model_selection import KFold, StratifiedKFold

from scenarios.training_data import TrainingData


def split_data(data: TrainingData, plan: dict):
    """(学習データ, 評価データ)の組を、順に返す"""
    # 1. holdout は、1回だけ分ける
    if plan["method"] == "holdout":
        yield data.split(plan["test_ratio"], plan["seed"])
        return

    # 2. kfold は、通常データとラベル付きデータを別々にk分割して、同じ番号どうしを組にする
    normal_folds = _kfold_indices(len(data.normal_x), plan, labels=None)
    labeled_folds = _kfold_indices(len(data.labeled_x), plan, labels=data.labels)
    for (normal_train, normal_test), (labeled_train, labeled_test) in zip(normal_folds, labeled_folds):
        yield (
            TrainingData(data.normal_x[normal_train], data.labeled_x[labeled_train], data.labels[labeled_train]),
            TrainingData(data.normal_x[normal_test], data.labeled_x[labeled_test], data.labels[labeled_test]),
        )


def _kfold_indices(row_count: int, plan: dict, labels) -> list:
    k = plan["k"]

    # 1. ラベルがある側は、層化の指定があればラベルの比率をそろえる
    if labels is not None and plan.get("stratified", True):
        smallest_class_count = min(Counter(labels).values())
        if k > smallest_class_count:
            raise ValueError(f"k={k} が、最も少ないラベルのサンプル数({smallest_class_count})より大きいです")
        splitter = StratifiedKFold(n_splits=k, shuffle=True, random_state=plan["seed"])
        return list(splitter.split(range(row_count), labels))

    # 2. それ以外は、シャッフルして分ける
    if k > row_count:
        raise ValueError(f"k={k} が、サンプル数({row_count})より大きいです")
    return list(KFold(n_splits=k, shuffle=True, random_state=plan["seed"]).split(range(row_count)))

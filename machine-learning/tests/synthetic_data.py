"""テスト用の合成データ(実データの代わり。次元数は引数で変えられる)"""
import numpy as np

from scenarios.training_data import TrainingData


def make_training_data(feature_count=8, seed=0) -> TrainingData:
    rng = np.random.default_rng(seed)

    # 1. 通常時: 原点まわりの小さなゆらぎ
    normal_x = rng.normal(0, 1, (200, feature_count))

    # 2. ストレス・疲労: 通常から外れ、それぞれ別の方向にずれる(各2タイプ)
    shifts = {"stress": [4.0, 7.0], "fatigue": [-4.0, -7.0]}
    labeled_parts, labels = [], []
    for label, offsets in shifts.items():
        for offset in offsets:
            part = rng.normal(0, 1, (40, feature_count))
            part[:, : feature_count // 2] += offset
            labeled_parts.append(part)
            labels += [label] * 40
    return TrainingData(normal_x, np.vstack(labeled_parts), np.array(labels))

"""学習・評価に使うデータのまとまり(次元数は問わない)"""
from dataclasses import dataclass

import numpy as np

from models.common import as_2d_array


@dataclass
class TrainingData:
    normal_x: np.ndarray    # 通常時のタイピング(オートエンコーダーの学習用)
    labeled_x: np.ndarray   # ラベル付きデータ(SVM・クラスタリングの学習用)
    labels: np.ndarray      # labeled_x の状態ラベル(例: "stress", "fatigue")

    @classmethod
    def from_npz(cls, npz_path) -> "TrainingData":
        # 1. npzから、3つの配列を読み込む
        with np.load(npz_path, allow_pickle=False) as saved:
            return cls(
                normal_x=as_2d_array(saved["normal_x"]),
                labeled_x=as_2d_array(saved["labeled_x"]),
                labels=saved["labels"].astype(str),
            )

    def split(self, test_ratio: float, seed: int):
        """学習用と評価用に分けて、(学習データ, 評価データ)を返す"""
        # 1. 通常データとラベル付きデータを、それぞれシャッフルして分ける
        rng = np.random.default_rng(seed)
        normal_train, normal_test = _split_rows(len(self.normal_x), test_ratio, rng)
        labeled_train, labeled_test = _split_rows(len(self.labeled_x), test_ratio, rng)

        # 2. 2つのTrainingDataにまとめる
        train = TrainingData(
            self.normal_x[normal_train],
            self.labeled_x[labeled_train],
            self.labels[labeled_train],
        )
        test = TrainingData(
            self.normal_x[normal_test],
            self.labeled_x[labeled_test],
            self.labels[labeled_test],
        )
        return train, test


def _split_rows(row_count: int, test_ratio: float, rng) -> tuple:
    order = rng.permutation(row_count)
    test_count = max(1, int(row_count * test_ratio))
    return order[test_count:], order[:test_count]

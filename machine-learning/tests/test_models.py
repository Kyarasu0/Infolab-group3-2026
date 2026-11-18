import numpy as np
import pytest

from models.autoencoder.autoencoder import Autoencoder, build_layer_sizes
from models.clustering.clustering_model import ClusteringModel
from models.common import as_2d_array, load_json
from models.svm.svm_classifier import SvmClassifier
from tests.synthetic_data import make_training_data


@pytest.mark.parametrize("feature_count", [1, 3, 8, 30])
def test_autoencoderは任意の次元数で学習と予測ができる(feature_count):
    data = make_training_data(feature_count)
    params = {**load_json("models/autoencoder/autoencoder.json"), "epochs": 3}
    autoencoder = Autoencoder(params)
    autoencoder.fit(data.normal_x)
    assert autoencoder.reconstruct(data.normal_x[:5]).shape == (5, feature_count)
    assert autoencoder.encode(data.normal_x[:5]).shape[1] <= feature_count


def test_層の大きさは入力から圧縮次元まで小さくなる():
    assert build_layer_sizes(16, 2, 2) == [16, 8, 4, 2]
    assert build_layer_sizes(3, 10, 1) == [3, 3, 3]


def test_autoencoderは異常データの誤差が通常より大きい():
    data = make_training_data()
    autoencoder = Autoencoder({**load_json("models/autoencoder/autoencoder.json"), "epochs": 30})
    autoencoder.fit(data.normal_x)
    assert autoencoder.reconstruction_error(data.labeled_x).mean() > \
        autoencoder.reconstruction_error(data.normal_x).mean()


def test_autoencoderは保存して読み込んでも同じ結果になる(tmp_path):
    data = make_training_data()
    autoencoder = Autoencoder({**load_json("models/autoencoder/autoencoder.json"), "epochs": 3})
    autoencoder.fit(data.normal_x)
    autoencoder.save(tmp_path)
    loaded = Autoencoder.load(tmp_path)
    assert np.allclose(autoencoder.encode(data.normal_x), loaded.encode(data.normal_x), atol=1e-5)


def test_配列の次元をそろえられる():
    assert as_2d_array([1, 2, 3]).shape == (1, 3)
    assert as_2d_array(np.zeros((4, 5, 6))).shape == (4, 30)


def test_svmとクラスタリングは任意の次元で動く(tmp_path):
    data = make_training_data(5)
    svm = SvmClassifier()
    svm.fit(data.labeled_x, data.labels)
    svm.save(tmp_path / "svm.joblib")
    assert set(SvmClassifier.load(tmp_path / "svm.joblib").predict(data.labeled_x)) <= {"stress", "fatigue"}
    clustering = ClusteringModel()
    clustering.fit(data.labeled_x)
    assert len(clustering.predict(data.labeled_x)) == len(data.labeled_x)

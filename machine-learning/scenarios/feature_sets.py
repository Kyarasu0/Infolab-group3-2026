"""オートエンコーダーの出力から、後段のモデルに渡す特徴量を作る"""
import numpy as np

from models.common import as_2d_array

FEATURE_NAMES = ("raw", "latent", "decoded", "residual", "latent_and_residual")
AUTOENCODER_FEATURE_NAMES = FEATURE_NAMES[1:]


def build_feature_sets(x, autoencoder=None) -> dict:
    """利用できる特徴量を、名前つきの辞書で返す(AEが無ければ raw のみ)"""
    # 1. 元の入力は、いつでも使える
    raw = as_2d_array(x)
    feature_sets = {"raw": raw}
    if autoencoder is None:
        return feature_sets

    # 2. AEが後ろの段にあるときは、圧縮後・復号後・残差も使える
    latent = autoencoder.encode(raw)
    decoded = autoencoder.decode(latent)
    residual = raw - decoded
    feature_sets["latent"] = latent
    feature_sets["decoded"] = decoded
    feature_sets["residual"] = residual
    feature_sets["latent_and_residual"] = np.hstack([latent, residual])
    return feature_sets

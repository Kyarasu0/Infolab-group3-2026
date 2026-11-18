"""通常時のデータを学習し、そこからの乖離(再構成誤差)を測るオートエンコーダー

入力の次元数は fit() に渡したデータから自動で決まる。
パラメータは autoencoder.json(またはシナリオの上書き値)で指定する。
"""
from pathlib import Path

import numpy as np
import torch
from torch import nn

from models.common import as_2d_array, load_json, save_json

DEFAULT_PARAMS_PATH = Path(__file__).with_name("autoencoder.json")


def build_layer_sizes(input_dim: int, latent_dim: int, hidden_layers: int) -> list:
    """入力次元から圧縮次元まで、等比で小さくなる層の大きさを返す"""
    # 1. 圧縮次元は入力次元を超えられないので、範囲に収める
    latent_dim = max(1, min(latent_dim, input_dim))

    # 2. 入力と圧縮の間に、hidden_layers 個の中間層を等比で置く
    sizes = np.geomspace(input_dim, latent_dim, hidden_layers + 2)
    return [max(1, int(round(size))) for size in sizes]


def build_mlp(layer_sizes: list) -> nn.Sequential:
    # 1. 層ごとに「全結合 + ReLU」を並べる(最後の層だけ活性化なし)
    layers = []
    for index in range(len(layer_sizes) - 1):
        layers.append(nn.Linear(layer_sizes[index], layer_sizes[index + 1]))
        if index < len(layer_sizes) - 2:
            layers.append(nn.ReLU())
    return nn.Sequential(*layers)


def _describe_layer(part: str, number: int, layer: nn.Module, include_values: bool) -> dict:
    # 活性化など、学習する値を持たない層は、種類だけ返す
    description = {"layer_number": number, "part": part, "type": type(layer).__name__}
    if not isinstance(layer, nn.Linear):
        description["parameter_count"] = 0
        return description

    # 全結合層は、重み(行列)とバイアスの形・個数・値の統計を返す
    description.update({"in_features": layer.in_features, "out_features": layer.out_features})
    description["parameter_count"] = sum(p.numel() for p in layer.parameters())
    for name, tensor in (("weight", layer.weight), ("bias", layer.bias)):
        values = tensor.detach().numpy()
        description[name] = {
            "shape": list(values.shape),
            "count": int(values.size),
            "mean": float(values.mean()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
        }
        if include_values:
            description[name]["values"] = values.tolist()
    return description


class Autoencoder:
    def __init__(self, params: dict = None):
        # 1. 引数が無ければ、既定のJSONを使う
        self.params = params or load_json(DEFAULT_PARAMS_PATH)
        self.layer_sizes = None
        self.encoder = None
        self.decoder = None
        self.mean = None
        self.std = None
        self.anomaly_threshold = None
        self.loss_history = []

    def fit(self, normal_x, on_epoch=None) -> list:
        # 1. 入力を2次元にそろえ、特徴量ごとに標準化する
        x = as_2d_array(normal_x)
        self.mean = x.mean(axis=0)
        self.std = np.where(x.std(axis=0) < 1e-8, 1.0, x.std(axis=0))
        scaled_x = torch.tensor((x - self.mean) / self.std, dtype=torch.float32)

        # 2. 入力次元に合わせて、エンコーダーとデコーダーを組み立てる
        torch.manual_seed(self.params["seed"])
        sizes = build_layer_sizes(
            x.shape[1], self.params["latent_dim"], self.params["hidden_layers"]
        )
        self.layer_sizes = sizes
        self.encoder = build_mlp(sizes)
        self.decoder = build_mlp(sizes[::-1])

        # 3. ミニバッチで学習し、エポックごとの損失を記録する
        self.loss_history = self._train(scaled_x, on_epoch)

        # 4. 通常データの誤差から、乖離とみなす閾値を決める
        errors = self.reconstruction_error(x)
        self.anomaly_threshold = float(
            np.percentile(errors, self.params["anomaly_percentile"])
        )
        return self.loss_history

    def encode(self, x) -> np.ndarray:
        # 1. 標準化して、圧縮ベクトルを返す
        return self._run(self.encoder, self._scale(as_2d_array(x)))

    def decode(self, latent) -> np.ndarray:
        # 1. 圧縮ベクトルを復号し、元のスケールに戻す
        decoded = self._run(self.decoder, np.asarray(latent, dtype=np.float64))
        return decoded * self.std + self.mean

    def reconstruct(self, x) -> np.ndarray:
        return self.decode(self.encode(x))

    def residual(self, x) -> np.ndarray:
        # 元の値と復号後の値の差(どの特徴量がズレたかが分かる)
        return as_2d_array(x) - self.reconstruct(x)

    def reconstruction_error(self, x) -> np.ndarray:
        # 標準化したスケールでの二乗誤差の平均(サンプルごとに1つ)
        return ((self.residual(x) / self.std) ** 2).mean(axis=1)

    def is_anomalous(self, x) -> np.ndarray:
        return self.reconstruction_error(x) >= self.anomaly_threshold

    def describe(self, include_values: bool = False) -> dict:
        """各層の構成とパラメータ量を返す(include_values=True で値そのものも含める)"""
        # 1. エンコーダーとデコーダーの層を、順番に説明する
        layers = []
        for part, network in (("encoder", self.encoder), ("decoder", self.decoder)):
            for layer in network:
                layers.append(_describe_layer(part, len(layers) + 1, layer, include_values))

        # 2. 全体のパラメータ数と、入力・圧縮の次元をまとめる
        return {
            "model": "autoencoder",
            "input_dim": self.layer_sizes[0],
            "latent_dim": self.layer_sizes[-1],
            "layer_sizes": self.layer_sizes,
            "total_parameters": sum(layer["parameter_count"] for layer in layers),
            "anomaly_threshold": self.anomaly_threshold,
            "hyperparameters": self.params,
            "layers": layers,
        }

    def save(self, directory) -> None:
        # 1. 重みとメタ情報を、フォルダに保存する
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        torch.save(
            {"encoder": self.encoder.state_dict(), "decoder": self.decoder.state_dict()},
            directory / "weights.pt",
        )
        save_json(
            {
                "params": self.params,
                "layer_sizes": self.layer_sizes,
                "mean": self.mean.tolist(),
                "std": self.std.tolist(),
                "anomaly_threshold": self.anomaly_threshold,
                "loss_history": self.loss_history,
            },
            directory / "meta.json",
        )

    @classmethod
    def load(cls, directory) -> "Autoencoder":
        # 1. メタ情報から、同じ形のネットワークを組み立てて重みを読む
        directory = Path(directory)
        meta = load_json(directory / "meta.json")
        model = cls(meta["params"])
        sizes = meta["layer_sizes"]
        model.layer_sizes = sizes
        model.encoder = build_mlp(sizes)
        model.decoder = build_mlp(sizes[::-1])
        weights = torch.load(directory / "weights.pt", weights_only=True)
        model.encoder.load_state_dict(weights["encoder"])
        model.decoder.load_state_dict(weights["decoder"])
        model.mean = np.array(meta["mean"])
        model.std = np.array(meta["std"])
        model.anomaly_threshold = meta["anomaly_threshold"]
        model.loss_history = meta["loss_history"]
        return model

    def _scale(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std

    def _run(self, network: nn.Sequential, values: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            tensor = torch.tensor(values, dtype=torch.float32)
            return network(tensor).numpy().astype(np.float64)

    def _train(self, scaled_x: torch.Tensor, on_epoch) -> list:
        parameters = list(self.encoder.parameters()) + list(self.decoder.parameters())
        optimizer = torch.optim.Adam(parameters, lr=self.params["learning_rate"])
        loss_function = nn.MSELoss()
        batch_size = self.params["batch_size"]
        history = []

        for epoch in range(self.params["epochs"]):
            order = torch.randperm(scaled_x.shape[0])
            epoch_loss = 0.0
            for start in range(0, len(order), batch_size):
                batch = scaled_x[order[start:start + batch_size]]
                loss = loss_function(self.decoder(self.encoder(batch)), batch)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * len(batch)
            history.append(epoch_loss / len(order))
            if on_epoch:
                on_epoch("autoencoder", epoch + 1, history[-1])
        return history

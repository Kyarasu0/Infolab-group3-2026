"""バックエンドの設定(環境変数で上書きできる)"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 学習済みモデルと結果の保存先
ARTIFACTS_DIR = Path(os.environ.get("ML_ARTIFACTS_DIR", PROJECT_ROOT / "artifacts"))

# 学習用データ(npz: normal_x, labeled_x, labels)
TRAINING_DATA_PATH = Path(
    os.environ.get("ML_TRAINING_DATA", PROJECT_ROOT / "data" / "training_data.npz")
)

# 起動時のモード("train" か "predict")と、予測で使う既定のシナリオ
INITIAL_MODE = os.environ.get("ML_MODE", "train")
DEFAULT_SCENARIO = os.environ.get("ML_DEFAULT_SCENARIO", "01-latent-to-svm")

# フロントエンドの開発サーバーなど、アクセスを許可する送信元
ALLOWED_ORIGINS = os.environ.get("ML_ALLOWED_ORIGINS", "http://localhost:5173").split(",")

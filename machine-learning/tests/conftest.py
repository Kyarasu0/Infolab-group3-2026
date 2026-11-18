"""テスト共通の設定(machine-learning/ と 2-Backend/ をimportできるようにする)"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "2-Backend"))

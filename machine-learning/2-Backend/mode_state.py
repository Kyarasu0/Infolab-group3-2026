"""学習モード / 予測モードの状態を持つ"""
import threading

MODES = ("train", "predict")


class ModeState:
    def __init__(self, initial_mode: str):
        self._lock = threading.Lock()
        self._mode = self._validated(initial_mode)

    @property
    def mode(self) -> str:
        return self._mode

    def change(self, new_mode: str) -> None:
        with self._lock:
            self._mode = self._validated(new_mode)

    @staticmethod
    def _validated(mode: str) -> str:
        if mode not in MODES:
            raise ValueError(f"モードは {MODES} のどちらかです: {mode}")
        return mode

"""学習などの重い処理を別スレッドで動かし、進捗をフロントに見せるための記録"""
import threading


class JobAlreadyRunningError(Exception):
    pass


class JobTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._status = {"state": "idle"}

    def status(self) -> dict:
        with self._lock:
            return {**self._status, "autoencoder_loss": list(self._status.get("autoencoder_loss", []))}

    def is_running(self) -> bool:
        return self._status["state"] == "running"

    def start(self, kind: str, scenario: str, work) -> None:
        """work(on_epoch) を別スレッドで実行する。同時に1つだけ"""
        # 1. 実行中なら受け付けない
        with self._lock:
            if self._status["state"] == "running":
                raise JobAlreadyRunningError("別の処理を実行中です")
            self._status = {"state": "running", "kind": kind, "scenario": scenario,
                            "epoch": 0, "autoencoder_loss": []}

        # 2. 別スレッドで実行し、結果かエラーを記録する
        threading.Thread(target=self._run, args=(work,), daemon=True).start()

    def _on_epoch(self, model_name: str, epoch: int, loss: float) -> None:
        # 学習曲線を1エポックずつ追記する(比較中は、シナリオをまたいで追記される)
        with self._lock:
            self._status["epoch"] = epoch
            self._status["autoencoder_loss"].append(loss)

    def _run(self, work) -> None:
        try:
            result = work(self._on_epoch)
            with self._lock:
                self._status.update(state="finished", result=result)
        except Exception as error:  # 失敗の理由を、画面から見られるようにする
            with self._lock:
                self._status.update(state="failed", error=str(error))

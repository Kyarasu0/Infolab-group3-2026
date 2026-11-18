"""機械学習バックエンドの入口(フロントエンドと、通知用バックエンドの両方から呼ばれる)

起動(machine-learning/ で実行):
    PYTHONPATH=. .venv/bin/uvicorn main:app --app-dir 2-Backend --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import prediction_service
import training_service
from backend_settings import ALLOWED_ORIGINS, INITIAL_MODE
from job_tracker import JobAlreadyRunningError, JobTracker
from mode_state import ModeState
from schemas import ModeRequest, PredictRequest, TrainRequest

app = FastAPI(title="Typing fatigue/stress ML backend")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])
mode_state = ModeState(INITIAL_MODE)
job_tracker = JobTracker()


def _require_mode(required_mode: str) -> None:
    # 現在のモードでは使えないAPIを、409で断る
    if mode_state.mode != required_mode:
        raise HTTPException(409, f"このAPIは {required_mode} モードでのみ使えます(現在: {mode_state.mode})")


def _start_job(kind: str, scenario: str, work) -> dict:
    try:
        job_tracker.start(kind, scenario, work)
    except JobAlreadyRunningError as error:
        raise HTTPException(409, str(error))
    return {"started": True, "kind": kind, "scenario": scenario}


# --- 状態・モード ---
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": mode_state.mode}


@app.get("/mode")
def get_mode() -> dict:
    return {"mode": mode_state.mode}


@app.put("/mode")
def change_mode(request: ModeRequest) -> dict:
    # 処理の最中は切り替えない
    if job_tracker.is_running():
        raise HTTPException(409, "学習などの実行中は、モードを変えられません")
    try:
        mode_state.change(request.mode)
    except ValueError as error:
        raise HTTPException(422, str(error))
    return {"mode": mode_state.mode}


# --- 学習モード(フロントエンド向け) ---
@app.get("/scenarios")
def list_scenarios() -> list:
    return training_service.list_scenarios()


@app.get("/scenarios/{name}/result")
def get_result(name: str) -> dict:
    return _read_file(name, "result.json")


@app.get("/scenarios/{name}/architecture")
def get_architecture(name: str) -> dict:
    return _read_file(name, "architecture.json")


@app.post("/train", status_code=202)
def train(request: TrainRequest) -> dict:
    _require_mode("train")

    def work(on_epoch):
        result = training_service.train_scenario(request.scenario, on_epoch)
        prediction_service.forget_runner(request.scenario)
        return result

    return _start_job("train", request.scenario, work)


@app.post("/compare", status_code=202)
def compare() -> dict:
    _require_mode("train")

    def work(on_epoch):
        results = training_service.compare_all(on_epoch)
        for result in results:
            prediction_service.forget_runner(result["scenario"])
        return results

    return _start_job("compare", "all", work)


@app.get("/compare/result")
def get_comparison() -> dict:
    return training_service.read_comparison()


@app.get("/jobs/current")
def get_current_job() -> dict:
    return job_tracker.status()


# --- 予測モード(通知用バックエンドなど、外部から呼ばれる) ---
@app.post("/predict")
def predict(request: PredictRequest) -> dict:
    _require_mode("predict")
    try:
        return prediction_service.predict(request.samples, request.scenario)
    except KeyError as error:
        raise HTTPException(404, str(error.args[0]))
    except FileNotFoundError as error:
        raise HTTPException(409, str(error))
    except ValueError as error:
        raise HTTPException(400, str(error))


def _read_file(name: str, file_name: str) -> dict:
    try:
        return training_service.read_scenario_file(name, file_name)
    except FileNotFoundError as error:
        raise HTTPException(404, str(error))

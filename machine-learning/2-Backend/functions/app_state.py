"""アプリ全体で1つだけ持つ状態(モード・実行中の処理)と、処理を始める関数"""
from fastapi import HTTPException

from functions.backend_settings import INITIAL_MODE
from functions.job_tracker import JobAlreadyRunningError, JobTracker
from functions.mode_state import ModeState

mode_state = ModeState(INITIAL_MODE)
job_tracker = JobTracker()


def start_job(kind: str, scenario: str, work) -> dict:
    # 1. 別スレッドで始める。実行中なら409で断る
    try:
        job_tracker.start(kind, scenario, work)
    except JobAlreadyRunningError as error:
        raise HTTPException(409, str(error))
    return {"status": "started", "kind": kind, "scenario": scenario}

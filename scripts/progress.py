import threading

_lock = threading.Lock()

progress_data = {
    "processed": 0,
    "total": 1,
    "errors": 0,
    "phase": "idle",
    "phase_detail": "",
    "log": [],
}

MAX_LOG_ENTRIES = 200


def set_progress(processed, total, errors, phase=None, phase_detail=None):
    with _lock:
        updates = {"processed": processed, "total": total, "errors": errors}
        if phase is not None:
            updates["phase"] = phase
        if phase_detail is not None:
            updates["phase_detail"] = phase_detail
        progress_data.update(updates)
    print(f"Progress updated: {processed}/{total} (errors: {errors}, phase: {progress_data['phase']})")


def add_log(message):
    with _lock:
        progress_data["log"].append(message)
        if len(progress_data["log"]) > MAX_LOG_ENTRIES:
            progress_data["log"] = progress_data["log"][-MAX_LOG_ENTRIES:]


def get_progress():
    with _lock:
        return progress_data.copy()


def reset_progress():
    global progress_data  # noqa: F824
    with _lock:
        progress_data = {
            "processed": 0,
            "total": 1,
            "errors": 0,
            "phase": "idle",
            "phase_detail": "",
            "log": [],
        }

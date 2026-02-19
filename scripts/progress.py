import time

progress_data = {
    "processed": 0,
    "total": 1,
    "errors": 0,
    "status": "idle",
    "phase": "idle",
    "phase_detail": "",
    "started_at": None,
}

def set_progress(processed, total, errors, status=None, phase=None, phase_detail=None):
    global progress_data
    progress_data = {
        "processed": processed,
        "total": total,
        "errors": errors,
        "status": status or ("completed" if processed >= total and phase != "error" else "running"),
        "phase": phase or progress_data.get("phase", "idle"),
        "phase_detail": phase_detail if phase_detail is not None else progress_data.get("phase_detail", ""),
        "started_at": progress_data.get("started_at"),
    }
    print(f"Progress updated: {processed}/{total} (errors: {errors}, phase: {progress_data['phase']}, detail: {progress_data['phase_detail']})")

def get_progress():
    return progress_data.copy()

def reset_progress():
    global progress_data
    progress_data = {
        "processed": 0,
        "total": 1,
        "errors": 0,
        "status": "idle",
        "phase": "idle",
        "phase_detail": "",
        "started_at": time.time(),
    }

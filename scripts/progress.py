import time
from collections import deque

progress_data = {
    "processed": 0,
    "total": 1,
    "errors": 0,
    "status": "idle",
    "phase": 0,
    "phase_name": "idle",
    "phase_message": "",
    "recent_items": [],
    "error_details": [],
    "start_time": None,
}

_recent_items = deque(maxlen=5)
_error_details = deque(maxlen=5)


def set_progress(processed, total, errors, status=None, phase=None, phase_name=None, phase_message=None):
    global progress_data
    progress_data = {
        "processed": processed,
        "total": total,
        "errors": errors,
        "status": status or ("completed" if processed >= total and total > 0 else "running"),
        "phase": phase if phase is not None else progress_data.get("phase", 0),
        "phase_name": phase_name or progress_data.get("phase_name", ""),
        "phase_message": phase_message or progress_data.get("phase_message", ""),
        "recent_items": list(_recent_items),
        "error_details": list(_error_details),
        "start_time": progress_data.get("start_time"),
    }
    print(f"Progress updated: {processed}/{total} (errors: {errors}, phase: {progress_data['phase_name']}, status: {progress_data['status']})")


def set_phase(phase, phase_name, phase_message):
    global progress_data
    progress_data["phase"] = phase
    progress_data["phase_name"] = phase_name
    progress_data["phase_message"] = phase_message
    print(f"Phase changed: {phase} - {phase_name}: {phase_message}")


def add_recent_item(item_name):
    _recent_items.append(item_name)
    progress_data["recent_items"] = list(_recent_items)


def add_error_detail(error_msg):
    _error_details.append(error_msg)
    progress_data["error_details"] = list(_error_details)


def get_progress():
    return progress_data.copy()


def reset_progress():
    global progress_data
    _recent_items.clear()
    _error_details.clear()
    progress_data = {
        "processed": 0,
        "total": 1,
        "errors": 0,
        "status": "idle",
        "phase": 0,
        "phase_name": "idle",
        "phase_message": "",
        "recent_items": [],
        "error_details": [],
        "start_time": time.time(),
    }

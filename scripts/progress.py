progress_data = {
    "processed": 0,
    "total": 1,
    "errors": 0,
    "status": "idle",
    "phase": "idle",
    "message": "Ready to start",
}

PHASES = ["scraping_urls", "extracting", "writing", "completed"]

def set_progress(processed, total, errors, phase=None, message=None, status=None):
    global progress_data
    if phase is None:
        if processed >= total and total > 0:
            phase = "completed"
        else:
            phase = progress_data.get("phase", "extracting")
    if status is None:
        status = "completed" if phase == "completed" else "running"
    progress_data = {
        "processed": processed,
        "total": total,
        "errors": errors,
        "status": status,
        "phase": phase,
        "message": message or progress_data.get("message", ""),
    }
    print(f"Progress updated: {processed}/{total} (errors: {errors}, phase: {phase}, status: {status})")

def set_phase(phase, message, status=None):
    global progress_data
    progress_data["phase"] = phase
    progress_data["message"] = message
    if status is None:
        status = "completed" if phase == "completed" else "running"
    progress_data["status"] = status
    print(f"Phase changed: {phase} - {message}")

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
        "message": "Ready to start",
    }

progress_data = {"processed": 0, "total": 1, "errors": 0, "status": "idle"}

def set_progress(processed, total, errors, status=None):
    """Thread-safe progress update"""
    global progress_data
    progress_data = {
        "processed": processed, 
        "total": total, 
        "errors": errors,
        "status": status or ("completed" if processed >= total else "running")
    }
    print(f"Progress updated: {processed}/{total} (errors: {errors}, status: {progress_data['status']})")

def get_progress():
    return progress_data.copy()

def reset_progress():
    """Reset progress to initial state"""
    global progress_data
    progress_data = {"processed": 0, "total": 1, "errors": 0, "status": "idle"}
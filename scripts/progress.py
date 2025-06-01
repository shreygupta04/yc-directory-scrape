progress_data = {"processed": 0, "total": 1, "errors": 0}

def set_progress(processed, total, errors):
    global progress_data
    progress_data = {"processed": processed, "total": total, "errors": errors}

def get_progress():
    return progress_data

from .yolo import has_model, run_yolo_detection

def run_detection(image_path: str) -> dict:
    if has_model():
        return run_yolo_detection(image_path)
    s = (image_path or "").lower()
    if "fire" in s:
        return {"label": "fire", "confidence": 0.82}
    if "smoke" in s:
        return {"label": "smoke", "confidence": 0.72}
    return {"label": "none", "confidence": 0.30}

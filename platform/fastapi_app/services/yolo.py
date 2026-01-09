from __future__ import annotations
from typing import Optional, Dict
import torch
from ..core.config import settings

_model = None
_names: Optional[Dict[int, str]] = None

def _try_import():
    try:
        from ultralytics import YOLO  # type: ignore
        return YOLO
    except Exception:
        return None

def get_model():
    global _model, _names
    if _model is not None:
        return _model
    YOLO = _try_import()
    if YOLO is None:
        return None
    # Use the resolved model path
    path = settings.get_model_path() or "yolov8n.pt"
    try:
        _model = YOLO(path)
        # names mapping available on model.model.names in ultralytics
        try:
            _names = getattr(getattr(_model, "model", None), "names", None)
        except Exception:
            _names = None
        return _model
    except Exception:
        return None

def has_model() -> bool:
    return get_model() is not None

def get_names() -> Dict[int, str]:
    get_model()
    return _names or {}

def warmup():
    m = get_model()
    if m is None:
        return False
    try:
        import numpy as np
        img = np.zeros((settings.IMGSZ, settings.IMGSZ, 3), dtype=np.uint8)
        _ = m.predict(img, conf=settings.CONF_THRESHOLD, device=(settings.DEVICE or ("mps" if torch.backends.mps.is_available() else "cpu")), imgsz=settings.IMGSZ, verbose=False)
        return True
    except Exception:
        return False

def run_yolo_detection(image_path: str) -> dict:
    m = get_model()
    if m is None:
        return {"label": "none", "confidence": 0.0}
    try:
        results = m.predict(
            source=image_path,
            conf=settings.CONF_THRESHOLD,
            device=(settings.DEVICE or ("mps" if torch.backends.mps.is_available() else "cpu")),
            imgsz=settings.IMGSZ,
            verbose=False,
        )
        best_label = "none"
        best_conf = 0.0
        # Iterate predictions; choose highest confidence
        for r in results:
            boxes = getattr(r, "boxes", None)
            if boxes is None:
                # try classification probabilities if present
                probs = getattr(r, "probs", None)
                if probs is not None:
                    try:
                        top_idx = int(probs.top1)
                        top_conf = float(probs.top1conf)
                        name = None
                        if _names and top_idx in _names:
                            name = _names[top_idx]
                        if top_conf > best_conf:
                            best_conf = top_conf
                            best_label = name or str(top_idx)
                    except Exception:
                        pass
                continue
            try:
                n = len(boxes)
            except Exception:
                n = 0
            if n > 0:
                try:
                    for i in range(n):
                        conf = float(boxes.conf[i].item())
                        cls = int(boxes.cls[i].item())
                        name = None
                        if _names and cls in _names:
                            name = _names[cls]
                        if conf > best_conf:
                            best_conf = conf
                            best_label = name or str(cls)
                except Exception:
                    pass
        # Map common labels to domain classes if available
        label = "none"
        l = (best_label or "").lower()
        if "fire" in l:
            label = "fire"
        elif "smoke" in l:
            label = "smoke"
        return {"label": label, "confidence": best_conf}
    except Exception:
        return {"label": "none", "confidence": 0.0}

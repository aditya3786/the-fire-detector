from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from datetime import datetime
from ..schemas import Alert, AlertCreate, AckResponse, DetectRequest, DetectResponse, DetectAlertResponse
from ..services.detection import run_detection
from ..core.config import settings
import os
import tempfile

router = APIRouter()

STORE: list[Alert] = []
COUNTER = 1

@router.get("/alerts", response_model=List[Alert])
def get_alerts():
    return STORE

@router.post("/alerts", response_model=Alert)
def create_alert(payload: AlertCreate):
    global COUNTER
    alert = Alert(
        id=COUNTER,
        timestamp=datetime.utcnow(),
        acknowledged=False,
        **payload.dict(),
    )
    STORE.insert(0, alert)
    COUNTER += 1
    return alert

@router.post("/alerts/{alert_id}/acknowledge", response_model=Alert)
def acknowledge_alert(alert_id: int):
    for a in STORE:
        if a.id == alert_id:
            a.acknowledged = True
            return a
    raise HTTPException(status_code=404, detail="Alert not found")

def _map_label_to_severity(label: str) -> str:
    if label == "fire":
        return "high"
    if label == "smoke":
        return "medium"
    return "low"

@router.post("/detect", response_model=DetectResponse)
def detect(payload: DetectRequest):
    candidate = payload.image_path or (os.path.join(settings.IMAGE_DIR, payload.filename) if payload.filename else None)
    if not candidate:
        raise HTTPException(status_code=400, detail="image_path or filename required")
    if not os.path.isfile(candidate):
        raise HTTPException(status_code=404, detail="image not found")
    res = run_detection(candidate)
    severity = _map_label_to_severity(res.get("label", ""))
    return DetectResponse(confidence=float(res.get("confidence", 0.0)), severity=severity)

@router.get("/detect/status")
def detect_status():
    from ..services.yolo import has_model
    ok = False
    try:
        ok = has_model()
    except Exception:
        ok = False
    return {
        "model_loaded": ok,
        "model_path": settings.MODEL_PATH or "yolov8n.pt",
        "device": settings.DEVICE or "cpu",
        "conf_threshold": settings.CONF_THRESHOLD,
        "imgsz": settings.IMGSZ,
    }

@router.post("/detect-and-alert", response_model=DetectAlertResponse)
def detect_and_alert(payload: DetectRequest):
    candidate = payload.image_path or (os.path.join(settings.IMAGE_DIR, payload.filename) if payload.filename else None)
    if not candidate:
        raise HTTPException(status_code=400, detail="image_path or filename required")
    if not os.path.isfile(candidate):
        raise HTTPException(status_code=404, detail="image not found")
    res = run_detection(candidate)
    severity = _map_label_to_severity(res.get("label", ""))
    confidence = float(res.get("confidence", 0.0))
    created = None
    if severity in ("high", "medium") or confidence >= settings.ALERT_CONF_THRESHOLD:
        global COUNTER
        created = Alert(
            id=COUNTER,
            timestamp=datetime.utcnow(),
            acknowledged=False,
            severity=severity,
            message=f"Detection: {res.get('label','unknown')} in {os.path.basename(candidate)}",
            confidence=confidence,
            type=res.get("label","unknown"),
            location="N/A",
        )
        STORE.insert(0, created)
        COUNTER += 1
    return DetectAlertResponse(confidence=confidence, severity=severity, alert=created)

@router.post("/detect/upload", response_model=DetectAlertResponse)
def detect_upload(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "upload")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = file.file.read()
        tmp.write(content)
        tmp_path = tmp.name
    res = run_detection(tmp_path)
    severity = _map_label_to_severity(res.get("label", ""))
    confidence = float(res.get("confidence", 0.0))
    created = None
    if severity in ("high", "medium") or confidence >= settings.ALERT_CONF_THRESHOLD:
        global COUNTER
        created = Alert(
            id=COUNTER,
            timestamp=datetime.utcnow(),
            acknowledged=False,
            severity=severity,
            message=f"Detection: {res.get('label','unknown')} in {os.path.basename(file.filename or 'upload')}",
            confidence=confidence,
            type=res.get("label","unknown"),
            location="N/A",
        )
        STORE.insert(0, created)
        COUNTER += 1
    return DetectAlertResponse(confidence=confidence, severity=severity, alert=created)

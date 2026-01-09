from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    severity: str
    message: str
    confidence: float
    type: str
    location: str

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    timestamp: datetime
    acknowledged: bool = False

    class Config:
        orm_mode = True

class AckResponse(BaseModel):
    id: int
    acknowledged: bool

class FireAlert(BaseModel):
    id: int
    severity: str
    message: str
    confidence: float
    timestamp: datetime
    acknowledged: bool

class DetectRequest(BaseModel):
    image_path: Optional[str] = None
    filename: Optional[str] = None

class DetectResponse(BaseModel):
    confidence: float
    severity: str

class DetectAlertResponse(BaseModel):
    confidence: float
    severity: str
    alert: Optional[Alert] = None

from pydantic_settings import BaseSettings
from typing import Optional, Union
import os

class Settings(BaseSettings):
    ALLOW_ORIGINS: Union[str, list[str]] = "*"
    MODEL_PATH: Optional[str] = None
    DEVICE: Optional[str] = None
    CONF_THRESHOLD: float = 0.10
    IMAGE_DIR: Optional[str] = "data/images"
    ALERT_CONF_THRESHOLD: float = 0.50
    IMGSZ: int = 512
    WARMUP: bool = True
    
    def get_allow_origins(self) -> list[str]:
        """Convert ALLOW_ORIGINS to list format"""
        if isinstance(self.ALLOW_ORIGINS, str):
            if self.ALLOW_ORIGINS == "*":
                return ["*"]
            # Split comma-separated values
            return [origin.strip() for origin in self.ALLOW_ORIGINS.split(",")]
        return self.ALLOW_ORIGINS
    
    def get_model_path(self) -> Optional[str]:
        """Resolve model path, handling relative paths and defaults"""
        if not self.MODEL_PATH:
            # Try default location
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            default_path = os.path.join(project_root, 'weights', 'best_swapped.pt')
            if os.path.exists(default_path):
                return default_path
            # Fallback to yolov8n.pt (will be downloaded by ultralytics)
            return None
        
        # If absolute path, use as is
        if os.path.isabs(self.MODEL_PATH):
            return self.MODEL_PATH if os.path.exists(self.MODEL_PATH) else None
        
        # Relative path - resolve from project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        resolved_path = os.path.join(project_root, self.MODEL_PATH)
        if os.path.exists(resolved_path):
            return resolved_path
        
        # Try default location as fallback
        default_path = os.path.join(project_root, 'weights', 'best_swapped.pt')
        if os.path.exists(default_path):
            return default_path
        
        return None

settings = Settings()

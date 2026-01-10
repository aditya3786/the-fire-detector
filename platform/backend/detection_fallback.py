"""
Fallback detection when FastAPI service is unavailable
"""
import os

def detect_image_local(image_path, filename):
    """
    Fallback detection - returns a basic response
    In production, this could use a local model or queue for processing
    """
    # For now, return a low severity result
    # This ensures the upload doesn't fail even if FastAPI is down
    return {
        'confidence': 0.15,
        'severity': 'low',
        'type': 'unknown',
        'message': f'Image uploaded: {filename} (awaiting processing)',
        'alert': None
    }

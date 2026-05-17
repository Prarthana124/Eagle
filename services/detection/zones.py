"""
services/detection/zones.py

Zone definitions are now loaded from config/zones.yaml via ZoneConfigLoader.
Set ZONES_CONFIG_PATH env var to override the default config location.
"""

import logging
import cv2
import numpy as np
from libs.config.zone_loader import ZoneConfigLoader

logger = logging.getLogger(__name__)

# Module-level singleton loader — starts hot-reload background thread
_loader = ZoneConfigLoader()
_loader.start()


class Zone:
    """Wrapper for a zone loaded from YAML to provide geometric utilities."""
    def __init__(self, data: dict):
        self.name = data.get("name", "Unknown")
        
        # Validate polygon points
        self.polygon = []
        for point in data.get("polygon", []):
            if isinstance(point, (list, tuple)) and len(point) == 2:
                try:
                    self.polygon.append([int(point[0]), int(point[1])])
                except (ValueError, TypeError):
                    pass
        self.valid = len(self.polygon) >= 3
        
        # Convert hex color to BGR for OpenCV
        hex_color = data.get("color_hex", "#FF0000").lstrip("#")
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            self.color_bgr = (b, g, r)
        except Exception:
            self.color_bgr = (0, 0, 255) # Fallback to Red
            
    def as_array(self) -> np.ndarray:
        if not self.valid:
            return np.array([])
        return np.array(self.polygon, dtype=np.int32)


def get_zones() -> list[Zone]:
    """
    Return the current list of Zone objects loaded from YAML.
    """
    return [Zone(z) for z in _loader.get_zones()]


def get_camera_id() -> str | None:
    """Return the camera_id from the active zone config."""
    return _loader.get_camera_id()


# Alias for legacy support in detection.py
DEFAULT_ZONES = get_zones()


def get_zones_for_point(x: float, y: float, zones: list[Zone] | None = None) -> list[Zone]:
    """
    Return a list of zones that contain the given point (x, y).
    """
    matched_zones = []
    _zones = zones if zones is not None else get_zones()
    for z in _zones:
        pts = z.as_array()
        if len(pts) >= 3:
            # pointPolygonTest returns +ve if inside, 0 if on edge, -ve if outside
            if cv2.pointPolygonTest(pts, (float(x), float(y)), measureDist=False) >= 0:
                matched_zones.append(z)
    return matched_zones

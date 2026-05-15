from __future__ import annotations

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    policy_path: str = "policies/default.yaml"
    detector_model: str = "yolov8n.pt"
    detection_confidence_threshold: float = 0.45
    detector_device: str = "cpu"
    tracker_fps: float = 30
    tracker_max_age: int = 30
    tracker_n_init: int = 3
    tracker_max_cosine_distance: float = 0.4
    camera_id: str = "cam_01"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

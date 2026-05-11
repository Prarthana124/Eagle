from __future__ import annotations
from pydantic import BaseModel, field_validator


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def center(self) -> tuple[float, float]:
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    @property
    def area(self) -> float:
        return (self.x2 - self.x1) * (self.y2 - self.y1)


class DetectionSchema(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBox
    zones_present: list[str] = []

    @field_validator("confidence")
    @classmethod
    def confidence_must_be_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {v}")
        return v


class DetectionFrameSchema(BaseModel):
    frame_id: int
    timestamp_ms: float = 0.0
    detections: list[DetectionSchema] = []
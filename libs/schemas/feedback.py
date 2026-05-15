from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime
import base64


# Request validation: incoming feedback from POST /feedback
class FeedbackRequest(BaseModel):
    alert_id: str = Field(
        ...,
        min_length=1,
        description="Unique alert identifier"
    )

    track_id: int = Field(
        ...,
        gt=0,
        description="Track ID from detection"
    )

    caption_sequence: List[str] = Field(
        ...,
        min_items=1,
        description="Sequence of captions"
    )

    original_label: str = Field(
        ...,
        min_length=1,
        description="Original model prediction"
    )

    human_label: str = Field(
        ...,
        min_length=1,
        description="Human correction label"
    )

    human_note: str = Field(
        "",
        description="Human explanation for correction"
    )

    frame_b64: str = Field(
        ...,
        min_length=1,
        description="Base64 encoded frame image"
    )

    @validator("frame_b64")
    def validate_base64(cls, v):
        try:
            base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError("Invalid base64 string")
        return v


# Redis storage schema: what gets persisted
class FeedbackRecord(BaseModel):
    alert_id: str
    track_id: int
    caption_sequence: List[str]
    original_label: str
    human_label: str
    human_note: str
    frame_b64: str
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# LLaVA format schema: what gets exported for fine-tuning
class Conversation(BaseModel):
    from_: str = Field(..., alias="from")
    value: str

    class Config:
        allow_population_by_field_name = True


class LLaVAConversation(BaseModel):
    image: str = Field(
        ...,
        description="Image filename"
    )

    conversations: List[Conversation] = Field(
        ...,
        min_items=1
    )

    @validator("conversations")
    def validate_conversations(cls, v):
        roles = [conv.from_ for conv in v]

        if not roles or roles[0] not in ["human", "system"]:
            raise ValueError(
                "First conversation must be human or system"
            )

        for i in range(1, len(roles)):
            if roles[i] == roles[i - 1]:
                raise ValueError(
                    "Conversations must alternate roles"
                )

        return v
"""
All LLM/VLM prompt templates for Eagle.
Keep prompts short and structured — reduces hallucination and token cost.
"""

# ── VLM captioning ────────────────────────────────────────────────────────────
CAPTIONING_PROMPT = (
    "Look at this surveillance camera frame. "
    "Describe ONLY what the person is physically doing. Be specific:\n"
    "- Their exact location (near door, at keypad, in corridor)\n"
    "- Their body posture (standing, reaching, walking, crouching)\n"
    "- Any object interaction (touching keypad, holding bag, looking at door)\n"
    "Do NOT guess intent. Describe only visible actions. 2–3 sentences maximum."
)

# ── Grounding check ───────────────────────────────────────────────────────────
GROUNDING_PROMPT = (
    'YOLO detected: {detections_text}\n'
    'VLM caption: "{caption}"\n'
    "Does the caption describe only objects that YOLO confirmed are present?\n"
    'Reply with only "GROUNDED" or "HALLUCINATION: <what was invented>".'
)

# ── Temporal reasoning ───────────────────────────────────────────────────────
REASONING_PROMPT = """\
You are a surveillance analyst AI.

Camera: {camera_id}
Zone: {zone_name}
Observation window: {duration_seconds:.0f} seconds

Behaviour sequence:
{sequence_text}

Visual descriptions:
{captions_text}

Classify this behaviour. Respond ONLY with valid JSON, no other text:
{{
    "label": "Suspicious" or "Normal",
    "confidence": <float 0.0–1.0>,
    "reason": "<one sentence, max 20 words>",
    "key_signal": "<the single most important observation>"
}}"""

# ── Strict retry prompt (after hallucination) ─────────────────────────────────
STRICT_CAPTIONING_PROMPT = (
    "Describe this surveillance frame using ONLY these detected object types: "
    "{allowed_labels}. "
    "Do not mention any other objects. 1–2 sentences."
)


def build_captioning_prompt(allowed_labels: list[str] | None = None) -> str:
    if allowed_labels:
        return STRICT_CAPTIONING_PROMPT.format(
            allowed_labels=", ".join(allowed_labels)
        )
    return CAPTIONING_PROMPT


def build_reasoning_prompt(
    sequence_text:    str,
    captions_text:    str,
    camera_id:        str   = "cam_01",
    zone_name:        str   = "unknown",
    duration_seconds: float = 0.0,
) -> str:
    return REASONING_PROMPT.format(
        camera_id        = camera_id,
        zone_name        = zone_name,
        duration_seconds = duration_seconds,
        sequence_text    = sequence_text,
        captions_text    = captions_text,
    )

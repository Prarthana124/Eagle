"""
memory.py — Redis-backed temporal event memory for Agentic Vision.

Key schema:
    track:{track_id}:events          → RLIST  of JSON TrackEvent   (max 50, ring buffer)
    track:{track_id}:meta            → HASH   {camera_id, zone_count, total_dwell, ...}
    track:{track_id}:zone_entries    → RLIST  of zone names (for repeated-approach detection)
    camera:{camera_id}:active_tracks → SET    of currently active track IDs

All keys have TTL = 300s (5 minutes) reset on every write.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Optional

import redis

from libs.schemas.memory import TrackEvent, TrackSequence

logger = logging.getLogger(__name__)

REDIS_URL           = os.getenv("REDIS_URL", "redis://localhost:6379")
MAX_EVENTS_PER_TRACK = 50
TRACK_TTL_SECONDS    = 300      # 5 minutes idle → key expires


def _get_client() -> redis.Redis:
    """Return a thread-safe Redis client. Lazily initialised."""
    return redis.from_url(REDIS_URL, decode_responses=True)


class MemoryStore:
    """
    Manages the Redis ring buffer for all active tracks.

    Usage:
        store = MemoryStore()
        store.store_event(event)
        sequence = store.get_sequence(track_id=7)
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None) -> None:
        self._r = redis_client or _get_client()

    # ── Write ────────────────────────────────────────────────────────────────

    def store_event(self, event: TrackEvent) -> None:
        """
        Append one TrackEvent to the ring buffer for this track_id.

        Steps:
          1. RPUSH serialized event onto the list
          2. LTRIM to keep only the last MAX_EVENTS_PER_TRACK entries
          3. Reset TTL so idle tracks auto-expire
          4. Update meta hash and active-tracks set

        Args:
            event: TrackEvent to store.
        """
        key_events = f"track:{event.track_id}:events"
        key_meta   = f"track:{event.track_id}:meta"
        key_zones  = f"track:{event.track_id}:zone_entries"
        key_active = f"camera:{event.camera_id}:active_tracks"

        pipe = self._r.pipeline()

        # Ring buffer
        pipe.rpush(key_events, event.model_dump_json())
        pipe.ltrim(key_events, -MAX_EVENTS_PER_TRACK, -1)
        pipe.expire(key_events, TRACK_TTL_SECONDS)

        # Meta
        pipe.hset(key_meta, mapping={
            "camera_id":          event.camera_id,
            "last_frame_id":      event.frame_id,
            "last_timestamp_ms":  event.timestamp_ms,
            "last_zone":          event.zone or "",
            "dwell_time_seconds": event.dwell_time_seconds,
        })
        pipe.expire(key_meta, TRACK_TTL_SECONDS)

        # Zone entry log (for repeated-approach detection)
        if event.action_hint.value == "zone_entry" and event.zone:
            pipe.rpush(key_zones, event.zone)
            pipe.expire(key_zones, TRACK_TTL_SECONDS)

        # Active set
        pipe.sadd(key_active, event.track_id)
        pipe.expire(key_active, TRACK_TTL_SECONDS)

        pipe.execute()

    def store_events(self, events: list[TrackEvent]) -> None:
        """Bulk-store multiple events (one pipeline call per batch)."""
        for evt in events:
            self.store_event(evt)

    # ── Read ─────────────────────────────────────────────────────────────────

    def get_sequence(self, track_id: int, last_n: int = MAX_EVENTS_PER_TRACK) -> TrackSequence:
        """
        Retrieve the last `last_n` events for a track as a TrackSequence.

        Args:
            track_id: The track to query.
            last_n:   Max events to return (default: all 50).

        Returns:
            TrackSequence with events in chronological order.
        """
        key = f"track:{track_id}:events"
        raw = self._r.lrange(key, -last_n, -1)

        if not raw:
            return TrackSequence(track_id=track_id)

        events = [TrackEvent.model_validate_json(r) for r in raw]

        zones_visited = list({e.zone for e in events if e.zone})
        total_dwell   = events[-1].dwell_time_seconds if events else 0.0

        return TrackSequence(
            track_id      = track_id,
            camera_id     = events[0].camera_id if events else "cam_01",
            events        = events,
            total_dwell   = total_dwell,
            zones_visited = zones_visited,
        )

    def get_zone_entry_count(self, track_id: int, zone: str) -> int:
        """
        Return how many times this track has entered the specified zone.
        Used for 'repeated approach' detection.
        """
        key = f"track:{track_id}:zone_entries"
        entries = self._r.lrange(key, 0, -1)
        return entries.count(zone)

    def get_active_track_ids(self, camera_id: str = "cam_01") -> set[int]:
        """Return all currently active track IDs for a camera."""
        key = f"camera:{camera_id}:active_tracks"
        return {int(tid) for tid in self._r.smembers(key)}

    # ── Delete / Expire ──────────────────────────────────────────────────────

    def expire_track(self, track_id: int, camera_id: str = "cam_01") -> None:
        """Manually expire all keys for a dead track."""
        keys = [
            f"track:{track_id}:events",
            f"track:{track_id}:meta",
            f"track:{track_id}:zone_entries",
        ]
        pipe = self._r.pipeline()
        for k in keys:
            pipe.delete(k)
        pipe.srem(f"camera:{camera_id}:active_tracks", track_id)
        pipe.execute()
        logger.info(f"Expired all keys for track #{track_id}")

    def flush_all_tracks(self) -> None:
        """⚠️ Delete ALL track data. Used in tests only."""
        pattern = "track:*"
        keys = list(self._r.scan_iter(pattern))
        if keys:
            self._r.delete(*keys)
        logger.warning(f"Flushed {len(keys)} track keys from Redis.")
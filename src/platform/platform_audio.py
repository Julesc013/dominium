"""Deterministic null audio surface abstraction (presentation-only stub)."""

from __future__ import annotations

from tools.xstack.compatx.canonical_json import canonical_sha256


def create_audio_device(*, device_id: str = "audio.null", sample_rate_hz: int = 48000, channels: int = 2) -> dict:
    return {
        "result": "complete",
        "audio_state": {
            "device_id": str(device_id or "audio.null"),
            "sample_rate_hz": int(max(8000, int(sample_rate_hz))),
            "channels": int(max(1, int(channels))),
            "closed": False,
            "submitted_frames": 0,
            "extensions": {},
        },
    }


def submit_audio_frame(*, audio_state: dict, frame_payload: dict) -> dict:
    state = dict(audio_state or {})
    if bool(state.get("closed", False)):
        return {
            "result": "refusal",
            "code": "refusal.platform.audio_closed",
            "message": "cannot submit frame to closed audio device",
        }
    next_frames = int(max(0, int(state.get("submitted_frames", 0)))) + 1
    state["submitted_frames"] = next_frames
    return {
        "result": "complete",
        "audio_state": state,
        "audio_event": {
            "event_type": "audio.submit",
            "device_id": str(state.get("device_id", "")),
            "submitted_frames": int(next_frames),
            "payload_fingerprint": str(canonical_sha256(dict(frame_payload or {}))),
        },
    }


def close_audio_device(*, audio_state: dict) -> dict:
    state = dict(audio_state or {})
    state["closed"] = True
    return {
        "result": "complete",
        "audio_state": state,
        "event": {
            "event_type": "audio.closed",
            "device_id": str(state.get("device_id", "")),
        },
    }

"""Canonical TIME-ANCHOR-0 tick helpers."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


TickT = int
TICK_BITS = 64
TICK_MAX = (1 << TICK_BITS) - 1
TICK_RESERVED_ROLLOVER_TICKS = 1_000_000
TICK_REFUSAL_THRESHOLD = TICK_MAX - TICK_RESERVED_ROLLOVER_TICKS
REFUSAL_TICK_OVERFLOW_IMMINENT = "refusal.time.tick_overflow_imminent"


class TickOverflowImminentError(ValueError):
    """Raised when a requested canonical tick advance exceeds the guarded range."""

    def __init__(self, *, current_tick: TickT, requested_delta: int) -> None:
        self.current_tick = int(current_tick)
        self.requested_delta = int(requested_delta)
        super().__init__(
            "canonical tick advance refused at {} with delta {}".format(
                int(current_tick),
                int(requested_delta),
            )
        )


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def normalize_tick_t(value: object, default_value: TickT = 0) -> TickT:
    tick_value = int(_as_int(value, int(default_value)))
    if tick_value < 0:
        tick_value = int(default_value)
    return assert_tick_t(tick_value)


def assert_tick_t(value: object) -> TickT:
    tick_value = int(_as_int(value, 0))
    if tick_value < 0:
        raise ValueError("canonical tick must be >= 0")
    if tick_value > TICK_MAX:
        raise ValueError("canonical tick must fit within uint64")
    return int(tick_value)


def tick_record_fingerprint(payload: Mapping[str, object] | None) -> str:
    row = dict(payload or {})
    return canonical_sha256(
        {
            "schema_version": "1.0.0",
            "tick_value": int(assert_tick_t(row.get("tick_value", 0))),
            "deterministic_fingerprint": "",
            "extensions": dict(sorted(dict(row.get("extensions") or {}).items(), key=lambda item: str(item[0]))),
        }
    )


def build_tick_record(
    *,
    tick_value: object,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "tick_value": int(assert_tick_t(tick_value)),
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    payload["deterministic_fingerprint"] = tick_record_fingerprint(payload)
    return payload


def tick_advance_allowed(current_tick: object, delta: object = 1) -> tuple[bool, dict]:
    current_value = int(assert_tick_t(current_tick))
    delta_value = int(max(0, _as_int(delta, 0)))
    target_tick = int(current_value + delta_value)
    allowed = target_tick <= TICK_REFUSAL_THRESHOLD
    return allowed, {
        "current_tick": int(current_value),
        "requested_delta": int(delta_value),
        "target_tick": int(target_tick),
        "threshold_tick": int(TICK_REFUSAL_THRESHOLD),
        "refusal_code": REFUSAL_TICK_OVERFLOW_IMMINENT,
    }


def advance_tick_value(current_tick: object, delta: object = 1) -> TickT:
    allowed, metadata = tick_advance_allowed(current_tick, delta)
    if not allowed:
        raise TickOverflowImminentError(
            current_tick=int(metadata["current_tick"]),
            requested_delta=int(metadata["requested_delta"]),
        )
    return assert_tick_t(int(metadata["target_tick"]))


__all__ = [
    "REFUSAL_TICK_OVERFLOW_IMMINENT",
    "TICK_BITS",
    "TICK_MAX",
    "TICK_REFUSAL_THRESHOLD",
    "TICK_RESERVED_ROLLOVER_TICKS",
    "TickOverflowImminentError",
    "TickT",
    "advance_tick_value",
    "assert_tick_t",
    "build_tick_record",
    "normalize_tick_t",
    "tick_advance_allowed",
    "tick_record_fingerprint",
]

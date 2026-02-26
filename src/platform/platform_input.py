"""Deterministic platform input abstraction and event normalization."""

from __future__ import annotations

from typing import List


def _to_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _sorted_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def create_keyboard_event(
    *,
    key: str,
    action: str,
    modifiers: List[str] | None = None,
    sequence: int = 0,
) -> dict:
    return {
        "event_type": "input.keyboard",
        "key": str(key or "").strip().lower(),
        "action": str(action or "").strip().lower(),
        "modifiers": _sorted_strings(list(modifiers or [])),
        "sequence": int(max(0, _to_int(sequence, 0))),
    }


def create_mouse_event(
    *,
    action: str,
    x: int,
    y: int,
    button: str = "left",
    wheel_delta: int = 0,
    modifiers: List[str] | None = None,
    sequence: int = 0,
) -> dict:
    return {
        "event_type": "input.mouse",
        "action": str(action or "").strip().lower(),
        "x": int(_to_int(x, 0)),
        "y": int(_to_int(y, 0)),
        "button": str(button or "").strip().lower(),
        "wheel_delta": int(_to_int(wheel_delta, 0)),
        "modifiers": _sorted_strings(list(modifiers or [])),
        "sequence": int(max(0, _to_int(sequence, 0))),
    }


def normalize_input_event(event: dict) -> dict:
    row = dict(event or {})
    event_type = str(row.get("event_type", "")).strip().lower()
    if event_type == "input.keyboard":
        return create_keyboard_event(
            key=str(row.get("key", "")),
            action=str(row.get("action", "")),
            modifiers=list(row.get("modifiers") or []),
            sequence=_to_int(row.get("sequence", 0), 0),
        )
    if event_type == "input.mouse":
        return create_mouse_event(
            action=str(row.get("action", "")),
            x=_to_int(row.get("x", 0), 0),
            y=_to_int(row.get("y", 0), 0),
            button=str(row.get("button", "left")),
            wheel_delta=_to_int(row.get("wheel_delta", 0), 0),
            modifiers=list(row.get("modifiers") or []),
            sequence=_to_int(row.get("sequence", 0), 0),
        )
    return {
        "event_type": "input.unknown",
        "sequence": int(max(0, _to_int(row.get("sequence", 0), 0))),
        "payload": dict(row),
    }


def queue_input_event(*, queue: List[dict] | None, event: dict, tick: int) -> dict:
    rows = [dict(item) for item in list(queue or []) if isinstance(item, dict)]
    normalized = normalize_input_event(dict(event or {}))
    normalized["tick"] = int(max(0, _to_int(tick, 0)))
    rows.append(normalized)
    ordered = sorted(
        rows,
        key=lambda item: (
            int(max(0, _to_int(item.get("tick", 0), 0))),
            int(max(0, _to_int(item.get("sequence", 0), 0))),
            str(item.get("event_type", "")),
            str(item.get("key", "")),
            str(item.get("action", "")),
        ),
    )
    return {
        "result": "complete",
        "queue": ordered,
    }

"""Structured deterministic shell logging helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping


def build_log_event(
    *,
    product_id: str,
    event_kind: str,
    message: str,
    simulation_tick: int | None = None,
    host_meta: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    return {
        "product_id": str(product_id).strip(),
        "event_kind": str(event_kind).strip(),
        "message": str(message),
        "simulation_tick": int(simulation_tick) if simulation_tick is not None else None,
        "host_meta": dict(host_meta or {}),
        "extensions": dict(extensions or {}),
    }


def append_jsonl(path: str, event: Mapping[str, object]) -> str:
    output_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(dict(event or {}), sort_keys=True))
        handle.write("\n")
    return output_path


__all__ = ["append_jsonl", "build_log_event"]

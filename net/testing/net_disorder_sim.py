"""Deterministic network disorder simulator (test harness only, tick-based)."""

from __future__ import annotations

import copy
from typing import Dict, Iterable, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_DISORDER_PROFILES: Dict[str, dict] = {
    "disorder.none": {
        "disorder_profile_id": "disorder.none",
        "description": "No-op network disorder profile.",
        "drop_modulo": 0,
        "duplicate_modulo": 0,
        "delay_ticks": 0,
        "delay_extra_modulo": 0,
        "delay_extra_ticks": 0,
        "reorder_bucket_modulo": 0,
    },
    "disorder.reorder_light": {
        "disorder_profile_id": "disorder.reorder_light",
        "description": "Deterministic reordering with no drop/duplication.",
        "drop_modulo": 0,
        "duplicate_modulo": 0,
        "delay_ticks": 0,
        "delay_extra_modulo": 0,
        "delay_extra_ticks": 0,
        "reorder_bucket_modulo": 5,
    },
    "disorder.drop_and_delay": {
        "disorder_profile_id": "disorder.drop_and_delay",
        "description": "Deterministic drop + delay profile for resync tests.",
        "drop_modulo": 5,
        "duplicate_modulo": 0,
        "delay_ticks": 1,
        "delay_extra_modulo": 3,
        "delay_extra_ticks": 1,
        "reorder_bucket_modulo": 7,
    },
    "disorder.dup_reorder_delay": {
        "disorder_profile_id": "disorder.dup_reorder_delay",
        "description": "Deterministic duplication + reorder + delay profile.",
        "drop_modulo": 0,
        "duplicate_modulo": 4,
        "delay_ticks": 1,
        "delay_extra_modulo": 2,
        "delay_extra_ticks": 1,
        "reorder_bucket_modulo": 11,
    },
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _message_id(message: dict) -> str:
    keys = (
        "msg_id",
        "envelope_id",
        "perceived_delta_id",
        "delta_id",
        "snapshot_id",
        "handshake_id",
        "intent_id",
    )
    for key in keys:
        token = str(message.get(key, "")).strip()
        if token:
            return token
    return canonical_sha256(dict(message))


def _message_sequence(message: dict) -> int:
    keys = (
        "sequence",
        "deterministic_sequence_number",
        "submission_tick",
        "tick",
    )
    for key in keys:
        if key not in message:
            continue
        return _as_int(message.get(key, 0), 0)
    return 0


def _message_sort_key(message: dict) -> Tuple[int, str]:
    return (_message_sequence(message), _message_id(message))


def _decision_seed(
    profile_id: str,
    channel_id: str,
    tick: int,
    message_id: str,
    sequence: int,
) -> str:
    payload = {
        "profile_id": str(profile_id),
        "channel_id": str(channel_id),
        "tick": int(tick),
        "message_id": str(message_id),
        "sequence": int(sequence),
    }
    return canonical_sha256(payload)


def _decision_value(seed: str) -> int:
    token = str(seed).strip()
    if not token:
        return 0
    return int(token[:16], 16)


def _normalize_profile(profile_payload: dict) -> dict:
    row = dict(profile_payload if isinstance(profile_payload, dict) else {})
    return {
        "disorder_profile_id": str(row.get("disorder_profile_id", "")).strip(),
        "description": str(row.get("description", "")).strip(),
        "drop_modulo": max(0, _as_int(row.get("drop_modulo", 0), 0)),
        "duplicate_modulo": max(0, _as_int(row.get("duplicate_modulo", 0), 0)),
        "delay_ticks": max(0, _as_int(row.get("delay_ticks", 0), 0)),
        "delay_extra_modulo": max(0, _as_int(row.get("delay_extra_modulo", 0), 0)),
        "delay_extra_ticks": max(0, _as_int(row.get("delay_extra_ticks", 0), 0)),
        "reorder_bucket_modulo": max(0, _as_int(row.get("reorder_bucket_modulo", 0), 0)),
    }


def resolve_disorder_profile(
    disorder_profile_id: str,
    profile_registry: dict | None = None,
) -> Dict[str, object]:
    merged = dict(DEFAULT_DISORDER_PROFILES)
    if isinstance(profile_registry, dict):
        for key in sorted(profile_registry.keys()):
            row = profile_registry.get(key)
            if not isinstance(row, dict):
                continue
            token = str(row.get("disorder_profile_id", "")).strip() or str(key).strip()
            if token:
                merged[token] = dict(row)
    requested = str(disorder_profile_id).strip()
    if not requested:
        requested = "disorder.none"
    selected = merged.get(requested)
    if not isinstance(selected, dict):
        return {
            "result": "refused",
            "reason_code": "refusal.net.disorder_profile_missing",
            "message": "network disorder profile '{}' is not declared".format(requested),
            "profile": {},
        }
    normalized = _normalize_profile(selected)
    if not str(normalized.get("disorder_profile_id", "")).strip():
        normalized["disorder_profile_id"] = requested
    return {"result": "complete", "profile": normalized}


class DeterministicNetDisorderSim:
    """Tick-based deterministic disorder simulator for loopback harness tests."""

    def __init__(
        self,
        *,
        disorder_profile_id: str,
        profile_registry: dict | None = None,
    ) -> None:
        resolved = resolve_disorder_profile(
            disorder_profile_id=str(disorder_profile_id),
            profile_registry=profile_registry,
        )
        if str(resolved.get("result", "")) != "complete":
            raise ValueError(str(resolved.get("reason_code", "refusal.net.disorder_profile_missing")))
        self.profile = dict(resolved.get("profile") or {})
        self.profile_id = str(self.profile.get("disorder_profile_id", "disorder.none")).strip() or "disorder.none"
        self._pending: Dict[str, Dict[int, List[dict]]] = {}

    def _channel_pending(self, channel_id: str) -> Dict[int, List[dict]]:
        token = str(channel_id).strip()
        channel = self._pending.get(token)
        if isinstance(channel, dict):
            return channel
        channel = {}
        self._pending[token] = channel
        return channel

    def _append_pending(self, channel_id: str, release_tick: int, message: dict) -> None:
        channel = self._channel_pending(channel_id)
        rows = list(channel.get(int(release_tick)) or [])
        rows.append(dict(message))
        rows = sorted((dict(item) for item in rows if isinstance(item, dict)), key=_message_sort_key)
        channel[int(release_tick)] = rows
        self._pending[str(channel_id)] = channel

    def inject(
        self,
        *,
        channel_id: str,
        tick: int,
        messages: Iterable[dict],
    ) -> Dict[str, object]:
        channel = str(channel_id).strip() or "channel.default"
        tick_value = max(0, _as_int(tick, 0))
        dropped = 0
        duplicated = 0
        queued = 0
        for message in sorted((dict(item) for item in list(messages or []) if isinstance(item, dict)), key=_message_sort_key):
            message_id = _message_id(message)
            sequence = _message_sequence(message)
            seed = _decision_seed(
                profile_id=self.profile_id,
                channel_id=channel,
                tick=int(tick_value),
                message_id=message_id,
                sequence=sequence,
            )
            decision = _decision_value(seed)
            drop_modulo = int(self.profile.get("drop_modulo", 0) or 0)
            if drop_modulo > 0 and (decision % drop_modulo) == 0:
                dropped += 1
                continue
            copies = 1
            duplicate_modulo = int(self.profile.get("duplicate_modulo", 0) or 0)
            if duplicate_modulo > 0 and (decision % duplicate_modulo) == 0:
                copies = 2
                duplicated += 1
            base_delay = int(self.profile.get("delay_ticks", 0) or 0)
            extra_modulo = int(self.profile.get("delay_extra_modulo", 0) or 0)
            extra_ticks = int(self.profile.get("delay_extra_ticks", 0) or 0)
            extra_delay = 0
            if extra_modulo > 0 and (decision % extra_modulo) == 0:
                extra_delay = max(0, extra_ticks)
            release_tick = int(tick_value + base_delay + extra_delay)
            for copy_index in range(copies):
                cloned = copy.deepcopy(message)
                ext = dict(cloned.get("extensions") or {})
                ext["disorder_profile_id"] = self.profile_id
                ext["disorder_channel_id"] = channel
                ext["disorder_injected_tick"] = int(tick_value)
                ext["disorder_release_tick"] = int(release_tick)
                ext["disorder_copy_index"] = int(copy_index)
                cloned["extensions"] = ext
                self._append_pending(channel_id=channel, release_tick=release_tick, message=cloned)
                queued += 1
        return {
            "result": "complete",
            "channel_id": channel,
            "tick": int(tick_value),
            "queued_count": int(queued),
            "dropped_count": int(dropped),
            "duplicated_count": int(duplicated),
        }

    def deliver(self, *, channel_id: str, tick: int) -> Dict[str, object]:
        channel = str(channel_id).strip() or "channel.default"
        tick_value = max(0, _as_int(tick, 0))
        pending = self._channel_pending(channel)
        due_ticks = sorted(token for token in pending.keys() if int(token) <= int(tick_value))
        due_rows: List[dict] = []
        for due_tick in due_ticks:
            rows = list(pending.get(int(due_tick)) or [])
            due_rows.extend(dict(item) for item in rows if isinstance(item, dict))
            if int(due_tick) in pending:
                del pending[int(due_tick)]
        self._pending[channel] = pending

        reorder_modulo = int(self.profile.get("reorder_bucket_modulo", 0) or 0)

        def sort_key(message: dict) -> Tuple[int, int, str]:
            message_id = _message_id(message)
            sequence = _message_sequence(message)
            if reorder_modulo <= 0:
                bucket = 0
            else:
                seed = _decision_seed(
                    profile_id=self.profile_id,
                    channel_id=channel,
                    tick=int(tick_value),
                    message_id=message_id,
                    sequence=sequence,
                )
                bucket = _decision_value(seed) % reorder_modulo
            return (int(bucket), int(sequence), message_id)

        delivered = sorted((dict(item) for item in due_rows if isinstance(item, dict)), key=sort_key)
        return {
            "result": "complete",
            "channel_id": channel,
            "tick": int(tick_value),
            "messages": delivered,
            "delivered_count": int(len(delivered)),
            "message_hash": canonical_sha256(delivered),
        }

    def flush(self, *, channel_id: str, until_tick: int) -> Dict[str, object]:
        channel = str(channel_id).strip() or "channel.default"
        tick_value = max(0, _as_int(until_tick, 0))
        rows: List[dict] = []
        for tick in range(0, tick_value + 1):
            delivered = self.deliver(channel_id=channel, tick=tick)
            rows.extend(list(delivered.get("messages") or []))
        return {
            "result": "complete",
            "channel_id": channel,
            "until_tick": int(tick_value),
            "messages": rows,
            "message_hash": canonical_sha256(rows),
        }


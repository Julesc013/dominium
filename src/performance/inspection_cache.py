"""Deterministic derived inspection snapshot cache helpers."""

from __future__ import annotations

from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def build_cache_key(
    *,
    target_id: str,
    truth_hash_anchor: str,
    policy_id: str,
    physics_profile_id: str,
    pack_lock_hash: str,
    desired_fidelity: str = "",
    epistemic_policy_id: str = "",
    section_policy_id: str = "",
) -> str:
    payload = {
        "target_id": str(target_id),
        "truth_hash_anchor": str(truth_hash_anchor),
        "policy_id": str(policy_id),
        "physics_profile_id": str(physics_profile_id),
        "pack_lock_hash": str(pack_lock_hash),
        "desired_fidelity": str(desired_fidelity),
        "epistemic_policy_id": str(epistemic_policy_id),
        "section_policy_id": str(section_policy_id),
    }
    return str(canonical_sha256(payload))


def build_inspection_snapshot(
    *,
    target_id: str,
    tick: int,
    physics_profile_id: str,
    pack_lock_hash: str,
    truth_hash_anchor: str,
    policy_id: str,
    target_payload: dict,
) -> dict:
    base = {
        "schema_version": "1.0.0",
        "target_id": str(target_id),
        "tick": int(max(0, _as_int(tick, 0))),
        "physics_profile_id": str(physics_profile_id),
        "pack_lock_hash": str(pack_lock_hash),
        "truth_hash_anchor": str(truth_hash_anchor),
        "cache_policy_id": str(policy_id),
        "target_payload": dict(target_payload or {}),
    }
    snapshot_hash = str(canonical_sha256(base))
    return {
        **base,
        "snapshot_id": "inspect.{}".format(snapshot_hash[:16]),
        "snapshot_hash": snapshot_hash,
    }


def cache_lookup_or_store(
    *,
    cache_state: dict | None,
    cache_policy: dict | None,
    cache_key: str,
    snapshot: dict,
    tick: int,
) -> dict:
    state = dict(cache_state or {})
    policy = dict(cache_policy or {})
    entries = dict(state.get("entries_by_key") or {})
    enable_caching = bool(policy.get("enable_caching", False))
    max_entries = max(0, _as_int(policy.get("max_cache_entries", 0), 0))
    normalized_tick = int(max(0, _as_int(tick, 0)))
    snapshot_payload = dict(snapshot or {})
    key_token = str(cache_key).strip()
    if not key_token:
        key_token = str(canonical_sha256(snapshot_payload))

    if not enable_caching:
        return {
            "result": "complete",
            "cache_hit": False,
            "cache_key": str(key_token),
            "snapshot": snapshot_payload,
            "snapshot_hash": str(snapshot_payload.get("snapshot_hash", "")),
            "cache_state": {
                "entries_by_key": {},
            },
            "evicted_keys": [],
        }

    existing_row = dict(entries.get(key_token) or {})
    if existing_row and str(existing_row.get("snapshot_hash", "")) == str(snapshot_payload.get("snapshot_hash", "")):
        existing_row["last_access_tick"] = int(normalized_tick)
        entries[key_token] = existing_row
        return {
            "result": "complete",
            "cache_hit": True,
            "cache_key": str(key_token),
            "snapshot": dict(existing_row.get("snapshot") or snapshot_payload),
            "snapshot_hash": str(existing_row.get("snapshot_hash", "")),
            "cache_state": {
                "entries_by_key": dict((str(key), dict(entries[key])) for key in sorted(entries.keys())),
            },
            "evicted_keys": [],
        }

    entries[key_token] = {
        "snapshot_hash": str(snapshot_payload.get("snapshot_hash", "")),
        "snapshot": dict(snapshot_payload),
        "created_tick": int(normalized_tick),
        "last_access_tick": int(normalized_tick),
    }

    evicted: List[str] = []
    if max_entries > 0 and len(entries) > max_entries:
        ranked_keys = sorted(
            entries.keys(),
            key=lambda key: (
                int(_as_int((entries.get(key) or {}).get("last_access_tick", 0), 0)),
                int(_as_int((entries.get(key) or {}).get("created_tick", 0), 0)),
                str(key),
            ),
        )
        for remove_key in ranked_keys[: len(entries) - int(max_entries)]:
            if str(remove_key) == str(key_token):
                continue
            entries.pop(remove_key, None)
            evicted.append(str(remove_key))
        # If capacity is one and only new key exists, keep deterministic single entry.
        if len(entries) > int(max_entries):
            ranked_keys = sorted(
                entries.keys(),
                key=lambda key: (
                    int(_as_int((entries.get(key) or {}).get("last_access_tick", 0), 0)),
                    int(_as_int((entries.get(key) or {}).get("created_tick", 0), 0)),
                    str(key),
                ),
            )
            while len(entries) > int(max_entries):
                remove_key = ranked_keys.pop(0)
                if str(remove_key) == str(key_token) and len(entries) > 1:
                    continue
                entries.pop(remove_key, None)
                evicted.append(str(remove_key))

    return {
        "result": "complete",
        "cache_hit": False,
        "cache_key": str(key_token),
        "snapshot": dict(snapshot_payload),
        "snapshot_hash": str(snapshot_payload.get("snapshot_hash", "")),
        "cache_state": {
            "entries_by_key": dict((str(key), dict(entries[key])) for key in sorted(entries.keys())),
        },
        "evicted_keys": sorted(set(str(item) for item in evicted if str(item).strip())),
    }

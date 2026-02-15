"""Deterministic SRZ hybrid intent routing helpers."""

from __future__ import annotations

from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import refusal


DEFAULT_SHARD_ID = "shard.0"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


def _shard_rows(shard_map: dict) -> List[dict]:
    rows = shard_map.get("shards")
    if not isinstance(rows, list):
        return []
    out: List[dict] = []
    for row in rows:
        if isinstance(row, dict):
            out.append(dict(row))
    return sorted(
        out,
        key=lambda item: (
            _as_int(item.get("priority", 0), 0),
            str(item.get("shard_id", "")),
        ),
    )


def shard_index(shard_map: dict) -> Dict[str, object]:
    rows = _shard_rows(shard_map)
    shard_ids = []
    object_owner = {}
    for row in rows:
        shard_id = str(row.get("shard_id", "")).strip()
        if not shard_id:
            continue
        shard_ids.append(shard_id)
        region_scope = row.get("region_scope")
        if not isinstance(region_scope, dict):
            continue
        for object_id in _sorted_tokens(list(region_scope.get("object_ids") or [])):
            object_owner[object_id] = shard_id
    shard_ids = _sorted_tokens(shard_ids)
    return {
        "shard_ids": shard_ids,
        "object_owner": dict((key, object_owner[key]) for key in sorted(object_owner.keys())),
    }


def _payload_inputs(envelope: dict) -> dict:
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        return {}
    inputs = payload.get("inputs")
    if isinstance(inputs, dict):
        return dict(inputs)
    return {}


def _routing_targets_from_payload(payload: dict, inputs: dict) -> Tuple[List[str], List[str]]:
    object_ids: List[str] = []
    site_ids: List[str] = []
    for key in ("object_id", "target_object_id"):
        token = str(payload.get(key, "")).strip()
        if token:
            object_ids.append(token)
        token_inputs = str(inputs.get(key, "")).strip()
        if token_inputs:
            object_ids.append(token_inputs)
    for key in ("site_id", "target_site_id"):
        token = str(payload.get(key, "")).strip()
        if token:
            site_ids.append(token)
        token_inputs = str(inputs.get(key, "")).strip()
        if token_inputs:
            site_ids.append(token_inputs)
    for key in ("target_object_ids", "object_ids"):
        rows = payload.get(key)
        if isinstance(rows, list):
            object_ids.extend(_sorted_tokens(rows))
        rows_inputs = inputs.get(key)
        if isinstance(rows_inputs, list):
            object_ids.extend(_sorted_tokens(rows_inputs))
    return _sorted_tokens(object_ids), _sorted_tokens(site_ids)


def _site_owner(site_id: str, site_registry: dict, fallback_owner: Dict[str, str]) -> str:
    rows = site_registry.get("sites")
    if not isinstance(rows, list):
        return ""
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("site_id", "")).strip() != str(site_id).strip():
            continue
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            return str(fallback_owner.get(object_id, ""))
    return ""


def _derive_target_shards(envelope: dict, shard_map: dict, site_registry: dict) -> List[str]:
    index = shard_index(shard_map)
    shard_ids = list(index.get("shard_ids") or [])
    object_owner = dict(index.get("object_owner") or {})
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        payload = {}
    inputs = _payload_inputs(envelope)
    object_ids, site_ids = _routing_targets_from_payload(payload, inputs)
    target_shards = []
    for object_id in object_ids:
        owner = str(object_owner.get(object_id, "")).strip()
        if owner:
            target_shards.append(owner)
    for site_id in site_ids:
        owner = _site_owner(site_id=site_id, site_registry=site_registry, fallback_owner=object_owner)
        if owner:
            target_shards.append(owner)
    if not target_shards:
        if DEFAULT_SHARD_ID in shard_ids:
            target_shards.append(DEFAULT_SHARD_ID)
        elif shard_ids:
            target_shards.append(str(shard_ids[0]))
    return _sorted_tokens(target_shards)


def _envelope_sort_key(envelope: dict) -> Tuple[int, str, str, int, str]:
    return (
        _as_int(envelope.get("submission_tick", 0), 0),
        str(envelope.get("target_shard_id", "")),
        str(envelope.get("source_peer_id", "")),
        _as_int(envelope.get("deterministic_sequence_number", 0), 0),
        str(envelope.get("intent_id", "")),
    )


def _sub_envelope_id(parent_envelope_id: str, shard_id: str) -> str:
    digest = canonical_sha256(
        {
            "parent_envelope_id": str(parent_envelope_id),
            "target_shard_id": str(shard_id),
        }
    )
    return "env.sub.{}".format(digest[:24])


def route_intent_envelope(
    envelope: dict,
    shard_map: dict,
    site_registry: dict | None = None,
) -> Dict[str, object]:
    payload = dict(envelope or {})
    index = shard_index(shard_map)
    shard_ids = list(index.get("shard_ids") or [])
    if not shard_ids:
        return refusal(
            "refusal.net.shard_target_invalid",
            "active shard map is missing shard definitions",
            "Configure a shard_map with at least one shard before routing envelopes.",
            {"shard_map_id": str(shard_map.get("shard_map_id", ""))},
            "$.shard_map.shards",
        )
    explicit_target = str(payload.get("target_shard_id", "")).strip()
    if explicit_target and explicit_target not in ("auto", "*"):
        if explicit_target not in shard_ids:
            return refusal(
                "refusal.net.shard_target_invalid",
                "target_shard_id '{}' is not defined by active shard map".format(explicit_target),
                "Route to a shard_id declared in shard_map.registry, or use target_shard_id='auto'.",
                {"target_shard_id": explicit_target},
                "$.intent_envelope.target_shard_id",
            )
        routed = dict(payload)
        routed["target_shard_id"] = explicit_target
        return {
            "result": "complete",
            "routed_envelopes": [routed],
        }

    target_shards = _derive_target_shards(
        envelope=payload,
        shard_map=shard_map,
        site_registry=dict(site_registry or {}),
    )
    if not target_shards:
        return refusal(
            "refusal.net.shard_target_invalid",
            "unable to derive target shard from envelope payload",
            "Set target_shard_id explicitly or include target object/site identifiers.",
            {"envelope_id": str(payload.get("envelope_id", ""))},
            "$.intent_envelope",
        )
    if len(target_shards) == 1:
        routed = dict(payload)
        routed["target_shard_id"] = str(target_shards[0])
        return {
            "result": "complete",
            "routed_envelopes": [routed],
        }

    parent_envelope_id = str(payload.get("envelope_id", "")).strip()
    routed_rows = []
    for shard_id in sorted(target_shards):
        sub = dict(payload)
        sub["target_shard_id"] = str(shard_id)
        sub["envelope_id"] = _sub_envelope_id(parent_envelope_id=parent_envelope_id, shard_id=shard_id)
        extensions = dict(sub.get("extensions") or {})
        extensions["parent_envelope_id"] = parent_envelope_id
        sub["extensions"] = extensions
        routed_rows.append(sub)
    return {
        "result": "complete",
        "routed_envelopes": sorted(routed_rows, key=_envelope_sort_key),
    }


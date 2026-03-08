"""Deterministic GEO-1 spatial object identity engine."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.kernel.geo_kernel import _as_map

from .geo_index_engine import _coerce_cell_key, _semantic_cell_key


REFUSAL_GEO_OBJECT_KIND_MISSING = "refusal.geo.object_kind_missing"

_OBJECT_KIND_REGISTRY_REL = "data/registries/object_kind_registry.json"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _object_kind_registry() -> dict:
    abs_path = os.path.join(_repo_root(), _OBJECT_KIND_REGISTRY_REL.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _object_kind_rows(registry_payload: Mapping[str, object] | None = None) -> dict:
    payload = _as_map(registry_payload) or _object_kind_registry()
    record = _as_map(payload.get("record"))
    rows = list(record.get("object_kinds") or [])
    out = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        object_kind_id = str(row.get("object_kind_id", "")).strip()
        if object_kind_id:
            out[object_kind_id] = dict(row)
    return out


def _local_subkey_payload(local_subkey: object) -> dict | None:
    if isinstance(local_subkey, bool):
        return None
    if isinstance(local_subkey, int):
        return {"subkey_type": "integer", "value": int(local_subkey)}
    token = str(local_subkey).strip()
    if not token:
        return None
    return {"subkey_type": "string", "value": token}


def geo_object_id(
    universe_identity_hash: str,
    cell_key: Mapping[str, object] | None,
    object_kind_id: str,
    local_subkey: object,
    *,
    object_kind_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    cell_key_row = _coerce_cell_key(cell_key)
    if cell_key_row is None:
        payload = {
            "result": "refused",
            "refusal_code": "refusal.geo.cell_key_invalid",
            "message": "cell_key is invalid",
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    object_kind_token = str(object_kind_id or "").strip()
    if not object_kind_token:
        payload = {
            "result": "refused",
            "refusal_code": REFUSAL_GEO_OBJECT_KIND_MISSING,
            "message": "object_kind_id is required",
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    object_kind_rows = _object_kind_rows(object_kind_registry_payload)
    if object_kind_token not in object_kind_rows:
        payload = {
            "result": "refused",
            "refusal_code": REFUSAL_GEO_OBJECT_KIND_MISSING,
            "message": "object_kind_id '{}' is missing".format(object_kind_token),
            "details": {"object_kind_id": object_kind_token},
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    local_subkey_payload = _local_subkey_payload(local_subkey)
    if local_subkey_payload is None:
        payload = {
            "result": "refused",
            "refusal_code": "refusal.geo.local_subkey_invalid",
            "message": "local_subkey must be a non-empty string or integer",
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    lineage_seed = {
        "universe_identity_hash": str(universe_identity_hash or "").strip(),
        "topology_profile_id": str(cell_key_row.get("topology_profile_id", "")),
        "partition_profile_id": str(cell_key_row.get("partition_profile_id", "")),
        "geo_cell_key": _semantic_cell_key(cell_key_row),
        "object_kind_id": object_kind_token,
        "local_subkey": local_subkey_payload,
    }
    object_id_hash = canonical_sha256(lineage_seed)
    identity = {
        "schema_version": "1.0.0",
        "object_kind_id": object_kind_token,
        "geo_cell_key": cell_key_row,
        "local_subkey": local_subkey_payload["value"],
        "object_id_hash": object_id_hash,
        "deterministic_fingerprint": "",
        "extensions": {
            "local_subkey_type": local_subkey_payload["subkey_type"],
            "source": "GEO1-5",
        },
    }
    identity["deterministic_fingerprint"] = canonical_sha256(dict(identity, deterministic_fingerprint=""))
    payload = {
        "result": "complete",
        "object_id_hash": object_id_hash,
        "object_identity": identity,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


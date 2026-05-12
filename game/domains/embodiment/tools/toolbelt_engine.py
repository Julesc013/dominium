"""Deterministic EMB-1 toolbelt registry, access, and availability helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


TOOL_CAPABILITY_REGISTRY_REL = os.path.join("data", "registries", "tool_capability_registry.json")
ENTITLEMENT_REGISTRY_REL = os.path.join("data", "registries", "entitlement_registry.json")
ACCESS_POLICY_REGISTRY_REL = os.path.join("data", "registries", "access_policy_registry.json")

DEFAULT_TOOL_ORDER = (
    "tool.terrain_edit",
    "tool.scanner_basic",
    "tool.logic_probe",
    "tool.logic_analyzer",
    "tool.teleport",
)

_PRIVILEGE_RANK = {
    "observer": 0,
    "operator": 1,
    "admin": 2,
}


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    current = here
    markers = (
        os.path.join("docs", "canon", "constitution_v1.md"),
        os.path.join("data", "registries"),
        os.path.join("tools", "xstack"),
    )
    while True:
        if all(os.path.exists(os.path.join(current, marker)) for marker in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.normpath(os.path.join(here, "..", "..", ".."))
        current = parent


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def _as_bool(value: object, default_value: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        token = value.strip().lower()
        if token in ("1", "true", "yes", "on"):
            return True
        if token in ("0", "false", "no", "off"):
            return False
    return bool(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _rows_by_id(payload: Mapping[str, object] | None, *, row_key: str, id_key: str) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get(row_key)
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get(row_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def tool_capability_rows_by_id(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(TOOL_CAPABILITY_REGISTRY_REL),
        row_key="tool_capabilities",
        id_key="tool_id",
    )


def tool_capability_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(TOOL_CAPABILITY_REGISTRY_REL))


def entitlement_rows_by_id(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(ENTITLEMENT_REGISTRY_REL),
        row_key="entitlements",
        id_key="entitlement_id",
    )


def entitlement_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(ENTITLEMENT_REGISTRY_REL))


def access_policy_rows_by_id(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(ACCESS_POLICY_REGISTRY_REL),
        row_key="access_policies",
        id_key="access_policy_id",
    )


def access_policy_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(ACCESS_POLICY_REGISTRY_REL))


def _privilege_rank(authority_context: Mapping[str, object] | None) -> int:
    privilege = str(_as_map(authority_context).get("privilege_level", "")).strip().lower()
    return int(_PRIVILEGE_RANK.get(privilege, -1))


def _refusal(*, code: str, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "reason_code": str(code or "").strip(),
        "message": str(message or "").strip(),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def evaluate_tool_access(
    *,
    tool_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool = True,
    capability_registry_payload: Mapping[str, object] | None = None,
    access_policy_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    tool_rows = tool_capability_rows_by_id(capability_registry_payload)
    tool_row = dict(tool_rows.get(str(tool_id or "").strip()) or {})
    if not tool_row:
        return _refusal(
            code="refusal.tool.unknown",
            message="tool capability is not registered",
            details={"tool_id": str(tool_id or "").strip()},
        )
    entitlements = set(_sorted_tokens(_as_map(authority_context).get("entitlements")))
    required_entitlement = str(tool_row.get("required_entitlement_id", "")).strip()
    if required_entitlement and required_entitlement not in entitlements:
        return _refusal(
            code="refusal.tool.entitlement_missing",
            message="tool capability requires an additional entitlement",
            details={"tool_id": str(tool_row.get("tool_id", "")).strip(), "missing_entitlement_id": required_entitlement},
        )
    access_rows = access_policy_rows_by_id(access_policy_registry_payload)
    access_policy_id = str(tool_row.get("access_policy_id", "")).strip()
    access_policy_row = dict(access_rows.get(access_policy_id) or {})
    if access_policy_id and not access_policy_row:
        return _refusal(
            code="refusal.tool.access_policy_missing",
            message="tool capability references an unknown access policy",
            details={"tool_id": str(tool_row.get("tool_id", "")).strip(), "access_policy_id": access_policy_id},
        )
    required_policy_entitlements = _sorted_tokens(access_policy_row.get("required_entitlements"))
    missing_policy_entitlements = [token for token in required_policy_entitlements if token not in entitlements]
    if missing_policy_entitlements:
        return _refusal(
            code="refusal.tool.access_policy_denied",
            message="tool capability is denied by access policy entitlements",
            details={
                "tool_id": str(tool_row.get("tool_id", "")).strip(),
                "access_policy_id": access_policy_id,
                "missing_entitlements": list(missing_policy_entitlements),
            },
        )
    required_privilege = str(access_policy_row.get("required_privilege_level", "")).strip().lower()
    if required_privilege and _privilege_rank(authority_context) < int(_PRIVILEGE_RANK.get(required_privilege, 99)):
        return _refusal(
            code="refusal.tool.access_policy_denied",
            message="tool capability requires a higher privilege level",
            details={
                "tool_id": str(tool_row.get("tool_id", "")).strip(),
                "access_policy_id": access_policy_id,
                "required_privilege_level": required_privilege,
            },
        )
    if _as_bool(access_policy_row.get("physical_access_required"), False) and not bool(has_physical_access):
        return _refusal(
            code="refusal.tool.physical_access_required",
            message="tool capability requires physical access",
            details={"tool_id": str(tool_row.get("tool_id", "")).strip(), "access_policy_id": access_policy_id},
        )
    payload = {
        "result": "complete",
        "tool_capability": dict(tool_row),
        "access_policy": dict(access_policy_row),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_tool_surface_row(
    *,
    tool_id: str,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool = True,
    capability_registry_payload: Mapping[str, object] | None = None,
    access_policy_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    access_result = evaluate_tool_access(
        tool_id=tool_id,
        authority_context=authority_context,
        has_physical_access=has_physical_access,
        capability_registry_payload=capability_registry_payload,
        access_policy_registry_payload=access_policy_registry_payload,
    )
    if str(access_result.get("result", "")).strip() == "complete":
        tool_row = dict(access_result.get("tool_capability") or {})
    else:
        tool_row = dict(tool_capability_rows_by_id(capability_registry_payload).get(str(tool_id or "").strip()) or {})
    extensions = _as_map(tool_row.get("extensions"))
    payload = {
        "tool_id": str(tool_id or "").strip(),
        "available": bool(str(access_result.get("result", "")).strip() == "complete"),
        "capability_kind": str(tool_row.get("capability_kind", "")).strip(),
        "required_entitlement_id": str(tool_row.get("required_entitlement_id", "")).strip(),
        "access_policy_id": str(tool_row.get("access_policy_id", "")).strip(),
        "display_name": str(extensions.get("display_name", "")).strip(),
        "ui_command_id": str(extensions.get("ui_command_id", "")).strip(),
        "allowed_process_ids": _sorted_tokens(extensions.get("allowed_process_ids")),
        "reason_code": str(access_result.get("reason_code", "")).strip(),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_toolbelt_availability_surface(
    *,
    authority_context: Mapping[str, object] | None,
    has_physical_access: bool = True,
    tool_ids: object = None,
    capability_registry_payload: Mapping[str, object] | None = None,
    access_policy_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    requested_ids = _sorted_tokens(tool_ids) or list(DEFAULT_TOOL_ORDER)
    rows = [
        build_tool_surface_row(
            tool_id=tool_id,
            authority_context=authority_context,
            has_physical_access=has_physical_access,
            capability_registry_payload=capability_registry_payload,
            access_policy_registry_payload=access_policy_registry_payload,
        )
        for tool_id in requested_ids
    ]
    payload = {
        "result": "complete",
        "tool_rows": [dict(row) for row in rows],
        "available_tool_ids": [str(row.get("tool_id", "")).strip() for row in rows if bool(row.get("available", False))],
        "tool_capability_registry_hash": tool_capability_registry_hash(capability_registry_payload),
        "entitlement_registry_hash": entitlement_registry_hash(),
        "access_policy_registry_hash": access_policy_registry_hash(access_policy_registry_payload),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "access_policy_registry_hash",
    "access_policy_rows_by_id",
    "build_tool_surface_row",
    "build_toolbelt_availability_surface",
    "entitlement_registry_hash",
    "entitlement_rows_by_id",
    "evaluate_tool_access",
    "tool_capability_registry_hash",
    "tool_capability_rows_by_id",
]

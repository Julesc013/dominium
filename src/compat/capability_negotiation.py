"""Deterministic CAP-NEG capability and feature negotiation engine."""

from __future__ import annotations

import json
import os
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


CAPABILITY_REGISTRY_REL = os.path.join("data", "registries", "capability_registry.json")
PRODUCT_REGISTRY_REL = os.path.join("data", "registries", "product_registry.json")
COMPAT_MODE_REGISTRY_REL = os.path.join("data", "registries", "compat_mode_registry.json")
SEMANTIC_CONTRACT_REGISTRY_REL = os.path.join("data", "registries", "semantic_contract_registry.json")
DEGRADE_LADDER_REGISTRY_REL = os.path.join("data", "registries", "degrade_ladder_registry.json")
CAPABILITY_FALLBACK_REGISTRY_REL = os.path.join("data", "registries", "capability_fallback_registry.json")

REFUSAL_NO_COMMON_PROTOCOL = "refusal.compat.no_common_protocol"
REFUSAL_CONTRACT_MISMATCH = "refusal.compat.contract_mismatch"
REFUSAL_MISSING_REQUIRED_CAP = "refusal.compat.missing_required_cap"

COMPAT_MODE_FULL = "compat.full"
COMPAT_MODE_DEGRADED = "compat.degraded"
COMPAT_MODE_READ_ONLY = "compat.read_only"
COMPAT_MODE_REFUSE = "compat.refuse"

DEFAULT_PROTOCOL_ID = "protocol.loopback.session"
DEFAULT_PROTOCOL_VERSION = "1.0.0"
READ_ONLY_LAW_PROFILE_ID = "law.observer.default"


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, path.replace("\\", "/")
    if not isinstance(payload, dict):
        return {}, path.replace("\\", "/")
    return dict(payload), ""


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _semver_tuple(value: object) -> Tuple[int, int, int]:
    token = str(value or "").strip()
    parts = token.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    out = []
    for item in parts:
        try:
            out.append(int(item))
        except ValueError:
            out.append(0)
    return (out[0], out[1], out[2])


def _semver_text(value: Tuple[int, int, int]) -> str:
    return "{}.{}.{}".format(int(value[0]), int(value[1]), int(value[2]))


def _contract_category_and_version(contract_id: object) -> Tuple[str, int]:
    token = str(contract_id or "").strip()
    if ".v" not in token:
        return "", 0
    head, tail = token.rsplit(".v", 1)
    try:
        return head, int(tail)
    except ValueError:
        return "", 0


def _contract_id(category_id: str, version: int) -> str:
    token = str(category_id or "").strip()
    if not token:
        return ""
    return "{}.v{}".format(token, int(version))


def load_capability_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, CAPABILITY_REGISTRY_REL))


def capability_ids(repo_root: str) -> Tuple[List[str], str]:
    payload, error = load_capability_registry(repo_root)
    if error:
        return [], error
    rows = _as_list(_as_map(payload.get("record")).get("capabilities"))
    return _sorted_tokens(_as_map(row).get("capability_id") for row in rows if isinstance(row, Mapping)), ""


def load_product_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, PRODUCT_REGISTRY_REL))


def load_compat_mode_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, COMPAT_MODE_REGISTRY_REL))


def load_semantic_contract_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, SEMANTIC_CONTRACT_REGISTRY_REL))


def load_degrade_ladder_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, DEGRADE_LADDER_REGISTRY_REL))


def load_capability_fallback_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, CAPABILITY_FALLBACK_REGISTRY_REL))


def _normalize_protocol_range(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    normalized = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "protocol_id": str(payload.get("protocol_id", DEFAULT_PROTOCOL_ID)).strip() or DEFAULT_PROTOCOL_ID,
        "min_version": str(payload.get("min_version", DEFAULT_PROTOCOL_VERSION)).strip() or DEFAULT_PROTOCOL_VERSION,
        "max_version": str(payload.get("max_version", DEFAULT_PROTOCOL_VERSION)).strip() or DEFAULT_PROTOCOL_VERSION,
        "deterministic_fingerprint": "",
        "extensions": _as_map(payload.get("extensions")),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def _normalize_contract_range(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    normalized = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "contract_category_id": str(payload.get("contract_category_id", "")).strip(),
        "min_version": max(1, _as_int(payload.get("min_version", 1), 1)),
        "max_version": max(1, _as_int(payload.get("max_version", 1), 1)),
        "deterministic_fingerprint": "",
        "extensions": _as_map(payload.get("extensions")),
    }
    if normalized["max_version"] < normalized["min_version"]:
        normalized["max_version"] = int(normalized["min_version"])
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def _normalize_degrade_rule(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    action_kind = str(payload.get("action_kind", "disable_feature")).strip() or "disable_feature"
    if action_kind == "switch_to_read_only":
        action_kind = "switch_to_read_only"
    normalized = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "rule_id": str(payload.get("rule_id", "")).strip(),
        "trigger_kind": str(payload.get("trigger_kind", "missing_optional_capability")).strip(),
        "trigger_id": str(payload.get("trigger_id", "")).strip(),
        "fallback_mode_id": str(payload.get("fallback_mode_id", COMPAT_MODE_DEGRADED)).strip() or COMPAT_MODE_DEGRADED,
        "action_kind": action_kind,
        "priority": max(0, _as_int(payload.get("priority", 0), 0)),
        "deterministic_fingerprint": "",
        "extensions": _as_map(payload.get("extensions")),
    }
    if not normalized["rule_id"]:
        normalized["rule_id"] = "degrade.{}".format(
            canonical_sha256(
                {
                    "trigger_kind": normalized["trigger_kind"],
                    "trigger_id": normalized["trigger_id"],
                    "fallback_mode_id": normalized["fallback_mode_id"],
                    "action_kind": normalized["action_kind"],
                    "priority": normalized["priority"],
                    "extensions": normalized["extensions"],
                }
            )[:16]
        )
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def _normalize_fallback_map(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    normalized = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "capability_id": str(payload.get("capability_id", "")).strip(),
        "fallback_action": str(payload.get("fallback_action", "disable_feature")).strip() or "disable_feature",
        "deterministic_fingerprint": "",
        "extensions": _as_map(payload.get("extensions")),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def semantic_contract_rows_by_category(repo_root: str) -> Tuple[Dict[str, dict], str]:
    payload, error = load_semantic_contract_registry(repo_root)
    if error:
        return {}, error
    rows = _as_list(_as_map(payload.get("record")).get("contracts"))
    out: Dict[str, dict] = {}
    for row in rows:
        category_id, version = _contract_category_and_version(_as_map(row).get("contract_id"))
        if not category_id or version < 1:
            continue
        current = dict(out.get(category_id) or {})
        if not current or version > int(current.get("version", 0) or 0):
            out[category_id] = {"contract_id": _contract_id(category_id, version), "version": int(version)}
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def _default_contract_ranges(repo_root: str) -> List[dict]:
    rows_by_category, _error = semantic_contract_rows_by_category(repo_root)
    out = []
    for category_id in sorted(rows_by_category.keys()):
        row = rows_by_category.get(category_id) or {}
        version = max(1, int(row.get("version", 1) or 1))
        out.append(
            _normalize_contract_range(
                {
                    "schema_version": "1.0.0",
                    "contract_category_id": category_id,
                    "min_version": version,
                    "max_version": version,
                    "extensions": {},
                }
            )
        )
    return out


def normalize_product_row(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    normalized = {
        "product_id": str(payload.get("product_id", "")).strip(),
        "default_protocol_versions_supported": [
            _normalize_protocol_range(item)
            for item in sorted(_as_list(payload.get("default_protocol_versions_supported")), key=lambda item: str(_as_map(item).get("protocol_id", "")))
        ],
        "default_semantic_contract_versions_supported": [
            _normalize_contract_range(item)
            for item in sorted(_as_list(payload.get("default_semantic_contract_versions_supported")), key=lambda item: str(_as_map(item).get("contract_category_id", "")))
        ],
        "default_feature_capabilities": _sorted_tokens(payload.get("default_feature_capabilities")),
        "default_required_capabilities": _sorted_tokens(payload.get("default_required_capabilities")),
        "default_optional_capabilities": _sorted_tokens(payload.get("default_optional_capabilities")),
        "default_degrade_ladders": [
            _normalize_degrade_rule(item)
            for item in sorted(_as_list(payload.get("default_degrade_ladders")), key=lambda item: (int(_as_map(item).get("priority", 0) or 0), str(_as_map(item).get("rule_id", ""))))
        ],
        "deterministic_fingerprint": "",
        "extensions": _as_map(payload.get("extensions")),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def normalize_compat_mode_row(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    normalized = {
        "compat_mode_id": str(payload.get("compat_mode_id", "")).strip(),
        "description": str(payload.get("description", "")).strip(),
        "deterministic_fingerprint": "",
        "extensions": _as_map(payload.get("extensions")),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def product_rows_by_id(repo_root: str) -> Tuple[Dict[str, dict], str]:
    payload, error = load_product_registry(repo_root)
    if error:
        return {}, error
    rows = _as_list(_as_map(payload.get("record")).get("products"))
    out: Dict[str, dict] = {}
    for row in rows:
        normalized = normalize_product_row(row)
        product_id = str(normalized.get("product_id", "")).strip()
        if product_id:
            out[product_id] = normalized
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def compat_mode_rows_by_id(repo_root: str) -> Tuple[Dict[str, dict], str]:
    payload, error = load_compat_mode_registry(repo_root)
    if error:
        return {}, error
    rows = _as_list(_as_map(payload.get("record")).get("compat_modes"))
    out: Dict[str, dict] = {}
    for row in rows:
        compat_mode_id = str(_as_map(row).get("compat_mode_id", "")).strip()
        if compat_mode_id:
            out[compat_mode_id] = normalize_compat_mode_row(row)
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def degrade_ladder_rows_by_product_id(repo_root: str) -> Tuple[Dict[str, dict], str]:
    payload, error = load_degrade_ladder_registry(repo_root)
    if error:
        return {}, error
    rows = _as_list(_as_map(payload.get("record")).get("degrade_ladders"))
    out: Dict[str, dict] = {}
    for row in rows:
        row_map = _as_map(row)
        product_id = str(row_map.get("product_id", "")).strip()
        if not product_id:
            continue
        out[product_id] = {
            "schema_version": str(row_map.get("schema_version", "1.0.0")).strip() or "1.0.0",
            "ladder_id": str(row_map.get("ladder_id", "")).strip(),
            "product_id": product_id,
            "rules": [
                _normalize_degrade_rule(item)
                for item in sorted(
                    _as_list(row_map.get("rules")),
                    key=lambda item: (
                        int(_as_map(item).get("priority", 0) or 0),
                        str(_as_map(item).get("rule_id", "")),
                    ),
                )
            ],
            "deterministic_fingerprint": str(row_map.get("deterministic_fingerprint", "")).strip(),
            "extensions": _as_map(row_map.get("extensions")),
        }
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def fallback_map_rows_by_capability_id(repo_root: str) -> Tuple[Dict[str, dict], str]:
    payload, error = load_capability_fallback_registry(repo_root)
    if error:
        return {}, error
    rows = _as_list(_as_map(payload.get("record")).get("fallback_maps"))
    out: Dict[str, dict] = {}
    for row in rows:
        normalized = _normalize_fallback_map(row)
        capability_id = str(normalized.get("capability_id", "")).strip()
        if capability_id:
            out[capability_id] = normalized
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def product_default_degrade_ladders(repo_root: str, product_id: str) -> List[dict]:
    ladder_rows, _error = degrade_ladder_rows_by_product_id(repo_root)
    ladder_row = dict(ladder_rows.get(str(product_id).strip()) or {})
    if ladder_row:
        return [dict(row) for row in list(ladder_row.get("rules") or []) if isinstance(row, Mapping)]
    rows_by_id, rows_error = product_rows_by_id(repo_root)
    if rows_error:
        return []
    row = dict(rows_by_id.get(str(product_id).strip()) or {})
    return [dict(row) for row in list(row.get("default_degrade_ladders") or []) if isinstance(row, Mapping)]


def build_endpoint_descriptor(
    *,
    product_id: str,
    product_version: str,
    protocol_versions_supported: Sequence[Mapping[str, object]] | None,
    semantic_contract_versions_supported: Sequence[Mapping[str, object]] | None,
    feature_capabilities: Sequence[object] | None,
    required_capabilities: Sequence[object] | None,
    optional_capabilities: Sequence[object] | None,
    degrade_ladders: Sequence[Mapping[str, object]] | None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "product_id": str(product_id or "").strip(),
        "product_version": str(product_version or "").strip() or "0.0.0+unknown",
        "protocol_versions_supported": [
            _normalize_protocol_range(item)
            for item in sorted(list(protocol_versions_supported or []), key=lambda item: str(_as_map(item).get("protocol_id", "")))
        ],
        "semantic_contract_versions_supported": [
            _normalize_contract_range(item)
            for item in sorted(list(semantic_contract_versions_supported or []), key=lambda item: str(_as_map(item).get("contract_category_id", "")))
        ],
        "feature_capabilities": _sorted_tokens(feature_capabilities),
        "required_capabilities": _sorted_tokens(required_capabilities),
        "optional_capabilities": _sorted_tokens(optional_capabilities),
        "degrade_ladders": [
            _normalize_degrade_rule(item)
            for item in sorted(list(degrade_ladders or []), key=lambda item: (int(_as_map(item).get("priority", 0) or 0), str(_as_map(item).get("rule_id", ""))))
        ],
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_default_endpoint_descriptor(
    repo_root: str,
    *,
    product_id: str,
    product_version: str,
    feature_capabilities: Sequence[object] | None = None,
    required_capabilities: Sequence[object] | None = None,
    optional_capabilities: Sequence[object] | None = None,
    allow_read_only: bool = False,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    rows_by_id, error = product_rows_by_id(repo_root)
    if error:
        return {}
    row = dict(rows_by_id.get(str(product_id).strip()) or {})
    contract_ranges = list(row.get("default_semantic_contract_versions_supported") or [])
    if not contract_ranges:
        contract_ranges = _default_contract_ranges(repo_root)
    merged_extensions = dict(row.get("extensions") or {})
    merged_extensions.update(_as_map(extensions))
    if allow_read_only:
        merged_extensions["official.compat.read_only_allowed"] = True
    return build_endpoint_descriptor(
        product_id=str(product_id),
        product_version=str(product_version),
        protocol_versions_supported=list(row.get("default_protocol_versions_supported") or []),
        semantic_contract_versions_supported=contract_ranges,
        feature_capabilities=list(row.get("default_feature_capabilities") or []) + list(feature_capabilities or []),
        required_capabilities=list(row.get("default_required_capabilities") or []) + list(required_capabilities or []),
        optional_capabilities=list(row.get("default_optional_capabilities") or []) + list(optional_capabilities or []),
        degrade_ladders=product_default_degrade_ladders(repo_root, str(product_id)),
        extensions=merged_extensions,
    )


def _filter_known_capabilities(repo_root: str, values: Sequence[object] | None) -> Tuple[List[str], List[str]]:
    known, _error = capability_ids(repo_root)
    known_set = set(known)
    filtered = []
    ignored = []
    for token in _sorted_tokens(values):
        if token in known_set:
            filtered.append(token)
        else:
            ignored.append(token)
    return filtered, ignored


def _protocol_candidates(descriptor_a: Mapping[str, object], descriptor_b: Mapping[str, object]) -> List[dict]:
    candidates = []
    rows_a = list(descriptor_a.get("protocol_versions_supported") or [])
    rows_b = list(descriptor_b.get("protocol_versions_supported") or [])
    for row_a in rows_a:
        left = _normalize_protocol_range(row_a)
        for row_b in rows_b:
            right = _normalize_protocol_range(row_b)
            if str(left.get("protocol_id", "")) != str(right.get("protocol_id", "")):
                continue
            lower = max(_semver_tuple(left.get("min_version")), _semver_tuple(right.get("min_version")))
            upper = min(_semver_tuple(left.get("max_version")), _semver_tuple(right.get("max_version")))
            if upper < lower:
                continue
            candidates.append(
                {
                    "protocol_id": str(left.get("protocol_id", "")),
                    "protocol_version": _semver_text(upper),
                }
            )
    return sorted(
        candidates,
        key=lambda row: (
            _semver_tuple(row.get("protocol_version")),
            str(row.get("protocol_id", "")),
        ),
    )


def _contract_choice(descriptor_a: Mapping[str, object], descriptor_b: Mapping[str, object]) -> Tuple[dict, List[str]]:
    rows_a = {
        str(_normalize_contract_range(row).get("contract_category_id", "")): _normalize_contract_range(row)
        for row in list(descriptor_a.get("semantic_contract_versions_supported") or [])
    }
    rows_b = {
        str(_normalize_contract_range(row).get("contract_category_id", "")): _normalize_contract_range(row)
        for row in list(descriptor_b.get("semantic_contract_versions_supported") or [])
    }
    common = sorted(set(rows_a.keys()) | set(rows_b.keys()))
    chosen = {}
    mismatched = []
    for category_id in common:
        left = dict(rows_a.get(category_id) or {})
        right = dict(rows_b.get(category_id) or {})
        if not left or not right:
            mismatched.append(category_id)
            continue
        lower = max(int(left.get("min_version", 1) or 1), int(right.get("min_version", 1) or 1))
        upper = min(int(left.get("max_version", 1) or 1), int(right.get("max_version", 1) or 1))
        if upper < lower:
            mismatched.append(category_id)
            continue
        chosen[category_id] = _contract_id(category_id, upper)
    return dict((key, chosen[key]) for key in sorted(chosen.keys())), sorted(mismatched)


def _required_capability_mismatches(repo_root: str, descriptor_a: Mapping[str, object], descriptor_b: Mapping[str, object]) -> List[dict]:
    features_a, _ignored_a = _filter_known_capabilities(repo_root, descriptor_a.get("feature_capabilities"))
    features_b, _ignored_b = _filter_known_capabilities(repo_root, descriptor_b.get("feature_capabilities"))
    required_a, _ignored_req_a = _filter_known_capabilities(repo_root, descriptor_a.get("required_capabilities"))
    required_b, _ignored_req_b = _filter_known_capabilities(repo_root, descriptor_b.get("required_capabilities"))
    violations = []
    for capability_id in sorted(set(required_a) - set(features_b)):
        violations.append(
            {
                "owner_product_id": str(descriptor_a.get("product_id", "")),
                "capability_id": capability_id,
                "reason_code": REFUSAL_MISSING_REQUIRED_CAP,
            }
        )
    for capability_id in sorted(set(required_b) - set(features_a)):
        violations.append(
            {
                "owner_product_id": str(descriptor_b.get("product_id", "")),
                "capability_id": capability_id,
                "reason_code": REFUSAL_MISSING_REQUIRED_CAP,
            }
        )
    return violations


def _all_degrade_rules(descriptor_a: Mapping[str, object], descriptor_b: Mapping[str, object]) -> List[dict]:
    rows = []
    for owner_index, descriptor in enumerate((descriptor_a, descriptor_b), start=1):
        owner_product_id = str(descriptor.get("product_id", "")).strip()
        for rule in list(descriptor.get("degrade_ladders") or []):
            normalized = _normalize_degrade_rule(rule)
            normalized["extensions"] = dict(normalized.get("extensions") or {})
            normalized["owner_product_id"] = owner_product_id
            normalized["owner_index"] = owner_index
            rows.append(normalized)
    return sorted(
        rows,
        key=lambda row: (
            int(row.get("priority", 0) or 0),
            str(row.get("owner_product_id", "")),
            str(row.get("rule_id", "")),
        ),
    )


def _matching_degrade_rule(rules: Sequence[Mapping[str, object]], *, trigger_kind: str, trigger_id: str) -> dict:
    for row in list(rules or []):
        if str(row.get("trigger_kind", "")) != str(trigger_kind):
            continue
        row_trigger = str(row.get("trigger_id", "")).strip()
        if row_trigger == str(trigger_id).strip():
            return dict(row)
    return {}


def _fallback_map_row(repo_root: str, capability_id: str) -> dict:
    rows_by_capability, _error = fallback_map_rows_by_capability_id(repo_root)
    return dict(rows_by_capability.get(str(capability_id or "").strip()) or {})


def _rule_with_fallback_defaults(repo_root: str, capability_id: str, rule: Mapping[str, object] | None) -> dict:
    normalized = _normalize_degrade_rule(rule)
    fallback_row = _fallback_map_row(repo_root, capability_id)
    fallback_extensions = dict(fallback_row.get("extensions") or {})
    normalized_extensions = dict(normalized.get("extensions") or {})
    for key, value in sorted(fallback_extensions.items(), key=lambda item: str(item[0])):
        normalized_extensions.setdefault(str(key), value)
    if not str(normalized.get("action_kind", "")).strip() and str(fallback_row.get("fallback_action", "")).strip():
        normalized["action_kind"] = str(fallback_row.get("fallback_action", "")).strip()
    normalized["extensions"] = normalized_extensions
    return normalized


def _normalize_action_kind(action_kind: str) -> str:
    token = str(action_kind or "").strip()
    if token == "switch_to_read_only":
        return "force_read_only"
    return token


def _fallback_candidates(row: Mapping[str, object] | None) -> List[str]:
    extensions = dict((dict(row or {})).get("extensions") or {})
    return _sorted_tokens(
        list(extensions.get("fallback_capability_ids") or [])
        + list(extensions.get("substitute_capability_ids") or [])
        + [extensions.get("substitute_capability_id", "")]
    )


def _select_fallback_capability(row: Mapping[str, object] | None, available_capabilities: Sequence[str]) -> str:
    enabled = set(_sorted_tokens(available_capabilities))
    for capability_id in _fallback_candidates(row):
        if capability_id in enabled:
            return capability_id
    return ""


def _disable_row(
    *,
    capability_id: str,
    reason_code: str,
    owner_product_id: str = "",
    user_message_key: str = "",
) -> dict:
    return {
        "capability_id": str(capability_id or "").strip(),
        "reason_code": str(reason_code or "").strip(),
        "owner_product_id": str(owner_product_id or "").strip(),
        "user_message_key": str(user_message_key or "").strip(),
    }


def _substitution_row(
    *,
    capability_id: str,
    substitute_capability_id: str,
    action_kind: str,
    owner_product_id: str = "",
    user_message_key: str = "",
) -> dict:
    return {
        "capability_id": str(capability_id or "").strip(),
        "substitute_capability_id": str(substitute_capability_id or "").strip(),
        "action_kind": str(action_kind or "").strip(),
        "owner_product_id": str(owner_product_id or "").strip(),
        "user_message_key": str(user_message_key or "").strip(),
    }


def _degrade_plan(
    repo_root: str,
    *,
    owner_feature_capabilities: Mapping[str, object],
    optional_missing: Sequence[str],
    contract_mismatches: Sequence[str],
    rules: Sequence[Mapping[str, object]],
    allow_read_only: bool,
) -> Tuple[str, List[dict], List[dict], List[dict]]:
    rows: List[dict] = []
    disabled_rows: List[dict] = []
    substituted_rows: List[dict] = []
    mode_id = COMPAT_MODE_FULL
    for capability_id in _sorted_tokens(optional_missing):
        matched = _matching_degrade_rule(rules, trigger_kind="missing_optional_capability", trigger_id=capability_id)
        row = dict(matched or {})
        if not row:
            fallback_row = _fallback_map_row(repo_root, capability_id)
            fallback_action = str(fallback_row.get("fallback_action", "disable_feature")).strip() or "disable_feature"
            row = _normalize_degrade_rule(
                {
                    "schema_version": "1.0.0",
                    "rule_id": "degrade.{}".format(capability_id.replace(".", "_")),
                    "trigger_kind": "missing_optional_capability",
                    "trigger_id": capability_id,
                    "fallback_mode_id": COMPAT_MODE_DEGRADED,
                    "action_kind": fallback_action,
                    "priority": 999,
                    "extensions": dict(fallback_row.get("extensions") or {}),
                }
            )
        row = _rule_with_fallback_defaults(repo_root, capability_id, row)
        row_extensions = dict(row.get("extensions") or {})
        owner_product_id = str(row.get("owner_product_id", "")).strip()
        user_message_key = str(row_extensions.get("user_message_key", "")).strip()
        action_kind = _normalize_action_kind(str(row.get("action_kind", "")).strip())
        owner_available_capabilities = list(
            owner_feature_capabilities.get(owner_product_id, owner_feature_capabilities.get("*", [])) or []
        )
        substitute_capability_id = str(row_extensions.get("substitute_capability_id", "")).strip()
        if not substitute_capability_id:
            substitute_capability_id = _select_fallback_capability(row, owner_available_capabilities)
        if action_kind in ("substitute_stub", "downgrade_mode") and substitute_capability_id:
            substituted_rows.append(
                _substitution_row(
                    capability_id=capability_id,
                    substitute_capability_id=substitute_capability_id,
                    action_kind=action_kind,
                    owner_product_id=owner_product_id,
                    user_message_key=user_message_key,
                )
            )
            disabled_rows.append(
                _disable_row(
                    capability_id=capability_id,
                    reason_code="degrade.feature_substituted",
                    owner_product_id=owner_product_id,
                    user_message_key=user_message_key,
                )
            )
        else:
            disabled_rows.append(
                _disable_row(
                    capability_id=capability_id,
                    reason_code="degrade.optional_capability_unavailable",
                    owner_product_id=owner_product_id,
                    user_message_key=user_message_key,
                )
            )
        rows.append(row)
        if str(row.get("fallback_mode_id", "")) == COMPAT_MODE_DEGRADED:
            mode_id = COMPAT_MODE_DEGRADED
    if contract_mismatches:
        if allow_read_only:
            for category_id in sorted(contract_mismatches):
                matched = _matching_degrade_rule(rules, trigger_kind="contract_mismatch", trigger_id="semantic_contract_bundle")
                row = dict(matched or {})
                if not row:
                    row = _normalize_degrade_rule(
                        {
                            "schema_version": "1.0.0",
                            "rule_id": "degrade.contract.read_only.{}".format(category_id.replace(".", "_")),
                            "trigger_kind": "contract_mismatch",
                            "trigger_id": "semantic_contract_bundle",
                            "fallback_mode_id": COMPAT_MODE_READ_ONLY,
                            "action_kind": "switch_to_read_only",
                            "priority": 1000,
                            "extensions": {
                                "law_profile_id_override": READ_ONLY_LAW_PROFILE_ID,
                                "contract_category_id": category_id,
                                "user_message_key": "explain.compat_read_only",
                            },
                        }
                    )
                else:
                    row = dict(row)
                    row_extensions = dict(row.get("extensions") or {})
                    row_extensions["contract_category_id"] = category_id
                    row["extensions"] = row_extensions
                rows.append(row)
            mode_id = COMPAT_MODE_READ_ONLY
        else:
            mode_id = COMPAT_MODE_REFUSE
    return mode_id, rows, disabled_rows, substituted_rows


def _registry_hash(repo_root: str, loader) -> str:
    payload, error = loader(repo_root)
    if error or not isinstance(payload, dict):
        return ""
    return canonical_sha256(payload)


def _refusal_payload(reason_code: str, message: str, relevant_ids: Mapping[str, object] | None = None) -> dict:
    return {
        "reason_code": str(reason_code or "").strip(),
        "message": str(message or "").strip(),
        "relevant_ids": {
            str(key): str(value).strip()
            for key, value in sorted(dict(relevant_ids or {}).items(), key=lambda item: str(item[0]))
            if str(value).strip()
        },
    }


def negotiate_endpoint_descriptors(
    repo_root: str,
    descriptor_a: Mapping[str, object],
    descriptor_b: Mapping[str, object],
    *,
    allow_read_only: bool = False,
    chosen_contract_bundle_hash: str = "",
) -> dict:
    normalized_a = build_endpoint_descriptor(
        product_id=str(_as_map(descriptor_a).get("product_id", "")).strip(),
        product_version=str(_as_map(descriptor_a).get("product_version", "")).strip(),
        protocol_versions_supported=list(_as_map(descriptor_a).get("protocol_versions_supported") or []),
        semantic_contract_versions_supported=list(_as_map(descriptor_a).get("semantic_contract_versions_supported") or []),
        feature_capabilities=list(_as_map(descriptor_a).get("feature_capabilities") or []),
        required_capabilities=list(_as_map(descriptor_a).get("required_capabilities") or []),
        optional_capabilities=list(_as_map(descriptor_a).get("optional_capabilities") or []),
        degrade_ladders=list(_as_map(descriptor_a).get("degrade_ladders") or []),
        extensions=_as_map(_as_map(descriptor_a).get("extensions")),
    )
    normalized_b = build_endpoint_descriptor(
        product_id=str(_as_map(descriptor_b).get("product_id", "")).strip(),
        product_version=str(_as_map(descriptor_b).get("product_version", "")).strip(),
        protocol_versions_supported=list(_as_map(descriptor_b).get("protocol_versions_supported") or []),
        semantic_contract_versions_supported=list(_as_map(descriptor_b).get("semantic_contract_versions_supported") or []),
        feature_capabilities=list(_as_map(descriptor_b).get("feature_capabilities") or []),
        required_capabilities=list(_as_map(descriptor_b).get("required_capabilities") or []),
        optional_capabilities=list(_as_map(descriptor_b).get("optional_capabilities") or []),
        degrade_ladders=list(_as_map(descriptor_b).get("degrade_ladders") or []),
        extensions=_as_map(_as_map(descriptor_b).get("extensions")),
    )
    protocols = _protocol_candidates(normalized_a, normalized_b)
    chosen_protocol = dict(protocols[-1]) if protocols else {}
    contracts, contract_mismatches = _contract_choice(normalized_a, normalized_b)
    feature_a, ignored_feature_a = _filter_known_capabilities(repo_root, normalized_a.get("feature_capabilities"))
    feature_b, ignored_feature_b = _filter_known_capabilities(repo_root, normalized_b.get("feature_capabilities"))
    optional_a, ignored_optional_a = _filter_known_capabilities(repo_root, normalized_a.get("optional_capabilities"))
    optional_b, ignored_optional_b = _filter_known_capabilities(repo_root, normalized_b.get("optional_capabilities"))
    enabled_capabilities = sorted(set(feature_a) & set(feature_b))
    required_violations = _required_capability_mismatches(repo_root, normalized_a, normalized_b)
    optional_missing = sorted(set(optional_a + optional_b) - set(enabled_capabilities))
    rules = _all_degrade_rules(normalized_a, normalized_b)
    compatibility_mode_id, degrade_plan, disabled_rows, substituted_rows = _degrade_plan(
        repo_root,
        owner_feature_capabilities={
            str(normalized_a.get("product_id", "")).strip(): list(feature_a),
            str(normalized_b.get("product_id", "")).strip(): list(feature_b),
            "*": list(feature_a) + list(feature_b),
        },
        optional_missing=optional_missing,
        contract_mismatches=contract_mismatches,
        rules=rules,
        allow_read_only=bool(allow_read_only),
    )
    refusal_payload = {}
    if not chosen_protocol:
        compatibility_mode_id = COMPAT_MODE_REFUSE
        refusal_payload = _refusal_payload(
            REFUSAL_NO_COMMON_PROTOCOL,
            "no mutually supported protocol version exists for the endpoint pair",
            {
                "product_a": str(normalized_a.get("product_id", "")).strip(),
                "product_b": str(normalized_b.get("product_id", "")).strip(),
            },
        )
    elif required_violations:
        compatibility_mode_id = COMPAT_MODE_REFUSE
        first_violation = dict(required_violations[0])
        refusal_payload = _refusal_payload(
            REFUSAL_MISSING_REQUIRED_CAP,
            "a required capability is missing from the peer endpoint",
            {
                "owner_product_id": str(first_violation.get("owner_product_id", "")).strip(),
                "capability_id": str(first_violation.get("capability_id", "")).strip(),
            },
        )
    elif contract_mismatches and not allow_read_only:
        compatibility_mode_id = COMPAT_MODE_REFUSE
        refusal_payload = _refusal_payload(
            REFUSAL_CONTRACT_MISMATCH,
            "semantic contract ranges do not overlap and read-only compatibility is disabled",
            {"contract_category_id": ",".join(sorted(contract_mismatches))},
        )
    if compatibility_mode_id == COMPAT_MODE_REFUSE and not refusal_payload:
        refusal_payload = _refusal_payload(
            REFUSAL_CONTRACT_MISMATCH,
            "no lawful deterministic compatibility mode exists for the endpoint pair",
            {
                "product_a": str(normalized_a.get("product_id", "")).strip(),
                "product_b": str(normalized_b.get("product_id", "")).strip(),
            },
        )
    for capability_id in _sorted_tokens(list(ignored_feature_a) + list(ignored_optional_a) + list(ignored_feature_b) + list(ignored_optional_b)):
        disabled_rows.append(
            _disable_row(
                capability_id=capability_id,
                reason_code="ignored.unknown_capability",
            )
        )
    endpoint_hashes = {
        "endpoint_a_hash": canonical_sha256(normalized_a),
        "endpoint_b_hash": canonical_sha256(normalized_b),
    }
    substitution_rows_by_capability = {
        str(row.get("capability_id", "")).strip(): dict(row) for row in list(substituted_rows or []) if isinstance(row, Mapping)
    }
    record = {
        "schema_version": "1.0.0",
        "negotiation_id": "",
        "endpoints": [
            {
                "product_id": str(normalized_a.get("product_id", "")).strip(),
                "product_version": str(normalized_a.get("product_version", "")).strip(),
                "endpoint_descriptor_hash": str(endpoint_hashes.get("endpoint_a_hash", "")).strip(),
            },
            {
                "product_id": str(normalized_b.get("product_id", "")).strip(),
                "product_version": str(normalized_b.get("product_version", "")).strip(),
                "endpoint_descriptor_hash": str(endpoint_hashes.get("endpoint_b_hash", "")).strip(),
            },
        ],
        "chosen_protocol_version": str(chosen_protocol.get("protocol_version", "")).strip(),
        "chosen_protocol_id": str(chosen_protocol.get("protocol_id", "")).strip(),
        "chosen_semantic_contract_versions": dict((key, contracts[key]) for key in sorted(contracts.keys())),
        "enabled_capabilities": list(enabled_capabilities),
        "disabled_capabilities": list(disabled_rows),
        "substituted_capabilities": list(substituted_rows),
        "compatibility_mode_id": str(compatibility_mode_id).strip() or COMPAT_MODE_REFUSE,
        "degrade_plan": [
            {
                "rule_id": str(row.get("rule_id", "")).strip(),
                "trigger_kind": str(row.get("trigger_kind", "")).strip(),
                "trigger_id": str(row.get("trigger_id", "")).strip(),
                "fallback_mode_id": str(row.get("fallback_mode_id", "")).strip(),
                "action_kind": str(row.get("action_kind", "")).strip(),
                "priority": int(row.get("priority", 0) or 0),
                "owner_product_id": str(row.get("owner_product_id", "")).strip(),
                "user_message_key": str(dict(row.get("extensions") or {}).get("user_message_key", "")).strip(),
                "substitute_capability_id": str(
                    dict(substitution_rows_by_capability.get(str(row.get("trigger_id", "")).strip()) or {}).get(
                        "substitute_capability_id", ""
                    )
                ).strip(),
            }
            for row in list(degrade_plan or [])
        ],
        "input_hashes": {
            "capability_registry_hash": _registry_hash(repo_root, load_capability_registry),
            "product_registry_hash": _registry_hash(repo_root, load_product_registry),
            "compat_mode_registry_hash": _registry_hash(repo_root, load_compat_mode_registry),
            "semantic_contract_registry_hash": _registry_hash(repo_root, load_semantic_contract_registry),
            "degrade_ladder_registry_hash": _registry_hash(repo_root, load_degrade_ladder_registry),
            "capability_fallback_registry_hash": _registry_hash(repo_root, load_capability_fallback_registry),
            "chosen_contract_bundle_hash": str(chosen_contract_bundle_hash or "").strip(),
            "endpoint_a_hash": str(endpoint_hashes.get("endpoint_a_hash", "")).strip(),
            "endpoint_b_hash": str(endpoint_hashes.get("endpoint_b_hash", "")).strip(),
        },
        "deterministic_fingerprint": "",
        "extensions": {
            "official.compat.read_only_allowed": bool(allow_read_only),
            "official.compat.contract_mismatches": list(sorted(contract_mismatches)),
            "official.compat.required_capability_violations": list(required_violations),
            "official.compat.refusal": dict(refusal_payload),
            "official.compat.read_only_law_profile_id": READ_ONLY_LAW_PROFILE_ID if compatibility_mode_id == COMPAT_MODE_READ_ONLY else "",
            "official.compat.mode_forced": bool(
                str(compatibility_mode_id).strip() in (COMPAT_MODE_DEGRADED, COMPAT_MODE_READ_ONLY)
            ),
        },
    }
    record["endpoints"] = sorted(
        (dict(row) for row in record.get("endpoints") or []),
        key=lambda row: (str(row.get("product_id", "")), str(row.get("endpoint_descriptor_hash", ""))),
    )
    record["disabled_capabilities"] = sorted(
        (dict(row) for row in record.get("disabled_capabilities") or []),
        key=lambda row: (
            str(row.get("capability_id", "")),
            str(row.get("reason_code", "")),
            str(row.get("owner_product_id", "")),
        ),
    )
    record["substituted_capabilities"] = sorted(
        (dict(row) for row in record.get("substituted_capabilities") or []),
        key=lambda row: (
            str(row.get("capability_id", "")),
            str(row.get("substitute_capability_id", "")),
            str(row.get("owner_product_id", "")),
        ),
    )
    record["degrade_plan"] = sorted(
        (dict(row) for row in record.get("degrade_plan") or []),
        key=lambda row: (
            int(row.get("priority", 0) or 0),
            str(row.get("owner_product_id", "")),
            str(row.get("rule_id", "")),
        ),
    )
    record["negotiation_id"] = "neg.{}".format(
        canonical_sha256(
            {
                "endpoint_a_hash": str(endpoint_hashes.get("endpoint_a_hash", "")).strip(),
                "endpoint_b_hash": str(endpoint_hashes.get("endpoint_b_hash", "")).strip(),
                "chosen_protocol_id": str(record.get("chosen_protocol_id", "")).strip(),
                "chosen_protocol_version": str(record.get("chosen_protocol_version", "")).strip(),
                "compatibility_mode_id": str(record.get("compatibility_mode_id", "")).strip(),
            }
        )[:16]
    )
    record["deterministic_fingerprint"] = canonical_sha256(dict(record, deterministic_fingerprint=""))
    return {
        "result": "complete" if str(record.get("compatibility_mode_id", "")) != COMPAT_MODE_REFUSE else "refused",
        "negotiation_record": record,
        "negotiation_record_hash": canonical_sha256(record),
        "endpoint_a": normalized_a,
        "endpoint_b": normalized_b,
        "endpoint_a_hash": str(endpoint_hashes.get("endpoint_a_hash", "")).strip(),
        "endpoint_b_hash": str(endpoint_hashes.get("endpoint_b_hash", "")).strip(),
        "compatibility_mode_id": str(record.get("compatibility_mode_id", "")).strip(),
        "refusal": dict(refusal_payload),
    }


def verify_negotiation_record(
    repo_root: str,
    negotiation_record: Mapping[str, object],
    descriptor_a: Mapping[str, object],
    descriptor_b: Mapping[str, object],
    *,
    allow_read_only: bool = False,
    chosen_contract_bundle_hash: str = "",
) -> dict:
    expected = negotiate_endpoint_descriptors(
        repo_root,
        descriptor_a,
        descriptor_b,
        allow_read_only=allow_read_only,
        chosen_contract_bundle_hash=chosen_contract_bundle_hash,
    )
    expected_record = dict(expected.get("negotiation_record") or {})
    actual_record = dict(negotiation_record or {})
    if not actual_record:
        return {
            "result": "refused",
            "reason_code": "refusal.compat.negotiation_record_missing",
            "message": "negotiation record is missing",
        }
    expected_hash = canonical_sha256(expected_record)
    actual_hash = canonical_sha256(actual_record)
    if expected_hash != actual_hash:
        return {
            "result": "refused",
            "reason_code": "refusal.compat.negotiation_record_mismatch",
            "message": "negotiation record does not match deterministic negotiation output",
            "expected_hash": expected_hash,
            "actual_hash": actual_hash,
        }
    return {
        "result": "complete",
        "negotiation_record_hash": actual_hash,
        "compatibility_mode_id": str(actual_record.get("compatibility_mode_id", "")).strip(),
    }


__all__ = [
    "COMPAT_MODE_DEGRADED",
    "COMPAT_MODE_FULL",
    "COMPAT_MODE_READ_ONLY",
    "COMPAT_MODE_REFUSE",
    "DEFAULT_PROTOCOL_ID",
    "DEFAULT_PROTOCOL_VERSION",
    "READ_ONLY_LAW_PROFILE_ID",
    "REFUSAL_CONTRACT_MISMATCH",
    "REFUSAL_MISSING_REQUIRED_CAP",
    "REFUSAL_NO_COMMON_PROTOCOL",
    "build_default_endpoint_descriptor",
    "build_endpoint_descriptor",
    "capability_ids",
    "compat_mode_rows_by_id",
    "load_capability_registry",
    "load_compat_mode_registry",
    "load_product_registry",
    "load_semantic_contract_registry",
    "negotiate_endpoint_descriptors",
    "normalize_compat_mode_row",
    "normalize_product_row",
    "product_rows_by_id",
    "semantic_contract_rows_by_category",
    "verify_negotiation_record",
]

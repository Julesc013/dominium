"""Deterministic runtime enforcement for negotiated CAP-NEG degrade state."""

from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_COMPAT_FEATURE_DISABLED = "refusal.compat.feature_disabled"
DEFAULT_UI_CAPABILITY_PREFERENCE = (
    "cap.ui.rendered",
    "cap.ui.tui",
    "cap.ui.cli",
)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _sorted_rows(rows: object, *keys: str) -> List[dict]:
    values = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    return sorted(values, key=lambda row: tuple(str(row.get(key, "")).strip() for key in keys))


def _substitution_by_capability(rows: Sequence[Mapping[str, object]] | None) -> dict:
    out = {}
    for row in _sorted_rows(rows, "capability_id", "substitute_capability_id", "owner_product_id"):
        capability_id = str(row.get("capability_id", "")).strip()
        if capability_id and capability_id not in out:
            out[capability_id] = dict(row)
    return out


def _disabled_by_capability(rows: Sequence[Mapping[str, object]] | None) -> dict:
    out = {}
    for row in _sorted_rows(rows, "capability_id", "reason_code", "owner_product_id"):
        capability_id = str(row.get("capability_id", "")).strip()
        if capability_id and capability_id not in out:
            out[capability_id] = dict(row)
    return out


def _effective_ui_capability_id(
    enabled_capability_ids: Sequence[str],
    substituted_by_capability: Mapping[str, object],
    preferred_ui_capabilities: Sequence[str],
) -> str:
    enabled = set(_sorted_tokens(enabled_capability_ids))
    for capability_id in list(preferred_ui_capabilities or DEFAULT_UI_CAPABILITY_PREFERENCE):
        token = str(capability_id or "").strip()
        if not token:
            continue
        if token in enabled:
            return token
        row = dict(substituted_by_capability.get(token) or {})
        substitute_capability_id = str(row.get("substitute_capability_id", "")).strip()
        if substitute_capability_id:
            return substitute_capability_id
    for capability_id in DEFAULT_UI_CAPABILITY_PREFERENCE:
        if capability_id in enabled:
            return capability_id
    return ""


def _mode_label_from_ui_capability(capability_id: str) -> str:
    token = str(capability_id or "").strip()
    if token == "cap.ui.rendered":
        return "rendered"
    if token == "cap.ui.tui":
        return "tui"
    if token == "cap.ui.cli":
        return "cli"
    return ""


def build_degrade_runtime_state(
    negotiation_record: Mapping[str, object] | None,
    *,
    preferred_ui_capabilities: Sequence[str] | None = None,
) -> dict:
    record = _as_map(negotiation_record)
    enabled_capability_ids = _sorted_tokens(record.get("enabled_capabilities"))
    disabled_rows = _sorted_rows(record.get("disabled_capabilities"), "capability_id", "reason_code", "owner_product_id")
    substituted_rows = _sorted_rows(
        record.get("substituted_capabilities"),
        "capability_id",
        "substitute_capability_id",
        "owner_product_id",
    )
    disabled_by_capability = _disabled_by_capability(disabled_rows)
    substituted_by_capability = _substitution_by_capability(substituted_rows)
    effective_ui_capability_id = _effective_ui_capability_id(
        enabled_capability_ids,
        substituted_by_capability,
        list(preferred_ui_capabilities or DEFAULT_UI_CAPABILITY_PREFERENCE),
    )
    payload = {
        "result": "complete",
        "compatibility_mode_id": str(record.get("compatibility_mode_id", "")).strip(),
        "enabled_capability_ids": list(enabled_capability_ids),
        "disabled_capability_ids": _sorted_tokens(disabled_by_capability.keys()),
        "disabled_capabilities": list(disabled_rows),
        "substituted_capabilities": list(substituted_rows),
        "effective_ui_capability_id": effective_ui_capability_id,
        "effective_ui_mode": _mode_label_from_ui_capability(effective_ui_capability_id),
        "explain_keys": _sorted_tokens(
            [row.get("user_message_key", "") for row in disabled_rows]
            + [row.get("user_message_key", "") for row in substituted_rows]
            + [
                "explain.compat_read_only"
                if str(record.get("compatibility_mode_id", "")).strip() == "compat.read_only"
                else ""
            ]
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def enforce_negotiated_capability(
    runtime_state: Mapping[str, object] | None,
    *,
    capability_id: str,
    action_label: str,
) -> dict:
    state = _as_map(runtime_state)
    capability_token = str(capability_id or "").strip()
    disabled_by_capability = _disabled_by_capability(state.get("disabled_capabilities"))
    substituted_by_capability = _substitution_by_capability(state.get("substituted_capabilities"))
    disabled_row = dict(disabled_by_capability.get(capability_token) or {})
    substituted_row = dict(substituted_by_capability.get(capability_token) or {})
    if not disabled_row and not substituted_row:
        return {"result": "complete"}
    details = {
        "capability_id": capability_token,
        "compatibility_mode_id": str(state.get("compatibility_mode_id", "")).strip(),
        "action_label": str(action_label or "").strip(),
        "substitute_capability_id": str(substituted_row.get("substitute_capability_id", "")).strip(),
        "owner_product_id": str((disabled_row or substituted_row).get("owner_product_id", "")).strip(),
        "explain_key": str((disabled_row or substituted_row).get("user_message_key", "")).strip() or "explain.feature_disabled",
    }
    payload = {
        "result": "refused",
        "reason_code": REFUSAL_COMPAT_FEATURE_DISABLED,
        "message": "feature is disabled by the negotiated compatibility mode",
        "details": dict((key, value) for key, value in sorted(details.items()) if str(value).strip()),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_compat_status_payload(
    negotiation_record: Mapping[str, object] | None,
    *,
    product_id: str = "",
    connection_id: str = "",
) -> dict:
    runtime_state = build_degrade_runtime_state(negotiation_record)
    payload = {
        "result": "complete",
        "product_id": str(product_id or "").strip(),
        "connection_id": str(connection_id or "").strip(),
        "compatibility_mode_id": str(runtime_state.get("compatibility_mode_id", "")).strip(),
        "effective_ui_mode": str(runtime_state.get("effective_ui_mode", "")).strip(),
        "disabled_capabilities": list(runtime_state.get("disabled_capabilities") or []),
        "substituted_capabilities": list(runtime_state.get("substituted_capabilities") or []),
        "explain_keys": list(runtime_state.get("explain_keys") or []),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_UI_CAPABILITY_PREFERENCE",
    "REFUSAL_COMPAT_FEATURE_DISABLED",
    "build_compat_status_payload",
    "build_degrade_runtime_state",
    "enforce_negotiated_capability",
]

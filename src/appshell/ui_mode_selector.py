"""Deterministic AppShell UI mode selection and degrade reporting."""

from __future__ import annotations

import json
import os
from typing import Iterable, Mapping, Sequence

from src.compat.capability_negotiation import fallback_map_rows_by_capability_id
from src.platform.platform_caps_probe import probe_platform_caps
from tools.xstack.compatx.canonical_json import canonical_sha256


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
UI_MODE_POLICY_REGISTRY_REL = os.path.join("data", "registries", "ui_mode_policy_registry.json")
MODE_TO_CAPABILITY_ID = {
    "os_native": "cap.ui.os_native",
    "rendered": "cap.ui.rendered",
    "tui": "cap.ui.tui",
    "cli": "cap.ui.cli",
}
EXPLICIT_LEGACY_MODE_IDS = {"headless"}

_CURRENT_UI_MODE_SELECTION: dict | None = None


def _token(value: object) -> str:
    return str(value or "").strip()


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted({_token(item) for item in list(values or []) if _token(item)})


def _ordered_tokens(values: Iterable[object]) -> list[str]:
    out: list[str] = []
    for item in list(values or []):
        token = _token(item)
        if token and token not in out:
            out.append(token)
    return out


def _repo_root(repo_root: str = "") -> str:
    token = _token(repo_root)
    return os.path.normpath(os.path.abspath(token or REPO_ROOT_HINT))


def _normalize_policy_row(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    gui_mode_order = _ordered_tokens(payload.get("gui_mode_order"))
    tty_mode_order = _ordered_tokens(payload.get("tty_mode_order"))
    headless_mode_order = _ordered_tokens(payload.get("headless_mode_order"))
    legacy_mode_ids = _ordered_tokens(payload.get("legacy_mode_ids"))
    supported = []
    for mode_id in gui_mode_order + tty_mode_order + headless_mode_order + legacy_mode_ids:
        if mode_id not in supported:
            supported.append(mode_id)
    normalized = {
        "schema_version": _token(payload.get("schema_version")) or "1.0.0",
        "product_id": _token(payload.get("product_id")),
        "gui_mode_order": list(gui_mode_order),
        "tty_mode_order": list(tty_mode_order),
        "headless_mode_order": list(headless_mode_order),
        "legacy_mode_ids": list(legacy_mode_ids),
        "supported_mode_ids": list(supported),
        "rendered_allowed": bool(payload.get("rendered_allowed", True)),
        "extensions": _as_map(payload.get("extensions")),
        "stability": _as_map(payload.get("stability")),
        "deterministic_fingerprint": _token(payload.get("deterministic_fingerprint")),
    }
    if not normalized["deterministic_fingerprint"]:
        normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def load_ui_mode_policy_registry(repo_root: str = "") -> tuple[dict, str]:
    payload, error = _read_json(os.path.join(_repo_root(repo_root), UI_MODE_POLICY_REGISTRY_REL))
    if error:
        return {}, error
    record = _as_map(payload.get("record"))
    policies: list[dict] = []
    rows = sorted(_as_list(record.get("policies")), key=lambda item: _token(_as_map(item).get("product_id")))
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        policies.append(_normalize_policy_row(row))
    record["policies"] = policies
    return {
        "schema_id": _token(payload.get("schema_id")),
        "schema_version": _token(payload.get("schema_version")),
        "record": record,
    }, ""


def policy_row_for_product(repo_root: str, product_id: str) -> dict:
    payload, _error = load_ui_mode_policy_registry(repo_root)
    for row in _as_list(_as_map(payload.get("record")).get("policies")):
        row_map = _as_map(row)
        if _token(row_map.get("product_id")) == _token(product_id):
            return row_map
    return {}


def supported_modes_for_product(product_id: str, repo_root: str = "") -> list[str]:
    return list(_as_map(policy_row_for_product(repo_root, product_id)).get("supported_mode_ids") or [])


def default_mode_for_product(product_id: str, repo_root: str = "", context_kind: str = "tty") -> str:
    policy = _as_map(policy_row_for_product(repo_root, product_id))
    if _token(context_kind) == "gui":
        order = _as_list(policy.get("gui_mode_order"))
    elif _token(context_kind) == "headless":
        order = _as_list(policy.get("headless_mode_order"))
    else:
        order = _as_list(policy.get("tty_mode_order"))
    return _token(order[0] if order else "")


def _mode_available(mode_id: str, probe: Mapping[str, object]) -> bool:
    if _token(mode_id) == "headless":
        return True
    available_modes = _as_map(probe.get("available_modes"))
    return bool(available_modes.get(_token(mode_id), False))


def _fallback_modes_for_capability(repo_root: str, capability_id: str) -> tuple[list[str], str]:
    rows_by_capability, _error = fallback_map_rows_by_capability_id(_repo_root(repo_root))
    row = _as_map(rows_by_capability.get(_token(capability_id)))
    extensions = _as_map(row.get("extensions"))
    modes = []
    for fallback_capability_id in _as_list(extensions.get("fallback_capability_ids")):
        for mode_id, token in MODE_TO_CAPABILITY_ID.items():
            if token == _token(fallback_capability_id):
                modes.append(mode_id)
                break
    return _sorted_tokens(modes), _token(extensions.get("user_message_key"))


def _refusal(
    product_id: str,
    requested_mode_id: str,
    supported_mode_ids: Sequence[str],
    *,
    refusal_code: str,
    message: str,
    remediation_hint: str,
    degrade_chain: Sequence[Mapping[str, object]] | None = None,
) -> dict:
    payload = {
        "result": "refused",
        "product_id": _token(product_id),
        "requested_mode_id": _token(requested_mode_id),
        "supported_mode_ids": list(_sorted_tokens(supported_mode_ids)),
        "selected_mode_id": "",
        "context_kind": "",
        "mode_source": "",
        "compatibility_mode_id": "compat.refuse",
        "degrade_chain": [dict(row) for row in list(degrade_chain or []) if isinstance(row, Mapping)],
        "refusal_code": _token(refusal_code),
        "message": _token(message),
        "remediation_hint": _token(remediation_hint),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _explicit_mode_selection(
    repo_root: str,
    *,
    product_id: str,
    requested_mode_id: str,
    supported_mode_ids: Sequence[str],
    probe: Mapping[str, object],
) -> dict:
    requested = _token(requested_mode_id).lower()
    if requested not in set(_sorted_tokens(supported_mode_ids)):
        return _refusal(
            product_id,
            requested,
            supported_mode_ids,
            refusal_code="refusal.debug.mode_unsupported",
            message="requested shell mode is not supported by this product",
            remediation_hint="Choose one of the declared AppShell modes for the product.",
        )
    if _mode_available(requested, probe):
        return {
            "result": "complete",
            "selected_mode_id": requested,
            "degrade_chain": [],
            "compatibility_mode_id": "compat.full",
        }
    if requested == "headless":
        return _refusal(
            product_id,
            requested,
            supported_mode_ids,
            refusal_code="refusal.compat.feature_disabled",
            message="requested headless mode is not available in the current shell context",
            remediation_hint="Use --mode cli or --mode tui for interactive shells, or launch from a non-interactive host.",
        )
    current = requested
    seen = set()
    degrade_chain: list[dict] = []
    while current and current not in seen:
        seen.add(current)
        capability_id = _token(MODE_TO_CAPABILITY_ID.get(current))
        fallback_modes, user_message_key = _fallback_modes_for_capability(repo_root, capability_id)
        next_mode = ""
        for candidate in fallback_modes:
            if candidate not in set(_sorted_tokens(supported_mode_ids)):
                continue
            next_mode = candidate
            degrade_chain.append(
                {
                    "from_mode_id": current,
                    "to_mode_id": candidate,
                    "step_kind": "capability_fallback",
                    "trigger_capability_id": capability_id,
                    "user_message_key": user_message_key,
                }
            )
            break
        if not next_mode:
            break
        if _mode_available(next_mode, probe):
            return {
                "result": "complete",
                "selected_mode_id": next_mode,
                "degrade_chain": degrade_chain,
                "compatibility_mode_id": "compat.degraded",
            }
        current = next_mode
    return _refusal(
        product_id,
        requested,
        supported_mode_ids,
        refusal_code="refusal.compat.feature_disabled",
        message="requested shell mode is unavailable and no deterministic fallback remained",
        remediation_hint="Choose a different explicit --mode or launch in a shell context that exposes the requested UI capability.",
        degrade_chain=degrade_chain,
    )


def _policy_order_for_context(policy: Mapping[str, object], context_kind: str) -> list[str]:
    token = _token(context_kind)
    if token == "gui":
        return list(_as_list(policy.get("gui_mode_order")))
    if token == "headless":
        return list(_as_list(policy.get("headless_mode_order")))
    return list(_as_list(policy.get("tty_mode_order")))


def _policy_mode_selection(
    repo_root: str,
    *,
    product_id: str,
    context_kind: str,
    policy: Mapping[str, object],
    probe: Mapping[str, object],
) -> dict:
    order = _policy_order_for_context(policy, context_kind)
    supported = set(_sorted_tokens(policy.get("supported_mode_ids")))
    if not order:
        return _refusal(
            product_id,
            "",
            list(supported),
            refusal_code="refusal.debug.mode_unsupported",
            message="product does not declare a shell policy for the current context",
            remediation_hint="Declare the product in ui_mode_policy_registry before launch.",
        )
    degrade_chain: list[dict] = []
    for index, mode_id in enumerate(order):
        mode_token = _token(mode_id)
        if mode_token not in supported:
            continue
        if _mode_available(mode_token, probe):
            return {
                "result": "complete",
                "selected_mode_id": mode_token,
                "degrade_chain": degrade_chain,
                "compatibility_mode_id": "compat.degraded" if degrade_chain else "compat.full",
            }
        next_mode = ""
        for candidate in order[index + 1 :]:
            candidate_token = _token(candidate)
            if candidate_token in supported:
                next_mode = candidate_token
                break
        if next_mode:
            capability_id = _token(MODE_TO_CAPABILITY_ID.get(mode_token))
            _fallback_modes, user_message_key = _fallback_modes_for_capability(repo_root, capability_id)
            degrade_chain.append(
                {
                    "from_mode_id": mode_token,
                    "to_mode_id": next_mode,
                    "step_kind": "policy_order",
                    "trigger_capability_id": capability_id,
                    "user_message_key": user_message_key,
                }
            )
    return _refusal(
        product_id,
        "",
        list(supported),
        refusal_code="refusal.compat.feature_disabled",
        message="no UI mode is available for the current shell context",
        remediation_hint="Retry with an explicit --mode cli, or launch from a TTY/GUI host that satisfies the product policy.",
        degrade_chain=degrade_chain,
    )


def select_ui_mode(
    repo_root: str,
    *,
    product_id: str,
    mode_resolution: Mapping[str, object] | None = None,
    probe_override: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = _repo_root(repo_root)
    product_token = _token(product_id)
    policy = _as_map(policy_row_for_product(repo_root_abs, product_token))
    supported_mode_ids = list(_as_list(policy.get("supported_mode_ids")))
    resolution = _as_map(mode_resolution)
    requested_mode_id = _token(resolution.get("requested_mode_id")).lower()
    mode_source = _token(resolution.get("mode_source")) or "default"
    probe = (
        dict(probe_override)
        if isinstance(probe_override, Mapping)
        else probe_platform_caps(repo_root_abs, product_id=product_token)
    )
    context_kind = _token(probe.get("context_kind")) or "headless"

    if requested_mode_id:
        selected = _explicit_mode_selection(
            repo_root_abs,
            product_id=product_token,
            requested_mode_id=requested_mode_id,
            supported_mode_ids=supported_mode_ids,
            probe=probe,
        )
    else:
        selected = _policy_mode_selection(
            repo_root_abs,
            product_id=product_token,
            context_kind=context_kind,
            policy=policy,
            probe=probe,
        )

    payload = {
        "result": _token(selected.get("result")) or "refused",
        "product_id": product_token,
        "requested_mode_id": requested_mode_id,
        "selected_mode_id": _token(selected.get("selected_mode_id")),
        "effective_mode_id": _token(selected.get("selected_mode_id")),
        "mode_source": mode_source if requested_mode_id else "{}_policy".format(context_kind),
        "mode_requested": bool(resolution.get("mode_requested", False)),
        "context_kind": context_kind,
        "supported_mode_ids": list(supported_mode_ids),
        "available_mode_ids": list(_as_list(probe.get("available_mode_ids"))),
        "compatibility_mode_id": _token(selected.get("compatibility_mode_id")) or "compat.refuse",
        "degrade_chain": [dict(row) for row in list(selected.get("degrade_chain") or []) if isinstance(row, Mapping)],
        "probe": dict(probe),
        "policy": dict(policy),
        "refusal_code": _token(selected.get("refusal_code")),
        "message": _token(selected.get("message")),
        "remediation_hint": _token(selected.get("remediation_hint")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def set_current_ui_mode_selection(selection: Mapping[str, object] | None) -> None:
    global _CURRENT_UI_MODE_SELECTION
    _CURRENT_UI_MODE_SELECTION = dict(selection or {}) if isinstance(selection, Mapping) else None


def get_current_ui_mode_selection() -> dict:
    return dict(_CURRENT_UI_MODE_SELECTION or {})


def clear_current_ui_mode_selection() -> None:
    set_current_ui_mode_selection(None)


__all__ = [
    "EXPLICIT_LEGACY_MODE_IDS",
    "MODE_TO_CAPABILITY_ID",
    "UI_MODE_POLICY_REGISTRY_REL",
    "clear_current_ui_mode_selection",
    "default_mode_for_product",
    "get_current_ui_mode_selection",
    "load_ui_mode_policy_registry",
    "policy_row_for_product",
    "select_ui_mode",
    "set_current_ui_mode_selection",
    "supported_modes_for_product",
]

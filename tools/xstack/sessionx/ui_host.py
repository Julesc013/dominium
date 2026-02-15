"""Descriptor-driven headless UI host for lab tooling windows."""

from __future__ import annotations

import copy
import os
import re
import unicodedata
from typing import Dict, List, Tuple

from tools.xstack.compatx.validator import validate_instance

from .common import refusal
from .scheduler import execute_single_intent_srz


SELECTOR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\[(?:\d+|\*)\])?(?:\.[A-Za-z_][A-Za-z0-9_]*(?:\[(?:\d+|\*)\])?)*$")
TEMPLATE_RE = re.compile(r"^\$\{([^}]+)\}$")
REPO_ROOT_HINT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def _sorted_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


def _normalize_query(value: object) -> str:
    token = str(value).strip().lower()
    if not token:
        return ""
    token = unicodedata.normalize("NFKD", token)
    token = token.encode("ascii", "ignore").decode("ascii")
    return " ".join(token.split())


def _selector_parts(selector: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for chunk in str(selector).split("."):
        if "[" in chunk and chunk.endswith("]"):
            name = chunk[: chunk.index("[")]
            index = chunk[chunk.index("[") + 1 : -1]
            out.append((name, index))
        else:
            out.append((chunk, ""))
    return out


def selector_get(payload: object, selector: str):
    token = str(selector).strip()
    if not SELECTOR_RE.fullmatch(token):
        return None
    current = payload
    for name, idx in _selector_parts(token):
        if not isinstance(current, dict):
            return None
        current = current.get(name)
        if idx == "":
            continue
        if not isinstance(current, list):
            return None
        if idx == "*":
            current = list(current)
            continue
        try:
            index = int(idx)
        except ValueError:
            return None
        if index < 0 or index >= len(current):
            return None
        current = current[index]
    return current


def _walk_widgets(widget: object) -> List[dict]:
    if not isinstance(widget, dict):
        return []
    out = [widget]
    children = widget.get("children")
    if isinstance(children, list):
        for item in children:
            out.extend(_walk_widgets(item))
    return out


def _window_by_id(ui_registry: dict, window_id: str) -> dict:
    for row in sorted(ui_registry.get("windows") or [], key=lambda item: str(item.get("window_id", ""))):
        if not isinstance(row, dict):
            continue
        if str(row.get("window_id", "")) == str(window_id):
            return dict(row)
    return {}


def _gating_failure(window: dict, law_profile: dict, authority_context: dict, perceived_model: dict) -> dict:
    lens_id = str((perceived_model.get("lens_id") if isinstance(perceived_model, dict) else "") or "")
    required_lenses = _sorted_tokens(list(window.get("required_lenses") or []))
    if required_lenses and lens_id not in required_lenses:
        return {
            "reason_code": "LENS_FORBIDDEN",
            "message": "window '{}' requires lens in {}".format(
                str(window.get("window_id", "")),
                ",".join(required_lenses),
            ),
            "relevant_ids": {
                "window_id": str(window.get("window_id", "")),
                "lens_id": lens_id,
            },
        }
    debug_allowances = law_profile.get("debug_allowances")
    if isinstance(debug_allowances, dict) and not bool(debug_allowances.get("allow_nondiegetic_overlays", False)):
        return {
            "reason_code": "LENS_FORBIDDEN",
            "message": "window '{}' unavailable under current law debug allowances".format(str(window.get("window_id", ""))),
            "relevant_ids": {
                "window_id": str(window.get("window_id", "")),
                "law_profile_id": str(law_profile.get("law_profile_id", "")),
            },
        }
    required_entitlements = _sorted_tokens(list(window.get("required_entitlements") or []))
    entitlements = _sorted_tokens(list(authority_context.get("entitlements") or []))
    missing = [token for token in required_entitlements if token not in entitlements]
    if missing:
        return {
            "reason_code": "ENTITLEMENT_MISSING",
            "message": "window '{}' missing entitlements {}".format(
                str(window.get("window_id", "")),
                ",".join(missing),
            ),
            "relevant_ids": {
                "window_id": str(window.get("window_id", "")),
                "missing_entitlements": ",".join(missing),
            },
        }
    return {}


def available_windows(
    ui_registry: dict,
    law_profile: dict,
    authority_context: dict,
    perceived_model: dict,
) -> Dict[str, object]:
    available: List[dict] = []
    unavailable: List[dict] = []
    tool_log: List[dict] = []
    for window in sorted(ui_registry.get("windows") or [], key=lambda item: str(item.get("window_id", ""))):
        if not isinstance(window, dict):
            continue
        failure = _gating_failure(window=window, law_profile=law_profile, authority_context=authority_context, perceived_model=perceived_model)
        if failure:
            unavailable.append(
                {
                    "window_id": str(window.get("window_id", "")),
                    "reason_code": str(failure.get("reason_code", "")),
                    "message": str(failure.get("message", "")),
                }
            )
            tool_log.append(
                {
                    "entry_type": "window_unavailable",
                    "window_id": str(window.get("window_id", "")),
                    "reason_code": str(failure.get("reason_code", "")),
                    "message": str(failure.get("message", "")),
                    "relevant_ids": dict(failure.get("relevant_ids") or {}),
                }
            )
            continue
        available.append(dict(window))
    return {
        "result": "complete",
        "available_windows": available,
        "unavailable_windows": unavailable,
        "tool_log": tool_log,
    }


def _resolve_template_value(value: object, perceived_model: dict, widget_state: dict, selection: dict):
    if isinstance(value, dict):
        out = {}
        for key in sorted(value.keys()):
            out[str(key)] = _resolve_template_value(value.get(key), perceived_model, widget_state, selection)
        return out
    if isinstance(value, list):
        return [_resolve_template_value(item, perceived_model, widget_state, selection) for item in value]
    if not isinstance(value, str):
        return value

    match = TEMPLATE_RE.fullmatch(value.strip())
    if not match:
        return value
    token = str(match.group(1))
    if token.startswith("widget."):
        return widget_state.get(token[len("widget.") :])
    if token.startswith("selection."):
        return selection.get(token[len("selection.") :])
    if token.startswith("perceived."):
        selector = token[len("perceived.") :]
        return selector_get(perceived_model, selector)
    return value


def _widget_action(window: dict, widget_id: str) -> dict:
    for widget in _walk_widgets(window.get("widgets")):
        if str(widget.get("widget_id", "")) != str(widget_id):
            continue
        action = widget.get("action_binding")
        if isinstance(action, dict):
            return dict(action)
    return {}


def build_intent_from_action(
    window: dict,
    widget_id: str,
    perceived_model: dict,
    authority_context: dict,
    widget_state: dict | None = None,
    selection: dict | None = None,
    sequence: int = 0,
) -> Dict[str, object]:
    action = _widget_action(window=window, widget_id=widget_id)
    if not action:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "no action_binding for widget '{}' in window '{}'".format(widget_id, str(window.get("window_id", ""))),
            "Select a widget that declares action_binding in the window descriptor.",
            {"window_id": str(window.get("window_id", "")), "widget_id": str(widget_id)},
            "$.widgets",
        )
    state = dict(widget_state or {})
    selected = dict(selection or {})
    payload = _resolve_template_value(
        action.get("payload_template"),
        perceived_model=perceived_model if isinstance(perceived_model, dict) else {},
        widget_state=state,
        selection=selected,
    )
    if not isinstance(payload, dict):
        payload = {}

    for key in ("target_object_id", "target_site_id"):
        value = payload.get(key)
        if str(value).strip():
            continue
        if key in payload:
            del payload[key]

    intent_id = "{}.{:04d}".format(str(action.get("intent_id", "")), max(0, int(sequence)))
    intent = {
        "intent_id": intent_id,
        "process_id": str(action.get("process_id", "")),
        "authority_context_ref": {
            "authority_origin": str(authority_context.get("authority_origin", "")),
            "law_profile_id": str(authority_context.get("law_profile_id", "")),
        },
        "inputs": payload,
    }
    return {
        "result": "complete",
        "intent": intent,
    }


def _append_log(tool_log: List[dict], row: dict) -> List[dict]:
    out = list(tool_log or [])
    out.append(dict(row))
    return out


def with_search_results(perceived_model: dict, query: str) -> dict:
    payload = copy.deepcopy(perceived_model if isinstance(perceived_model, dict) else {})
    navigation = payload.get("navigation")
    sites = payload.get("sites")
    if not isinstance(navigation, dict):
        return payload
    if not isinstance(sites, dict):
        sites = {}
    normalized = _normalize_query(query)
    object_ids = list((navigation.get("search_index") or {}).get(normalized) or [])
    site_ids = list((sites.get("search_index") or {}).get(normalized) or [])
    rows = []
    for object_id in sorted(set(str(item).strip() for item in object_ids if str(item).strip())):
        rows.append({"kind": "object", "object_id": object_id, "site_id": ""})
    for site_id in sorted(set(str(item).strip() for item in site_ids if str(item).strip())):
        rows.append({"kind": "site", "object_id": "", "site_id": site_id})
    navigation["search_results"] = rows
    payload["navigation"] = navigation
    return payload


def dispatch_window_action(
    ui_registry: dict,
    window_id: str,
    widget_id: str,
    perceived_model: dict,
    universe_state: dict,
    law_profile: dict,
    authority_context: dict,
    navigation_indices: dict | None = None,
    widget_state: dict | None = None,
    selection: dict | None = None,
    sequence: int = 0,
    tool_log: List[dict] | None = None,
) -> Dict[str, object]:
    log_rows = list(tool_log or [])
    window = _window_by_id(ui_registry=ui_registry, window_id=window_id)
    if not window:
        refused = refusal(
            "PROCESS_INPUT_INVALID",
            "window '{}' is not present in ui registry".format(window_id),
            "Select a valid window_id compiled into ui.registry.",
            {"window_id": str(window_id)},
            "$.window_id",
        )
        refused["tool_log"] = _append_log(
            log_rows,
            {
                "entry_type": "refusal",
                "window_id": str(window_id),
                "reason_code": "PROCESS_INPUT_INVALID",
                "message": "window not found",
            },
        )
        return refused

    gating = _gating_failure(window=window, law_profile=law_profile, authority_context=authority_context, perceived_model=perceived_model)
    if gating:
        refused = refusal(
            str(gating.get("reason_code", "ENTITLEMENT_MISSING")),
            str(gating.get("message", "")),
            "Grant required entitlements/lens permissions or switch to an allowed profile.",
            dict(gating.get("relevant_ids") or {}),
            "$.window_id",
        )
        refused["tool_log"] = _append_log(
            log_rows,
            {
                "entry_type": "refusal",
                "window_id": str(window_id),
                "reason_code": str(gating.get("reason_code", "")),
                "message": str(gating.get("message", "")),
                "relevant_ids": dict(gating.get("relevant_ids") or {}),
            },
        )
        return refused

    built = build_intent_from_action(
        window=window,
        widget_id=widget_id,
        perceived_model=perceived_model,
        authority_context=authority_context,
        widget_state=widget_state or {},
        selection=selection or {},
        sequence=sequence,
    )
    if built.get("result") != "complete":
        built["tool_log"] = _append_log(
            log_rows,
            {
                "entry_type": "refusal",
                "window_id": str(window_id),
                "reason_code": str((built.get("refusal") or {}).get("reason_code", "")),
                "message": str((built.get("refusal") or {}).get("message", "")),
            },
        )
        return built

    intent = dict(built.get("intent") or {})
    next_state = copy.deepcopy(universe_state if isinstance(universe_state, dict) else {})
    executed = execute_single_intent_srz(
        repo_root=REPO_ROOT_HINT,
        universe_state=next_state,
        law_profile=law_profile,
        authority_context=authority_context,
        intent=intent,
        navigation_indices=navigation_indices,
        worker_count=1,
    )
    if executed.get("result") != "complete":
        executed["tool_log"] = _append_log(
            log_rows,
            {
                "entry_type": "refusal",
                "window_id": str(window_id),
                "reason_code": str((executed.get("refusal") or {}).get("reason_code", "")),
                "message": str((executed.get("refusal") or {}).get("message", "")),
                "intent_id": str(intent.get("intent_id", "")),
                "process_id": str(intent.get("process_id", "")),
            },
        )
        executed["intent"] = intent
        return executed

    out_log = _append_log(
        log_rows,
        {
            "entry_type": "process",
            "window_id": str(window_id),
            "intent_id": str(intent.get("intent_id", "")),
            "process_id": str(intent.get("process_id", "")),
            "outcome": "complete",
            "state_hash_anchor": str(executed.get("state_hash_anchor", "")),
            "tick": int(executed.get("tick", 0) or 0),
        },
    )
    return {
        "result": "complete",
        "intent": intent,
        "execution": {
            "result": "complete",
            "state_hash_anchor": str(executed.get("state_hash_anchor", "")),
            "tick": int(executed.get("tick", 0) or 0),
            "tick_hash_anchor": str(executed.get("tick_hash_anchor", "")),
            "composite_hash": str(executed.get("composite_hash", "")),
        },
        "universe_state": dict(executed.get("universe_state") or {}),
        "tool_log": out_log,
    }


def validate_ui_window_descriptor(repo_root: str, payload: dict) -> Dict[str, object]:
    return validate_instance(
        repo_root=repo_root,
        schema_name="ui_window",
        payload=payload,
        strict_top_level=True,
    )

"""Deterministic component graph resolution for release/install planning."""

from __future__ import annotations

import json
import os
from typing import Mapping, Sequence

from src.lib.provides.provider_resolution import (
    RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY,
    resolve_providers,
)
from src.platform.target_matrix import select_target_matrix_row
from tools.xstack.compatx.canonical_json import canonical_sha256


COMPONENT_KIND_BINARY = "binary"
COMPONENT_KIND_PACK = "pack"
COMPONENT_KIND_PROFILE = "profile"
COMPONENT_KIND_LOCK = "lock"
COMPONENT_KIND_DOCS = "docs"
COMPONENT_KIND_SDK = "sdk"
COMPONENT_KIND_MANIFEST = "manifest"

YANK_POLICY_WARN = "warn"
YANK_POLICY_REFUSE = "refuse"

EDGE_KIND_REQUIRES = "requires"
EDGE_KIND_RECOMMENDS = "recommends"
EDGE_KIND_SUGGESTS = "suggests"
EDGE_KIND_CONFLICTS = "conflicts"
EDGE_KIND_PROVIDES = "provides"

REFUSAL_COMPONENT_GRAPH_MISSING = "refusal.component_graph.missing"
REFUSAL_COMPONENT_GRAPH_UNSATISFIED = "refusal.component_graph.unsatisfied"
REFUSAL_COMPONENT_GRAPH_CONFLICT = "refusal.component_graph.conflict"
REFUSAL_COMPONENT_GRAPH_PROVIDER = "refusal.component_graph.provider_resolution"
REFUSAL_INSTALL_PROFILE_MISSING = "refusal.install_profile.missing"

DEFAULT_COMPONENT_GRAPH_REGISTRY_REL = os.path.join("data", "registries", "component_graph_registry.json")
DEFAULT_INSTALL_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "install_profile_registry.json")
DEFAULT_COMPONENT_GRAPH_ID = "graph.release.v0_0_0_mock"
DEFAULT_INSTALL_PROFILE_ID = "install.profile.full"
LEGACY_INSTALL_PROFILE_ALIASES = {
    "install_profile.mvp_default": DEFAULT_INSTALL_PROFILE_ID,
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_unique_strings(values: object) -> list[str]:
    return sorted({str(value).strip() for value in _as_list(values) if str(value).strip()})


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _normalize_filters(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    return {
        "platform_ids": _sorted_unique_strings(item.get("platform_ids")),
        "exclude_platform_ids": _sorted_unique_strings(item.get("exclude_platform_ids")),
        "arch_ids": _sorted_unique_strings(item.get("arch_ids")),
        "exclude_arch_ids": _sorted_unique_strings(item.get("exclude_arch_ids")),
        "abi_ids": _sorted_unique_strings(item.get("abi_ids")),
        "exclude_abi_ids": _sorted_unique_strings(item.get("exclude_abi_ids")),
        "required_capability_ids": _sorted_unique_strings(item.get("required_capability_ids")),
        "excluded_capability_ids": _sorted_unique_strings(item.get("excluded_capability_ids")),
        "required_contract_ids": _sorted_unique_strings(item.get("required_contract_ids")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }


def canonicalize_component_descriptor(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    yank_policy = _token(item.get("yank_policy")).lower() or YANK_POLICY_WARN
    if yank_policy not in {YANK_POLICY_WARN, YANK_POLICY_REFUSE}:
        yank_policy = YANK_POLICY_WARN
    normalized = {
        "component_id": _token(item.get("component_id")),
        "component_kind": _token(item.get("component_kind")),
        "content_hash": _token(item.get("content_hash")).lower(),
        "version": _token(item.get("version")),
        "platform_filters": _normalize_filters(_as_map(item.get("platform_filters"))),
        "capability_filters": _normalize_filters(_as_map(item.get("capability_filters"))),
        "contract_requirements": dict(_normalize_tree(_as_map(item.get("contract_requirements")))),
        "trust_requirements": dict(_normalize_tree(_as_map(item.get("trust_requirements")))),
        "provides_ids": _sorted_unique_strings(item.get("provides_ids")),
        "yanked": bool(item.get("yanked", False)),
        "yank_reason": _token(item.get("yank_reason")),
        "yank_policy": yank_policy,
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_component_edge(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "from_component_id": _token(item.get("from_component_id")),
        "edge_kind": _token(item.get("edge_kind")),
        "to_component_selector": _token(item.get("to_component_selector")),
        "filters": _normalize_filters(_as_map(item.get("filters"))),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_component_graph(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    components = sorted(
        (
            canonicalize_component_descriptor(row)
            for row in list(item.get("components") or [])
            if _token(_as_map(row).get("component_id"))
        ),
        key=lambda row: _token(row.get("component_id")),
    )
    edges = sorted(
        (
            canonicalize_component_edge(row)
            for row in list(item.get("edges") or [])
            if _token(_as_map(row).get("from_component_id")) and _token(_as_map(row).get("to_component_selector"))
        ),
        key=lambda row: (
            _token(row.get("from_component_id")),
            _token(row.get("edge_kind")),
            _token(row.get("to_component_selector")),
        ),
    )
    normalized = {
        "graph_id": _token(item.get("graph_id")),
        "release_id": _token(item.get("release_id")),
        "components": components,
        "edges": edges,
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_install_plan(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "plan_id": _token(item.get("plan_id")),
        "target_platform": _token(item.get("target_platform")),
        "target_arch": _token(item.get("target_arch")),
        "install_profile_id": _token(item.get("install_profile_id")),
        "selected_components": _sorted_unique_strings(item.get("selected_components")),
        "resolved_providers": [
            dict(_normalize_tree(_as_map(row)))
            for row in sorted(
                (_as_map(row) for row in list(item.get("resolved_providers") or [])),
                key=lambda row: (
                    _token(row.get("provides_id")),
                    _token(row.get("chosen_pack_id")),
                    _token(row.get("resolution_policy_id")),
                ),
            )
            if _token(_as_map(row).get("provides_id"))
        ],
        "verification_steps": [
            dict(_normalize_tree(_as_map(row)))
            for row in sorted(
                (_as_map(row) for row in list(item.get("verification_steps") or [])),
                key=lambda row: (
                    _token(row.get("step_id")),
                    _token(row.get("component_id")),
                    _token(row.get("action")),
                ),
            )
            if _token(_as_map(row).get("step_id"))
        ],
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def _canonical_install_profile_id(value: object) -> str:
    token = _token(value)
    return _token(LEGACY_INSTALL_PROFILE_ALIASES.get(token, token))


def canonicalize_install_profile(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "install_profile_id": _canonical_install_profile_id(item.get("install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID,
        "required_selectors": _sorted_unique_strings(item.get("required_selectors")),
        "optional_selectors": _sorted_unique_strings(item.get("optional_selectors")),
        "default_mod_policy_id": _token(item.get("default_mod_policy_id")) or "mod_policy.lab",
        "default_overlay_conflict_policy_id": _token(item.get("default_overlay_conflict_policy_id")) or "overlay.conflict.last_wins",
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def load_component_graph_registry(repo_root: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), DEFAULT_COMPONENT_GRAPH_REGISTRY_REL))


def load_install_profile_registry(repo_root: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), DEFAULT_INSTALL_PROFILE_REGISTRY_REL))


def select_component_graph(
    registry_payload: Mapping[str, object] | None,
    *,
    graph_id: str = "",
    release_id: str = "",
) -> dict:
    record = _as_map(_as_map(registry_payload).get("record"))
    rows = []
    for row in list(record.get("graphs") or []):
        item = canonicalize_component_graph(_as_map(row))
        if not _token(item.get("graph_id")):
            continue
        item["stability"] = dict(_normalize_tree(_as_map(_as_map(row).get("stability"))))
        rows.append(item)
    rows = sorted(rows, key=lambda row: (_token(row.get("release_id")), _token(row.get("graph_id"))))
    graph_token = _token(graph_id)
    if graph_token:
        for row in rows:
            if _token(row.get("graph_id")) == graph_token:
                return row
        return {}
    release_token = _token(release_id)
    if release_token:
        for row in rows:
            if _token(row.get("release_id")) == release_token:
                return row
    for row in rows:
        if _token(row.get("graph_id")) == DEFAULT_COMPONENT_GRAPH_ID:
            return row
    return rows[0] if rows else {}


def load_default_component_graph(
    repo_root: str,
    *,
    graph_id: str = "",
    release_id: str = "",
) -> dict:
    return select_component_graph(load_component_graph_registry(repo_root), graph_id=graph_id, release_id=release_id)


def select_install_profile(
    registry_payload: Mapping[str, object] | None,
    *,
    install_profile_id: str = "",
) -> dict:
    record = _as_map(_as_map(registry_payload).get("record"))
    rows = []
    for row in list(record.get("install_profiles") or []):
        item = canonicalize_install_profile(_as_map(row))
        if not _token(item.get("install_profile_id")):
            continue
        item["stability"] = dict(_normalize_tree(_as_map(_as_map(row).get("stability"))))
        rows.append(item)
    rows = sorted(rows, key=lambda row: _token(row.get("install_profile_id")))
    selected_id = _canonical_install_profile_id(install_profile_id)
    if selected_id:
        for row in rows:
            if _token(row.get("install_profile_id")) == selected_id:
                return row
        return {}
    for row in rows:
        if _token(row.get("install_profile_id")) == DEFAULT_INSTALL_PROFILE_ID:
            return row
    return rows[0] if rows else {}


def _matches_filters(
    filters: Mapping[str, object] | None,
    *,
    target_platform: str,
    target_arch: str,
    target_abi: str,
    capability_ids: Sequence[str] | None,
    contract_ids: Sequence[str] | None,
) -> bool:
    item = _normalize_filters(_as_map(filters))
    capability_set = set(_sorted_unique_strings(capability_ids))
    contract_set = set(_sorted_unique_strings(contract_ids))
    platform_token = _token(target_platform)
    arch_token = _token(target_arch)
    abi_token = _token(target_abi)
    allow_platforms = list(item.get("platform_ids") or [])
    if allow_platforms and platform_token not in allow_platforms:
        return False
    if platform_token and platform_token in set(item.get("exclude_platform_ids") or []):
        return False
    allow_arches = list(item.get("arch_ids") or [])
    if allow_arches and arch_token not in allow_arches:
        return False
    if arch_token and arch_token in set(item.get("exclude_arch_ids") or []):
        return False
    allow_abis = list(item.get("abi_ids") or [])
    if allow_abis and abi_token not in allow_abis:
        return False
    if abi_token and abi_token in set(item.get("exclude_abi_ids") or []):
        return False
    required_caps = set(item.get("required_capability_ids") or [])
    if required_caps and not required_caps.issubset(capability_set):
        return False
    if capability_set.intersection(set(item.get("excluded_capability_ids") or [])):
        return False
    required_contracts = set(item.get("required_contract_ids") or [])
    if required_contracts and not required_contracts.issubset(contract_set):
        return False
    return True


def _provider_declarations_for_component(component: Mapping[str, object], outgoing_edges: Sequence[Mapping[str, object]]) -> list[dict]:
    item = canonicalize_component_descriptor(component)
    provider_ids = set(_sorted_unique_strings(item.get("provides_ids")))
    for edge in list(outgoing_edges or []):
        edge_row = canonicalize_component_edge(edge)
        if _token(edge_row.get("edge_kind")) == EDGE_KIND_PROVIDES:
            provider_ids.add(_token(edge_row.get("to_component_selector")))
    priority = int(_as_map(item.get("extensions")).get("provider_priority", 0) or 0)
    required_caps = _sorted_unique_strings(_as_map(item.get("capability_filters")).get("required_capability_ids"))
    return [
        {
            "pack_id": _token(item.get("component_id")),
            "provides_id": provider_id,
            "provides_type": "template_set",
            "priority": priority,
            "extensions": {"required_capabilities": required_caps},
        }
        for provider_id in sorted(provider_ids)
        if provider_id
    ]


def _candidate_components_for_selector(
    selector: str,
    components: Mapping[str, Mapping[str, object]],
    outgoing_edges: Mapping[str, Sequence[Mapping[str, object]]],
) -> list[str]:
    token = _token(selector)
    if not token:
        return []
    if token in components:
        return [token]
    candidates: set[str] = set()
    for component_id in sorted(components.keys()):
        item = canonicalize_component_descriptor(_as_map(components.get(component_id)))
        provider_ids = set(_sorted_unique_strings(item.get("provides_ids")))
        for edge in list(outgoing_edges.get(component_id, [])):
            edge_row = canonicalize_component_edge(edge)
            if _token(edge_row.get("edge_kind")) != EDGE_KIND_PROVIDES:
                continue
            provider_ids.add(_token(edge_row.get("to_component_selector")))
        if token in provider_ids:
            candidates.add(component_id)
    return sorted(candidates)


def _sorted_reason_rows(selection_reasons: Mapping[str, set[str]]) -> list[dict]:
    rows = []
    for component_id in sorted(str(key).strip() for key in dict(selection_reasons or {}).keys() if str(key).strip()):
        reasons = sorted(str(reason).strip() for reason in set(selection_reasons.get(component_id) or set()) if str(reason).strip())
        rows.append({"component_id": component_id, "reasons": reasons})
    return rows


def _sorted_optional_rows(rows: Sequence[Mapping[str, object]]) -> list[dict]:
    out = []
    for row in list(rows or []):
        item = _as_map(row)
        selector = _token(item.get("selector"))
        if not selector:
            continue
        out.append(
            {
                "selector": selector,
                "component_ids": _sorted_unique_strings(item.get("component_ids")),
                "reason": _token(item.get("reason")) or "optional_by_default_not_selected",
            }
        )
    return sorted(out, key=lambda item: (_token(item.get("selector")), ",".join(list(item.get("component_ids") or []))))


def _verification_steps(selected_component_ids: Sequence[str], resolved_providers: Sequence[Mapping[str, object]]) -> list[dict]:
    steps: list[dict] = []
    for component_id in sorted({str(value).strip() for value in list(selected_component_ids or []) if str(value).strip()}):
        steps.append({"step_id": "verify.component.{}".format(component_id), "component_id": component_id, "action": "verify_content_hash"})
    for row in list(resolved_providers or []):
        item = _as_map(row)
        provides_id = _token(item.get("provides_id"))
        chosen = _token(item.get("chosen_pack_id"))
        if not provides_id or not chosen:
            continue
        steps.append({"step_id": "verify.provider.{}.{}".format(provides_id, chosen), "component_id": chosen, "action": "verify_provider_selection"})
    return steps


def resolve_component_graph(
    component_graph: Mapping[str, object] | None,
    *,
    install_profile_id: str = DEFAULT_INSTALL_PROFILE_ID,
    install_profile: Mapping[str, object] | None = None,
    target_platform: str = "",
    target_arch: str = "",
    target_abi: str = "",
    capability_ids: Sequence[str] | None = None,
    contract_ids: Sequence[str] | None = None,
    requested_component_ids: Sequence[str] | None = None,
    installed_state: Mapping[str, object] | None = None,
    include_recommends: bool = True,
    include_suggests: bool = False,
    strict_conflicts: bool = True,
    provides_resolution_policy_id: str = RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY,
) -> dict:
    graph = canonicalize_component_graph(component_graph)
    effective_install_profile_id = _canonical_install_profile_id(install_profile_id) or DEFAULT_INSTALL_PROFILE_ID
    components = {
        _token(row.get("component_id")): row
        for row in list(graph.get("components") or [])
        if _token(_as_map(row).get("component_id"))
    }
    outgoing_edges: dict[str, list[dict]] = {}
    for edge in list(graph.get("edges") or []):
        row = canonicalize_component_edge(edge)
        from_component_id = _token(row.get("from_component_id"))
        if not from_component_id:
            continue
        outgoing_edges.setdefault(from_component_id, []).append(row)
    for component_id in list(outgoing_edges.keys()):
        outgoing_edges[component_id] = sorted(
            outgoing_edges[component_id],
            key=lambda row: (_token(row.get("edge_kind")), _token(row.get("to_component_selector"))),
        )

    requested_selectors = _sorted_unique_strings(requested_component_ids)
    profile_payload = canonicalize_install_profile(
        install_profile
        or {
            "install_profile_id": effective_install_profile_id,
            "required_selectors": requested_selectors or _sorted_unique_strings(_as_map(graph.get("extensions")).get("default_requested_components")),
            "optional_selectors": [],
        }
    )
    effective_install_profile_id = _token(profile_payload.get("install_profile_id")) or effective_install_profile_id
    profile_required_selectors = _sorted_unique_strings(profile_payload.get("required_selectors"))
    profile_optional_selectors = _sorted_unique_strings(profile_payload.get("optional_selectors"))

    errors: list[dict] = []
    selected_component_ids: set[str] = set()
    processed_component_ids: set[str] = set()
    pending_component_ids: list[str] = []
    required_provides_ids: set[str] = set()
    selected_provider_components: set[str] = set()
    resolved_providers: list[dict] = []
    selection_reasons: dict[str, set[str]] = {}
    provides_reasons: dict[str, set[str]] = {}
    disabled_optional_components: list[dict] = []

    for selector in profile_required_selectors:
        if selector in components:
            pending_component_ids.append(selector)
            selection_reasons.setdefault(selector, set()).add(
                "profile_required:{}:{}".format(effective_install_profile_id, selector)
            )
            continue
        required_provides_ids.add(selector)
        provides_reasons.setdefault(selector, set()).add(
            "profile_required:{}:{}".format(effective_install_profile_id, selector)
        )
    for selector in requested_selectors:
        if selector in components:
            pending_component_ids.append(selector)
            selection_reasons.setdefault(selector, set()).add("explicit_request:{}".format(selector))
            continue
        required_provides_ids.add(selector)
        provides_reasons.setdefault(selector, set()).add("explicit_request:{}".format(selector))
    for selector in profile_optional_selectors:
        disabled_optional_components.append(
            {
                "selector": selector,
                "component_ids": _candidate_components_for_selector(selector, components, outgoing_edges),
                "reason": "optional_by_default_not_selected",
            }
        )

    while True:
        progressed = False
        while pending_component_ids:
            component_id = sorted(set(pending_component_ids))[0]
            pending_component_ids = [value for value in pending_component_ids if value != component_id]
            component = _as_map(components.get(component_id))
            if not component:
                errors.append({"code": REFUSAL_COMPONENT_GRAPH_UNSATISFIED, "message": "required component '{}' is missing from the graph".format(component_id), "component_id": component_id})
                continue
            if not _matches_filters(
                _as_map(component.get("platform_filters")),
                target_platform=target_platform,
                target_arch=target_arch,
                target_abi=target_abi,
                capability_ids=capability_ids,
                contract_ids=contract_ids,
            ):
                errors.append({"code": REFUSAL_COMPONENT_GRAPH_UNSATISFIED, "message": "component '{}' is not available for the requested target".format(component_id), "component_id": component_id})
                continue
            selected_component_ids.add(component_id)
            if component_id in processed_component_ids:
                continue
            processed_component_ids.add(component_id)
            progressed = True
            for edge in list(outgoing_edges.get(component_id, [])):
                if not _matches_filters(
                    _as_map(edge.get("filters")),
                    target_platform=target_platform,
                    target_arch=target_arch,
                    target_abi=target_abi,
                    capability_ids=capability_ids,
                    contract_ids=contract_ids,
                ):
                    continue
                edge_kind = _token(edge.get("edge_kind"))
                selector = _token(edge.get("to_component_selector"))
                selector_is_component = selector in components
                if edge_kind == EDGE_KIND_CONFLICTS and strict_conflicts and selector in selected_component_ids:
                    errors.append({"code": REFUSAL_COMPONENT_GRAPH_CONFLICT, "message": "component '{}' conflicts with '{}'".format(component_id, selector), "component_id": component_id, "conflicts_with": selector})
                    continue
                if edge_kind not in {EDGE_KIND_REQUIRES, EDGE_KIND_RECOMMENDS, EDGE_KIND_SUGGESTS}:
                    continue
                include_edge = edge_kind == EDGE_KIND_REQUIRES or (edge_kind == EDGE_KIND_RECOMMENDS and include_recommends) or (edge_kind == EDGE_KIND_SUGGESTS and include_suggests)
                if not include_edge or not selector:
                    continue
                if selector_is_component:
                    if selector not in selected_component_ids:
                        pending_component_ids.append(selector)
                    selection_reasons.setdefault(selector, set()).add(
                        "edge_{}:{}->{}".format(edge_kind, component_id, selector)
                    )
                    continue
                required_provides_ids.add(selector)
                provides_reasons.setdefault(selector, set()).add(
                    "edge_{}:{}->{}".format(edge_kind, component_id, selector)
                )

        provider_declarations: list[dict] = []
        for component_id in sorted(selected_component_ids):
            provider_declarations.extend(_provider_declarations_for_component(_as_map(components.get(component_id)), outgoing_edges.get(component_id, [])))
        provider_result = resolve_providers(
            instance_id=effective_install_profile_id,
            required_provides_ids=sorted(required_provides_ids),
            provider_declarations=provider_declarations,
            resolution_policy_id=provides_resolution_policy_id,
        )
        if _token(provider_result.get("result")) == "refused":
            for row in list(provider_result.get("errors") or []):
                item = _as_map(row)
                errors.append({"code": REFUSAL_COMPONENT_GRAPH_PROVIDER, "message": _token(item.get("message")) or "provider resolution failed", "details": item})
            resolved_providers = list(provider_result.get("provides_resolutions") or [])
            break
        resolved_providers = list(provider_result.get("provides_resolutions") or [])
        new_provider_components = [
            _token(_as_map(row).get("chosen_pack_id"))
            for row in resolved_providers
            if _token(_as_map(row).get("chosen_pack_id")) and _token(_as_map(row).get("chosen_pack_id")) not in selected_component_ids
        ]
        for row in resolved_providers:
            item = _as_map(row)
            chosen_component_id = _token(item.get("chosen_pack_id"))
            provides_id = _token(item.get("provides_id"))
            if not chosen_component_id:
                continue
            selection_reasons.setdefault(chosen_component_id, set()).add(
                "provider_resolution:{}->{}".format(provides_id, chosen_component_id)
            )
            selection_reasons.setdefault(chosen_component_id, set()).update(set(provides_reasons.get(provides_id) or set()))
        new_provider_components = sorted(set(new_provider_components) - selected_provider_components)
        if new_provider_components:
            selected_provider_components.update(new_provider_components)
            pending_component_ids.extend(new_provider_components)
            continue
        if not progressed:
            break

    if strict_conflicts:
        for component_id in sorted(selected_component_ids):
            for edge in list(outgoing_edges.get(component_id, [])):
                if _token(_as_map(edge).get("edge_kind")) != EDGE_KIND_CONFLICTS:
                    continue
                selector = _token(_as_map(edge).get("to_component_selector"))
                if selector and selector in selected_component_ids:
                    errors.append({"code": REFUSAL_COMPONENT_GRAPH_CONFLICT, "message": "component '{}' conflicts with '{}'".format(component_id, selector), "component_id": component_id, "conflicts_with": selector})

    installed_ids = set(_sorted_unique_strings(_as_map(installed_state).get("installed_component_ids")))
    fetch_ids = sorted(component_id for component_id in sorted(selected_component_ids) if component_id not in installed_ids)
    plan = canonicalize_install_plan(
        {
            "plan_id": "install_plan.{}".format(canonical_sha256({"graph_id": _token(graph.get("graph_id")), "install_profile_id": effective_install_profile_id, "target_platform": _token(target_platform), "target_arch": _token(target_arch), "target_abi": _token(target_abi), "selected_components": sorted(selected_component_ids), "resolved_providers": resolved_providers})[:16]),
            "target_platform": _token(target_platform),
            "target_arch": _token(target_arch),
            "install_profile_id": effective_install_profile_id,
            "selected_components": sorted(selected_component_ids),
            "resolved_providers": resolved_providers,
            "verification_steps": _verification_steps(sorted(selected_component_ids), resolved_providers),
            "extensions": {
                "graph_id": _token(graph.get("graph_id")),
                "release_id": _token(graph.get("release_id")),
                "target_abi": _token(target_abi),
                "requested_component_ids": requested_selectors,
                "requested_selectors": requested_selectors,
                "profile_required_selectors": profile_required_selectors,
                "profile_optional_selectors": profile_optional_selectors,
                "required_provides_ids": sorted(required_provides_ids),
                "component_fetch_list": fetch_ids,
                "installed_component_ids": sorted(installed_ids),
                "provides_resolution_policy_id": _token(provides_resolution_policy_id),
                "selection_reasons": _sorted_reason_rows(selection_reasons),
                "disabled_optional_components": _sorted_optional_rows(disabled_optional_components),
                "selected_component_descriptors": [components[component_id] for component_id in sorted(selected_component_ids) if component_id in components],
            },
        }
    )
    return {
        "result": "complete" if not errors else "refused",
        "refusal_code": _token(_as_map(errors[0]).get("code")) if errors else "",
        "install_plan": plan,
        "graph_id": _token(graph.get("graph_id")),
        "release_id": _token(graph.get("release_id")),
        "install_profile": profile_payload,
        "selected_component_descriptors": [components[component_id] for component_id in sorted(selected_component_ids) if component_id in components],
        "errors": errors,
    }


def build_default_component_install_plan(
    repo_root: str,
    *,
    graph_id: str = "",
    release_id: str = "",
    install_profile_id: str = DEFAULT_INSTALL_PROFILE_ID,
    target_platform: str = "",
    target_arch: str = "",
    target_abi: str = "",
    capability_ids: Sequence[str] | None = None,
    contract_ids: Sequence[str] | None = None,
    requested_component_ids: Sequence[str] | None = None,
    installed_state: Mapping[str, object] | None = None,
    include_recommends: bool = True,
    include_suggests: bool = False,
    strict_conflicts: bool = True,
    provides_resolution_policy_id: str = RESOLUTION_POLICY_DETERMINISTIC_HIGHEST_PRIORITY,
) -> dict:
    graph = load_default_component_graph(repo_root, graph_id=graph_id, release_id=release_id)
    profile_registry = load_install_profile_registry(repo_root)
    profile_payload = select_install_profile(profile_registry, install_profile_id=install_profile_id)
    if not graph:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_COMPONENT_GRAPH_MISSING,
            "errors": [{"code": REFUSAL_COMPONENT_GRAPH_MISSING, "message": "component graph registry is missing"}],
            "install_plan": canonicalize_install_plan(
                {
                    "plan_id": "install_plan.missing",
                    "target_platform": _token(target_platform),
                    "target_arch": _token(target_arch),
                    "install_profile_id": _canonical_install_profile_id(install_profile_id) or DEFAULT_INSTALL_PROFILE_ID,
                    "selected_components": [],
                    "resolved_providers": [],
                    "verification_steps": [],
                    "extensions": {"graph_id": "", "release_id": _token(release_id)},
                }
            ),
        }
    if not profile_payload:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_INSTALL_PROFILE_MISSING,
            "errors": [
                {
                    "code": REFUSAL_INSTALL_PROFILE_MISSING,
                    "message": "install profile '{}' is missing".format(_canonical_install_profile_id(install_profile_id) or DEFAULT_INSTALL_PROFILE_ID),
                }
            ],
            "install_plan": canonicalize_install_plan(
                {
                    "plan_id": "install_plan.profile_missing",
                    "target_platform": _token(target_platform),
                    "target_arch": _token(target_arch),
                    "install_profile_id": _canonical_install_profile_id(install_profile_id) or DEFAULT_INSTALL_PROFILE_ID,
                    "selected_components": [],
                    "resolved_providers": [],
                    "verification_steps": [],
                    "extensions": {"graph_id": _token(graph.get("graph_id")), "release_id": _token(graph.get("release_id"))},
                }
            ),
        }
    return resolve_component_graph(
        graph,
        install_profile_id=_token(profile_payload.get("install_profile_id")) or install_profile_id,
        install_profile=profile_payload,
        target_platform=target_platform,
        target_arch=target_arch,
        target_abi=target_abi,
        capability_ids=capability_ids,
        contract_ids=contract_ids,
        requested_component_ids=requested_component_ids,
        installed_state=installed_state,
        include_recommends=include_recommends,
        include_suggests=include_suggests,
        strict_conflicts=strict_conflicts,
        provides_resolution_policy_id=provides_resolution_policy_id,
    )


def validate_instance_against_install_plan(
    install_plan: Mapping[str, object] | None,
    instance_manifest: Mapping[str, object] | None,
) -> dict:
    plan = _as_map(install_plan)
    manifest = _as_map(instance_manifest)
    selected_ids = set(_sorted_unique_strings(plan.get("selected_components")))
    descriptor_rows = {
        _token(_as_map(row).get("component_id")): _as_map(row)
        for row in list(_as_map(plan.get("extensions")).get("selected_component_descriptors") or [])
        if _token(_as_map(row).get("component_id"))
    }
    if not descriptor_rows:
        descriptor_rows = {
            _token(_as_map(row).get("component_id")): _as_map(row)
            for row in list(_as_map(plan).get("selected_component_descriptors") or [])
            if _token(_as_map(row).get("component_id"))
        }
    missing: list[str] = []
    pack_lock_hash = _token(manifest.get("pack_lock_hash"))
    profile_bundle_hash = _token(manifest.get("profile_bundle_hash"))
    required_product_builds = sorted(dict(_as_map(manifest.get("required_product_builds"))).keys())
    if pack_lock_hash:
        has_lock = False
        for component_id in sorted(selected_ids):
            item = _as_map(descriptor_rows.get(component_id))
            if _token(item.get("component_kind")) != COMPONENT_KIND_LOCK:
                continue
            if pack_lock_hash == _token(_as_map(item.get("extensions")).get("pack_lock_hash")) or component_id == "lock.pack_lock.mvp_default":
                has_lock = True
                break
        if not has_lock:
            missing.append("lock.pack_lock")
    if profile_bundle_hash:
        has_profile = False
        for component_id in sorted(selected_ids):
            item = _as_map(descriptor_rows.get(component_id))
            if _token(item.get("component_kind")) != COMPONENT_KIND_PROFILE:
                continue
            if profile_bundle_hash == _token(_as_map(item.get("extensions")).get("profile_bundle_hash")) or component_id == "profile.bundle.mvp_default":
                has_profile = True
                break
        if not has_profile:
            missing.append("profile.bundle")
    selected_product_ids = {
        _token(_as_map(_as_map(descriptor_rows.get(component_id)).get("extensions")).get("product_id"))
        for component_id in sorted(selected_ids)
        if _token(_as_map(descriptor_rows.get(component_id)).get("component_kind")) == COMPONENT_KIND_BINARY
    }
    selected_product_ids.discard("")
    for product_id in required_product_builds:
        if product_id not in selected_product_ids:
            missing.append("binary.{}".format(product_id))
    return {
        "result": "complete" if not missing else "refused",
        "refusal_code": REFUSAL_COMPONENT_GRAPH_UNSATISFIED if missing else "",
        "missing_component_ids": sorted(set(missing)),
        "install_plan_fingerprint": _token(_as_map(plan).get("deterministic_fingerprint")),
    }


def platform_targets_for_tag(platform_tag: str, repo_root: str = "") -> dict:
    token = _token(platform_tag).lower()
    if _token(repo_root):
        row = select_target_matrix_row(repo_root, platform_tag=token)
        if row:
            extensions = _as_map(row.get("extensions"))
            return {
                "target_id": _token(row.get("target_id")),
                "platform_id": _token(extensions.get("platform_id")),
                "os_id": _token(row.get("os_id")),
                "arch_id": _token(row.get("arch_id")),
                "abi_id": _token(row.get("abi_id")),
                "tier": int(row.get("tier", 3) or 3),
                "platform_tag": token,
            }
    mapping = {
        "win64": {
            "target_id": "target.os_winnt.abi_msvc.arch_x86_64",
            "platform_id": "platform.winnt",
            "os_id": "os.winnt",
            "arch_id": "arch.x86_64",
            "abi_id": "abi.msvc",
            "tier": 1,
            "platform_tag": "win64",
        },
        "linux-x86_64": {
            "target_id": "target.os_linux.abi_glibc.arch_x86_64",
            "platform_id": "platform.linux_gtk",
            "os_id": "os.linux",
            "arch_id": "arch.x86_64",
            "abi_id": "abi.glibc",
            "tier": 1,
            "platform_tag": "linux-x86_64",
        },
        "macos-universal": {
            "target_id": "target.os_macosx.abi_cocoa.arch_arm64",
            "platform_id": "platform.macos_cocoa",
            "os_id": "os.macosx",
            "arch_id": "arch.arm64",
            "abi_id": "abi.cocoa",
            "tier": 2,
            "platform_tag": "macos-universal",
        },
        "posix-min": {
            "target_id": "target.os_posix.abi_null.arch_x86_64",
            "platform_id": "platform.posix_min",
            "os_id": "os.posix",
            "arch_id": "arch.x86_64",
            "abi_id": "abi.null",
            "tier": 3,
            "platform_tag": "posix-min",
        },
    }
    return dict(
        mapping.get(
            token,
            {
                "target_id": "",
                "platform_id": "",
                "os_id": "",
                "arch_id": "",
                "abi_id": "",
                "tier": 3,
                "platform_tag": token,
            },
        )
    )


__all__ = [
    "COMPONENT_KIND_BINARY",
    "COMPONENT_KIND_DOCS",
    "COMPONENT_KIND_LOCK",
    "COMPONENT_KIND_MANIFEST",
    "COMPONENT_KIND_PACK",
    "COMPONENT_KIND_PROFILE",
    "COMPONENT_KIND_SDK",
    "DEFAULT_COMPONENT_GRAPH_ID",
    "DEFAULT_COMPONENT_GRAPH_REGISTRY_REL",
    "DEFAULT_INSTALL_PROFILE_ID",
    "DEFAULT_INSTALL_PROFILE_REGISTRY_REL",
    "EDGE_KIND_CONFLICTS",
    "EDGE_KIND_PROVIDES",
    "EDGE_KIND_RECOMMENDS",
    "EDGE_KIND_REQUIRES",
    "EDGE_KIND_SUGGESTS",
    "REFUSAL_COMPONENT_GRAPH_CONFLICT",
    "REFUSAL_COMPONENT_GRAPH_MISSING",
    "REFUSAL_COMPONENT_GRAPH_PROVIDER",
    "REFUSAL_COMPONENT_GRAPH_UNSATISFIED",
    "REFUSAL_INSTALL_PROFILE_MISSING",
    "YANK_POLICY_REFUSE",
    "YANK_POLICY_WARN",
    "build_default_component_install_plan",
    "canonicalize_component_descriptor",
    "canonicalize_component_edge",
    "canonicalize_component_graph",
    "canonicalize_install_profile",
    "canonicalize_install_plan",
    "deterministic_fingerprint",
    "load_component_graph_registry",
    "load_default_component_graph",
    "load_install_profile_registry",
    "platform_targets_for_tag",
    "resolve_component_graph",
    "select_component_graph",
    "select_install_profile",
    "validate_instance_against_install_plan",
]

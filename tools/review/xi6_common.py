"""Deterministic Xi-6 architecture freeze helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import defaultdict
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.architecture_graph_bootstrap_common import (  # noqa: E402
    build_architecture_snapshot,
    write_architecture_snapshot,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
MODULE_REGISTRY_REL = "data/architecture/module_registry.json"
MODULE_DEP_GRAPH_REL = "data/architecture/module_dependency_graph.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"
SYMBOL_INDEX_REL = "data/audit/symbol_index.json"

ARCHITECTURE_GRAPH_V1_REL = "data/architecture/architecture_graph.v1.json"
MODULE_REGISTRY_V1_REL = "data/architecture/module_registry.v1.json"
MODULE_BOUNDARY_RULES_V1_REL = "data/architecture/module_boundary_rules.v1.json"
SINGLE_ENGINE_REGISTRY_REL = "data/architecture/single_engine_registry.json"

ARCHITECTURE_GRAPH_SPEC_V1_REL = "docs/architecture/ARCHITECTURE_GRAPH_SPEC_v1.md"
MODULE_BOUNDARIES_V1_REL = "docs/architecture/MODULE_BOUNDARIES_v1.md"
XI_6_FINAL_REL = "docs/audit/XI_6_FINAL.md"

XI_5A_FINAL_REL = "docs/audit/XI_5A_FINAL.md"
XI_5X1_FINAL_REL = "docs/audit/XI_5X1_FINAL.md"
XI_5X2_FINAL_REL = "docs/audit/XI_5X2_FINAL.md"
XI5X2_GATE_MODEL_REL = "data/restructure/xi5x2_xi6_gate_model.json"

ARCH_GRAPH_UPDATE_TAG_REL = "data/architecture/arch_graph_update_request.json"

VALIDATION_STRICT_REL = "data/audit/validation_report_STRICT.json"
ARCH_AUDIT2_REL = "data/audit/arch_audit2_report.json"
WORLDGEN_LOCK_VERIFY_REL = "data/audit/worldgen_lock_verify.json"
BASELINE_UNIVERSE_VERIFY_REL = "data/audit/baseline_universe_verify.json"
GAMEPLAY_VERIFY_REL = "data/audit/gameplay_verify.json"
DISASTER_SUITE_RUN_REL = "data/audit/disaster_suite_run.json"
ECOSYSTEM_VERIFY_RUN_REL = "data/audit/ecosystem_verify_run.json"
UPDATE_SIM_RUN_REL = "data/audit/update_sim_run.json"
TRUST_STRICT_RUN_REL = "data/audit/trust_strict_run.json"

XI6_TARGETED_TESTS = (
    "test_arch_graph_v1_hash_stable",
    "test_module_boundary_rules_valid",
    "test_single_engine_registry_enforced",
    "test_arch_drift_detected_without_tag",
)

NON_RUNTIME_DOMAINS = {
    "archive",
    "artifacts",
    "attic",
    "build",
    "data",
    "dist",
    "docs",
    "governance",
    "ide",
    "legacy",
    "locks",
    "profiles",
    "quarantine",
    "repo",
    "schemas",
    "specs",
    "templates",
    "tests",
}
TRUTH_FORBIDDEN_PREFIXES = ("field", "fields", "process", "universe")
UI_RENDER_PREFIXES = (
    "apps.client.render",
    "apps.client.ui",
    "apps.client.presentation",
    "ui",
)
APP_PREFIXES = ("apps.", "appshell")
TOOLS_PREFIX = "tools."
ARCH_UPDATE_TAG = "ARCH-GRAPH-UPDATE"
STABLE_TOOL_SUPPORT_MODULES = {
    "tools.compatx.core",
    "tools.xstack.compatx",
}

ENGINE_SPECS = (
    {
        "engine_id": "cap_neg",
        "semantic_area": "CAP-NEG",
        "canonical_module_id": "compat",
        "canonical_entrypoint_symbols": ("negotiate_endpoint_descriptors", "verify_negotiation_record"),
        "canonical_file_paths": ("compat/capability_negotiation.py",),
        "allowed_definition_modules": ("compat",),
        "description": "Compatibility negotiation must stay inside the canonical compatibility negotiation engine.",
    },
    {
        "engine_id": "geo_overlay_merge",
        "semantic_area": "GEO",
        "canonical_module_id": "geo.overlay",
        "canonical_entrypoint_symbols": ("merge_overlay_view", "overlay_proof_surface"),
        "canonical_file_paths": ("geo/overlay/overlay_merge_engine.py",),
        "allowed_definition_modules": ("geo", "geo.overlay"),
        "description": "Overlay merge and proof synthesis must stay inside the GEO overlay engine surface.",
    },
    {
        "engine_id": "geo_id_generation",
        "semantic_area": "GEO",
        "canonical_module_id": "geo.index",
        "canonical_entrypoint_symbols": ("geo_object_id",),
        "canonical_file_paths": ("geo/index/object_id_engine.py",),
        "allowed_definition_modules": ("geo", "geo.index"),
        "description": "Deterministic spatial object identity must stay inside the GEO object-id engine surface.",
    },
    {
        "engine_id": "mw_refinement_scheduler",
        "semantic_area": "MW",
        "canonical_module_id": "worldgen.refinement",
        "canonical_entrypoint_symbols": ("build_scheduler_plan",),
        "canonical_file_paths": ("worldgen/refinement/refinement_scheduler.py",),
        "allowed_definition_modules": ("worldgen.refinement",),
        "description": "Worldgen refinement scheduling must stay inside the canonical MW refinement scheduler.",
    },
    {
        "engine_id": "trust_verifier",
        "semantic_area": "TRUST",
        "canonical_module_id": "security.trust",
        "canonical_entrypoint_symbols": ("verify_artifact_trust",),
        "canonical_file_paths": ("security/trust/trust_verifier.py",),
        "allowed_definition_modules": ("security.trust",),
        "description": "Artifact trust verification must stay inside the canonical trust verifier.",
    },
    {
        "engine_id": "pack_compat_verifier",
        "semantic_area": "PACK-COMPAT",
        "canonical_module_id": "packs.compat",
        "canonical_entrypoint_symbols": ("validate_pack_compat_manifest",),
        "canonical_file_paths": ("packs/compat/pack_compat_validator.py",),
        "allowed_definition_modules": ("packs.compat",),
        "description": "Pack compatibility verification must stay inside the canonical pack compatibility validator.",
    },
    {
        "engine_id": "update_resolver",
        "semantic_area": "UPDATE",
        "canonical_module_id": "release",
        "canonical_entrypoint_symbols": ("resolve_update_plan",),
        "canonical_file_paths": ("release/update_resolver.py",),
        "allowed_definition_modules": ("release",),
        "description": "Update resolution must stay inside the release update resolver.",
    },
    {
        "engine_id": "virtual_paths_resolver",
        "semantic_area": "VPATH",
        "canonical_module_id": "appshell.paths",
        "canonical_entrypoint_symbols": ("vpath_resolve", "vpath_resolve_existing"),
        "canonical_file_paths": ("appshell/paths/virtual_paths.py",),
        "allowed_definition_modules": ("appshell.paths",),
        "description": "Virtual path resolution must stay inside the AppShell paths module.",
    },
    {
        "engine_id": "time_anchor_engine",
        "semantic_area": "TIME-ANCHOR",
        "canonical_module_id": "engine.time",
        "canonical_entrypoint_symbols": ("load_time_anchor_policy", "time_anchor_policy_fingerprint"),
        "canonical_file_paths": ("engine/time/epoch_anchor_engine.py",),
        "allowed_definition_modules": ("engine.time",),
        "description": "Time anchor policy loading and hashing must stay inside the time-anchor engine.",
    },
)

_SNAPSHOT_CACHE: dict[str, dict[str, object]] = {}


class Xi6InputsMissing(RuntimeError):
    """Raised when Xi-6 authoritative inputs are unavailable."""


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _repo_root(path: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(path or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, _norm_rel(rel_path).replace("/", os.sep))))


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _write_json(repo_root: str, rel_path: str, payload: Mapping[str, object]) -> str:
    abs_path = _repo_abs(repo_root, rel_path)
    _ensure_parent(abs_path)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return abs_path


def _write_text(repo_root: str, rel_path: str, text: str) -> str:
    abs_path = _repo_abs(repo_root, rel_path)
    _ensure_parent(abs_path)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return abs_path


def _read_json(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    with open(abs_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise Xi6InputsMissing(
            json.dumps(
                {"code": "refusal.xi.missing_inputs", "missing_inputs": [rel_path]},
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _load_optional_json(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    if not os.path.isfile(abs_path):
        return {}
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _required_inputs() -> tuple[str, ...]:
    return (
        ARCHITECTURE_GRAPH_REL,
        MODULE_REGISTRY_REL,
        MODULE_DEP_GRAPH_REL,
        BUILD_GRAPH_REL,
        SYMBOL_INDEX_REL,
        XI_5A_FINAL_REL,
        XI_5X1_FINAL_REL,
        XI_5X2_FINAL_REL,
        XI5X2_GATE_MODEL_REL,
        "docs/canon/constitution_v1.md",
        "docs/canon/glossary_v1.md",
        "AGENTS.md",
    )


def ensure_inputs(repo_root: str) -> None:
    missing = [rel for rel in _required_inputs() if not os.path.exists(_repo_abs(repo_root, rel))]
    if missing:
        raise Xi6InputsMissing(
            json.dumps(
                {"code": "refusal.xi.missing_inputs", "missing_inputs": sorted(set(missing))},
                indent=2,
                sort_keys=True,
            )
        )
    gate_model = _read_json(repo_root, XI5X2_GATE_MODEL_REL)
    if not bool(gate_model.get("xi6_ready")):
        raise Xi6InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi.missing_inputs",
                    "missing_inputs": [XI5X2_GATE_MODEL_REL],
                    "reason": "xi5x2 gate model does not authorize Xi-6",
                },
                indent=2,
                sort_keys=True,
            )
        )


def _sorted_unique_strings(values: Iterable[object]) -> list[str]:
    return sorted({str(item).strip() for item in list(values or []) if str(item).strip()})


def _payload_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(payload or {})
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _content_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(payload or {}))


def _python_env(repo_root: str) -> dict[str, str]:
    env = dict(os.environ)
    roots = [_repo_root(repo_root)]
    existing = _token(env.get("PYTHONPATH"))
    if existing:
        roots.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(roots)
    return env


def refresh_architecture_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    snapshot = build_architecture_snapshot(root)
    write_architecture_snapshot(root, snapshot)
    graph = dict(snapshot.get("architecture_graph") or {})
    _SNAPSHOT_CACHE[root] = graph
    return graph


def live_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    cached = _SNAPSHOT_CACHE.get(root)
    if cached is None:
        snapshot = build_architecture_snapshot(root)
        cached = dict(snapshot.get("architecture_graph") or {})
        _SNAPSHOT_CACHE[root] = cached
    return cached


def _module_rows_by_id(architecture_graph: Mapping[str, object]) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    for row in list(dict(architecture_graph or {}).get("modules") or []):
        item = dict(row or {})
        module_id = _token(item.get("module_id"))
        if module_id:
            rows[module_id] = item
    return rows


def _dependency_map(architecture_graph: Mapping[str, object]) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for module_id, row in sorted(_module_rows_by_id(architecture_graph).items()):
        rows[module_id] = sorted(_sorted_unique_strings(row.get("dependencies")))
    return rows


def _id_token(value: object) -> str:
    token = _token(value).strip(".").lower().replace("-", "_").replace(" ", "_")
    return token


def _module_role(module_id: str, row: Mapping[str, object]) -> str:
    module_id = _token(module_id)
    domain = _token(row.get("domain"))
    root = _norm_rel(row.get("module_root"))
    if module_id == "unknown.root":
        return "support"
    if module_id.startswith("tools.") or module_id == "tools":
        return "tooling"
    if domain in {"docs", "governance", "ide", "schemas", "specs"}:
        return "documentation"
    if domain in {"data", "archive", "artifacts", "profiles", "templates"}:
        return "data"
    if domain in {"tests"} or root.startswith("tests/"):
        return "test"
    if domain in {"legacy", "attic", "quarantine"}:
        return "archive"
    if module_id.startswith(UI_RENDER_PREFIXES):
        return "ui_renderer"
    if module_id.startswith(APP_PREFIXES) or module_id == "apps":
        return "application"
    if domain in NON_RUNTIME_DOMAINS:
        return "support"
    return "runtime"


def _platform_adapter_modules(values: Iterable[object]) -> list[str]:
    out: list[str] = []
    for item in _sorted_unique_strings(values):
        lowered = item.lower()
        if any(
            token in lowered
            for token in (
                "adapter",
                "backend",
                "platform",
                "renderers",
                "renderer",
                "win32",
                "xcode",
                "metal",
                "vulkan",
                "dx",
                "gl",
                "sdl",
            )
        ):
            out.append(item)
    return out


def _truth_forbidden_modules(all_module_ids: Iterable[object], allowed: Iterable[object]) -> list[str]:
    allowed_set = set(_sorted_unique_strings(allowed))
    out = []
    for module_id in _sorted_unique_strings(all_module_ids):
        if module_id in allowed_set:
            continue
        if module_id.startswith(TRUTH_FORBIDDEN_PREFIXES):
            out.append(module_id)
    return out


def _freeze_manifest(
    payload: Mapping[str, object],
    *,
    identity_id: str,
    contract_id: str,
    stability_class: str = "stable",
) -> dict[str, object]:
    frozen = dict(payload or {})
    frozen["identity"] = {
        "id": identity_id,
        "kind": "identity.manifest",
    }
    frozen["contract_id"] = contract_id
    frozen["stability_class"] = stability_class
    frozen["content_hash"] = ""
    frozen["deterministic_fingerprint"] = ""
    frozen["content_hash"] = _content_hash(frozen)
    frozen["deterministic_fingerprint"] = _payload_fingerprint(frozen)
    return frozen


def build_module_boundary_rules_payload(
    architecture_graph: Mapping[str, object],
    module_registry: Mapping[str, object],
) -> dict[str, object]:
    module_rows = _module_rows_by_id(architecture_graph)
    dependency_map = _dependency_map(architecture_graph)
    all_module_ids = sorted(module_rows)
    registry_rows = {
        _token(row.get("module_id")): dict(row or {})
        for row in list(dict(module_registry or {}).get("modules") or [])
        if _token(dict(row or {}).get("module_id"))
    }
    rules: list[dict[str, object]] = []
    provisional_allowance_count = 0

    for module_id in all_module_ids:
        row = dict(module_rows.get(module_id) or {})
        registry_row = dict(registry_rows.get(module_id) or {})
        allowed_deps = _sorted_unique_strings(dependency_map.get(module_id) or [])
        role = _module_role(module_id, row)
        forbidden_deps: list[str] = []
        provisional_allowances: list[dict[str, object]] = []

        if role == "ui_renderer":
            for dep in _truth_forbidden_modules(all_module_ids, allowed_deps):
                forbidden_deps.append(dep)
            current_truth = sorted(dep for dep in allowed_deps if dep.startswith(TRUTH_FORBIDDEN_PREFIXES))
            if current_truth:
                provisional_allowances.append(
                    {
                        "allowance_id": "ui_truth_surface",
                        "replacement_plan": "Route UI and renderer reads through declared perceived-model or process-owned surfaces before tightening Xi-7/Φ boundaries.",
                        "retained_dependencies": current_truth,
                        "reason": "current repo still carries direct truth-adjacent dependencies that need later boundary tightening.",
                    }
                )
        elif role == "application":
            for dep in _truth_forbidden_modules(all_module_ids, allowed_deps):
                if not dep.startswith("process"):
                    forbidden_deps.append(dep)
            current_truth = sorted(dep for dep in allowed_deps if dep.startswith(TRUTH_FORBIDDEN_PREFIXES) and not dep.startswith("process"))
            if current_truth:
                provisional_allowances.append(
                    {
                        "allowance_id": "app_truth_surface",
                        "replacement_plan": "Move app-facing truth access behind declared process/runtime façades before the next boundary tightening pass.",
                        "retained_dependencies": current_truth,
                        "reason": "apps must not mutate truth directly; current repo still exposes truth-adjacent imports that need later isolation.",
                    }
                )

        if role in {"runtime", "application", "ui_renderer"}:
            tool_deps = sorted(
                dep
                for dep in allowed_deps
                if dep.startswith(TOOLS_PREFIX) and dep not in STABLE_TOOL_SUPPORT_MODULES
            )
            if tool_deps:
                provisional_allowances.append(
                    {
                        "allowance_id": "runtime_tools_contamination",
                        "replacement_plan": "Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.",
                        "retained_dependencies": tool_deps,
                        "reason": "runtime-facing modules should not gain new tools dependencies after Xi-6.",
                    }
                )
            forbidden_deps.extend(
                dep
                for dep in all_module_ids
                if dep.startswith(TOOLS_PREFIX) and dep not in allowed_deps and dep not in STABLE_TOOL_SUPPORT_MODULES
            )

        if module_id == "unknown.root":
            provisional_allowances.append(
                {
                    "allowance_id": "repo_root_support_surface",
                    "replacement_plan": "Classify repo-root support files into a declared repo/support domain in a later non-runtime cleanup pass.",
                    "retained_dependencies": [],
                    "reason": "root support files remain intentionally frozen as a provisional support surface.",
                }
            )

        allowed_products = _sorted_unique_strings(row.get("related_build_targets") or registry_row.get("related_build_targets") or [])
        forbidden_products: list[str] = []
        if role in {"archive", "documentation", "test", "data"}:
            forbidden_products = _sorted_unique_strings(allowed_products)
            allowed_products = []

        rule = {
            "module_id": module_id,
            "module_root": _norm_rel(row.get("module_root") or registry_row.get("module_root")),
            "domain": _token(row.get("domain") or registry_row.get("domain")),
            "role": role,
            "allowed_dependency_modules": allowed_deps,
            "forbidden_dependency_modules": _sorted_unique_strings(forbidden_deps),
            "allowed_products": allowed_products,
            "forbidden_products": forbidden_products,
            "allowed_platform_adapters": _platform_adapter_modules(allowed_deps),
            "stability_class": "provisional" if provisional_allowances else "stable",
            "provisional_allowances": provisional_allowances,
            "replacement_plan": provisional_allowances[0]["replacement_plan"] if provisional_allowances else "",
            "deterministic_fingerprint": "",
        }
        rule["deterministic_fingerprint"] = _payload_fingerprint(rule)
        provisional_allowance_count += len(provisional_allowances)
        rules.append(rule)

    payload = {
        "report_id": "xi.6.module_boundary_rules.v1",
        "source_architecture_graph_fingerprint": _token(architecture_graph.get("deterministic_fingerprint")),
        "source_module_registry_fingerprint": _token(module_registry.get("deterministic_fingerprint")),
        "module_rule_count": len(rules),
        "provisional_allowance_count": provisional_allowance_count,
        "modules": rules,
    }
    return _freeze_manifest(
        payload,
        identity_id="module_boundary_rules.v1",
        contract_id="contract.arch.module_boundaries.v1",
    )


def build_single_engine_registry_payload(repo_root: str) -> dict[str, object]:
    symbol_index = _read_json(repo_root, SYMBOL_INDEX_REL)
    rows = [dict(item or {}) for item in list(symbol_index.get("symbols") or [])]
    engines: list[dict[str, object]] = []

    for spec in ENGINE_SPECS:
        symbols = []
        duplicate_findings = []
        allowed_modules = set(_sorted_unique_strings(spec.get("allowed_definition_modules") or []))
        allowed_paths = set(_sorted_unique_strings(spec.get("canonical_file_paths") or []))
        for symbol_name in _sorted_unique_strings(spec.get("canonical_entrypoint_symbols") or []):
            matches = [
                row
                for row in rows
                if _token(row.get("symbol_name")) == symbol_name
            ]
            observed = []
            for row in matches:
                item = {
                    "file_path": _norm_rel(row.get("file_path")),
                    "line_number": int(row.get("line_number", 0) or 0),
                    "module_id": _token(row.get("module_id")),
                    "symbol_kind": _token(row.get("symbol_kind")),
                    "symbol_name": symbol_name,
                }
                observed.append(item)
                if item["symbol_kind"] != "function":
                    continue
                if item["module_id"] not in allowed_modules or item["file_path"] not in allowed_paths:
                    duplicate_findings.append(
                        {
                            "file_path": item["file_path"],
                            "line_number": item["line_number"],
                            "module_id": item["module_id"],
                            "reason": "canonical engine symbol defined outside the allowlisted engine surface",
                            "symbol_name": symbol_name,
                        }
                    )
            symbols.append(
                {
                    "symbol_name": symbol_name,
                    "observed_definitions": sorted(
                        observed,
                        key=lambda item: (
                            _token(item.get("module_id")),
                            _norm_rel(item.get("file_path")),
                            int(item.get("line_number", 0) or 0),
                            _token(item.get("symbol_kind")),
                        ),
                    ),
                }
            )

        engine = {
            "engine_id": _token(spec.get("engine_id")),
            "semantic_area": _token(spec.get("semantic_area")),
            "canonical_module_id": _token(spec.get("canonical_module_id")),
            "canonical_entrypoint_symbols": _sorted_unique_strings(spec.get("canonical_entrypoint_symbols") or []),
            "canonical_file_paths": _sorted_unique_strings(spec.get("canonical_file_paths") or []),
            "allowed_definition_modules": _sorted_unique_strings(spec.get("allowed_definition_modules") or []),
            "description": _token(spec.get("description")),
            "forbidden_duplicates": duplicate_findings,
            "symbols": symbols,
            "deterministic_fingerprint": "",
        }
        engine["deterministic_fingerprint"] = _payload_fingerprint(engine)
        engines.append(engine)

    payload = {
        "report_id": "xi.6.single_engine_registry.v1",
        "engine_count": len(engines),
        "engines": engines,
        "source_symbol_index_fingerprint": _token(symbol_index.get("deterministic_fingerprint")),
    }
    return _freeze_manifest(
        payload,
        identity_id="single_engine_registry.v1",
        contract_id="contract.arch.single_engine_registry.v1",
    )


def recompute_fingerprint(payload: Mapping[str, object]) -> str:
    return _payload_fingerprint(payload)


def recompute_content_hash(payload: Mapping[str, object]) -> str:
    body = dict(payload or {})
    body["content_hash"] = ""
    body["deterministic_fingerprint"] = ""
    return _content_hash(body)


def load_architecture_graph_v1(repo_root: str) -> dict[str, object]:
    return _read_json(repo_root, ARCHITECTURE_GRAPH_V1_REL)


def load_module_boundary_rules(repo_root: str) -> dict[str, object]:
    return _read_json(repo_root, MODULE_BOUNDARY_RULES_V1_REL)


def load_single_engine_registry(repo_root: str) -> dict[str, object]:
    return _read_json(repo_root, SINGLE_ENGINE_REGISTRY_REL)


def _active_update_tags(repo_root: str, update_tag_payload: Mapping[str, object] | None = None) -> list[str]:
    payload = dict(update_tag_payload or _load_optional_json(repo_root, ARCH_GRAPH_UPDATE_TAG_REL))
    tags = []
    for key in ("tags", "required_tags", "update_tags"):
        value = payload.get(key)
        if isinstance(value, (list, tuple)):
            tags.extend(_sorted_unique_strings(value))
        elif _token(value):
            tags.append(_token(value))
    return _sorted_unique_strings(tags)


def has_arch_graph_update_tag(repo_root: str, update_tag_payload: Mapping[str, object] | None = None) -> bool:
    return ARCH_UPDATE_TAG in set(_active_update_tags(repo_root, update_tag_payload))


def evaluate_architecture_drift(
    repo_root: str,
    live_graph: Mapping[str, object] | None = None,
    frozen_graph: Mapping[str, object] | None = None,
    update_tag_payload: Mapping[str, object] | None = None,
) -> dict[str, object]:
    frozen = dict(frozen_graph or load_architecture_graph_v1(repo_root))
    raw_live = dict(live_graph or live_snapshot(repo_root))
    candidate = _freeze_manifest(
        raw_live,
        identity_id="architecture_graph.v1",
        contract_id="contract.arch.graph.v1",
    )
    frozen_hash = _token(frozen.get("content_hash"))
    live_hash = _token(candidate.get("content_hash"))
    drifted = frozen_hash != live_hash
    tag_present = has_arch_graph_update_tag(repo_root, update_tag_payload)
    module_delta = sorted(
        set(_module_rows_by_id(candidate).keys()).symmetric_difference(set(_module_rows_by_id(frozen).keys()))
    )
    report = {
        "drifted": drifted,
        "frozen_content_hash": frozen_hash,
        "live_content_hash": live_hash,
        "arch_graph_update_tag_present": tag_present,
        "module_delta_preview": module_delta[:25],
        "status": "pass" if (not drifted or tag_present) else "fail",
    }
    if drifted and not tag_present:
        report["reason"] = "live architecture graph differs from architecture_graph.v1 without ARCH-GRAPH-UPDATE"
    elif drifted:
        report["reason"] = "live architecture graph differs, but an ARCH-GRAPH-UPDATE tag is present"
    else:
        report["reason"] = "live architecture graph matches architecture_graph.v1"
    report["deterministic_fingerprint"] = _payload_fingerprint(report)
    return report


def build_architecture_drift_report(repo_root: str) -> dict[str, object]:
    return evaluate_architecture_drift(repo_root)


def build_boundary_findings(
    repo_root: str,
    *,
    live_graph: Mapping[str, object] | None = None,
    boundary_rules: Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    graph = dict(live_graph or live_snapshot(repo_root))
    rules_payload = dict(boundary_rules or load_module_boundary_rules(repo_root))
    rules = {
        _token(row.get("module_id")): dict(row or {})
        for row in list(rules_payload.get("modules") or [])
        if _token(dict(row or {}).get("module_id"))
    }
    modules = _module_rows_by_id(graph)
    findings: list[dict[str, object]] = []

    for module_id, row in sorted(modules.items()):
        if module_id not in rules:
            findings.append(
                {
                    "finding_id": "module_not_registered.{}".format(_id_token(module_id)),
                    "message": "new module root appears without Xi-6 registration",
                    "module_id": module_id,
                    "file_path": _norm_rel(row.get("module_root")),
                    "line_number": 1,
                    "remediation": "refresh architecture graph/module registry with ARCH-GRAPH-UPDATE before changing boundaries",
                    "rule_id": "INV-MODULE-BOUNDARIES-RESPECTED",
                    "severity": "fail",
                }
            )
        if _token(row.get("domain")) == "unknown" and module_id != "unknown.root":
            findings.append(
                {
                    "finding_id": "module_unknown_domain.{}".format(_id_token(module_id)),
                    "message": "module domain remains unknown after Xi-6 freeze",
                    "module_id": module_id,
                    "file_path": _norm_rel(row.get("module_root")),
                    "line_number": 1,
                    "remediation": "classify the module into a declared domain before introducing new dependencies",
                    "rule_id": "INV-MODULE-BOUNDARIES-RESPECTED",
                    "severity": "fail",
                }
            )

    for module_id, rule in sorted(rules.items()):
        deps = set(_sorted_unique_strings((modules.get(module_id) or {}).get("dependencies") or []))
        allowed = set(_sorted_unique_strings(rule.get("allowed_dependency_modules") or []))
        forbidden = set(_sorted_unique_strings(rule.get("forbidden_dependency_modules") or []))
        for dep in sorted(deps - allowed):
            findings.append(
                {
                    "finding_id": "module_unapproved_dependency.{}.{}".format(_id_token(module_id), _id_token(dep)),
                    "message": "module '{}' gained dependency '{}' outside frozen Xi-6 boundaries".format(module_id, dep),
                    "module_id": module_id,
                    "dependency_module_id": dep,
                    "file_path": _norm_rel((modules.get(module_id) or {}).get("module_root")),
                    "line_number": 1,
                    "remediation": "update module_boundary_rules.v1 only via ARCH-GRAPH-UPDATE or remove the dependency",
                    "rule_id": "INV-MODULE-BOUNDARIES-RESPECTED",
                    "severity": "fail",
                }
            )
        for dep in sorted(deps & forbidden):
            findings.append(
                {
                    "finding_id": "module_forbidden_dependency.{}.{}".format(_id_token(module_id), _id_token(dep)),
                    "message": "module '{}' depends on forbidden module '{}'".format(module_id, dep),
                    "module_id": module_id,
                    "dependency_module_id": dep,
                    "file_path": _norm_rel((modules.get(module_id) or {}).get("module_root")),
                    "line_number": 1,
                    "remediation": "route through an approved façade or update the boundary plan through manual review",
                    "rule_id": "INV-MODULE-BOUNDARIES-RESPECTED",
                    "severity": "fail",
                }
            )

    return sorted(
        findings,
        key=lambda item: (
            _norm_rel(item.get("file_path")),
            int(item.get("line_number", 0) or 0),
            _token(item.get("finding_id")),
        ),
    )


def build_ui_truth_leak_findings(
    repo_root: str,
    *,
    live_graph: Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    graph = dict(live_graph or live_snapshot(repo_root))
    modules = _module_rows_by_id(graph)
    findings: list[dict[str, object]] = []
    for module_id, row in sorted(modules.items()):
        if _module_role(module_id, row) != "ui_renderer":
            continue
        deps = _sorted_unique_strings(row.get("dependencies") or [])
        for dep in deps:
            if not dep.startswith(TRUTH_FORBIDDEN_PREFIXES):
                continue
            findings.append(
                {
                    "finding_id": "ui_truth_leak.{}.{}".format(_id_token(module_id), _id_token(dep)),
                    "message": "UI or renderer module '{}' reads truth-adjacent module '{}'".format(module_id, dep),
                    "module_id": module_id,
                    "dependency_module_id": dep,
                    "file_path": _norm_rel(row.get("module_root")),
                    "line_number": 1,
                    "remediation": "route the dependency through a perceived-model or process-owned interface",
                    "rule_id": "INV-MODULE-BOUNDARIES-RESPECTED",
                    "severity": "fail",
                }
            )
    return findings


def build_single_engine_findings(
    repo_root: str,
    *,
    single_engine_registry: Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    registry = dict(single_engine_registry or load_single_engine_registry(repo_root))
    findings: list[dict[str, object]] = []
    for engine in list(registry.get("engines") or []):
        entry = dict(engine or {})
        engine_id = _token(entry.get("engine_id"))
        allowed_modules = set(_sorted_unique_strings(entry.get("allowed_definition_modules") or []))
        canonical_paths = set(_sorted_unique_strings(entry.get("canonical_file_paths") or []))
        for symbol_row in list(entry.get("symbols") or []):
            symbol_entry = dict(symbol_row or {})
            symbol_name = _token(symbol_entry.get("symbol_name"))
            definitions = []
            for observed in list(symbol_entry.get("observed_definitions") or []):
                item = dict(observed or {})
                key = (
                    _token(item.get("module_id")),
                    _norm_rel(item.get("file_path")),
                    int(item.get("line_number", 0) or 0),
                    _token(item.get("symbol_kind")),
                )
                if key not in definitions:
                    definitions.append(key)
            if not any(key[3] == "function" for key in definitions):
                findings.append(
                    {
                        "finding_id": "missing_engine_symbol.{}.{}".format(engine_id, _id_token(symbol_name)),
                        "message": "canonical engine '{}' is missing required function symbol '{}'".format(engine_id, symbol_name),
                        "file_path": canonical_paths and sorted(canonical_paths)[0] or "",
                        "line_number": 1,
                        "remediation": "restore the canonical engine entrypoint before Xi-7 enforcement",
                        "rule_id": "INV-SINGLE-CANONICAL-ENGINES",
                        "severity": "fail",
                    }
                )
            for module_id, file_path, line_number, symbol_kind in definitions:
                if symbol_kind != "function":
                    continue
                if module_id in allowed_modules and file_path in canonical_paths:
                    continue
                findings.append(
                    {
                        "finding_id": "duplicate_engine_symbol.{}.{}.{}.{}".format(
                            engine_id,
                            _id_token(symbol_name),
                            _id_token(module_id),
                            _id_token(file_path),
                        ),
                        "message": "semantic engine '{}' has duplicate function symbol '{}' outside the canonical surface".format(engine_id, symbol_name),
                        "module_id": module_id,
                        "file_path": file_path,
                        "line_number": line_number,
                        "remediation": "collapse duplicate semantics into the canonical engine module or convert the surface to a re-export only",
                        "rule_id": "INV-SINGLE-CANONICAL-ENGINES",
                        "severity": "fail",
                    }
                )
    return sorted(findings, key=lambda item: (_norm_rel(item.get("file_path")), int(item.get("line_number", 0) or 0), _token(item.get("finding_id"))))


def _render_architecture_graph_spec(
    frozen_graph: Mapping[str, object],
    frozen_registry: Mapping[str, object],
    single_engine_registry: Mapping[str, object],
) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-6",
        "Replacement Target: superseded by a later explicit ARCH-GRAPH-UPDATE freeze only",
        "",
        "# Architecture Graph Spec v1",
        "",
        "This document freezes the post-Xi-5 architecture graph as the canonical Xi-6 baseline.",
        "",
        "## Identity",
        "",
        "- graph id: `{}`".format(_token(dict(frozen_graph.get("identity") or {}).get("id"))),
        "- graph contract id: `{}`".format(_token(frozen_graph.get("contract_id"))),
        "- graph content hash: `{}`".format(_token(frozen_graph.get("content_hash"))),
        "- graph fingerprint: `{}`".format(_token(frozen_graph.get("deterministic_fingerprint"))),
        "- module registry id: `{}`".format(_token(dict(frozen_registry.get("identity") or {}).get("id"))),
        "- module registry content hash: `{}`".format(_token(frozen_registry.get("content_hash"))),
        "- module count: `{}`".format(len(list(frozen_graph.get("modules") or []))),
        "- concept count: `{}`".format(len(list(frozen_graph.get("concepts") or []))),
        "- canonical semantic engines: `{}`".format(len(list(single_engine_registry.get("engines") or []))),
        "",
        "## Freeze Rules",
        "",
        "- `architecture_graph.v1.json` is the authoritative structural baseline for Xi-6 and later drift checks.",
        "- live architecture changes require an `ARCH-GRAPH-UPDATE` tag before the frozen baseline may diverge.",
        "- module roots must remain registered; new unregistered module roots are invariant failures.",
        "- frozen graph hashes are computed canonically and must not depend on wallclock state.",
        "",
        "## Provisional Notes",
        "",
        "- `unknown.root` is retained as a provisional repo-support surface pending later non-runtime cleanup.",
        "- transitional compat helpers still located under `tools.compatx.core` and `tools.xstack.compatx` are treated as explicit support bridges during Xi-6.",
    ]
    return "\n".join(lines) + "\n"


def _render_module_boundaries_doc(boundary_rules: Mapping[str, object]) -> str:
    modules = [dict(item or {}) for item in list(boundary_rules.get("modules") or [])]
    provisional = [row for row in modules if list(row.get("provisional_allowances") or [])]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-6",
        "Replacement Target: superseded by a later explicit ARCH-GRAPH-UPDATE freeze only",
        "",
        "# Module Boundaries v1",
        "",
        "The canonical per-module rule matrix lives in `data/architecture/module_boundary_rules.v1.json`.",
        "",
        "## Constitutional Alignment",
        "",
        "- renderers and UI must not read TruthModel directly; Xi-6 forbids new truth-adjacent dependencies from frozen UI surfaces.",
        "- applications must not mutate truth outside processes; Xi-6 freezes current app dependency surfaces and blocks undeclared new truth edges.",
        "- tools must not contaminate runtime; Xi-6 blocks new runtime-to-tools dependencies outside explicit support bridges.",
        "",
        "## Rule Summary",
        "",
        "- module count: `{}`".format(len(modules)),
        "- provisional module count: `{}`".format(len(provisional)),
        "- boundary fingerprint: `{}`".format(_token(boundary_rules.get("deterministic_fingerprint"))),
        "",
        "## Provisional Allowances",
        "",
    ]
    if not provisional:
        lines.append("- none")
    for row in provisional:
        allowances = [dict(item or {}) for item in list(row.get("provisional_allowances") or [])]
        allowance_ids = ", ".join(_token(item.get("allowance_id")) for item in allowances)
        replacement = _token(row.get("replacement_plan")) or (_token(allowances[0].get("replacement_plan")) if allowances else "")
        lines.append("- `{}` -> `{}`; replacement plan: {}".format(_token(row.get("module_id")), allowance_ids, replacement))
    lines.extend(
        [
            "",
            "## Canonical Artifact",
            "",
            "- every frozen module rule records allowed dependencies, forbidden dependencies, allowed products, forbidden products, allowed platform adapters, stability class, and a per-rule deterministic fingerprint.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_final_report(
    frozen_graph: Mapping[str, object],
    boundary_rules: Mapping[str, object],
    single_engine_registry: Mapping[str, object],
    gate_runs: Sequence[Mapping[str, object]],
) -> str:
    provisional = []
    for row in list(boundary_rules.get("modules") or []):
        item = dict(row or {})
        for allowance in list(item.get("provisional_allowances") or []):
            provisional.append(
                {
                    "module_id": _token(item.get("module_id")),
                    "allowance_id": _token(dict(allowance or {}).get("allowance_id")),
                    "replacement_plan": _token(dict(allowance or {}).get("replacement_plan")),
                }
            )
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-6",
        "Replacement Target: superseded by a later explicit ARCH-GRAPH-UPDATE freeze only",
        "",
        "# XI-6 Final",
        "",
        "## Frozen Graph",
        "",
        "- architecture_graph.v1 hash: `{}`".format(_token(frozen_graph.get("content_hash"))),
        "- architecture_graph.v1 fingerprint: `{}`".format(_token(frozen_graph.get("deterministic_fingerprint"))),
        "- module boundary rules hash: `{}`".format(_token(boundary_rules.get("content_hash"))),
        "- module boundary rules fingerprint: `{}`".format(_token(boundary_rules.get("deterministic_fingerprint"))),
        "",
        "## Single Canonical Engines",
        "",
    ]
    for row in list(single_engine_registry.get("engines") or []):
        entry = dict(row or {})
        lines.append("- `{}` -> `{}`".format(_token(entry.get("engine_id")), _token(entry.get("canonical_module_id"))))
    lines.extend(["", "## Provisional Allowances", ""])
    if not provisional:
        lines.append("- none")
    for row in provisional:
        lines.append(
            "- `{}` / `{}` -> {}".format(
                _token(row.get("module_id")),
                _token(row.get("allowance_id")),
                _token(row.get("replacement_plan")),
            )
        )
    lines.extend(["", "## Validation", ""])
    for row in list(gate_runs or []):
        entry = dict(row or {})
        lines.append("- `{}`: `{}`".format(_token(entry.get("gate_id")), _token(entry.get("status"))))
    xi7_ready = all(_token(dict(row or {}).get("status")) == "pass" for row in list(gate_runs or []))
    lines.extend(["", "## Xi-7 Readiness", "", "- ready for Xi-7 CI guard integration: `{}`".format("true" if xi7_ready else "false")])
    return "\n".join(lines) + "\n"


def _run_subprocess_gate(repo_root: str, gate_id: str, command: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=repo_root,
        env=_python_env(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    payload: dict[str, object] = {
        "gate_id": gate_id,
        "evidence_mode": "subprocess",
        "command": command,
        "returncode": int(completed.returncode),
        "status": "pass" if completed.returncode == 0 else "fail",
    }
    text = str(completed.stdout or "").strip()
    if text:
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = {}
        if isinstance(parsed, dict):
            for field_name in (
                "deterministic_fingerprint",
                "result",
                "matched_case_count",
                "mismatched_case_count",
                "error_count",
                "warning_count",
            ):
                token = parsed.get(field_name)
                if token not in (None, ""):
                    payload[field_name] = token
        else:
            payload["output_excerpt"] = text.splitlines()[-20:]
    return payload


def collect_gate_runs(repo_root: str) -> list[dict[str, object]]:
    subset = ",".join(XI6_TARGETED_TESTS)
    return [
        _run_subprocess_gate(repo_root, "build_verify", ["cmake", "--build", "--preset", "verify", "--config", "Debug", "--target", "all_runtime"]),
        _run_subprocess_gate(repo_root, "validate_strict", ["python", "-B", "tools/ci/validate_all.py", "--repo-root", ".", "--strict"]),
        _run_subprocess_gate(repo_root, "arch_audit_2", ["python", "-B", "tools/audit/tool_run_arch_audit.py", "--repo-root", "."]),
        _run_subprocess_gate(repo_root, "omega_1_worldgen_lock", ["python", "-B", "tools/worldgen/tool_verify_worldgen_lock.py", "--repo-root", "."]),
        _run_subprocess_gate(repo_root, "omega_2_baseline_universe", ["python", "-B", "tools/mvp/tool_verify_baseline_universe.py", "--repo-root", "."]),
        _run_subprocess_gate(repo_root, "omega_3_gameplay_loop", ["python", "-B", "tools/mvp/tool_verify_gameplay_loop.py", "--repo-root", "."]),
        _run_subprocess_gate(repo_root, "omega_4_disaster_suite", ["python", "-B", "tools/mvp/tool_run_disaster_suite.py", "--repo-root", "."]),
        _run_subprocess_gate(repo_root, "omega_5_ecosystem_verify", ["python", "-B", "tools/mvp/tool_verify_ecosystem.py", "--repo-root", "."]),
        _run_subprocess_gate(repo_root, "omega_6_update_sim", ["python", "-B", "tools/mvp/tool_run_update_sim.py", "--repo-root", "."]),
        _run_subprocess_gate(repo_root, "trust_strict_suite", ["python", "-B", "tools/security/tool_run_trust_strict_suite.py", "--repo-root", "."]),
        _run_subprocess_gate(
            repo_root,
            "targeted_xi6_tests",
            [
                "python",
                "-B",
                "tools/xstack/testx/runner.py",
                "--repo-root",
                ".",
                "--profile",
                "FAST",
                "--cache",
                "off",
                "--subset",
                subset,
            ],
        ),
    ]


def write_xi6_outputs(
    repo_root: str,
    frozen_graph: Mapping[str, object],
    frozen_registry: Mapping[str, object],
    boundary_rules: Mapping[str, object],
    single_engine_registry: Mapping[str, object],
    gate_runs: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, str]:
    written = {
        "architecture_graph_v1": _write_json(repo_root, ARCHITECTURE_GRAPH_V1_REL, dict(frozen_graph or {})),
        "module_registry_v1": _write_json(repo_root, MODULE_REGISTRY_V1_REL, dict(frozen_registry or {})),
        "module_boundary_rules_v1": _write_json(repo_root, MODULE_BOUNDARY_RULES_V1_REL, dict(boundary_rules or {})),
        "single_engine_registry": _write_json(repo_root, SINGLE_ENGINE_REGISTRY_REL, dict(single_engine_registry or {})),
        "architecture_graph_spec_v1": _write_text(
            repo_root,
            ARCHITECTURE_GRAPH_SPEC_V1_REL,
            _render_architecture_graph_spec(frozen_graph, frozen_registry, single_engine_registry),
        ),
        "module_boundaries_v1": _write_text(
            repo_root,
            MODULE_BOUNDARIES_V1_REL,
            _render_module_boundaries_doc(boundary_rules),
        ),
        "xi_6_final": _write_text(
            repo_root,
            XI_6_FINAL_REL,
            _render_final_report(frozen_graph, boundary_rules, single_engine_registry, list(gate_runs or [])),
        ),
    }
    return written


def run_xi6(repo_root: str, run_gates: bool = True) -> dict[str, object]:
    root = _repo_root(repo_root)
    ensure_inputs(root)
    live = refresh_architecture_snapshot(root)
    raw_graph = _read_json(root, ARCHITECTURE_GRAPH_REL)
    raw_registry = _read_json(root, MODULE_REGISTRY_REL)

    frozen_graph = _freeze_manifest(
        raw_graph,
        identity_id="architecture_graph.v1",
        contract_id="contract.arch.graph.v1",
    )
    frozen_registry = _freeze_manifest(
        raw_registry,
        identity_id="module_registry.v1",
        contract_id="contract.arch.module_registry.v1",
    )
    boundary_rules = build_module_boundary_rules_payload(raw_graph, raw_registry)
    single_engine_registry = build_single_engine_registry_payload(root)

    write_xi6_outputs(
        root,
        frozen_graph,
        frozen_registry,
        boundary_rules,
        single_engine_registry,
        [],
    )

    gate_runs = collect_gate_runs(root) if run_gates else []
    write_xi6_outputs(
        root,
        frozen_graph,
        frozen_registry,
        boundary_rules,
        single_engine_registry,
        gate_runs,
    )

    drift_report = build_architecture_drift_report(root)
    boundary_findings = build_boundary_findings(root, live_graph=live, boundary_rules=boundary_rules)
    ui_truth_findings = build_ui_truth_leak_findings(root, live_graph=live)
    single_engine_findings = build_single_engine_findings(root, single_engine_registry=single_engine_registry)
    passed = all(_token(row.get("status")) == "pass" for row in gate_runs)
    if drift_report.get("status") != "pass":
        passed = False
    if boundary_findings or ui_truth_findings or single_engine_findings:
        passed = False

    return {
        "result": "complete" if passed else "blocked",
        "architecture_graph_v1": frozen_graph,
        "module_registry_v1": frozen_registry,
        "module_boundary_rules": boundary_rules,
        "single_engine_registry": single_engine_registry,
        "drift_report": drift_report,
        "boundary_findings": boundary_findings,
        "ui_truth_leak_findings": ui_truth_findings,
        "single_engine_findings": single_engine_findings,
        "gate_runs": gate_runs,
    }


__all__ = [
    "ARCHITECTURE_GRAPH_V1_REL",
    "MODULE_REGISTRY_V1_REL",
    "MODULE_BOUNDARY_RULES_V1_REL",
    "SINGLE_ENGINE_REGISTRY_REL",
    "XI_6_FINAL_REL",
    "XI6_TARGETED_TESTS",
    "Xi6InputsMissing",
    "build_architecture_drift_report",
    "build_boundary_findings",
    "build_module_boundary_rules_payload",
    "build_single_engine_findings",
    "build_single_engine_registry_payload",
    "build_ui_truth_leak_findings",
    "ensure_inputs",
    "evaluate_architecture_drift",
    "has_arch_graph_update_tag",
    "live_snapshot",
    "load_architecture_graph_v1",
    "load_module_boundary_rules",
    "load_single_engine_registry",
    "recompute_content_hash",
    "recompute_fingerprint",
    "refresh_architecture_snapshot",
    "run_xi6",
    "write_xi6_outputs",
]

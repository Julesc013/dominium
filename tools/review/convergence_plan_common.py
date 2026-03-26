"""Deterministic XI-3 convergence-planning helpers."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


DUPLICATE_CLUSTER_RANKINGS_REL = "data/analysis/duplicate_cluster_rankings.json"
IMPLEMENTATION_SCORES_REL = "data/analysis/implementation_scores.json"
DUPLICATE_IMPLS_REL = "data/audit/duplicate_impls.json"
SHADOW_MODULES_REL = "data/audit/shadow_modules.json"
ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
MODULE_DEP_GRAPH_REL = "data/architecture/module_dependency_graph.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"
DOC_SYMBOL_LINKS_REL = "data/audit/doc_symbol_links.json"

CONVERGENCE_PLAN_REL = "data/refactor/convergence_plan.json"
CONVERGENCE_ACTIONS_REL = "data/refactor/convergence_actions.json"
CONVERGENCE_RISK_MAP_REL = "data/refactor/convergence_risk_map.json"

CONVERGENCE_PLAN_DOC_REL = "docs/refactor/CONVERGENCE_PLAN.md"
CONVERGENCE_RISK_REPORT_REL = "docs/refactor/CONVERGENCE_RISK_REPORT.md"
CONVERGENCE_CHECKLIST_REL = "docs/refactor/CONVERGENCE_CHECKLIST.md"
XI_3_FINAL_REL = "docs/audit/XI_3_FINAL.md"

OUTPUT_REL_PATHS = {
    CONVERGENCE_PLAN_REL,
    CONVERGENCE_ACTIONS_REL,
    CONVERGENCE_RISK_MAP_REL,
    CONVERGENCE_PLAN_DOC_REL,
    CONVERGENCE_RISK_REPORT_REL,
    CONVERGENCE_CHECKLIST_REL,
    XI_3_FINAL_REL,
}

REQUIRED_INPUTS = {
    "architecture_graph": ARCHITECTURE_GRAPH_REL,
    "build_graph": BUILD_GRAPH_REL,
    "duplicate_cluster_rankings": DUPLICATE_CLUSTER_RANKINGS_REL,
    "duplicate_impls": DUPLICATE_IMPLS_REL,
    "implementation_scores": IMPLEMENTATION_SCORES_REL,
    "module_dependency_graph": MODULE_DEP_GRAPH_REL,
    "shadow_modules": SHADOW_MODULES_REL,
}

DOC_REPORT_DATE = "2026-03-26"
SOURCE_LIKE_DIRS = {"Source", "Sources", "source", "src"}
TEST_PATH_PREFIXES = ("Testing/", "game/tests/", "tests/", "tools/xstack/testx/tests/")
PRODUCTION_PRODUCT_TOKENS = {"client", "launcher", "server", "setup"}
HIGH_RISK_REASON_ORDER = (
    "semantic_contracts",
    "worldgen_lock_or_overlay",
    "protocol_negotiation",
    "trust_enforcement",
    "pack_compat_install_resolver",
    "time_anchor",
    "ipc_attach",
)
MEDIUM_RISK_REASON_ORDER = ("ui_mode_selector", "virtual_paths", "supervisor")
CORE_QUARANTINE_REASONS = {
    "semantic_contracts",
    "protocol_negotiation",
    "time_anchor",
    "worldgen_lock_or_overlay",
}
ENFORCEMENT_PROPOSALS = (
    "INV-NO-SRC-DIRECTORY",
    "INV-NO-DUPLICATE-SEMANTIC-ENGINE",
    "INV-ARCH-GRAPH-MATCH",
    "INV-NO-HARDCODED-BUNDLE-CONTENTS",
)
HIGH_RISK_LIMIT = 20
MANUAL_REVIEW_LIMIT = 20
ACTION_SYMBOL_SAMPLE_LIMIT = 12
ACTION_KIND_ORDER = {"keep": 0, "merge": 1, "rewire": 2, "deprecate": 3, "quarantine": 4}
RISK_ORDER = {"HIGH": 0, "MED": 1, "LOW": 2}
GENERIC_ACTION_SYMBOLS = {
    "_authority_context",
    "_ensure_dir",
    "_error",
    "_law_profile",
    "_load_json",
    "_norm",
    "_read",
    "_read_json",
    "_read_text",
    "_refusal",
    "_repo_root",
    "_run",
    "_rows",
    "_sorted_tokens",
    "_state",
    "_write",
    "_write_json",
    "_write_text",
    "authority_context",
    "build_report",
    "check_list",
    "check_version",
    "copy_dir",
    "deterministic_fingerprint",
    "ensure_dir",
    "entries",
    "fail",
    "get",
    "has",
    "is_dir",
    "list_dir",
    "load_json",
    "main",
    "norm",
    "path_join",
    "read_file_text",
    "read_json",
    "read_text",
    "report_json_path",
    "run",
    "run_cmd",
    "usage",
    "validation",
    "void",
    "write_json",
    "write_text",
}


class XiInputMissingError(RuntimeError):
    """Raised when the required XI inputs are missing."""

    def __init__(self, missing_paths: Sequence[str]):
        super().__init__("missing XI inputs")
        self.missing_paths = sorted({_norm_rel(path) for path in missing_paths if _token(path)})
        self.refusal_code = "refusal.xi.missing_inputs"
        self.remediation = "Run Ξ-0 through Ξ-2 first."


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, _norm_rel(rel_path).replace("/", os.sep))))


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload)))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _required_inputs(repo_root: str) -> dict[str, dict]:
    root = _repo_root(repo_root)
    missing = []
    payloads: dict[str, dict] = {}
    for key, rel_path in sorted(REQUIRED_INPUTS.items()):
        abs_path = _repo_abs(root, rel_path)
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
            continue
        payload = _read_json(abs_path)
        if not payload:
            missing.append(rel_path)
            continue
        payloads[key] = payload
    optional_doc_links = _repo_abs(root, DOC_SYMBOL_LINKS_REL)
    payloads["doc_symbol_links"] = _read_json(optional_doc_links) if os.path.isfile(optional_doc_links) else {}
    if missing:
        raise XiInputMissingError(missing)
    return payloads


def _term_fragments(value: object) -> list[str]:
    normalized = re.sub(r"[^A-Za-z0-9]+", " ", _norm_rel(value))
    return [part.lower() for part in normalized.split() if part]


def _simple_symbol_name(symbol_name: object) -> str:
    token = _token(symbol_name)
    if not token:
        return ""
    token = token.split("::")[-1]
    token = token.split(".")[-1]
    return token


def _tests_only_path(path: object) -> bool:
    norm = _norm_rel(path)
    return any(norm.startswith(prefix) for prefix in TEST_PATH_PREFIXES)


def _source_like_path(path: object) -> bool:
    parts = [part for part in _norm_rel(path).split("/") if part]
    return any(part in SOURCE_LIKE_DIRS for part in parts)


def _is_runtime_path(path: object) -> bool:
    norm = _norm_rel(path)
    if _tests_only_path(norm):
        return False
    return norm.startswith(("app/", "apps/", "client/", "engine/", "game/", "launcher/", "server/", "setup/", "src/"))


def _action_with_fingerprint(payload: Mapping[str, object]) -> dict[str, object]:
    data = dict(payload)
    data["deterministic_fingerprint"] = canonical_sha256(data)
    return data


def _extract_doc_symbol_links(payload: Mapping[str, object]) -> dict[str, list[str]]:
    rows = payload.get("links") or payload.get("symbols") or payload.get("entries") or []
    mapping: defaultdict[str, set[str]] = defaultdict(set)
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            symbol = _token(row.get("symbol_name") or row.get("symbol") or row.get("name"))
            if not symbol:
                continue
            docs: list[str] = []
            for key in ("doc_path", "file_path", "path"):
                value = _token(row.get(key))
                if value:
                    docs.append(_norm_rel(value))
            refs = row.get("docs") or row.get("doc_paths") or row.get("references") or []
            if isinstance(refs, list):
                docs.extend(_norm_rel(item) for item in refs if _token(item))
            for doc in docs:
                mapping[symbol].add(doc)
    return {symbol: sorted(paths) for symbol, paths in sorted(mapping.items())}


def _production_target_count(values: Iterable[object]) -> int:
    count = 0
    for value in values:
        token = _token(value).lower()
        if any(part in token for part in PRODUCTION_PRODUCT_TOKENS):
            count += 1
    return count


def _correct_module_root(file_path: object, module_id: object, module_roots: Mapping[str, str]) -> bool:
    file_token = _norm_rel(file_path)
    root = _norm_rel(module_roots.get(_token(module_id), ""))
    if not file_token or not root:
        return False
    return file_token == root or file_token.startswith(root + "/")


def _file_family_key(file_path: object) -> str:
    parts = [part for part in _norm_rel(file_path).split("/") if part]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return "/".join(parts[:-1])


def _module_family_key(module_id: object) -> str:
    token = _token(module_id)
    if "." not in token:
        return token
    return token.rsplit(".", 1)[0]


def _shadow_links(shadow_modules: Sequence[Mapping[str, object]]) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    by_module_id: dict[str, dict[str, object]] = {}
    by_root: dict[str, dict[str, object]] = {}
    for row in sorted(shadow_modules, key=lambda item: (_token(item.get("shadow_module_id")), _token(item.get("shadow_module_root")))):
        module_id = _token(row.get("shadow_module_id"))
        module_root = _norm_rel(row.get("shadow_module_root"))
        if module_id:
            by_module_id[module_id] = dict(row)
        if module_root:
            by_root[module_root] = dict(row)
    return by_module_id, by_root


def _generic_action_symbol(symbol_name: object) -> bool:
    lowered = _simple_symbol_name(symbol_name).lower()
    return bool(lowered) and lowered in GENERIC_ACTION_SYMBOLS


def _exact_duplicate_index(groups: Sequence[Mapping[str, object]]) -> dict[str, list[str]]:
    by_file: defaultdict[str, set[str]] = defaultdict(set)
    for group in groups:
        symbol_name = _token(group.get("symbol_name"))
        for definition in group.get("definitions") or []:
            if not isinstance(definition, dict):
                continue
            file_path = _norm_rel(definition.get("file_path"))
            if file_path and symbol_name:
                by_file[file_path].add(symbol_name)
    return {file_path: sorted(symbols) for file_path, symbols in sorted(by_file.items())}


def _risk_reasons_for_values(
    symbol_name: object,
    file_path: object,
    module_id: object,
    focus_tags: Sequence[object],
    docs: Sequence[object],
    targets: Sequence[object],
) -> list[str]:
    reasons: set[str] = set()
    focus_values = {_token(value) for value in focus_tags if _token(value)}
    if "contracts" in focus_values:
        reasons.add("semantic_contracts")
    if "worldgen" in focus_values:
        reasons.add("worldgen_lock_or_overlay")
    if "protocol_negotiation" in focus_values:
        reasons.add("protocol_negotiation")
    if "trust_enforcement" in focus_values:
        reasons.add("trust_enforcement")
    if "pack_verification" in focus_values:
        reasons.add("pack_compat_install_resolver")
    if "time_anchors" in focus_values:
        reasons.add("time_anchor")
    joined = " ".join(
        [
            _token(symbol_name),
            _norm_rel(file_path),
            _token(module_id),
            " ".join(_norm_rel(item) for item in docs if _token(item)),
            " ".join(_token(item) for item in targets if _token(item)),
        ]
    ).lower()
    if "ipc" in joined and "attach" in joined:
        reasons.add("ipc_attach")
    if "ui" in joined and "selector" in joined:
        reasons.add("ui_mode_selector")
    if "mode selector" in joined:
        reasons.add("ui_mode_selector")
    if "virtual" in joined and ("path" in joined or "paths" in joined):
        reasons.add("virtual_paths")
    if "supervisor" in joined:
        reasons.add("supervisor")
    if "overlay" in joined or "worldgen" in joined:
        reasons.add("worldgen_lock_or_overlay")
    if "negotiat" in joined or "handshake" in joined or "cap_neg" in joined:
        reasons.add("protocol_negotiation")
    if "trust" in joined or "receipt" in joined:
        reasons.add("trust_enforcement")
    if "pack" in joined or "install" in joined or "bundle" in joined:
        reasons.add("pack_compat_install_resolver")
    if "time" in joined or "anchor" in joined or "epoch" in joined:
        reasons.add("time_anchor")
    if "contract" in joined or "schema" in joined or "compat" in joined:
        reasons.add("semantic_contracts")
    ordered = [reason for reason in HIGH_RISK_REASON_ORDER if reason in reasons]
    ordered.extend(reason for reason in MEDIUM_RISK_REASON_ORDER if reason in reasons)
    return ordered


def _risk_level_from_context(reasons: Sequence[object], file_path: object, module_id: object) -> str:
    reason_tokens = {_token(reason) for reason in reasons if _token(reason)}
    if any(reason in reason_tokens for reason in HIGH_RISK_REASON_ORDER):
        return "HIGH"
    if any(reason in reason_tokens for reason in MEDIUM_RISK_REASON_ORDER):
        return "MED"
    if _is_runtime_path(file_path) or _token(module_id).startswith(("app", "apps", "client", "engine", "game", "launcher", "server", "setup")):
        return "MED"
    return "LOW"


def _phase_for_risk(action_kind: str, risk_level: str) -> str:
    if action_kind == "keep":
        return "phase_0_selection_record"
    if action_kind == "quarantine":
        return "phase_5_deprecation_and_quarantine"
    if action_kind == "rewire":
        return "phase_4_rewire_sweep"
    if action_kind == "deprecate":
        return "phase_5_deprecation_and_quarantine"
    if risk_level == "HIGH":
        return "phase_3_high_risk_merges"
    if risk_level == "MED":
        return "phase_2_medium_risk_merges"
    return "phase_1_safe_merges"


def _required_test_commands(risk_level: str, reasons: Sequence[object], include_convergence_tests: bool = True) -> list[str]:
    commands: list[str] = []
    if include_convergence_tests:
        commands.append(
            "python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable"
        )
    if risk_level == "LOW":
        commands.append("python tools/validation/tool_run_validation.py --repo-root . --profile FAST")
    else:
        commands.append("python tools/validation/tool_run_validation.py --repo-root . --profile STRICT")
        commands.extend(
            [
                "python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .",
                "python tools/mvp/tool_verify_baseline_universe.py --repo-root .",
                "python tools/mvp/tool_verify_gameplay_loop.py --repo-root .",
                "python tools/mvp/tool_run_disaster_suite.py --repo-root .",
            ]
        )
    reason_tokens = {_token(reason) for reason in reasons if _token(reason)}
    if "protocol_negotiation" in reason_tokens or "semantic_contracts" in reason_tokens:
        commands.append("python tools/compat/tool_run_interop_stress.py --repo-root .")
    if "pack_compat_install_resolver" in reason_tokens:
        commands.append("python tools/mvp/tool_run_product_boot_matrix.py --repo-root .")
        commands.append("python tools/mvp/tool_run_all_stress.py --repo-root .")
    if "trust_enforcement" in reason_tokens:
        commands.append("python tools/security/tool_run_trust_strict_suite.py --repo-root .")
    if "time_anchor" in reason_tokens:
        commands.append("python tools/time/tool_verify_longrun_ticks.py --repo-root .")
    if "ipc_attach" in reason_tokens:
        commands.append("python tools/appshell/tool_run_ipc_unify.py --repo-root .")
    if "supervisor" in reason_tokens:
        commands.append("python tools/appshell/tool_run_supervisor_hardening.py --repo-root .")
    if risk_level == "HIGH":
        commands.append("python tools/convergence/tool_run_convergence_gate.py --repo-root .")
    seen: set[str] = set()
    ordered: list[str] = []
    for command in commands:
        if command not in seen:
            seen.add(command)
            ordered.append(command)
    return ordered


def _build_indexes(payloads: Mapping[str, dict]) -> dict[str, object]:
    architecture_modules = list(dict(payloads.get("architecture_graph") or {}).get("modules") or [])
    shadow_modules = list(dict(payloads.get("shadow_modules") or {}).get("modules") or [])
    build_targets = list(dict(payloads.get("build_graph") or {}).get("targets") or [])
    module_edges = list(dict(payloads.get("module_dependency_graph") or {}).get("edges") or [])
    duplicate_groups = list(dict(payloads.get("duplicate_impls") or {}).get("groups") or [])
    implementation_rows = list(dict(payloads.get("implementation_scores") or {}).get("implementations") or [])
    doc_symbol_links = _extract_doc_symbol_links(dict(payloads.get("doc_symbol_links") or {}))

    module_roots: dict[str, str] = {}
    module_entries: dict[str, dict[str, object]] = {}
    for row in architecture_modules:
        if not isinstance(row, dict):
            continue
        module_id = _token(row.get("module_id"))
        if not module_id:
            continue
        module_entries[module_id] = dict(row)
        module_roots[module_id] = _norm_rel(row.get("module_root"))

    module_dependencies: defaultdict[str, set[str]] = defaultdict(set)
    for row in module_edges:
        if not isinstance(row, dict):
            continue
        source = _token(row.get("from_module_id"))
        target = _token(row.get("to_module_id"))
        if source and target:
            module_dependencies[source].add(target)

    file_to_targets: defaultdict[str, set[str]] = defaultdict(set)
    file_to_products: defaultdict[str, set[str]] = defaultdict(set)
    for row in build_targets:
        if not isinstance(row, dict):
            continue
        target_id = _token(row.get("target_id"))
        product_id = _token(row.get("product_id"))
        for source in row.get("sources") or []:
            file_path = _norm_rel(source)
            if not file_path:
                continue
            if target_id:
                file_to_targets[file_path].add(target_id)
            if product_id:
                file_to_products[file_path].add(product_id)

    impl_by_cluster_file: dict[tuple[str, str], dict[str, object]] = {}
    cluster_rows: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in implementation_rows:
        if not isinstance(row, dict):
            continue
        cluster_id = _token(row.get("cluster_id"))
        file_path = _norm_rel(row.get("file_path"))
        if not cluster_id or not file_path:
            continue
        data = dict(row)
        data["file_path"] = file_path
        data["module_id"] = _token(data.get("module_id"))
        data["symbol_name"] = _token(data.get("symbol_name"))
        data["build_targets_using_file"] = sorted({_token(item) for item in data.get("build_targets_using_file") or [] if _token(item)})
        data["docs_referencing_symbol"] = sorted(
            {
                _norm_rel(item)
                for item in list(data.get("docs_referencing_symbol") or []) + doc_symbol_links.get(_token(data.get("symbol_name")), [])
                if _token(item)
            }
        )
        data["dependency_edges"] = sorted({_norm_rel(item) for item in data.get("dependency_edges") or [] if _token(item)})
        data["focus_tags"] = sorted({_token(item) for item in data.get("focus_tags") or [] if _token(item)})
        impl_by_cluster_file[(cluster_id, file_path)] = data
        cluster_rows[cluster_id].append(data)

    shadow_by_module_id, shadow_by_root = _shadow_links(shadow_modules)
    exact_symbols_by_file = _exact_duplicate_index(duplicate_groups)

    return {
        "cluster_rows": {cluster_id: sorted(rows, key=lambda item: (_norm_rel(item.get("file_path")), _token(item.get("module_id")))) for cluster_id, rows in sorted(cluster_rows.items())},
        "doc_symbol_links": doc_symbol_links,
        "exact_symbols_by_file": exact_symbols_by_file,
        "file_to_products": {key: sorted(values) for key, values in sorted(file_to_products.items())},
        "file_to_targets": {key: sorted(values) for key, values in sorted(file_to_targets.items())},
        "impl_by_cluster_file": impl_by_cluster_file,
        "module_dependencies": {key: sorted(values) for key, values in sorted(module_dependencies.items())},
        "module_entries": module_entries,
        "module_roots": module_roots,
        "shadow_by_module_id": shadow_by_module_id,
        "shadow_by_root": shadow_by_root,
    }


def _selection_key(candidate: Mapping[str, object], module_roots: Mapping[str, str]) -> tuple[object, ...]:
    file_path = _norm_rel(candidate.get("file_path"))
    module_id = _token(candidate.get("module_id"))
    build_targets = candidate.get("build_targets_using_file") or []
    return (
        -round(float(candidate.get("total_score", 0.0) or 0.0), 6),
        -int(_correct_module_root(file_path, module_id, module_roots)),
        int(_source_like_path(file_path)),
        -_production_target_count(build_targets),
        file_path,
        module_id,
        _token(candidate.get("symbol_name")),
    )


def _winner_tie_break(candidates: Sequence[Mapping[str, object]], winner: Mapping[str, object], module_roots: Mapping[str, str]) -> str:
    if len(candidates) <= 1:
        return "sole_candidate"
    score = round(float(winner.get("total_score", 0.0) or 0.0), 6)
    score_ties = [row for row in candidates if round(float(row.get("total_score", 0.0) or 0.0), 6) == score]
    if len(score_ties) == 1:
        return "highest_total_score"
    root_matches = [row for row in score_ties if _correct_module_root(row.get("file_path"), row.get("module_id"), module_roots)]
    winner_is_root = _correct_module_root(winner.get("file_path"), winner.get("module_id"), module_roots)
    if winner_is_root and len(root_matches) == 1:
        return "correct_module_root"
    non_src = [row for row in (root_matches or score_ties) if not _source_like_path(row.get("file_path"))]
    if not _source_like_path(winner.get("file_path")) and len(non_src) == 1:
        return "prefer_not_under_src"
    winner_prod = _production_target_count(winner.get("build_targets_using_file") or [])
    prod_matches = [row for row in (non_src or root_matches or score_ties) if _production_target_count(row.get("build_targets_using_file") or []) == winner_prod]
    if len(prod_matches) == 1:
        return "production_target_count"
    return "lexicographic_file_path"


def _candidate_evidence(candidate: Mapping[str, object], indexes: Mapping[str, object]) -> dict[str, object]:
    file_path = _norm_rel(candidate.get("file_path"))
    module_id = _token(candidate.get("module_id"))
    module_roots = dict(indexes.get("module_roots") or {})
    build_targets = sorted({_token(item) for item in candidate.get("build_targets_using_file") or [] if _token(item)})
    docs = sorted({_norm_rel(item) for item in candidate.get("docs_referencing_symbol") or [] if _token(item)})
    dependency_edges = sorted({_norm_rel(item) for item in candidate.get("dependency_edges") or [] if _token(item)})
    risk_reasons = _risk_reasons_for_values(
        candidate.get("symbol_name"),
        file_path,
        module_id,
        candidate.get("focus_tags") or [],
        docs,
        build_targets,
    )
    return {
        "architecture_score": round(float(candidate.get("architecture_score", 0.0) or 0.0), 4),
        "build_targets_using_file": build_targets,
        "correct_module_root": _correct_module_root(file_path, module_id, module_roots),
        "dependency_complexity": int(candidate.get("dependency_complexity", len(dependency_edges)) or 0),
        "dependency_edges": dependency_edges,
        "dependency_score": round(float(candidate.get("dependency_score", 0.0) or 0.0), 4),
        "determinism_evidence": sorted({_token(item) for item in candidate.get("determinism_evidence") or [] if _token(item)}),
        "determinism_score": round(float(candidate.get("determinism_score", 0.0) or 0.0), 4),
        "docs_referencing_symbol": docs,
        "documentation_score": round(float(candidate.get("documentation_score", 0.0) or 0.0), 4),
        "file_path": file_path,
        "focus_tags": sorted({_token(item) for item in candidate.get("focus_tags") or [] if _token(item)}),
        "integration_score": round(float(candidate.get("integration_score", 0.0) or 0.0), 4),
        "module_dependency_edges": list(dict(indexes.get("module_dependencies") or {}).get(module_id, [])),
        "module_id": module_id,
        "number_of_call_sites": int(candidate.get("number_of_call_sites", 0) or 0),
        "production_target_count": _production_target_count(build_targets),
        "risk_level": _risk_level_from_context(risk_reasons, file_path, module_id),
        "risk_reasons": risk_reasons,
        "source_like_path": _source_like_path(file_path),
        "symbol_name": _token(candidate.get("symbol_name")),
        "test_score": round(float(candidate.get("test_score", 0.0) or 0.0), 4),
        "total_score": round(float(candidate.get("total_score", 0.0) or 0.0), 4),
    }


def _related_files(winner: Mapping[str, object], secondary: Mapping[str, object]) -> bool:
    if _file_family_key(winner.get("file_path")) == _file_family_key(secondary.get("file_path")):
        return True
    if _module_family_key(winner.get("module_id")) == _module_family_key(secondary.get("module_id")):
        return True
    return False


def _shadow_relation(candidate: Mapping[str, object], indexes: Mapping[str, object]) -> dict[str, object]:
    module_id = _token(candidate.get("module_id"))
    file_path = _norm_rel(candidate.get("file_path"))
    module_roots = dict(indexes.get("module_roots") or {})
    shadow_by_module_id = dict(indexes.get("shadow_by_module_id") or {})
    shadow_by_root = dict(indexes.get("shadow_by_root") or {})
    shadow = shadow_by_module_id.get(module_id)
    if shadow is None:
        root = _norm_rel(module_roots.get(module_id, ""))
        shadow = shadow_by_root.get(root) or shadow_by_root.get(_file_family_key(file_path))
    return dict(shadow or {})


def _secondary_docs(winner: Mapping[str, object], secondary: Mapping[str, object]) -> list[str]:
    docs = set(_norm_rel(item) for item in winner.get("docs_referencing_symbol") or [] if _token(item))
    docs.update(_norm_rel(item) for item in secondary.get("docs_referencing_symbol") or [] if _token(item))
    return sorted(docs)


def _secondary_disposition(winner: Mapping[str, object], secondary: Mapping[str, object], indexes: Mapping[str, object]) -> tuple[str, list[str]]:
    winner_score = float(winner.get("total_score", 0.0) or 0.0)
    secondary_score = float(secondary.get("total_score", 0.0) or 0.0)
    score_delta = round(winner_score - secondary_score, 4)
    reasons = _risk_reasons_for_values(
        secondary.get("symbol_name"),
        secondary.get("file_path"),
        secondary.get("module_id"),
        secondary.get("focus_tags") or [],
        secondary.get("docs_referencing_symbol") or [],
        secondary.get("build_targets_using_file") or [],
    )
    if score_delta < 10.0 and any(reason in CORE_QUARANTINE_REASONS for reason in reasons):
        return "QUARANTINE", ["core_semantic_small_score_delta"]

    merge_signals: list[str] = []
    if float(secondary.get("test_score", 0.0) or 0.0) > float(winner.get("test_score", 0.0) or 0.0):
        merge_signals.append("additional_tests_surface")
    if float(secondary.get("determinism_score", 0.0) or 0.0) > float(winner.get("determinism_score", 0.0) or 0.0):
        merge_signals.append("determinism_signal")
    if len(secondary.get("docs_referencing_symbol") or []) > len(winner.get("docs_referencing_symbol") or []):
        merge_signals.append("documentation_reference_surface")
    if _production_target_count(secondary.get("build_targets_using_file") or []) > _production_target_count(winner.get("build_targets_using_file") or []):
        merge_signals.append("production_target_surface")
    if float(secondary.get("integration_score", 0.0) or 0.0) > float(winner.get("integration_score", 0.0) or 0.0) and score_delta <= 12.0:
        merge_signals.append("integration_depth_delta")
    if int(secondary.get("dependency_complexity", 0) or 0) < int(winner.get("dependency_complexity", 0) or 0) and score_delta <= 8.0:
        merge_signals.append("dependency_hygiene_delta")
    exact_symbols_by_file = dict(indexes.get("exact_symbols_by_file") or {})
    secondary_symbols = set(exact_symbols_by_file.get(_norm_rel(secondary.get("file_path")), []))
    winner_symbols = set(exact_symbols_by_file.get(_norm_rel(winner.get("file_path")), []))
    if _related_files(winner, secondary) and sorted(secondary_symbols - winner_symbols):
        merge_signals.append("unique_symbol_delta")
    if _shadow_relation(secondary, indexes):
        merge_signals.append("shadow_module_surface")
    if score_delta == 0.0:
        merge_signals.append("score_tie_requires_delta_merge")

    if merge_signals:
        return "MERGE", sorted(set(merge_signals))
    return "DROP", []


def _cluster_decisions(cluster: Mapping[str, object], indexes: Mapping[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    cluster_id = _token(cluster.get("cluster_id"))
    symbol_name = _token(cluster.get("symbol_name"))
    candidates: list[dict[str, object]] = []
    module_roots = dict(indexes.get("module_roots") or {})
    cluster_rows = dict(indexes.get("cluster_rows") or {}).get(cluster_id, [])
    impl_by_cluster_file = dict(indexes.get("impl_by_cluster_file") or {})
    seen_paths: set[str] = set()
    for row in cluster.get("ranked_candidates") or []:
        if not isinstance(row, dict):
            continue
        file_path = _norm_rel(row.get("file_path"))
        if not file_path or file_path in seen_paths:
            continue
        seen_paths.add(file_path)
        merged = dict(impl_by_cluster_file.get((cluster_id, file_path)) or {})
        merged.update(dict(row))
        if not merged.get("symbol_name"):
            merged["symbol_name"] = symbol_name
        if not merged.get("focus_tags"):
            merged["focus_tags"] = sorted({_token(item) for item in cluster.get("focus_tags") or [] if _token(item)})
        candidates.append(_candidate_evidence(merged, indexes))
    for row in cluster_rows:
        file_path = _norm_rel(row.get("file_path"))
        if not file_path or file_path in seen_paths:
            continue
        seen_paths.add(file_path)
        candidates.append(_candidate_evidence(row, indexes))
    candidates = sorted(candidates, key=lambda item: _selection_key(item, module_roots))
    winner = dict(candidates[0]) if candidates else {
        "file_path": "",
        "module_id": "",
        "symbol_name": symbol_name,
        "focus_tags": sorted({_token(item) for item in cluster.get("focus_tags") or [] if _token(item)}),
        "build_targets_using_file": [],
        "docs_referencing_symbol": [],
        "risk_reasons": [],
        "risk_level": "LOW",
        "dependency_complexity": 0,
        "total_score": 0.0,
    }
    winner["decision_basis"] = _winner_tie_break(candidates, winner, module_roots) if candidates else "missing_candidate"
    winner["candidate_rank"] = 1
    secondaries: list[dict[str, object]] = []
    for rank, candidate in enumerate(candidates[1:], start=2):
        disposition, signals = _secondary_disposition(winner, candidate, indexes)
        secondary = dict(candidate)
        secondary["candidate_rank"] = rank
        secondary["disposition"] = disposition
        secondary["merge_signals"] = signals
        secondary["score_delta"] = round(float(winner.get("total_score", 0.0) or 0.0) - float(candidate.get("total_score", 0.0) or 0.0), 4)
        secondaries.append(secondary)
    return winner, secondaries


def _action_payload(
    cluster: Mapping[str, object],
    kind: str,
    canonical: Mapping[str, object],
    secondary: Mapping[str, object] | None,
    required_tests: Sequence[object],
    affected_docs: Sequence[object],
    affected_targets: Sequence[object],
) -> dict[str, object]:
    cluster_id = _token(cluster.get("cluster_id"))
    symbol_name = _token(cluster.get("symbol_name"))
    secondary_file = _norm_rel((secondary or {}).get("file_path"))
    suffix = canonical_sha256({"cluster_id": cluster_id, "kind": kind, "secondary_file": secondary_file})[:12]
    payload = {
        "action_id": f"convergence.action.{kind}.{suffix}",
        "affected_docs": sorted({_norm_rel(item) for item in affected_docs if _token(item)}),
        "affected_symbols": sorted({_token(symbol_name)} | {_token(item) for item in (secondary or {}).get("merge_signals") or [] if False})[:ACTION_SYMBOL_SAMPLE_LIMIT],
        "affected_targets": sorted({_token(item) for item in affected_targets if _token(item)}),
        "canonical_file": _norm_rel(canonical.get("file_path")),
        "canonical_module_id": _token(canonical.get("module_id")),
        "cluster_id": cluster_id,
        "cluster_kind": _token(cluster.get("cluster_kind")),
        "focus_tags": sorted({_token(item) for item in cluster.get("focus_tags") or [] if _token(item)}),
        "kind": kind,
        "required_tests": [str(item) for item in required_tests if _token(item)],
        "secondary_file": secondary_file,
        "secondary_module_id": _token((secondary or {}).get("module_id")),
        "symbol_name": symbol_name,
    }
    if secondary:
        payload["merge_signals"] = sorted({_token(item) for item in secondary.get("merge_signals") or [] if _token(item)})
        payload["score_delta"] = round(float(secondary.get("score_delta", 0.0) or 0.0), 4)
    else:
        payload["merge_signals"] = []
        payload["score_delta"] = 0.0
    payload["affected_symbols"] = [symbol_name] if symbol_name else []
    return _action_with_fingerprint(payload)


def _cluster_actions(cluster: Mapping[str, object], winner: Mapping[str, object], secondaries: Sequence[Mapping[str, object]], indexes: Mapping[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    focus_tags = sorted({_token(item) for item in cluster.get("focus_tags") or [] if _token(item)})
    symbol_name = _token(cluster.get("symbol_name"))
    cluster_risk_reasons = _risk_reasons_for_values(
        winner.get("symbol_name"),
        winner.get("file_path"),
        winner.get("module_id"),
        focus_tags,
        winner.get("docs_referencing_symbol") or [],
        winner.get("build_targets_using_file") or [],
    )
    cluster_risk_level = _risk_level_from_context(cluster_risk_reasons, winner.get("file_path"), winner.get("module_id"))
    actions: list[dict[str, object]] = []
    keep_tests = _required_test_commands(cluster_risk_level, cluster_risk_reasons)
    keep_action = _action_payload(
        cluster,
        "keep",
        winner,
        None,
        keep_tests,
        winner.get("docs_referencing_symbol") or [],
        winner.get("build_targets_using_file") or [],
    )
    keep_action["phase"] = _phase_for_risk("keep", cluster_risk_level)
    keep_action["risk_level"] = cluster_risk_level
    keep_action["risk_reasons"] = cluster_risk_reasons
    keep_action["deterministic_fingerprint"] = canonical_sha256({key: value for key, value in keep_action.items() if key != "deterministic_fingerprint"})
    actions.append(keep_action)

    summary = {
        "cluster_id": _token(cluster.get("cluster_id")),
        "cluster_kind": _token(cluster.get("cluster_kind")),
        "confidence_class": _token(cluster.get("confidence_class")),
        "focus_tags": focus_tags,
        "symbol_name": symbol_name,
        "canonical_candidate": winner,
        "risk_level": cluster_risk_level,
        "risk_reasons": cluster_risk_reasons,
        "secondary_candidates": [],
        "cluster_resolution": "keep",
    }

    if _generic_action_symbol(symbol_name):
        summary["execution_note"] = "generic_symbol_secondary_actions_suppressed"
        return sorted(
            actions,
            key=lambda item: (
                _token(item.get("cluster_id")),
                ACTION_KIND_ORDER.get(_token(item.get("kind")), 99),
                _norm_rel(item.get("secondary_file")),
                _norm_rel(item.get("canonical_file")),
            ),
        ), summary

    secondary_paths = [_norm_rel(item.get("file_path")) for item in secondaries if _norm_rel(item.get("file_path"))]
    tests_only_cluster = bool(_tests_only_path(winner.get("file_path"))) and bool(secondary_paths) and all(_tests_only_path(path) for path in secondary_paths)
    if tests_only_cluster and not focus_tags:
        summary["execution_note"] = "tests_only_secondary_actions_suppressed"
        return sorted(
            actions,
            key=lambda item: (
                _token(item.get("cluster_id")),
                ACTION_KIND_ORDER.get(_token(item.get("kind")), 99),
                _norm_rel(item.get("secondary_file")),
                _norm_rel(item.get("canonical_file")),
            ),
        ), summary

    non_runtime_cluster = (
        not focus_tags
        and not _is_runtime_path(winner.get("file_path"))
        and bool(secondary_paths)
        and all(not _is_runtime_path(path) for path in secondary_paths)
    )
    if non_runtime_cluster:
        summary["execution_note"] = "non_runtime_secondary_actions_suppressed"
        return sorted(
            actions,
            key=lambda item: (
                _token(item.get("cluster_id")),
                ACTION_KIND_ORDER.get(_token(item.get("kind")), 99),
                _norm_rel(item.get("secondary_file")),
                _norm_rel(item.get("canonical_file")),
            ),
        ), summary

    cluster_has_merge = False
    cluster_has_quarantine = False
    for secondary in secondaries:
        disposition = _token(secondary.get("disposition")).upper()
        risk_reasons = _risk_reasons_for_values(
            secondary.get("symbol_name"),
            secondary.get("file_path"),
            secondary.get("module_id"),
            secondary.get("focus_tags") or [],
            _secondary_docs(winner, secondary),
            sorted(set(winner.get("build_targets_using_file") or []) | set(secondary.get("build_targets_using_file") or [])),
        )
        risk_level = _risk_level_from_context(risk_reasons, secondary.get("file_path"), secondary.get("module_id"))
        required_tests = _required_test_commands(risk_level, risk_reasons)
        affected_targets = sorted(set(winner.get("build_targets_using_file") or []) | set(secondary.get("build_targets_using_file") or []))
        affected_docs = _secondary_docs(winner, secondary)
        secondary_summary = {
            "candidate_rank": int(secondary.get("candidate_rank", 0) or 0),
            "disposition": disposition.lower(),
            "file_path": _norm_rel(secondary.get("file_path")),
            "merge_signals": sorted({_token(item) for item in secondary.get("merge_signals") or [] if _token(item)}),
            "module_id": _token(secondary.get("module_id")),
            "risk_level": risk_level,
            "risk_reasons": risk_reasons,
            "score_delta": round(float(secondary.get("score_delta", 0.0) or 0.0), 4),
            "total_score": round(float(secondary.get("total_score", 0.0) or 0.0), 4),
        }
        summary["secondary_candidates"].append(secondary_summary)
        if disposition == "QUARANTINE":
            cluster_has_quarantine = True
            action = _action_payload(cluster, "quarantine", winner, secondary, required_tests, affected_docs, affected_targets)
            action["phase"] = _phase_for_risk("quarantine", risk_level)
            action["risk_level"] = risk_level
            action["risk_reasons"] = risk_reasons
            action["deterministic_fingerprint"] = canonical_sha256({key: value for key, value in action.items() if key != "deterministic_fingerprint"})
            actions.append(action)
            continue
        if disposition == "MERGE":
            cluster_has_merge = True
            merge_action = _action_payload(cluster, "merge", winner, secondary, required_tests, affected_docs, affected_targets)
            merge_action["phase"] = _phase_for_risk("merge", risk_level)
            merge_action["risk_level"] = risk_level
            merge_action["risk_reasons"] = risk_reasons
            merge_action["deterministic_fingerprint"] = canonical_sha256({key: value for key, value in merge_action.items() if key != "deterministic_fingerprint"})
            actions.append(merge_action)
        rewire_needed = bool(
            secondary.get("build_targets_using_file")
            or secondary.get("docs_referencing_symbol")
            or secondary.get("number_of_call_sites")
            or _source_like_path(secondary.get("file_path"))
            or _shadow_relation(secondary, indexes)
        )
        if rewire_needed and disposition != "QUARANTINE":
            rewire_action = _action_payload(cluster, "rewire", winner, secondary, required_tests, affected_docs, affected_targets)
            rewire_action["phase"] = _phase_for_risk("rewire", risk_level)
            rewire_action["risk_level"] = risk_level
            rewire_action["risk_reasons"] = risk_reasons
            rewire_action["deterministic_fingerprint"] = canonical_sha256({key: value for key, value in rewire_action.items() if key != "deterministic_fingerprint"})
            actions.append(rewire_action)
        if disposition != "QUARANTINE":
            deprecate_action = _action_payload(cluster, "deprecate", winner, secondary, required_tests, affected_docs, affected_targets)
            deprecate_action["phase"] = _phase_for_risk("deprecate", risk_level)
            deprecate_action["risk_level"] = risk_level
            deprecate_action["risk_reasons"] = risk_reasons
            deprecate_action["deterministic_fingerprint"] = canonical_sha256({key: value for key, value in deprecate_action.items() if key != "deterministic_fingerprint"})
            actions.append(deprecate_action)
    if cluster_has_quarantine:
        summary["cluster_resolution"] = "quarantine"
    elif cluster_has_merge:
        summary["cluster_resolution"] = "merge"
    return sorted(actions, key=lambda item: (_token(item.get("cluster_id")), ACTION_KIND_ORDER.get(_token(item.get("kind")), 99), _norm_rel(item.get("secondary_file")), _norm_rel(item.get("canonical_file")))), summary


def _phase_plan(actions: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    phase_commands = {
        "phase_1_safe_merges": [
            "python tools/xstack/testx/runner.py --repo-root . --profile FAST",
            "python tools/validation/tool_run_validation.py --repo-root . --profile FAST",
        ],
        "phase_2_medium_risk_merges": [
            "python tools/validation/tool_run_validation.py --repo-root . --profile STRICT",
            "python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .",
            "python tools/mvp/tool_verify_baseline_universe.py --repo-root .",
            "python tools/mvp/tool_verify_gameplay_loop.py --repo-root .",
            "python tools/mvp/tool_run_disaster_suite.py --repo-root .",
        ],
        "phase_3_high_risk_merges": [
            "python tools/convergence/tool_run_convergence_gate.py --repo-root .",
        ],
        "phase_4_rewire_sweep": [
            "python tools/review/tool_run_duplicate_impl_scan.py --repo-root .",
            "python tools/review/tool_run_implementation_scoring.py --repo-root .",
            "python tools/validation/tool_run_validation.py --repo-root . --profile STRICT",
        ],
        "phase_5_deprecation_and_quarantine": [
            "python tools/review/tool_run_convergence_plan.py --repo-root .",
            "python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable",
        ],
        "phase_6_src_removal_execution": [
            "python tools/review/tool_run_convergence_plan.py --repo-root .",
            "python tools/convergence/tool_run_convergence_gate.py --repo-root .",
        ],
    }
    phase_titles = {
        "phase_1_safe_merges": "Phase 1 - Safe merges (LOW risk)",
        "phase_2_medium_risk_merges": "Phase 2 - Medium risk merges",
        "phase_3_high_risk_merges": "Phase 3 - High risk merges (one per PR)",
        "phase_4_rewire_sweep": "Phase 4 - Rewire sweep",
        "phase_5_deprecation_and_quarantine": "Phase 5 - Deprecation and quarantine decisions",
        "phase_6_src_removal_execution": "Phase 6 - SRC removal execution (Ξ-5)",
    }
    phase_descriptions = {
        "phase_1_safe_merges": "Execute merge actions for LOW-risk clusters and validate with FAST gates.",
        "phase_2_medium_risk_merges": "Execute MED-risk merges, then run STRICT validation plus the four Ω regression verifies.",
        "phase_3_high_risk_merges": "Execute one HIGH-risk merge action per PR and require the full convergence gate.",
        "phase_4_rewire_sweep": "Update call sites and includes to the chosen canonical implementations, then rerun review and STRICT validation.",
        "phase_5_deprecation_and_quarantine": "Review quarantined items manually, convert them to merge/rewire/deprecate, and record deprecations without deletion.",
        "phase_6_src_removal_execution": "Remove source-like shadow surfaces only after all rewires complete and the convergence gate passes.",
    }
    grouped: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for action in actions:
        grouped[_token(action.get("phase"))].append(action)
    ordered = []
    for phase_id in (
        "phase_1_safe_merges",
        "phase_2_medium_risk_merges",
        "phase_3_high_risk_merges",
        "phase_4_rewire_sweep",
        "phase_5_deprecation_and_quarantine",
        "phase_6_src_removal_execution",
    ):
        phase_actions = sorted(
            grouped.get(phase_id, []),
            key=lambda item: (RISK_ORDER.get(_token(item.get("risk_level")), 9), _token(item.get("cluster_id")), ACTION_KIND_ORDER.get(_token(item.get("kind")), 99), _norm_rel(item.get("secondary_file"))),
        )
        ordered.append(
            {
                "action_count": len(phase_actions),
                "actions": [str(item.get("action_id")) for item in phase_actions],
                "description": phase_descriptions[phase_id],
                "gates": list(phase_commands[phase_id]),
                "phase_id": phase_id,
                "title": phase_titles[phase_id],
            }
        )
    return ordered


def _plan_summary(cluster_summaries: Sequence[Mapping[str, object]], actions: Sequence[Mapping[str, object]]) -> dict[str, object]:
    resolution_counts = Counter(_token(item.get("cluster_resolution")) for item in cluster_summaries)
    action_counts = Counter(_token(item.get("kind")) for item in actions)
    risk_counts = Counter(_token(item.get("risk_level")) for item in actions)
    affected_modules = Counter()
    source_like_clusters = 0
    for item in cluster_summaries:
        canonical = dict(item.get("canonical_candidate") or {})
        module_id = _token(canonical.get("module_id"))
        if module_id:
            affected_modules[module_id] += 1
        if _source_like_path(canonical.get("file_path")) or any(_source_like_path(row.get("file_path")) for row in item.get("secondary_candidates") or []):
            source_like_clusters += 1
    return {
        "action_counts": {key: int(action_counts.get(key, 0)) for key in ("keep", "merge", "rewire", "deprecate", "quarantine")},
        "cluster_resolution_counts": {key: int(resolution_counts.get(key, 0)) for key in ("keep", "merge", "quarantine")},
        "most_affected_modules": [
            {"cluster_count": int(count), "module_id": module_id}
            for module_id, count in sorted(affected_modules.items(), key=lambda item: (-item[1], item[0]))[:20]
        ],
        "risk_counts": {key: int(risk_counts.get(key, 0)) for key in ("HIGH", "MED", "LOW")},
        "source_like_cluster_count": int(source_like_clusters),
    }


def _risk_entries(actions: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    entries = []
    for action in actions:
        if _token(action.get("kind")) == "keep":
            continue
        entries.append(
            {
                "action_id": _token(action.get("action_id")),
                "canonical_file": _norm_rel(action.get("canonical_file")),
                "cluster_id": _token(action.get("cluster_id")),
                "kind": _token(action.get("kind")),
                "phase": _token(action.get("phase")),
                "risk_level": _token(action.get("risk_level")),
                "risk_reasons": sorted({_token(item) for item in action.get("risk_reasons") or [] if _token(item)}),
                "secondary_file": _norm_rel(action.get("secondary_file")),
                "symbol_name": _token(action.get("symbol_name")),
            }
        )
    return sorted(entries, key=lambda item: (RISK_ORDER.get(item["risk_level"], 9), item["cluster_id"], ACTION_KIND_ORDER.get(item["kind"], 99), item["secondary_file"], item["canonical_file"]))


def _top_high_risk_items(cluster_summaries: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    high = []
    for item in cluster_summaries:
        if _token(item.get("risk_level")) != "HIGH":
            continue
        secondaries = sorted(
            [row for row in item.get("secondary_candidates") or [] if isinstance(row, dict)],
            key=lambda row: (ACTION_KIND_ORDER.get(_token(row.get("disposition")), 99), -round(float(row.get("total_score", 0.0) or 0.0), 4), _norm_rel(row.get("file_path"))),
        )
        top_secondary = secondaries[0] if secondaries else {}
        high.append(
            {
                "canonical_file": _norm_rel(dict(item.get("canonical_candidate") or {}).get("file_path")),
                "cluster_id": _token(item.get("cluster_id")),
                "cluster_resolution": _token(item.get("cluster_resolution")),
                "focus_tags": sorted({_token(tag) for tag in item.get("focus_tags") or [] if _token(tag)}),
                "risk_reasons": sorted({_token(tag) for tag in item.get("risk_reasons") or [] if _token(tag)}),
                "secondary_file": _norm_rel(top_secondary.get("file_path")),
                "secondary_disposition": _token(top_secondary.get("disposition")),
                "symbol_name": _token(item.get("symbol_name")),
            }
        )
    return sorted(high, key=lambda item: (item["cluster_resolution"] != "quarantine", item["cluster_id"], item["canonical_file"], item["secondary_file"]))[:HIGH_RISK_LIMIT]


def _manual_review_items(cluster_summaries: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    rows = []
    for item in cluster_summaries:
        if _token(item.get("cluster_resolution")) != "quarantine":
            continue
        secondaries = [row for row in item.get("secondary_candidates") or [] if _token(row.get("disposition")) == "quarantine"]
        for secondary in secondaries:
            rows.append(
                {
                    "canonical_file": _norm_rel(dict(item.get("canonical_candidate") or {}).get("file_path")),
                    "cluster_id": _token(item.get("cluster_id")),
                    "risk_level": _token(secondary.get("risk_level")),
                    "risk_reasons": sorted({_token(tag) for tag in secondary.get("risk_reasons") or [] if _token(tag)}),
                    "score_delta": round(float(secondary.get("score_delta", 0.0) or 0.0), 4),
                    "secondary_file": _norm_rel(secondary.get("file_path")),
                    "symbol_name": _token(item.get("symbol_name")),
                }
            )
    return sorted(rows, key=lambda item: (RISK_ORDER.get(item["risk_level"], 9), item["score_delta"], item["cluster_id"], item["secondary_file"]))[:MANUAL_REVIEW_LIMIT]


def _build_snapshot(repo_root: str) -> dict[str, object]:
    payloads = _required_inputs(repo_root)
    indexes = _build_indexes(payloads)
    ranking_payload = dict(payloads.get("duplicate_cluster_rankings") or {})
    clusters = list(ranking_payload.get("clusters") or [])
    cluster_summaries: list[dict[str, object]] = []
    all_actions: list[dict[str, object]] = []
    for cluster in sorted(clusters, key=lambda item: (_token(item.get("cluster_id")), _token(item.get("symbol_name")))):
        winner, secondaries = _cluster_decisions(cluster, indexes)
        actions, summary = _cluster_actions(cluster, winner, secondaries, indexes)
        cluster_summaries.append(summary)
        all_actions.extend(actions)
    all_actions = sorted(
        all_actions,
        key=lambda item: (_token(item.get("cluster_id")), ACTION_KIND_ORDER.get(_token(item.get("kind")), 99), _norm_rel(item.get("secondary_file")), _norm_rel(item.get("canonical_file"))),
    )
    summary = _plan_summary(cluster_summaries, all_actions)
    phase_boundary = {
        "description": "All src/ implementations must be merge/rewire/deprecate first. src/ removal happens only after all rewires complete and the convergence gate passes.",
        "phase_boundary_id": "src_merge_rewire_before_removal",
        "required_completion_phases": [
            "phase_4_rewire_sweep",
            "phase_5_deprecation_and_quarantine",
            "phase_6_src_removal_execution",
        ],
    }
    convergence_plan = {
        "cluster_count": len(cluster_summaries),
        "clusters": cluster_summaries,
        "decision_rules": [
            "highest_total_score",
            "correct_module_root",
            "prefer_not_under_src",
            "production_target_count",
            "lexicographic_file_path",
        ],
        "enforcement_proposals": list(ENFORCEMENT_PROPOSALS),
        "phase_boundaries": [phase_boundary],
        "phases": _phase_plan(all_actions),
        "report_id": "xi.3.convergence.plan.v1",
        "summary": summary,
    }
    convergence_plan["deterministic_fingerprint"] = canonical_sha256(convergence_plan)

    convergence_actions = {
        "action_count": len(all_actions),
        "actions": all_actions,
        "report_id": "xi.3.convergence.actions.v1",
    }
    convergence_actions["deterministic_fingerprint"] = canonical_sha256(convergence_actions)

    risk_entries = _risk_entries(all_actions)
    convergence_risk_map = {
        "entries": risk_entries,
        "high_risk_items": _top_high_risk_items(cluster_summaries),
        "manual_review_items": _manual_review_items(cluster_summaries),
        "report_id": "xi.3.convergence.risk.v1",
        "risk_counts": summary["risk_counts"],
    }
    convergence_risk_map["deterministic_fingerprint"] = canonical_sha256(convergence_risk_map)

    return {
        "convergence_actions": convergence_actions,
        "convergence_plan": convergence_plan,
        "convergence_risk_map": convergence_risk_map,
    }


def render_convergence_plan(snapshot: Mapping[str, object]) -> str:
    plan = dict(snapshot.get("convergence_plan") or {})
    summary = dict(plan.get("summary") or {})
    lines = [
        "# Deterministic Convergence Plan",
        "",
        f"- Generated: {DOC_REPORT_DATE}",
        f"- Duplicate clusters: {int(plan.get('cluster_count', 0) or 0)}",
        f"- Actions: {int(dict(snapshot.get('convergence_actions') or {}).get('action_count', 0) or 0)}",
        f"- Fingerprint: `{_token(plan.get('deterministic_fingerprint'))}`",
        "",
        "## Resolution Summary",
        "",
        f"- Keep-only clusters: {int(dict(summary.get('cluster_resolution_counts') or {}).get('keep', 0) or 0)}",
        f"- Merge-required clusters: {int(dict(summary.get('cluster_resolution_counts') or {}).get('merge', 0) or 0)}",
        f"- Quarantine clusters: {int(dict(summary.get('cluster_resolution_counts') or {}).get('quarantine', 0) or 0)}",
        f"- Source-like impacted clusters: {int(summary.get('source_like_cluster_count', 0) or 0)}",
        "",
        "## Deterministic Selection Rules",
        "",
        "1. Highest total score wins.",
        "2. If scores tie, prefer the implementation inside the correct module root.",
        "3. If still tied, prefer the implementation outside source-like directories.",
        "4. If still tied, prefer the implementation used by more production targets.",
        "5. If still tied, prefer the lexicographically earliest file path.",
        "",
        "## Phase Boundary",
        "",
        "- All `src/` implementations must be merge/rewire/deprecate first.",
        "- `src/` removal is deferred until rewires complete and the convergence gate passes.",
        "",
        "## Top Convergence Candidates",
        "",
        "| Cluster | Resolution | Canonical | Top secondary | Risk |",
        "| --- | --- | --- | --- | --- |",
    ]
    clusters = list(plan.get("clusters") or [])
    ordered = sorted(
        clusters,
        key=lambda item: (
            {"quarantine": 0, "merge": 1, "keep": 2}.get(_token(item.get("cluster_resolution")), 9),
            RISK_ORDER.get(_token(item.get("risk_level")), 9),
            _token(item.get("cluster_id")),
        ),
    )[:20]
    for item in ordered:
        canonical = dict(item.get("canonical_candidate") or {})
        secondaries = list(item.get("secondary_candidates") or [])
        top_secondary = dict(secondaries[0] if secondaries else {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("cluster_id")),
                _token(item.get("cluster_resolution")),
                _norm_rel(canonical.get("file_path")),
                _norm_rel(top_secondary.get("file_path")),
                _token(item.get("risk_level")),
            )
        )
    lines.extend(
        [
            "",
            "## Enforcement Proposals",
            "",
        ]
    )
    for proposal in plan.get("enforcement_proposals") or []:
        lines.append(f"- `{_token(proposal)}`")
    lines.append("")
    return "\n".join(lines)


def render_convergence_risk_report(snapshot: Mapping[str, object]) -> str:
    risk_map = dict(snapshot.get("convergence_risk_map") or {})
    lines = [
        "# Convergence Risk Report",
        "",
        f"- Generated: {DOC_REPORT_DATE}",
        f"- Fingerprint: `{_token(risk_map.get('deterministic_fingerprint'))}`",
        f"- HIGH risk actions: {int(dict(risk_map.get('risk_counts') or {}).get('HIGH', 0) or 0)}",
        f"- MED risk actions: {int(dict(risk_map.get('risk_counts') or {}).get('MED', 0) or 0)}",
        f"- LOW risk actions: {int(dict(risk_map.get('risk_counts') or {}).get('LOW', 0) or 0)}",
        "",
        "## Top HIGH Risk Items",
        "",
        "| Cluster | Symbol | Canonical | Secondary | Resolution | Reasons |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in risk_map.get("high_risk_items") or []:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("cluster_id")),
                _token(item.get("symbol_name")),
                _norm_rel(item.get("canonical_file")),
                _norm_rel(item.get("secondary_file")),
                _token(item.get("cluster_resolution")),
                ", ".join(_token(reason) for reason in item.get("risk_reasons") or [] if _token(reason)),
            )
        )
    lines.extend(
        [
            "",
            "## Manual Review Queue",
            "",
            "| Cluster | Symbol | Canonical | Secondary | Score delta | Reasons |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in risk_map.get("manual_review_items") or []:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("cluster_id")),
                _token(item.get("symbol_name")),
                _norm_rel(item.get("canonical_file")),
                _norm_rel(item.get("secondary_file")),
                round(float(item.get("score_delta", 0.0) or 0.0), 2),
                ", ".join(_token(reason) for reason in item.get("risk_reasons") or [] if _token(reason)),
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_convergence_checklist(snapshot: Mapping[str, object]) -> str:
    plan = dict(snapshot.get("convergence_plan") or {})
    phases = list(plan.get("phases") or [])
    lines = [
        "# Convergence Checklist",
        "",
        f"- Generated: {DOC_REPORT_DATE}",
        "",
    ]
    for phase in phases:
        lines.append(f"## {_token(phase.get('title'))}")
        lines.append("")
        lines.append(f"- {_token(phase.get('description'))}")
        lines.append(f"- Planned action count: {int(phase.get('action_count', 0) or 0)}")
        for gate in phase.get("gates") or []:
            lines.append(f"- Gate: `{_token(gate)}`")
        lines.append("")
    lines.append("## SRC Policy")
    lines.append("")
    lines.append("- Execute merge/rewire/deprecate actions for all source-like implementations before any removal work.")
    lines.append("- Remove source-like directories only in Ξ-5 after rewires complete and Ω regression gates pass.")
    lines.append("")
    return "\n".join(lines)


def render_xi_3_final(snapshot: Mapping[str, object]) -> str:
    plan = dict(snapshot.get("convergence_plan") or {})
    summary = dict(plan.get("summary") or {})
    risk_map = dict(snapshot.get("convergence_risk_map") or {})
    lines = [
        "# XI-3 Final",
        "",
        f"- Generated: {DOC_REPORT_DATE}",
        f"- Duplicate clusters: {int(plan.get('cluster_count', 0) or 0)}",
        f"- Keep-only clusters: {int(dict(summary.get('cluster_resolution_counts') or {}).get('keep', 0) or 0)}",
        f"- Merge-required clusters: {int(dict(summary.get('cluster_resolution_counts') or {}).get('merge', 0) or 0)}",
        f"- Quarantine clusters: {int(dict(summary.get('cluster_resolution_counts') or {}).get('quarantine', 0) or 0)}",
        "",
        "## Top HIGH Risk Items",
        "",
    ]
    for item in risk_map.get("high_risk_items") or []:
        lines.append(
            "- `{}` -> canonical `{}` vs secondary `{}` ({})".format(
                _token(item.get("cluster_id")),
                _norm_rel(item.get("canonical_file")),
                _norm_rel(item.get("secondary_file")),
                _token(item.get("cluster_resolution")),
            )
        )
    lines.extend(
        [
            "",
            "## Recommended Manual Review",
            "",
        ]
    )
    for item in risk_map.get("manual_review_items") or []:
        lines.append(
            "- `{}` `{}` score delta `{}`".format(
                _token(item.get("cluster_id")),
                _norm_rel(item.get("secondary_file")),
                round(float(item.get("score_delta", 0.0) or 0.0), 2),
            )
        )
    readiness = "ready" if int(dict(summary.get("cluster_resolution_counts") or {}).get("quarantine", 0) or 0) == 0 else "ready_with_manual_review"
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            f"- Ξ-4 readiness: `{readiness}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_convergence_plan_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written = {}
    written[CONVERGENCE_PLAN_REL] = _write_canonical_json(_repo_abs(root, CONVERGENCE_PLAN_REL), dict(snapshot.get("convergence_plan") or {}))
    written[CONVERGENCE_ACTIONS_REL] = _write_canonical_json(_repo_abs(root, CONVERGENCE_ACTIONS_REL), dict(snapshot.get("convergence_actions") or {}))
    written[CONVERGENCE_RISK_MAP_REL] = _write_canonical_json(_repo_abs(root, CONVERGENCE_RISK_MAP_REL), dict(snapshot.get("convergence_risk_map") or {}))
    written[CONVERGENCE_PLAN_DOC_REL] = _write_text(_repo_abs(root, CONVERGENCE_PLAN_DOC_REL), render_convergence_plan(snapshot) + "\n")
    written[CONVERGENCE_RISK_REPORT_REL] = _write_text(_repo_abs(root, CONVERGENCE_RISK_REPORT_REL), render_convergence_risk_report(snapshot) + "\n")
    written[CONVERGENCE_CHECKLIST_REL] = _write_text(_repo_abs(root, CONVERGENCE_CHECKLIST_REL), render_convergence_checklist(snapshot) + "\n")
    written[XI_3_FINAL_REL] = _write_text(_repo_abs(root, XI_3_FINAL_REL), render_xi_3_final(snapshot) + "\n")
    return written


def build_convergence_plan_snapshot(repo_root: str) -> dict[str, object]:
    return _build_snapshot(repo_root)


__all__ = [
    "ARCHITECTURE_GRAPH_REL",
    "BUILD_GRAPH_REL",
    "CONVERGENCE_ACTIONS_REL",
    "CONVERGENCE_CHECKLIST_REL",
    "CONVERGENCE_PLAN_DOC_REL",
    "CONVERGENCE_PLAN_REL",
    "CONVERGENCE_RISK_MAP_REL",
    "CONVERGENCE_RISK_REPORT_REL",
    "DOC_SYMBOL_LINKS_REL",
    "DUPLICATE_CLUSTER_RANKINGS_REL",
    "DUPLICATE_IMPLS_REL",
    "IMPLEMENTATION_SCORES_REL",
    "MODULE_DEP_GRAPH_REL",
    "OUTPUT_REL_PATHS",
    "SHADOW_MODULES_REL",
    "XI_3_FINAL_REL",
    "XiInputMissingError",
    "build_convergence_plan_snapshot",
    "render_convergence_checklist",
    "render_convergence_plan",
    "render_convergence_risk_report",
    "render_xi_3_final",
    "write_convergence_plan_snapshot",
]

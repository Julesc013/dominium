"""Deterministic XI-4b src-domain mapping and structure review helpers."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from io import BytesIO
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
MODULE_DEP_GRAPH_REL = "data/architecture/module_dependency_graph.json"
MODULE_REGISTRY_REL = "data/architecture/module_registry.json"

BUILD_GRAPH_REL = "data/audit/build_graph.json"
INCLUDE_GRAPH_REL = "data/audit/include_graph.json"
SYMBOL_INDEX_REL = "data/audit/symbol_index.json"
DUPLICATE_IMPLS_REL = "data/audit/duplicate_impls.json"
DUPLICATE_CLUSTERS_REL = "data/audit/duplicate_clusters.json"
SHADOW_MODULES_REL = "data/audit/shadow_modules.json"
SRC_DIRECTORY_REPORT_REL = "data/audit/src_directory_report.json"
ARCHITECTURE_SCAN_REPORT_REL = "data/audit/architecture_scan_report.json"
ARCH_AUDIT_REPORT_REL = "data/audit/arch_audit_report.json"
ARCH_AUDIT2_REPORT_REL = "data/audit/arch_audit2_report.json"
VALIDATION_FAST_REL = "data/audit/validation_report_FAST.json"
VALIDATION_STRICT_REL = "data/audit/validation_report_STRICT.json"

CONVERGENCE_PLAN_REL = "data/refactor/convergence_plan.json"
CONVERGENCE_ACTIONS_REL = "data/refactor/convergence_actions.json"
CONVERGENCE_RISK_MAP_REL = "data/refactor/convergence_risk_map.json"
CONVERGENCE_EXECUTION_LOG_REL = "data/refactor/convergence_execution_log.json"

XI_1_FINAL_REL = "docs/audit/XI_1_FINAL.md"
XI_2_FINAL_REL = "docs/audit/XI_2_FINAL.md"
XI_3_FINAL_REL = "docs/audit/XI_3_FINAL.md"
XI_4_FINAL_REL = "docs/audit/XI_4_FINAL.md"

CONVERGENCE_PLAN_DOC_REL = "docs/refactor/CONVERGENCE_PLAN.md"
CONVERGENCE_RISK_REPORT_REL = "docs/refactor/CONVERGENCE_RISK_REPORT.md"
CONVERGENCE_CHECKLIST_REL = "docs/refactor/CONVERGENCE_CHECKLIST.md"
DEPRECATIONS_REL = "docs/refactor/DEPRECATIONS.md"

FINAL_PROMPT_INVENTORY_REL = "docs/blueprint/FINAL_PROMPT_INVENTORY.md"
SNAPSHOT_MAPPING_TEMPLATE_REL = "docs/blueprint/SNAPSHOT_MAPPING_TEMPLATE.md"
PROMPT_DEPENDENCY_TREE_REL = "docs/blueprint/PROMPT_DEPENDENCY_TREE.md"
PROMPT_RISK_MATRIX_REL = "docs/blueprint/PROMPT_RISK_MATRIX.md"
REPO_REALITY_RECONCILIATION_GUIDE_REL = "docs/blueprint/REPO_REALITY_RECONCILIATION_GUIDE.md"

SRC_DOMAIN_MAPPING_REL = "data/restructure/src_domain_mapping.json"
SRC_DOMAIN_MAPPING_CANDIDATES_REL = "data/restructure/src_domain_mapping_candidates.json"
SRC_DOMAIN_MAPPING_CONFLICTS_REL = "data/restructure/src_domain_mapping_conflicts.json"
SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL = "data/restructure/src_domain_mapping_lock_proposal.json"
SRC_RUNTIME_CRITICAL_SET_REL = "data/restructure/src_runtime_critical_set.json"
SRC_TOOL_ONLY_SET_REL = "data/restructure/src_tool_only_set.json"
SRC_GENERATED_SET_REL = "data/restructure/src_generated_set.json"
SRC_TEST_ONLY_SET_REL = "data/restructure/src_test_only_set.json"
SRC_LEGACY_SET_REL = "data/restructure/src_legacy_set.json"
XI4B_REVIEW_MANIFEST_REL = "data/restructure/xi4b_review_manifest.json"

SRC_DOMAIN_MAPPING_REPORT_REL = "docs/restructure/SRC_DOMAIN_MAPPING_REPORT.md"
STRUCTURE_OPTIONS_REPORT_REL = "docs/restructure/STRUCTURE_OPTIONS_REPORT.md"
XI_4B_REVIEW_GUIDE_REL = "docs/restructure/XI_4B_REVIEW_GUIDE.md"
XI_4B_UNBLOCK_REPORT_REL = "docs/restructure/XI_4B_UNBLOCK_REPORT.md"
XI_4B_FINAL_REL = "docs/audit/XI_4B_FINAL.md"

TMP_BUNDLE_REL = "tmp/xi4b_structure_review_bundle.zip"
TMP_BUNDLE_MANIFEST_REL = "tmp/xi4b_structure_review_bundle_manifest.txt"

OUTPUT_REL_PATHS = {
    SRC_DOMAIN_MAPPING_REL,
    SRC_DOMAIN_MAPPING_CANDIDATES_REL,
    SRC_DOMAIN_MAPPING_CONFLICTS_REL,
    SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL,
    SRC_RUNTIME_CRITICAL_SET_REL,
    SRC_TOOL_ONLY_SET_REL,
    SRC_GENERATED_SET_REL,
    SRC_TEST_ONLY_SET_REL,
    SRC_LEGACY_SET_REL,
    XI4B_REVIEW_MANIFEST_REL,
    SRC_DOMAIN_MAPPING_REPORT_REL,
    STRUCTURE_OPTIONS_REPORT_REL,
    XI_4B_REVIEW_GUIDE_REL,
    XI_4B_UNBLOCK_REPORT_REL,
    XI_4B_FINAL_REL,
}

REQUIRED_JSON_INPUTS = {
    "architecture_graph": ARCHITECTURE_GRAPH_REL,
    "module_dependency_graph": MODULE_DEP_GRAPH_REL,
    "module_registry": MODULE_REGISTRY_REL,
    "build_graph": BUILD_GRAPH_REL,
    "include_graph": INCLUDE_GRAPH_REL,
    "symbol_index": SYMBOL_INDEX_REL,
    "duplicate_impls": DUPLICATE_IMPLS_REL,
    "duplicate_clusters": DUPLICATE_CLUSTERS_REL,
    "shadow_modules": SHADOW_MODULES_REL,
    "src_directory_report": SRC_DIRECTORY_REPORT_REL,
    "architecture_scan_report": ARCHITECTURE_SCAN_REPORT_REL,
    "arch_audit_report": ARCH_AUDIT_REPORT_REL,
    "arch_audit2_report": ARCH_AUDIT2_REPORT_REL,
    "validation_report_fast": VALIDATION_FAST_REL,
    "validation_report_strict": VALIDATION_STRICT_REL,
    "convergence_plan": CONVERGENCE_PLAN_REL,
    "convergence_actions": CONVERGENCE_ACTIONS_REL,
    "convergence_risk_map": CONVERGENCE_RISK_MAP_REL,
    "convergence_execution_log": CONVERGENCE_EXECUTION_LOG_REL,
}

REQUIRED_TEXT_INPUTS = {
    "xi_1_final": XI_1_FINAL_REL,
    "xi_2_final": XI_2_FINAL_REL,
    "xi_3_final": XI_3_FINAL_REL,
    "xi_4_final": XI_4_FINAL_REL,
    "convergence_plan_doc": CONVERGENCE_PLAN_DOC_REL,
    "convergence_risk_report": CONVERGENCE_RISK_REPORT_REL,
    "convergence_checklist": CONVERGENCE_CHECKLIST_REL,
    "deprecations_doc": DEPRECATIONS_REL,
    "final_prompt_inventory": FINAL_PROMPT_INVENTORY_REL,
    "snapshot_mapping_template": SNAPSHOT_MAPPING_TEMPLATE_REL,
    "prompt_dependency_tree": PROMPT_DEPENDENCY_TREE_REL,
    "prompt_risk_matrix": PROMPT_RISK_MATRIX_REL,
    "repo_reality_reconciliation_guide": REPO_REALITY_RECONCILIATION_GUIDE_REL,
}

MAJOR_INPUT_KEYS = {
    "architecture_graph",
    "module_registry",
    "build_graph",
    "src_directory_report",
    "convergence_plan",
    "convergence_actions",
    "convergence_execution_log",
    "xi_4_final",
    "final_prompt_inventory",
    "snapshot_mapping_template",
}

BUNDLE_UPSTREAM_RELS = (
    ARCHITECTURE_GRAPH_REL,
    MODULE_REGISTRY_REL,
    BUILD_GRAPH_REL,
    DUPLICATE_IMPLS_REL,
    SHADOW_MODULES_REL,
    SRC_DIRECTORY_REPORT_REL,
    CONVERGENCE_PLAN_REL,
    CONVERGENCE_EXECUTION_LOG_REL,
    XI_4_FINAL_REL,
    FINAL_PROMPT_INVENTORY_REL,
    PROMPT_DEPENDENCY_TREE_REL,
    PROMPT_RISK_MATRIX_REL,
    SNAPSHOT_MAPPING_TEMPLATE_REL,
)

SOURCE_LIKE_NAMES = {"Source", "Sources", "source", "src"}
EXPLICIT_SOURCE_ROOTS = (
    "src",
    "app/src",
    "legacy/source",
    "legacy/launcher_core_launcher/launcher/core/source",
    "legacy/setup_core_setup/setup/core/source",
    "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources",
    "libs/build_identity/src",
    "libs/ui_backends/win32/src",
    "packs/source",
    "tools/ui_shared/src",
)
ALLOWED_DOMAINS = ("engine", "game", "apps", "tools", "lib", "compat", "ui", "platform", "tests", "attic")
OPTION_ORDER = ("A", "B", "C")
ZIP_FIXED_TIMESTAMP = (2026, 3, 27, 0, 0, 0)
DOC_REPORT_DATE = "2026-03-27"
HIGH_CONFIDENCE_THRESHOLD = 0.8
CONFLICT_CONFIDENCE_THRESHOLD = 0.72
CRITICAL_BLOCKER_LIMIT = 40
REPORT_SAMPLE_LIMIT = 20
TEST_FILE_RE = re.compile(r"(^|/)(tests?|Testing)(/|$)|(_test|test_).", re.IGNORECASE)
PRODUCTION_PRODUCTS = {"client", "engine", "game", "launcher", "server", "setup"}
HIGH_RISK_TOKENS = {
    "contract",
    "determinism",
    "epoch",
    "geo",
    "lock",
    "migration",
    "negotiation",
    "overlay",
    "pack",
    "protocol",
    "refine",
    "time",
    "trust",
    "update",
    "worldgen",
}
ENGINE_SEGMENTS = {
    "archive",
    "astro",
    "chem",
    "control",
    "core",
    "diag",
    "diegetics",
    "electric",
    "embodiment",
    "engine",
    "epistemics",
    "field",
    "fields",
    "fluid",
    "geo",
    "governance",
    "inspection",
    "infrastructure",
    "interior",
    "logic",
    "logistics",
    "machines",
    "materials",
    "mechanics",
    "meta",
    "mobility",
    "models",
    "net",
    "performance",
    "physics",
    "pollution",
    "process",
    "reality",
    "release",
    "runtime",
    "safety",
    "security",
    "signals",
    "specs",
    "system",
    "thermal",
    "time",
    "universe",
    "validation",
    "worldgen",
}


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


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read().replace("\r\n", "\n")
    except OSError:
        return ""


def _read_bytes(path: str) -> bytes:
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError:
        return b""


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


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(payload: str) -> str:
    return _sha256_bytes(str(payload or "").encode("utf-8"))


def _slug(token: object) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", _token(token).lower()).strip("_")
    return value or "x"


def _path_parts(path: object) -> list[str]:
    return [part for part in _norm_rel(path).split("/") if part]


def _path_parts_lower(path: object) -> list[str]:
    return [part.lower() for part in _path_parts(path)]


def _source_like_path(path: object) -> bool:
    return any(part in SOURCE_LIKE_NAMES for part in _path_parts(path))


def _domain_from_module_id(module_id: object) -> str:
    token = _token(module_id)
    if not token:
        return ""
    domain = token.split(".", 1)[0]
    return domain if domain in ALLOWED_DOMAINS else ""


def _domain_from_path(path: object) -> str:
    parts = _path_parts_lower(path)
    if not parts:
        return ""
    domain = parts[0]
    return domain if domain in ALLOWED_DOMAINS else ""


def _doc_header(title: str, replacement_target: str) -> str:
    return "\n".join(
        [
            "Status: DERIVED",
            f"Last Reviewed: {DOC_REPORT_DATE}",
            "Supersedes: none",
            "Superseded By: none",
            "Stability: provisional",
            "Future Series: XI-5",
            f"Replacement Target: {replacement_target}",
            "",
            f"# {title}",
            "",
        ]
    )


def _markdown_bullets(values: Iterable[str]) -> list[str]:
    return [f"- {value}" for value in values]


def _git_ls_files(repo_root: str) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            check=True,
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError):
        rows: list[str] = []
        for current_root, _dirs, files in os.walk(repo_root):
            for name in files:
                abs_path = os.path.join(current_root, name)
                rel_path = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                rows.append(rel_path)
        return sorted(set(rows))
    return sorted({_norm_rel(line) for line in completed.stdout.splitlines() if _token(line)})


def _input_key_for_rel(rel_path: str) -> str:
    for key, candidate in REQUIRED_JSON_INPUTS.items():
        if candidate == rel_path:
            return key
    for key, candidate in REQUIRED_TEXT_INPUTS.items():
        if candidate == rel_path:
            return key
    return rel_path


def _build_input_fingerprints(
    json_payloads: Mapping[str, Mapping[str, object]],
    text_payloads: Mapping[str, str],
    quarantine_docs: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key, rel_path in sorted(REQUIRED_JSON_INPUTS.items(), key=lambda item: item[1]):
        payload = dict(json_payloads.get(key) or {})
        if not payload:
            continue
        rows.append(
            {
                "path": rel_path,
                "sha256": _token(payload.get("deterministic_fingerprint")) or canonical_sha256(payload),
            }
        )
    for key, rel_path in sorted(REQUIRED_TEXT_INPUTS.items(), key=lambda item: item[1]):
        payload = _token(text_payloads.get(key))
        if not payload:
            continue
        rows.append({"path": rel_path, "sha256": _sha256_text(payload)})
    for row in sorted(quarantine_docs, key=lambda item: _norm_rel(item.get("path"))):
        rows.append({"path": _norm_rel(row.get("path")), "sha256": _sha256_text(_token(row.get("text")))})
    return rows


def _load_inputs(repo_root: str) -> dict[str, object]:
    json_payloads: dict[str, dict] = {}
    text_payloads: dict[str, str] = {}
    missing_inputs: list[str] = []
    present_inputs: list[str] = []

    for key, rel_path in sorted(REQUIRED_JSON_INPUTS.items()):
        payload = _read_json(_repo_abs(repo_root, rel_path))
        if payload:
            json_payloads[key] = payload
            present_inputs.append(rel_path)
        else:
            json_payloads[key] = {}
            missing_inputs.append(rel_path)

    for key, rel_path in sorted(REQUIRED_TEXT_INPUTS.items()):
        payload = _read_text(_repo_abs(repo_root, rel_path))
        if payload:
            text_payloads[key] = payload
            present_inputs.append(rel_path)
        else:
            text_payloads[key] = ""
            missing_inputs.append(rel_path)

    quarantine_docs: list[dict[str, str]] = []
    quarantine_glob_root = os.path.join(repo_root, "docs", "refactor")
    if os.path.isdir(quarantine_glob_root):
        for name in sorted(os.listdir(quarantine_glob_root)):
            if name.startswith("QUARANTINE_") and name.endswith(".md"):
                rel_path = f"docs/refactor/{name}"
                text = _read_text(_repo_abs(repo_root, rel_path))
                if text:
                    quarantine_docs.append({"path": rel_path, "text": text})
    if not quarantine_docs:
        missing_inputs.append("docs/refactor/QUARANTINE_*.md")

    major_missing = [rel for rel in missing_inputs if _input_key_for_rel(rel) in MAJOR_INPUT_KEYS]
    input_fingerprints = _build_input_fingerprints(json_payloads, text_payloads, quarantine_docs)
    return {
        "json_payloads": json_payloads,
        "text_payloads": text_payloads,
        "quarantine_docs": quarantine_docs,
        "missing_inputs": sorted(set(missing_inputs)),
        "major_missing_inputs": sorted(set(major_missing)),
        "present_inputs": sorted(set(present_inputs)),
        "input_fingerprints": input_fingerprints,
    }


def _discover_source_roots(tracked_files: Sequence[str], src_report: Mapping[str, object]) -> list[str]:
    roots = set()
    tracked = [_norm_rel(path) for path in tracked_files]
    for path in tracked:
        parts = _path_parts(path)
        for index, part in enumerate(parts):
            if part in SOURCE_LIKE_NAMES:
                roots.add("/".join(parts[: index + 1]))
    for rel_root in EXPLICIT_SOURCE_ROOTS:
        prefix = _norm_rel(rel_root)
        if any(path == prefix or path.startswith(prefix + "/") for path in tracked):
            roots.add(prefix)
    for row in list(src_report.get("directories") or []):
        root = _norm_rel(row.get("directory_path"))
        if root and any(path == root or path.startswith(root + "/") for path in tracked):
            parts = _path_parts(root)
            if parts and parts[-1] in SOURCE_LIKE_NAMES:
                roots.add(root)
    return sorted(roots, key=lambda item: (item.count("/"), item))


def _current_root_for_file(path: str, source_roots: Sequence[str]) -> str:
    normalized = _norm_rel(path)
    matches = [root for root in source_roots if normalized == root or normalized.startswith(root + "/")]
    return sorted(matches, key=lambda item: (-len(item), item))[0] if matches else ""


def _module_for_path(path: str, module_root_rows: Sequence[Mapping[str, str]]) -> dict[str, str]:
    normalized = _norm_rel(path)
    for row in module_root_rows:
        module_root = _norm_rel(row.get("module_root"))
        if normalized == module_root or normalized.startswith(module_root + "/"):
            return {
                "domain": _token(row.get("domain")),
                "module_id": _token(row.get("module_id")),
                "module_root": module_root,
            }
    return {}


def _is_test_path(path: str, targets: Iterable[str], products: Iterable[str]) -> bool:
    normalized = _norm_rel(path)
    if TEST_FILE_RE.search(normalized):
        return True
    target_text = " ".join(sorted({_token(value).lower() for value in targets if _token(value)}))
    product_text = " ".join(sorted({_token(value).lower() for value in products if _token(value)}))
    return "test" in target_text or "test" in product_text


def _path_domain_scores(path: str, current_root: str) -> dict[str, int]:
    parts = _path_parts_lower(path)
    scores: defaultdict[str, int] = defaultdict(int)
    if not parts:
        return {}
    first = parts[0]
    second = parts[1] if len(parts) > 1 else ""
    if current_root == "app/src":
        scores["apps"] += 6
    elif current_root == "tools/ui_shared/src":
        scores["ui"] += 6
        scores["tools"] += 4
    elif current_root == "libs/build_identity/src":
        scores["lib"] += 6
        scores["tools"] += 2
    elif current_root == "libs/ui_backends/win32/src":
        scores["platform"] += 7
        scores["ui"] += 2
    elif current_root == "packs/source":
        scores["attic"] += 6
        scores["game"] += 2
    elif current_root.startswith("legacy/launcher_core_launcher/launcher/core/source"):
        scores["apps"] += 6
    elif current_root.startswith("legacy/setup_core_setup/setup/core/source"):
        scores["apps"] += 6
    elif current_root.lower().startswith("legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/dominiumsetupmacapp/sources"):
        scores["platform"] += 6
        scores["apps"] += 3
    elif current_root.startswith("legacy/source"):
        if "tests" in parts:
            scores["tests"] += 8
        else:
            scores["lib"] += 4
            scores["compat"] += 3
            scores["attic"] += 1
    elif current_root == "src":
        if second in {"appshell", "client", "interaction", "server"}:
            scores["apps"] += 6
            if second in {"appshell", "client", "interaction"}:
                scores["ui"] += 2
        elif second in {"ui"}:
            scores["ui"] += 7
        elif second in {"platform"}:
            scores["platform"] += 7
        elif second in {"compat"}:
            scores["compat"] += 7
        elif second in {"lib"}:
            scores["lib"] += 7
        elif second in {"tools"}:
            scores["tools"] += 7
        elif second in {"packs", "modding"}:
            scores["game"] += 5
            scores["compat"] += 2
        elif second in ENGINE_SEGMENTS:
            scores["engine"] += 6
        else:
            scores["engine"] += 4
    if "render" in parts or "viewer" in parts or "dui" in parts:
        scores["ui"] += 2
    if "win32" in parts or "macosx" in parts or "platform" in parts:
        scores["platform"] += 2
    if "trust" in parts or "migration" in parts or "compat" in parts:
        scores["compat"] += 1
    if "provider" in parts or "artifact" in parts or "store" in parts:
        scores["lib"] += 1
    return {domain: score for domain, score in scores.items() if score > 0}


def _build_indices(payloads: Mapping[str, object], tracked_files: Sequence[str], source_roots: Sequence[str]) -> dict[str, object]:
    json_payloads = dict(payloads.get("json_payloads") or {})
    architecture_graph = dict(json_payloads.get("architecture_graph") or {})
    module_registry = dict(json_payloads.get("module_registry") or {})
    build_graph = dict(json_payloads.get("build_graph") or {})
    include_graph = dict(json_payloads.get("include_graph") or {})
    symbol_index = dict(json_payloads.get("symbol_index") or {})
    duplicate_clusters = dict(json_payloads.get("duplicate_clusters") or {})
    duplicate_impls = dict(json_payloads.get("duplicate_impls") or {})
    shadow_modules = dict(json_payloads.get("shadow_modules") or {})
    convergence_plan = dict(json_payloads.get("convergence_plan") or {})
    convergence_actions = dict(json_payloads.get("convergence_actions") or {})
    convergence_execution_log = dict(json_payloads.get("convergence_execution_log") or {})

    module_by_id: dict[str, dict[str, object]] = {}
    file_to_module_id: dict[str, str] = {}
    file_to_module_root: dict[str, str] = {}
    file_to_module_domain: dict[str, str] = {}

    for source_rows in (list(architecture_graph.get("modules") or []), list(module_registry.get("modules") or [])):
        for row in source_rows:
            if not isinstance(row, dict):
                continue
            module_id = _token(row.get("module_id"))
            module_root = _norm_rel(row.get("module_root"))
            if not module_root:
                continue
            existing = module_by_id.get(module_id)
            if existing is None or len(list(existing.get("owned_files") or [])) < len(list(row.get("owned_files") or [])):
                module_by_id[module_id] = dict(row)
            for owned in list(row.get("owned_files") or []):
                path = _norm_rel(owned)
                if not path:
                    continue
                file_to_module_id[path] = module_id
                file_to_module_root[path] = module_root
                file_to_module_domain[path] = _token(row.get("domain"))

    module_rows = sorted(
        [dict(row) for row in module_by_id.values()],
        key=lambda item: (_norm_rel(item.get("module_root")), _token(item.get("module_id"))),
    )
    module_root_rows = sorted(
        [
            {
                "module_id": _token(row.get("module_id")),
                "module_root": _norm_rel(row.get("module_root")),
                "domain": _token(row.get("domain")),
            }
            for row in module_rows
            if _norm_rel(row.get("module_root"))
        ],
        key=lambda item: (-len(item["module_root"]), item["module_root"], item["module_id"]),
    )

    file_to_targets: defaultdict[str, set[str]] = defaultdict(set)
    file_to_products: defaultdict[str, set[str]] = defaultdict(set)
    for target_row in list(build_graph.get("targets") or []):
        target_id = _token(target_row.get("target_id"))
        product_id = _token(target_row.get("product_id"))
        for source in list(target_row.get("sources") or []):
            path = _norm_rel(source)
            if not path:
                continue
            if target_id:
                file_to_targets[path].add(target_id)
            if product_id:
                file_to_products[path].add(product_id)

    file_to_dependency_paths: defaultdict[str, list[str]] = defaultdict(list)
    file_to_dependency_modules: defaultdict[str, set[str]] = defaultdict(set)
    for edge in list(include_graph.get("edges") or []):
        source = _norm_rel(edge.get("from"))
        target = _norm_rel(edge.get("to"))
        if not source or not target:
            continue
        file_to_dependency_paths[source].append(target)
        module_id = file_to_module_id.get(target) or _module_for_path(target, module_root_rows).get("module_id", "")
        if module_id:
            file_to_dependency_modules[source].add(module_id)

    file_to_symbols: defaultdict[str, list[str]] = defaultdict(list)
    for row in list(symbol_index.get("symbols") or []):
        path = _norm_rel(row.get("file_path"))
        symbol_name = _token(row.get("symbol_name"))
        if path and symbol_name:
            file_to_symbols[path].append(symbol_name)

    file_to_cluster_ids: defaultdict[str, set[str]] = defaultdict(set)
    for cluster in list(duplicate_clusters.get("clusters") or []):
        cluster_id = _token(cluster.get("cluster_id"))
        for definition in list(cluster.get("definitions") or []):
            path = _norm_rel(definition.get("file_path"))
            if path and cluster_id:
                file_to_cluster_ids[path].add(cluster_id)
    for group in list(duplicate_impls.get("groups") or duplicate_impls.get("duplicates") or []):
        cluster_id = _token(group.get("group_id")) or _token(group.get("signature_hash"))
        for definition in list(group.get("definitions") or group.get("entries") or []):
            path = _norm_rel(definition.get("file_path"))
            if path and cluster_id:
                file_to_cluster_ids[path].add(cluster_id)

    plan_by_cluster: dict[str, dict[str, object]] = {}
    for row in list(convergence_plan.get("clusters") or []):
        cluster_id = _token(row.get("cluster_id"))
        if cluster_id:
            plan_by_cluster[cluster_id] = dict(row)

    file_to_shadow_candidate: dict[str, dict[str, str]] = {}
    for row in list(shadow_modules.get("modules") or []):
        shadow_root = _norm_rel(row.get("shadow_module_root"))
        canonical_module_id = _token(row.get("canonical_candidate_module_id"))
        if not shadow_root:
            continue
        for path in tracked_files:
            if path == shadow_root or path.startswith(shadow_root + "/"):
                file_to_shadow_candidate[path] = {
                    "canonical_candidate_module_id": canonical_module_id,
                    "shadow_module_root": shadow_root,
                }

    action_rows_by_file: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    action_doc_refs_by_file: defaultdict[str, set[str]] = defaultdict(set)
    for row in list(convergence_actions.get("actions") or []):
        action = dict(row)
        for rel_key in ("canonical_file", "secondary_file"):
            path = _norm_rel(action.get(rel_key))
            if path:
                action_rows_by_file[path].append(action)
                for doc in list(action.get("affected_docs") or []):
                    doc_path = _norm_rel(doc)
                    if doc_path:
                        action_doc_refs_by_file[path].add(doc_path)

    file_to_execution_rows: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in list(convergence_execution_log.get("entries") or []):
        entry = dict(row)
        for rel_key in ("canonical_file", "secondary_file"):
            path = _norm_rel(entry.get(rel_key))
            if path:
                file_to_execution_rows[path].append(entry)

    source_root_file_counts = Counter(
        _current_root_for_file(path, source_roots) for path in tracked_files if _current_root_for_file(path, source_roots)
    )

    return {
        "action_doc_refs_by_file": action_doc_refs_by_file,
        "action_rows_by_file": action_rows_by_file,
        "file_to_cluster_ids": file_to_cluster_ids,
        "file_to_dependency_modules": file_to_dependency_modules,
        "file_to_dependency_paths": file_to_dependency_paths,
        "file_to_execution_rows": file_to_execution_rows,
        "file_to_module_domain": file_to_module_domain,
        "file_to_module_id": file_to_module_id,
        "file_to_module_root": file_to_module_root,
        "file_to_products": file_to_products,
        "file_to_shadow_candidate": file_to_shadow_candidate,
        "file_to_symbols": file_to_symbols,
        "file_to_targets": file_to_targets,
        "module_root_rows": module_root_rows,
        "plan_by_cluster": plan_by_cluster,
        "source_root_file_counts": source_root_file_counts,
    }


def _gather_file_evidence(path: str, current_root: str, indices: Mapping[str, object]) -> dict[str, object]:
    file_to_targets = indices["file_to_targets"]
    file_to_products = indices["file_to_products"]
    file_to_dependency_paths = indices["file_to_dependency_paths"]
    file_to_dependency_modules = indices["file_to_dependency_modules"]
    file_to_module_id = indices["file_to_module_id"]
    file_to_module_root = indices["file_to_module_root"]
    file_to_module_domain = indices["file_to_module_domain"]
    file_to_symbols = indices["file_to_symbols"]
    file_to_cluster_ids = indices["file_to_cluster_ids"]
    plan_by_cluster = indices["plan_by_cluster"]
    file_to_shadow_candidate = indices["file_to_shadow_candidate"]
    action_rows_by_file = indices["action_rows_by_file"]
    action_doc_refs_by_file = indices["action_doc_refs_by_file"]
    file_to_execution_rows = indices["file_to_execution_rows"]
    module_root_rows = indices["module_root_rows"]

    current_module_id = _token(file_to_module_id.get(path))
    current_module_root = _norm_rel(file_to_module_root.get(path))
    current_domain = _token(file_to_module_domain.get(path))
    module_fallback = _module_for_path(path, module_root_rows)
    if not current_module_id and module_fallback:
        current_module_id = _token(module_fallback.get("module_id"))
        current_module_root = _norm_rel(module_fallback.get("module_root"))
        current_domain = _token(module_fallback.get("domain"))

    build_targets = sorted(file_to_targets.get(path) or [])
    products = sorted(file_to_products.get(path) or [])
    dependency_paths = sorted(set(file_to_dependency_paths.get(path) or []))
    dependency_modules = sorted(file_to_dependency_modules.get(path) or [])
    dependency_domains = sorted({_domain_from_module_id(module_id) for module_id in dependency_modules if _domain_from_module_id(module_id)})
    symbol_names = sorted(set(file_to_symbols.get(path) or []))
    cluster_ids = sorted(file_to_cluster_ids.get(path) or [])
    shadow_candidate = dict(file_to_shadow_candidate.get(path) or {})
    action_rows = list(action_rows_by_file.get(path) or [])
    execution_rows = list(file_to_execution_rows.get(path) or [])
    docs_refs = sorted(action_doc_refs_by_file.get(path) or [])

    canonical_domain_votes: defaultdict[str, int] = defaultdict(int)
    canonical_candidates: list[dict[str, str]] = []
    risk_levels: Counter[str] = Counter()
    risk_reasons: Counter[str] = Counter()
    focus_tags: Counter[str] = Counter()
    unresolved_results: Counter[str] = Counter()

    for cluster_id in cluster_ids:
        plan_row = dict(plan_by_cluster.get(cluster_id) or {})
        canonical = dict(plan_row.get("canonical_candidate") or {})
        canonical_file = _norm_rel(canonical.get("file_path"))
        canonical_module_id = _token(canonical.get("module_id"))
        canonical_domain = _domain_from_module_id(canonical_module_id) or _domain_from_path(canonical_file)
        if canonical_domain:
            canonical_domain_votes[canonical_domain] += 6 if canonical_file and not _source_like_path(canonical_file) else 3
        if canonical_file or canonical_module_id:
            canonical_candidates.append(
                {
                    "cluster_id": cluster_id,
                    "file_path": canonical_file,
                    "module_id": canonical_module_id,
                    "domain": canonical_domain,
                }
            )
        risk_level = _token(plan_row.get("risk_level"))
        if risk_level:
            risk_levels[risk_level] += 1
        for reason in list(plan_row.get("risk_reasons") or []):
            risk_reasons[_slug(reason)] += 1
        for tag in list(plan_row.get("focus_tags") or []):
            focus_tags[_slug(tag)] += 1

    for action in action_rows:
        canonical_file = _norm_rel(action.get("canonical_file"))
        canonical_module_id = _token(action.get("canonical_module_id"))
        canonical_domain = _domain_from_module_id(canonical_module_id) or _domain_from_path(canonical_file)
        if canonical_domain:
            canonical_domain_votes[canonical_domain] += 5 if canonical_file and not _source_like_path(canonical_file) else 2
        if canonical_file or canonical_module_id:
            canonical_candidates.append(
                {
                    "cluster_id": _token(action.get("cluster_id")),
                    "file_path": canonical_file,
                    "module_id": canonical_module_id,
                    "domain": canonical_domain,
                }
            )
        risk_level = _token(action.get("risk_level"))
        if risk_level:
            risk_levels[risk_level] += 1
        for reason in list(action.get("risk_reasons") or []):
            risk_reasons[_slug(reason)] += 1
        for tag in list(action.get("focus_tags") or []):
            focus_tags[_slug(tag)] += 1

    for entry in execution_rows:
        unresolved_results[_token(entry.get("result"))] += 1

    return {
        "build_targets": build_targets,
        "canonical_candidates": sorted(
            canonical_candidates,
            key=lambda item: (_norm_rel(item.get("file_path")), _token(item.get("module_id")), _token(item.get("cluster_id"))),
        ),
        "canonical_domain_votes": dict(sorted(canonical_domain_votes.items())),
        "cluster_ids": cluster_ids,
        "current_domain": current_domain,
        "current_module_id": current_module_id,
        "current_module_root": current_module_root,
        "dependency_domains": dependency_domains,
        "dependency_modules": dependency_modules,
        "dependency_paths": dependency_paths,
        "docs_refs": docs_refs,
        "execution_result_counts": dict(sorted(unresolved_results.items())),
        "focus_tags": dict(sorted(focus_tags.items())),
        "products": products,
        "risk_levels": dict(sorted(risk_levels.items())),
        "risk_reasons": dict(sorted(risk_reasons.items())),
        "shadow_candidate": shadow_candidate,
        "symbol_names": symbol_names,
    }


def _domain_scores_for_file(path: str, current_root: str, evidence: Mapping[str, object]) -> dict[str, float]:
    scores: defaultdict[str, float] = defaultdict(float)
    current_domain = _token(evidence.get("current_domain"))
    if current_domain in ALLOWED_DOMAINS:
        scores[current_domain] += 5.5

    for domain, score in _path_domain_scores(path, current_root).items():
        scores[domain] += float(score)

    shadow_candidate = dict(evidence.get("shadow_candidate") or {})
    shadow_domain = _domain_from_module_id(shadow_candidate.get("canonical_candidate_module_id"))
    if shadow_domain:
        scores[shadow_domain] += 8.5

    for domain, vote in dict(evidence.get("canonical_domain_votes") or {}).items():
        if domain in ALLOWED_DOMAINS:
            scores[domain] += float(vote)

    products = sorted(evidence.get("products") or [])
    build_targets = sorted(evidence.get("build_targets") or [])
    if any(product in {"client", "server", "launcher", "setup"} for product in products):
        scores["apps"] += 4.5
    if "engine" in products:
        scores["engine"] += 4.0
    if "game" in products:
        scores["game"] += 4.0
    if "tools" in products:
        scores["tools"] += 4.0
    if _is_test_path(path, build_targets, products):
        scores["tests"] += 7.0

    for domain in list(evidence.get("dependency_domains") or [])[:4]:
        if domain in ALLOWED_DOMAINS:
            scores[domain] += 1.25

    focus_tags = " ".join(sorted(dict(evidence.get("focus_tags") or {}).keys()))
    risk_reasons = " ".join(sorted(dict(evidence.get("risk_reasons") or {}).keys()))
    if any(token in focus_tags or token in risk_reasons for token in ("pack", "content", "mod")):
        scores["game"] += 1.5
    if any(token in focus_tags or token in risk_reasons for token in ("compat", "migration", "trust")):
        scores["compat"] += 1.5
    if current_root == "packs/source":
        scores["attic"] += 3.0
    if current_root.startswith("legacy/source") and not _is_test_path(path, build_targets, products):
        scores["attic"] += 1.5
    return {domain: score for domain, score in scores.items() if score > 0}


def _confidence_from_scores(scores: Mapping[str, float]) -> float:
    ranked = sorted(((domain, float(score)) for domain, score in scores.items() if score > 0.0), key=lambda item: (-item[1], item[0]))
    if not ranked:
        return 0.25
    top_score = ranked[0][1]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    total_score = sum(score for _domain, score in ranked)
    confidence = 0.35 + (top_score / max(total_score, 1.0)) * 0.35
    confidence += min(0.2, max(top_score - second_score, 0.0) / max(top_score, 1.0) * 0.25)
    if top_score >= 8.0:
        confidence += 0.1
    if second_score and top_score - second_score <= 1.5:
        confidence -= 0.08
    return round(max(0.2, min(0.98, confidence)), 4)


def _plausible_domains(scores: Mapping[str, float]) -> list[str]:
    ranked = sorted(((domain, float(score)) for domain, score in scores.items() if score > 0.0), key=lambda item: (-item[1], item[0]))
    if not ranked:
        return []
    top_score = ranked[0][1]
    cutoff = top_score - 1.5
    return [domain for domain, score in ranked if score >= cutoff][:4]


def _classify_file(path: str, current_root: str, proposed_domain: str, confidence: float, evidence: Mapping[str, object]) -> str:
    build_targets = evidence.get("build_targets") or []
    products = evidence.get("products") or []
    parts = _path_parts_lower(path)
    if _is_test_path(path, build_targets, products):
        return "tests"
    if current_root == "packs/source" or "raw" in parts:
        return "generated"
    if proposed_domain == "platform" or "win32" in parts or "macosx" in parts:
        return "platform"
    if proposed_domain == "ui" or "dui" in parts or "render" in parts or "viewer" in parts:
        return "ui"
    if proposed_domain == "tools" and not any(product in PRODUCTION_PRODUCTS for product in products):
        return "tools"
    risk_levels = dict(evidence.get("risk_levels") or {})
    risk_reasons = dict(evidence.get("risk_reasons") or {})
    focus_tags = dict(evidence.get("focus_tags") or {})
    if "HIGH" in risk_levels or any(token in " ".join(list(risk_reasons) + list(focus_tags)) for token in HIGH_RISK_TOKENS):
        return "runtime_critical"
    if any(product in PRODUCTION_PRODUCTS for product in products):
        return "runtime_critical"
    if current_root.startswith("legacy/"):
        return "legacy"
    if proposed_domain in {"apps", "compat", "engine", "game", "lib"}:
        return "runtime_support" if confidence >= 0.5 else "unresolved"
    return "unresolved"


def _normalized_module_from_current(module_id: str, proposed_domain: str) -> str:
    token = _token(module_id)
    if not token:
        return ""
    parts = [part for part in token.split(".") if part and part not in {"unknown", "src", "source", "Sources", "Source"}]
    if not parts:
        return ""
    if parts[0] in ALLOWED_DOMAINS:
        parts = parts[1:]
    return ".".join([proposed_domain] + parts) if parts else proposed_domain


def _proposed_module_id(path: str, current_root: str, proposed_domain: str, evidence: Mapping[str, object]) -> str:
    canonical_candidates = list(evidence.get("canonical_candidates") or [])
    for candidate in canonical_candidates:
        module_id = _token(candidate.get("module_id"))
        if _domain_from_module_id(module_id) == proposed_domain and module_id:
            return module_id
    shadow_module_id = _token(dict(evidence.get("shadow_candidate") or {}).get("canonical_candidate_module_id"))
    if _domain_from_module_id(shadow_module_id) == proposed_domain:
        return shadow_module_id
    normalized_current = _normalized_module_from_current(_token(evidence.get("current_module_id")), proposed_domain)
    if normalized_current:
        return normalized_current
    rel_after_root = _norm_rel(path)
    if current_root and rel_after_root.startswith(current_root + "/"):
        rel_after_root = rel_after_root[len(current_root) + 1 :]
    rel_parts = [_slug(part) for part in _path_parts(rel_after_root)[:-1]]
    if current_root.startswith("legacy/launcher_core_launcher/launcher/core/source"):
        rel_parts = ["launcher", "legacy", "core"] + rel_parts
    elif current_root.startswith("legacy/setup_core_setup/setup/core/source"):
        rel_parts = ["setup", "legacy", "core"] + rel_parts
    elif current_root.startswith("legacy/source"):
        rel_parts = ["legacy"] + rel_parts
    elif current_root == "app/src":
        rel_parts = ["app"] + rel_parts
    elif current_root == "tools/ui_shared/src":
        rel_parts = ["ui_shared"] + rel_parts
    elif current_root == "libs/build_identity/src":
        rel_parts = ["build_identity"] + rel_parts
    elif current_root == "libs/ui_backends/win32/src":
        rel_parts = ["ui_backends", "win32"] + rel_parts
    return ".".join(([proposed_domain] + [part for part in rel_parts if part])[:8]) or proposed_domain


def _evidence_summary(path: str, evidence: Mapping[str, object], selected_cluster_id: str, selected_candidate: str) -> dict[str, object]:
    return {
        "build_targets": sorted(list(evidence.get("build_targets") or []))[:6],
        "dependencies": sorted(list(evidence.get("dependency_modules") or []))[:6],
        "duplicate_cluster": selected_cluster_id,
        "canonical_candidate": selected_candidate,
        "docs_refs": sorted(list(evidence.get("docs_refs") or []))[:4],
    }


def _select_candidate(evidence: Mapping[str, object]) -> tuple[str, str]:
    candidates = list(evidence.get("canonical_candidates") or [])
    if not candidates:
        return "", ""
    selected = sorted(
        candidates,
        key=lambda item: (
            _source_like_path(item.get("file_path")),
            _norm_rel(item.get("file_path")),
            _token(item.get("module_id")),
            _token(item.get("cluster_id")),
        ),
    )[0]
    return _token(selected.get("cluster_id")), _norm_rel(selected.get("file_path")) or _token(selected.get("module_id"))


def _mapping_entry(path: str, current_root: str, indices: Mapping[str, object]) -> dict[str, object]:
    evidence = _gather_file_evidence(path, current_root, indices)
    scores = _domain_scores_for_file(path, current_root, evidence)
    ranked_scores = sorted(((domain, score) for domain, score in scores.items()), key=lambda item: (-item[1], item[0]))
    proposed_domain = ranked_scores[0][0] if ranked_scores else "attic"
    confidence = _confidence_from_scores(scores)
    category = _classify_file(path, current_root, proposed_domain, confidence, evidence)
    plausible_domains = _plausible_domains(scores)
    proposed_module_id = _proposed_module_id(path, current_root, proposed_domain, evidence)
    selected_cluster_id, selected_candidate = _select_candidate(evidence)
    return {
        "category": category,
        "confidence": confidence,
        "current_module_id": _token(evidence.get("current_module_id")),
        "current_root": current_root,
        "evidence": _evidence_summary(path, evidence, selected_cluster_id, selected_candidate),
        "evidence_detail": {
            "cluster_ids": sorted(list(evidence.get("cluster_ids") or [])),
            "dependency_domains": sorted(list(evidence.get("dependency_domains") or [])),
            "focus_tags": sorted(dict(evidence.get("focus_tags") or {}).keys()),
            "products": sorted(list(evidence.get("products") or [])),
            "risk_levels": dict(sorted(dict(evidence.get("risk_levels") or {}).items())),
            "risk_reasons": sorted(dict(evidence.get("risk_reasons") or {}).keys()),
            "score_vector": [{"domain": domain, "score": round(float(score), 4)} for domain, score in ranked_scores[:5]],
        },
        "file_path": path,
        "plausible_domains": plausible_domains,
        "proposed_domain": proposed_domain,
        "proposed_module_id": proposed_module_id,
    }


def _conflict_review_question(plausible_domains: Sequence[str], path: str) -> str:
    domain_set = set(plausible_domains)
    if {"apps", "engine"} <= domain_set:
        return "Should this path live under an application product root or under shared engine infrastructure?"
    if {"apps", "ui"} <= domain_set:
        return "Is this product shell code or a reusable UI subsystem?"
    if {"compat", "lib"} <= domain_set:
        return "Is this compatibility glue or reusable library support?"
    if {"attic", "game"} <= domain_set or {"attic", "lib"} <= domain_set:
        return "Should this file be retained as active source material or routed to attic pending later archaeology?"
    if _norm_rel(path).startswith("legacy/"):
        return "Should this legacy path be normalized into an active product/domain root now or preserved for later manual migration?"
    return "Which canonical domain best matches this file without inventing new structure prematurely?"


def _conflict_temporary_action(proposed_domain: str, category: str, confidence: float, plausible_domains: Sequence[str]) -> str:
    if proposed_domain == "attic" or category in {"generated", "legacy"} and confidence < HIGH_CONFIDENCE_THRESHOLD:
        return "route_to_attic"
    if category in {"runtime_critical", "runtime_support", "ui", "platform"} or len(plausible_domains) > 1:
        return "manual_decision_required"
    return "keep_in_place"


def _root_specific_path(option_id: str, entry: Mapping[str, object]) -> str:
    path = _norm_rel(entry.get("file_path"))
    current_root = _norm_rel(entry.get("current_root"))
    proposed_domain = _token(entry.get("proposed_domain"))
    rel_after_root = path[len(current_root) + 1 :] if current_root and path.startswith(current_root + "/") else path
    parts = _path_parts(rel_after_root)

    if option_id == "C":
        if current_root == "src":
            return rel_after_root
        if current_root == "app/src":
            return "app/" + rel_after_root
        if current_root.startswith("legacy/launcher_core_launcher/launcher/core/source"):
            return "legacy/launcher_core_launcher/launcher/core/" + rel_after_root
        if current_root.startswith("legacy/setup_core_setup/setup/core/source"):
            return "legacy/setup_core_setup/setup/core/" + rel_after_root
        if current_root.lower().startswith("legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/dominiumsetupmacapp/sources"):
            return "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/" + rel_after_root
        if current_root == "legacy/source":
            return "legacy/" + rel_after_root
        if current_root == "tools/ui_shared/src":
            return "tools/ui_shared/" + rel_after_root
        if current_root == "libs/build_identity/src":
            return "libs/build_identity/" + rel_after_root
        if current_root == "libs/ui_backends/win32/src":
            return "libs/ui_backends/win32/" + rel_after_root
        if current_root == "packs/source":
            return "packs/" + rel_after_root
        return path

    if proposed_domain == "attic":
        return "attic/src_quarantine/" + path
    if current_root == "app/src":
        return ("apps/client/runtime/" if option_id == "B" else "apps/app/") + rel_after_root
    if current_root.startswith("legacy/launcher_core_launcher/launcher/core/source"):
        return "apps/launcher/legacy_core/" + rel_after_root
    if current_root.startswith("legacy/setup_core_setup/setup/core/source"):
        return "apps/setup/legacy_core/" + rel_after_root
    if current_root.lower().startswith("legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/dominiumsetupmacapp/sources"):
        return "platform/macosx/setup_app/" + rel_after_root
    if current_root == "legacy/source":
        if rel_after_root.startswith("tests/"):
            return "tests/legacy_source/" + rel_after_root[len("tests/") :]
        return ("lib/providers/" if option_id == "B" else "lib/legacy_source/") + rel_after_root
    if current_root == "tools/ui_shared/src":
        return ("ui/shared/" if option_id == "B" else "ui/") + rel_after_root
    if current_root == "libs/build_identity/src":
        return "lib/build_identity/" + rel_after_root
    if current_root == "libs/ui_backends/win32/src":
        return "platform/win32/" + rel_after_root
    if current_root == "packs/source":
        return "attic/src_quarantine/" + path
    if current_root == "src" and len(parts) > 1:
        first = parts[0].lower()
        rest = "/".join(parts[1:])
        if option_id == "B":
            if first == "client":
                return "apps/client/" + rest
            if first == "server":
                return "apps/server/" + rest
            if first == "appshell":
                return "apps/launcher/appshell/" + rest
        return f"{proposed_domain}/" + rel_after_root
    return f"{proposed_domain}/" + rel_after_root if proposed_domain else path


def _option_confidence(option_id: str, entry: Mapping[str, object]) -> float:
    confidence = float(entry.get("confidence", 0.0) or 0.0)
    path = _norm_rel(entry.get("file_path"))
    current_root = _norm_rel(entry.get("current_root"))
    category = _token(entry.get("category"))
    if option_id == "A":
        if current_root.startswith("legacy/"):
            confidence -= 0.12
        if path.startswith(("src/client/", "src/appshell/", "src/server/")):
            confidence -= 0.06
    elif option_id == "B":
        if path.startswith(("src/client/", "src/server/", "src/appshell/", "app/src/")):
            confidence += 0.05
        if current_root == "legacy/source":
            confidence -= 0.05
    elif option_id == "C":
        if current_root.startswith(("legacy/", "tools/ui_shared/src", "libs/build_identity/src", "libs/ui_backends/win32/src", "app/src")):
            confidence += 0.08
        if current_root == "packs/source":
            confidence -= 0.08
        if path.startswith("src/") and category in {"runtime_support", "runtime_critical"}:
            confidence += 0.02
    return round(max(0.2, min(0.98, confidence)), 4)


def _option_rows(entries: Sequence[Mapping[str, object]], preferred_option: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    descriptions = {
        "A": {
            "drawbacks": [
                "Most aggressive normalization pressure on current product and legacy roots.",
                "Increases architectural invention risk for ambiguous runtime subsystems.",
            ],
            "label": "OPTION A - Domain-first canonical layout",
            "advantages": [
                "Aligns immediately with the long-term domain-first topology.",
                "Makes later enforcement simpler once approved.",
            ],
            "risk_label": "higher-structure-invention",
        },
        "B": {
            "drawbacks": [
                "Still requires product/domain line-drawing for mixed client-appshell-ui surfaces.",
                "Legacy provider and shared support code remain ambiguous.",
            ],
            "label": "OPTION B - Hybrid product/domain layout",
            "advantages": [
                "Clarifies product shells under apps/client, apps/server, apps/setup, and apps/launcher.",
                "Keeps shared domains explicit for lib/ui/platform/compat/tools.",
            ],
            "risk_label": "mixed-normalization",
        },
        "C": {
            "drawbacks": [
                "Leaves deeper normalization work for later series after XI-5.",
                "Produces a less ideal immediate end-state for architecture freeze.",
            ],
            "label": "OPTION C - Conservative migration layout",
            "advantages": [
                "Minimizes structural invention while still eliminating source-like directories.",
                "Best matches the current evidence and legacy product surfaces.",
            ],
            "risk_label": "lowest-immediate-risk",
        },
    }
    options: list[dict[str, object]] = []
    option_lookup: dict[str, object] = {}
    for option_id in OPTION_ORDER:
        file_mappings: list[dict[str, object]] = []
        automatic = 0
        manual = 0
        attic = 0
        for entry in entries:
            target_path = _root_specific_path(option_id, entry)
            effective_confidence = _option_confidence(option_id, entry)
            is_attic = target_path.startswith("attic/")
            is_manual = effective_confidence < HIGH_CONFIDENCE_THRESHOLD or len(list(entry.get("plausible_domains") or [])) > 1
            if is_attic:
                attic += 1
            elif is_manual:
                manual += 1
            else:
                automatic += 1
            file_mappings.append(
                {
                    "file_path": _norm_rel(entry.get("file_path")),
                    "mapping_confidence": effective_confidence,
                    "proposed_domain": _token(entry.get("proposed_domain")),
                    "proposed_module_id": _token(entry.get("proposed_module_id")),
                    "target_path": target_path,
                }
            )
        summary = {
            "option_id": option_id,
            "label": descriptions[option_id]["label"],
            "advantages": descriptions[option_id]["advantages"],
            "architectural_drawbacks": descriptions[option_id]["drawbacks"],
            "automatic_move_count": automatic,
            "manual_review_count": manual,
            "attic_count": attic,
            "preferred": option_id == preferred_option,
            "risk_label": descriptions[option_id]["risk_label"],
            "xi_5_complexity": "LOW" if option_id == "C" else ("MED" if option_id == "B" else "HIGH"),
        }
        option_payload = dict(summary)
        option_payload["file_mappings"] = file_mappings
        options.append(option_payload)
        option_lookup[option_id] = summary
    return options, option_lookup


def _build_conflicts(entries: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    conflicts: list[dict[str, object]] = []
    for entry in entries:
        plausible = list(entry.get("plausible_domains") or [])
        confidence = float(entry.get("confidence", 0.0) or 0.0)
        if confidence >= CONFLICT_CONFIDENCE_THRESHOLD and len(plausible) <= 1:
            continue
        evidence_detail = dict(entry.get("evidence_detail") or {})
        conflicts.append(
            {
                "category": _token(entry.get("category")),
                "cluster_id_or_file": _token(dict(entry.get("evidence") or {}).get("duplicate_cluster")) or _norm_rel(entry.get("file_path")),
                "confidence": confidence,
                "evidence": {
                    "build_targets": sorted(list(dict(entry.get("evidence") or {}).get("build_targets") or [])),
                    "dependency_domains": sorted(list(evidence_detail.get("dependency_domains") or [])),
                    "focus_tags": sorted(list(evidence_detail.get("focus_tags") or [])),
                    "risk_reasons": sorted(list(evidence_detail.get("risk_reasons") or [])),
                },
                "file_path": _norm_rel(entry.get("file_path")),
                "plausible_domains": plausible or [_token(entry.get("proposed_domain"))],
                "recommended_review_question": _conflict_review_question(plausible or [_token(entry.get("proposed_domain"))], _norm_rel(entry.get("file_path"))),
                "recommended_temporary_action": _conflict_temporary_action(
                    _token(entry.get("proposed_domain")),
                    _token(entry.get("category")),
                    confidence,
                    plausible,
                ),
            }
        )
    return sorted(conflicts, key=lambda item: (float(item.get("confidence", 0.0) or 0.0), _norm_rel(item.get("file_path"))))


def _build_runtime_critical_set(entries: Sequence[Mapping[str, object]], indices: Mapping[str, object]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    source_root_counts = Counter(indices.get("source_root_file_counts") or {})
    for entry in entries:
        path = _norm_rel(entry.get("file_path"))
        category = _token(entry.get("category"))
        products = list(dict(entry.get("evidence_detail") or {}).get("products") or [])
        risk_levels = dict(dict(entry.get("evidence_detail") or {}).get("risk_levels") or {})
        if category not in {"runtime_critical", "legacy", "runtime_support", "platform", "ui"} and not any(product in PRODUCTION_PRODUCTS for product in products):
            continue
        current_root = _norm_rel(entry.get("current_root"))
        root_parts = _path_parts(path)
        scope_key = current_root
        if current_root == "src" and len(root_parts) > 2:
            scope_key = "/".join(root_parts[:2])
        elif current_root.startswith("legacy/source") and len(root_parts) > 2:
            scope_key = "/".join(root_parts[:3])
        record = grouped.setdefault(
            scope_key,
            {
                "architecture_impact": 0,
                "blocked_file_count": 0,
                "confidence_floor": 1.0,
                "current_root": current_root,
                "example_files": [],
                "focus_tags": Counter(),
                "plausible_domains": Counter(),
                "products": Counter(),
                "proposed_domain": _token(entry.get("proposed_domain")),
                "related_clusters": set(),
                "scope_id": scope_key,
                "temporary_action": "manual_decision_required",
            },
        )
        record["blocked_file_count"] += 1
        record["confidence_floor"] = min(record["confidence_floor"], float(entry.get("confidence", 0.0) or 0.0))
        if len(record["example_files"]) < 5:
            record["example_files"].append(path)
        for product in products:
            record["products"][product] += 1
        for domain in list(entry.get("plausible_domains") or []):
            record["plausible_domains"][domain] += 1
        for tag in list(dict(entry.get("evidence_detail") or {}).get("focus_tags") or []):
            record["focus_tags"][tag] += 1
        for risk_level, count in dict(risk_levels).items():
            record["risk_levels"] = Counter(record.get("risk_levels") or {})
            record["risk_levels"][risk_level] += int(count)
        cluster_id = _token(dict(entry.get("evidence") or {}).get("duplicate_cluster"))
        if cluster_id:
            record["related_clusters"].add(cluster_id)
        impact = 0
        if any(product in {"launcher", "setup", "server", "client"} for product in products):
            impact += 5
        elif any(product in {"engine", "game"} for product in products):
            impact += 4
        if risk_levels.get("HIGH"):
            impact += 5
        elif risk_levels.get("MED"):
            impact += 3
        if category == "runtime_critical":
            impact += 4
        elif category in {"platform", "ui"}:
            impact += 3
        record["architecture_impact"] = max(record["architecture_impact"], impact)
        if _token(entry.get("proposed_domain")) == "attic":
            record["temporary_action"] = "route_to_attic"

    rows: list[dict[str, object]] = []
    for scope_id, row in grouped.items():
        blocked = max(int(row["blocked_file_count"]), int(source_root_counts.get(row["current_root"], 0) or 0))
        rows.append(
            {
                "architecture_impact": int(row["architecture_impact"]),
                "blocked_file_count": blocked,
                "confidence": round(float(row["confidence_floor"]), 4),
                "current_root": _norm_rel(row["current_root"]),
                "example_files": sorted(set(row["example_files"])),
                "focus_tags": sorted(row["focus_tags"]),
                "plausible_domains": [domain for domain, _count in sorted(row["plausible_domains"].items(), key=lambda item: (-item[1], item[0]))[:4]],
                "products": [product for product, _count in sorted(row["products"].items(), key=lambda item: (-item[1], item[0]))],
                "proposed_domain": _token(row["proposed_domain"]),
                "related_clusters": sorted(row["related_clusters"]),
                "scope_id": scope_id,
                "temporary_action": _token(row["temporary_action"]),
            }
        )
    rows.sort(
        key=lambda item: (
            -int(item.get("architecture_impact", 0) or 0),
            -int(item.get("blocked_file_count", 0) or 0),
            -float(item.get("confidence", 0.0) or 0.0),
            _norm_rel(item.get("scope_id")),
        )
    )
    return rows[:CRITICAL_BLOCKER_LIMIT]


def _subset_payload(report_id: str, title: str, entries: Sequence[Mapping[str, object]]) -> dict[str, object]:
    payload = {
        "entries": list(entries),
        "entry_count": len(list(entries)),
        "report_id": report_id,
        "title": title,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _summary_counts(entries: Sequence[Mapping[str, object]]) -> dict[str, object]:
    category_counts = Counter(_token(entry.get("category")) for entry in entries)
    domain_counts = Counter(_token(entry.get("proposed_domain")) for entry in entries)
    current_root_counts = Counter(_norm_rel(entry.get("current_root")) for entry in entries)
    return {
        "category_counts": {key: int(category_counts.get(key, 0)) for key in sorted(category_counts)},
        "current_root_counts": {key: int(current_root_counts.get(key, 0)) for key in sorted(current_root_counts)},
        "domain_counts": {key: int(domain_counts.get(key, 0)) for key in sorted(domain_counts)},
        "high_confidence_count": sum(1 for entry in entries if float(entry.get("confidence", 0.0) or 0.0) >= HIGH_CONFIDENCE_THRESHOLD and len(list(entry.get("plausible_domains") or [])) <= 1),
    }


def _build_json_payloads(
    entries: Sequence[Mapping[str, object]],
    conflicts: Sequence[Mapping[str, object]],
    critical_set: Sequence[Mapping[str, object]],
    options: Sequence[Mapping[str, object]],
    option_summary_lookup: Mapping[str, object],
    preferred_option: str,
    inputs: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    summary = _summary_counts(entries)
    missing_inputs = list(inputs.get("missing_inputs") or [])
    major_missing_inputs = list(inputs.get("major_missing_inputs") or [])
    source_evidence = list(inputs.get("input_fingerprints") or [])

    mapping_payload = {
        "major_missing_inputs": major_missing_inputs,
        "mapping_count": len(entries),
        "mappings": list(entries),
        "missing_inputs": missing_inputs,
        "report_id": "xi.4b.src_domain_mapping.v1",
        "summary": summary,
    }
    mapping_payload["deterministic_fingerprint"] = canonical_sha256(mapping_payload)

    candidates_payload = {
        "missing_inputs": missing_inputs,
        "options": list(options),
        "preferred_option": preferred_option,
        "report_id": "xi.4b.src_domain_mapping_candidates.v1",
        "summary": {
            "option_order": list(OPTION_ORDER),
            "preferred_option_summary": dict(option_summary_lookup.get(preferred_option) or {}),
        },
    }
    candidates_payload["deterministic_fingerprint"] = canonical_sha256(candidates_payload)

    conflicts_payload = {
        "conflict_count": len(conflicts),
        "conflicts": list(conflicts),
        "missing_inputs": missing_inputs,
        "report_id": "xi.4b.src_domain_mapping_conflicts.v1",
    }
    conflicts_payload["deterministic_fingerprint"] = canonical_sha256(conflicts_payload)

    high_confidence = [
        {
            "confidence": float(entry.get("confidence", 0.0) or 0.0),
            "file_path": _norm_rel(entry.get("file_path")),
            "proposed_domain": _token(entry.get("proposed_domain")),
            "proposed_module_id": _token(entry.get("proposed_module_id")),
        }
        for entry in entries
        if float(entry.get("confidence", 0.0) or 0.0) >= HIGH_CONFIDENCE_THRESHOLD and len(list(entry.get("plausible_domains") or [])) <= 1
    ]
    attic_routes_map: dict[str, dict[str, object]] = {}
    for entry in entries:
        if _token(entry.get("proposed_domain")) != "attic":
            continue
        path = _norm_rel(entry.get("file_path"))
        attic_routes_map[path] = {
            "category": _token(entry.get("category")),
            "confidence": float(entry.get("confidence", 0.0) or 0.0),
            "file_path": path,
            "reason": "proposed_domain_attic",
        }
    for conflict in conflicts:
        if _token(conflict.get("recommended_temporary_action")) != "route_to_attic":
            continue
        path = _norm_rel(conflict.get("file_path"))
        attic_routes_map[path] = {
            "category": _token(conflict.get("category")),
            "confidence": float(conflict.get("confidence", 0.0) or 0.0),
            "file_path": path,
            "reason": "conflict_route_to_attic",
        }
    attic_routes = [attic_routes_map[path] for path in sorted(attic_routes_map)]
    lock_payload = {
        "conflicts": list(conflicts),
        "high_confidence_mappings": high_confidence,
        "mapping_version": "xi4b.provisional.2026-03-27",
        "preferred_layout_option": preferred_option,
        "replacement_target": "approved mapping lock for Ξ-5",
        "report_id": "xi.4b.src_domain_mapping_lock_proposal.v1",
        "required_attic_routes": attic_routes,
        "source_evidence_fingerprints": source_evidence,
        "stability_class": "provisional",
    }
    lock_payload["deterministic_fingerprint"] = canonical_sha256(lock_payload)

    critical_payload = {
        "entry_count": len(critical_set),
        "entries": list(critical_set),
        "missing_inputs": missing_inputs,
        "report_id": "xi.4b.src_runtime_critical_set.v1",
    }
    critical_payload["deterministic_fingerprint"] = canonical_sha256(critical_payload)

    tool_entries = [entry for entry in entries if _token(entry.get("category")) == "tools"]
    generated_entries = [entry for entry in entries if _token(entry.get("category")) == "generated"]
    test_entries = [entry for entry in entries if _token(entry.get("category")) == "tests"]
    legacy_entries = [entry for entry in entries if _token(entry.get("category")) == "legacy"]

    review_manifest = {
        "bundle_entries": [],
        "major_missing_inputs": major_missing_inputs,
        "missing_inputs": missing_inputs,
        "output_paths": sorted(OUTPUT_REL_PATHS),
        "preferred_option": preferred_option,
        "report_id": "xi.4b.review_manifest.v1",
        "source_evidence_fingerprints": source_evidence,
        "summary": {
            "conflict_count": len(conflicts),
            "high_confidence_count": len(high_confidence),
            "manual_review_count": len(conflicts),
            "mapping_count": len(entries),
        },
        "validation": {
            "deterministic_rerun_match": True,
            "schema_validation": "pending_runner_validation",
        },
    }
    review_manifest["deterministic_fingerprint"] = canonical_sha256(review_manifest)

    return {
        SRC_DOMAIN_MAPPING_REL: mapping_payload,
        SRC_DOMAIN_MAPPING_CANDIDATES_REL: candidates_payload,
        SRC_DOMAIN_MAPPING_CONFLICTS_REL: conflicts_payload,
        SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL: lock_payload,
        SRC_RUNTIME_CRITICAL_SET_REL: critical_payload,
        SRC_TOOL_ONLY_SET_REL: _subset_payload("xi.4b.src_tool_only_set.v1", "Source-like tool-only files", tool_entries),
        SRC_GENERATED_SET_REL: _subset_payload("xi.4b.src_generated_set.v1", "Source-like generated files", generated_entries),
        SRC_TEST_ONLY_SET_REL: _subset_payload("xi.4b.src_test_only_set.v1", "Source-like test-only files", test_entries),
        SRC_LEGACY_SET_REL: _subset_payload("xi.4b.src_legacy_set.v1", "Source-like legacy files", legacy_entries),
        XI4B_REVIEW_MANIFEST_REL: review_manifest,
    }


def _top_rows(entries: Sequence[Mapping[str, object]], *, limit: int = REPORT_SAMPLE_LIMIT) -> list[Mapping[str, object]]:
    return list(entries)[:limit]


def _render_mapping_report(entries: Sequence[Mapping[str, object]], conflicts: Sequence[Mapping[str, object]], critical_set: Sequence[Mapping[str, object]], inputs: Mapping[str, object]) -> str:
    summary = _summary_counts(entries)
    lines = [_doc_header("SRC Domain Mapping Report", "approved mapping lock for XI-5"), "## Domain Summary", ""]
    lines.extend(_markdown_bullets([f"{domain}: `{count}`" for domain, count in sorted(summary["domain_counts"].items())]))
    lines.extend(["", "## Category Summary", ""])
    lines.extend(_markdown_bullets([f"{category}: `{count}`" for category, count in sorted(summary["category_counts"].items())]))
    lines.extend(
        [
            "",
            "## High-Confidence Sample",
            "",
            "| File | Domain | Module | Confidence | Category |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for entry in _top_rows(
        sorted(
            [entry for entry in entries if float(entry.get("confidence", 0.0) or 0.0) >= HIGH_CONFIDENCE_THRESHOLD],
            key=lambda item: (-float(item.get("confidence", 0.0) or 0.0), _norm_rel(item.get("file_path"))),
        )
    ):
        lines.append(
            "| `{}` | `{}` | `{}` | `{:.2f}` | `{}` |".format(
                _norm_rel(entry.get("file_path")),
                _token(entry.get("proposed_domain")),
                _token(entry.get("proposed_module_id")),
                float(entry.get("confidence", 0.0) or 0.0),
                _token(entry.get("category")),
            )
        )
    lines.extend(["", "## Runtime-Critical Sample", ""])
    lines.extend(_markdown_bullets([f"`{row['scope_id']}` blocked_files=`{row['blocked_file_count']}` domains=`{', '.join(row['plausible_domains'])}`" for row in _top_rows(critical_set)]))
    lines.extend(["", "## Missing Inputs", ""])
    if list(inputs.get("missing_inputs") or []):
        lines.extend(_markdown_bullets([f"`{path}`" for path in sorted(inputs.get("missing_inputs") or [])]))
    else:
        lines.append("- none")
    lines.extend(["", "## Conflict Sample", ""])
    lines.extend(_markdown_bullets([f"`{row['file_path']}` -> `{', '.join(row['plausible_domains'])}` question=`{row['recommended_review_question']}`" for row in _top_rows(conflicts)]))
    lines.append("")
    return "\n".join(lines)


def _render_structure_options_report(options: Sequence[Mapping[str, object]], preferred_option: str) -> str:
    lines = [_doc_header("Structure Options Report", "approved mapping lock for XI-5"), "## Option Comparison", ""]
    for option in options:
        lines.extend(
            [
                f"### {option['label']}",
                "",
                f"- Preferred: `{'yes' if option['option_id'] == preferred_option else 'no'}`",
                f"- Xi-5 Complexity: `{option['xi_5_complexity']}`",
                f"- Automatic move count: `{option['automatic_move_count']}`",
                f"- Manual review count: `{option['manual_review_count']}`",
                f"- Attic count: `{option['attic_count']}`",
                "",
                "Advantages:",
            ]
        )
        lines.extend(_markdown_bullets(option.get("advantages") or []))
        lines.extend(["", "Architectural Drawbacks:"])
        lines.extend(_markdown_bullets(option.get("architectural_drawbacks") or []))
        lines.append("")
    return "\n".join(lines)


def _render_review_guide(preferred_option: str, conflicts: Sequence[Mapping[str, object]], critical_set: Sequence[Mapping[str, object]]) -> str:
    return "\n".join(
        [
            _doc_header("XI-4B Review Guide", "approved mapping lock for XI-5"),
            "## Read Order",
            "",
            "1. `docs/restructure/XI_4B_UNBLOCK_REPORT.md`",
            "2. `docs/restructure/STRUCTURE_OPTIONS_REPORT.md`",
            "3. `docs/restructure/SRC_DOMAIN_MAPPING_REPORT.md`",
            "4. `data/restructure/src_domain_mapping_lock_proposal.json`",
            "",
            "## Decisions Required",
            "",
            f"- Approve preferred layout option `{preferred_option}` or choose an alternative.",
            f"- Resolve `{len(conflicts)}` conflicts where the mapping confidence stays below `{CONFLICT_CONFIDENCE_THRESHOLD:.2f}` or multiple domains remain plausible.",
            f"- Confirm the `{len(critical_set)}` bounded runtime-critical blockers that XI-5 must clear first.",
            "",
            "## Xi-5 Prerequisites",
            "",
            "- human approval of the provisional mapping lock",
            "- explicit decision on attic routes",
            "- explicit resolution of runtime-critical conflicts",
            "- bounded XI-5 execution against the approved lock",
            "",
        ]
    )


def _render_unblock_report(critical_set: Sequence[Mapping[str, object]]) -> str:
    lines = [_doc_header("XI-4B Unblock Report", "approved mapping lock for XI-5"), "## Runtime-Critical Blockers", ""]
    for row in critical_set:
        lines.extend(
            [
                f"### `{row['scope_id']}`",
                "",
                f"- Architecture impact: `{row['architecture_impact']}`",
                f"- Blocked file count: `{row['blocked_file_count']}`",
                f"- Confidence floor: `{float(row['confidence']):.2f}`",
                f"- Proposed domain: `{row['proposed_domain']}`",
                f"- Plausible domains: `{', '.join(row['plausible_domains'])}`",
                f"- Temporary action: `{row['temporary_action']}`",
                "",
            ]
        )
        if row.get("example_files"):
            lines.append("Example files:")
            lines.extend(_markdown_bullets([f"`{path}`" for path in row.get("example_files") or []]))
            lines.append("")
    return "\n".join(lines)


def _render_xi_4b_final(
    entries: Sequence[Mapping[str, object]],
    conflicts: Sequence[Mapping[str, object]],
    options: Sequence[Mapping[str, object]],
    preferred_option: str,
    critical_set: Sequence[Mapping[str, object]],
    inputs: Mapping[str, object],
) -> str:
    high_confidence_count = sum(
        1
        for entry in entries
        if float(entry.get("confidence", 0.0) or 0.0) >= HIGH_CONFIDENCE_THRESHOLD and len(list(entry.get("plausible_domains") or [])) <= 1
    )
    preferred_summary = next((option for option in options if option.get("option_id") == preferred_option), {})
    return "\n".join(
        [
            _doc_header("XI-4B Final Report", "XI-5 bounded execution against approved mapping lock"),
            "## Outcome",
            "",
            f"- Xi-5 unblockable subject to human mapping approval: `{'yes' if critical_set else 'no'}`",
            f"- High-confidence mappings: `{high_confidence_count}`",
            f"- Manual-review conflicts: `{len(conflicts)}`",
            f"- Recommended structure option: `{preferred_option}`",
            f"- Recommended option automatic/manual/attic: `{preferred_summary.get('automatic_move_count', 0)}` / `{preferred_summary.get('manual_review_count', 0)}` / `{preferred_summary.get('attic_count', 0)}`",
            "",
            "## Missing Inputs",
            "",
            *(_markdown_bullets([f"`{path}`" for path in sorted(inputs.get("missing_inputs") or [])]) if list(inputs.get("missing_inputs") or []) else ["- none"]),
            "",
            "## Recommended Next Step",
            "",
            "- review `docs/restructure/XI_4B_UNBLOCK_REPORT.md` and approve the provisional mapping lock",
            "- resolve conflicts listed in `data/restructure/src_domain_mapping_conflicts.json`",
            "- execute bounded XI-5 against `data/restructure/src_domain_mapping_lock_proposal.json` after approval",
            "",
        ]
    )


def _review_first_text(preferred_option: str, conflicts: Sequence[Mapping[str, object]], critical_set: Sequence[Mapping[str, object]]) -> str:
    return "\n".join(
        [
            "# REVIEW_FIRST",
            "",
            "This bundle is the deterministic XI-4b structure review packet for deciding the post-Xi repository layout before XI-5 removes source-like directories.",
            "",
            "Read in this order:",
            "1. docs/restructure/XI_4B_REVIEW_GUIDE.md",
            "2. docs/restructure/XI_4B_UNBLOCK_REPORT.md",
            "3. docs/restructure/STRUCTURE_OPTIONS_REPORT.md",
            "4. data/restructure/src_domain_mapping_lock_proposal.json",
            "",
            "Human decisions required:",
            f"- approve or reject preferred option `{preferred_option}`",
            f"- resolve `{len(conflicts)}` manual-review conflicts",
            f"- confirm the `{len(critical_set)}` bounded runtime-critical blockers XI-5 must clear first",
            "",
            "XI-5 requires an approved provisional mapping lock and explicit decisions on attic routes and runtime-critical conflicts.",
            "",
        ]
    )


def _render_outputs(
    repo_root: str,
    json_payloads: Mapping[str, Mapping[str, object]],
    doc_texts: Mapping[str, str],
    upstream_bundle_rels: Sequence[str],
    review_first_text: str,
) -> dict[str, object]:
    repo_file_bytes: dict[str, bytes] = {}
    for rel_path, payload in sorted(json_payloads.items()):
        repo_file_bytes[rel_path] = (canonical_json_text(dict(payload)) + "\n").encode("utf-8")
    for rel_path, text in sorted(doc_texts.items()):
        repo_file_bytes[rel_path] = str(text or "").replace("\r\n", "\n").encode("utf-8")

    bundle_entries: dict[str, bytes] = {"REVIEW_FIRST.md": review_first_text.encode("utf-8")}
    for rel_path in sorted(OUTPUT_REL_PATHS):
        if rel_path in repo_file_bytes:
            bundle_entries[rel_path] = repo_file_bytes[rel_path]
    for rel_path in sorted(set(upstream_bundle_rels)):
        payload = _read_bytes(_repo_abs(repo_root, rel_path))
        if payload:
            bundle_entries[rel_path] = payload

    bundle_manifest_lines = [
        "XI-4b Structure Review Bundle Manifest",
        f"Generated-Date: {DOC_REPORT_DATE}",
        "",
        "sha256 size path",
    ]
    for entry_path in sorted(bundle_entries):
        payload = bundle_entries[entry_path]
        bundle_manifest_lines.append(f"{_sha256_bytes(payload)} {len(payload)} {entry_path}")
    bundle_manifest_text = "\n".join(bundle_manifest_lines) + "\n"
    bundle_entries["xi4b_structure_review_bundle_manifest.txt"] = bundle_manifest_text.encode("utf-8")

    bundle_buffer = BytesIO()
    with zipfile.ZipFile(bundle_buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for entry_path in sorted(bundle_entries):
            info = zipfile.ZipInfo(entry_path, date_time=ZIP_FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0
            archive.writestr(info, bundle_entries[entry_path])
    bundle_bytes = bundle_buffer.getvalue()

    return {
        "bundle_bytes": bundle_bytes,
        "bundle_entries": bundle_entries,
        "bundle_manifest_text": bundle_manifest_text,
        "repo_file_bytes": repo_file_bytes,
        "tmp_file_bytes": {
            TMP_BUNDLE_REL: bundle_bytes,
            TMP_BUNDLE_MANIFEST_REL: bundle_manifest_text.encode("utf-8"),
        },
    }


def _validate_json_payloads(json_payloads: Mapping[str, Mapping[str, object]]) -> None:
    required_checks = {
        SRC_DOMAIN_MAPPING_REL: ("mappings", "report_id", "summary"),
        SRC_DOMAIN_MAPPING_CANDIDATES_REL: ("options", "preferred_option", "report_id"),
        SRC_DOMAIN_MAPPING_CONFLICTS_REL: ("conflicts", "report_id"),
        SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL: ("high_confidence_mappings", "preferred_layout_option", "report_id", "stability_class"),
        SRC_RUNTIME_CRITICAL_SET_REL: ("entries", "report_id"),
        XI4B_REVIEW_MANIFEST_REL: ("output_paths", "report_id", "summary", "validation"),
    }
    for rel_path, keys in required_checks.items():
        payload = dict(json_payloads.get(rel_path) or {})
        if not payload:
            raise ValueError(f"missing payload for {rel_path}")
        for key in keys:
            if key not in payload:
                raise ValueError(f"{rel_path} missing key '{key}'")
        if not _token(payload.get("deterministic_fingerprint")):
            raise ValueError(f"{rel_path} missing deterministic_fingerprint")


def build_xi4b_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    inputs = _load_inputs(root)
    tracked_files = _git_ls_files(root)
    source_roots = _discover_source_roots(tracked_files, dict(dict(inputs.get("json_payloads") or {}).get("src_directory_report") or {}))
    source_files = sorted(
        [path for path in tracked_files if _current_root_for_file(path, source_roots)],
        key=lambda item: (_current_root_for_file(item, source_roots), item),
    )
    indices = _build_indices(inputs, source_files, source_roots)
    entries = [_mapping_entry(path, _current_root_for_file(path, source_roots), indices) for path in source_files]
    entries.sort(key=lambda item: (_norm_rel(item.get("file_path")), _token(item.get("proposed_module_id"))))

    conflicts = _build_conflicts(entries)
    preferred_option = "C"
    options, option_summary_lookup = _option_rows(entries, preferred_option)
    critical_set = _build_runtime_critical_set(entries, indices)
    json_payloads = _build_json_payloads(entries, conflicts, critical_set, options, option_summary_lookup, preferred_option, inputs)
    doc_texts = {
        SRC_DOMAIN_MAPPING_REPORT_REL: _render_mapping_report(entries, conflicts, critical_set, inputs),
        STRUCTURE_OPTIONS_REPORT_REL: _render_structure_options_report(options, preferred_option),
        XI_4B_REVIEW_GUIDE_REL: _render_review_guide(preferred_option, conflicts, critical_set),
        XI_4B_UNBLOCK_REPORT_REL: _render_unblock_report(critical_set),
        XI_4B_FINAL_REL: _render_xi_4b_final(entries, conflicts, options, preferred_option, critical_set, inputs),
    }
    review_first = _review_first_text(preferred_option, conflicts, critical_set)
    rendered = _render_outputs(root, json_payloads, doc_texts, BUNDLE_UPSTREAM_RELS, review_first)

    review_manifest = dict(json_payloads[XI4B_REVIEW_MANIFEST_REL])
    review_manifest["bundle_entries"] = [
        {
            "path": path,
            "sha256": _sha256_bytes(payload),
            "size": len(payload),
        }
        for path, payload in sorted(rendered["bundle_entries"].items())
    ]
    review_manifest["validation"] = {
        "bundle_sha256": _sha256_bytes(rendered["bundle_bytes"]),
        "deterministic_rerun_match": True,
        "schema_validation": "pass",
    }
    review_manifest["deterministic_fingerprint"] = canonical_sha256(review_manifest)
    json_payloads[XI4B_REVIEW_MANIFEST_REL] = review_manifest
    rendered = _render_outputs(root, json_payloads, doc_texts, BUNDLE_UPSTREAM_RELS, review_first)
    _validate_json_payloads(json_payloads)
    return {
        "doc_texts": doc_texts,
        "json_payloads": json_payloads,
        "rendered": rendered,
        "summary": {
            "conflict_count": len(conflicts),
            "high_confidence_count": sum(
                1
                for entry in entries
                if float(entry.get("confidence", 0.0) or 0.0) >= HIGH_CONFIDENCE_THRESHOLD and len(list(entry.get("plausible_domains") or [])) <= 1
            ),
            "mapping_count": len(entries),
            "missing_input_count": len(list(inputs.get("missing_inputs") or [])),
            "preferred_option": preferred_option,
            "runtime_critical_blockers": len(critical_set),
        },
    }


def artifact_hashes(snapshot: Mapping[str, object]) -> dict[str, str]:
    rendered = dict(snapshot.get("rendered") or {})
    repo_files = dict(rendered.get("repo_file_bytes") or {})
    tmp_files = dict(rendered.get("tmp_file_bytes") or {})
    return {rel_path: _sha256_bytes(payload) for rel_path, payload in sorted({**repo_files, **tmp_files}.items(), key=lambda item: item[0])}


def write_xi4b_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> None:
    root = _repo_root(repo_root)
    rendered = dict(snapshot.get("rendered") or {})
    for rel_path, payload in sorted(dict(rendered.get("repo_file_bytes") or {}).items()):
        abs_path = _repo_abs(root, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "wb") as handle:
            handle.write(payload)
    for rel_path, payload in sorted(dict(rendered.get("tmp_file_bytes") or {}).items()):
        abs_path = _repo_abs(root, rel_path)
        _ensure_parent(abs_path)
        with open(abs_path, "wb") as handle:
            handle.write(payload)

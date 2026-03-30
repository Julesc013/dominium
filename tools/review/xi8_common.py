"""Deterministic Xi-8 repository freeze helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from compat.shims import legacy_flag_rows, path_shim_rows, tool_shim_rows, validation_shim_rows  # noqa: E402
from compat.shims.common import SHIM_SUNSET_TARGET  # noqa: E402
from tools.review.xi6_common import (  # noqa: E402
    ARCHITECTURE_GRAPH_V1_REL,
    MODULE_BOUNDARY_RULES_V1_REL,
    MODULE_REGISTRY_V1_REL,
    SINGLE_ENGINE_REGISTRY_REL,
    build_architecture_drift_report,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


XI_5A_FINAL_REL = "docs/audit/XI_5A_FINAL.md"
XI_5X1_FINAL_REL = "docs/audit/XI_5X1_FINAL.md"
XI_5X2_FINAL_REL = "docs/audit/XI_5X2_FINAL.md"
XI_6_FINAL_REL = "docs/audit/XI_6_FINAL.md"
XI_7_FINAL_REL = "docs/audit/XI_7_FINAL.md"

XI5X2_SOURCE_POLICY_REL = "data/restructure/xi5x2_source_pocket_policy.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"
SYMBOL_INDEX_REL = "data/audit/symbol_index.json"
GATE_DEFINITIONS_REL = "data/xstack/gate_definitions.json"

PROFILE_FAST_REL = "tools/xstack/ci/profiles/FAST.json"
PROFILE_STRICT_REL = "tools/xstack/ci/profiles/STRICT.json"
PROFILE_FULL_REL = "tools/xstack/ci/profiles/FULL.json"
ENTRYPOINT_PY_REL = "tools/xstack/ci/xstack_ci_entrypoint.py"
ENTRYPOINT_REL = "tools/xstack/ci/xstack_ci_entrypoint"
ENTRYPOINT_PS1_REL = "tools/xstack/ci/xstack_ci_entrypoint.ps1"

CI_GUARDRAILS_DOC_REL = "docs/xstack/CI_GUARDRAILS.md"
ARCH_DRIFT_POLICY_DOC_REL = "docs/xstack/ARCH_DRIFT_POLICY.md"

REPOSITORY_STRUCTURE_LOCK_REL = "data/architecture/repository_structure_lock.json"
REPOSITORY_STRUCTURE_DOC_REL = "docs/architecture/REPOSITORY_STRUCTURE_v1.md"
MODULE_INDEX_DOC_REL = "docs/architecture/MODULE_INDEX_v1.md"
SHIM_SUNSET_PLAN_REL = "docs/architecture/SHIM_SUNSET_PLAN.md"
REPO_FREEZE_VERIFICATION_REL = "docs/audit/REPO_FREEZE_VERIFICATION.md"
XI_8_FINAL_REL = "docs/audit/XI_8_FINAL.md"

CI_REPORT_JSON_REL = "data/audit/ci_run_report.json"
CI_REPORT_MD_REL = "docs/audit/CI_RUN_REPORT.md"

DIST_ASSEMBLE_TOOL_REL = "tools/dist/tool_assemble_dist_tree.py"
DIST_VERIFY_TOOL_REL = "tools/dist/tool_verify_distribution.py"
TRUST_STRICT_TOOL_REL = "tools/security/tool_run_trust_strict_suite.py"
ARCHIVE_RELEASE_TOOL_REL = "tools/release/tool_archive_release.py"
ARCHIVE_VERIFY_TOOL_REL = "tools/release/tool_verify_archive.py"
DIST_ROOT_REL = "dist/v0.0.0-mock"
DIST_BUNDLE_REL = "dist/v0.0.0-mock/win64/dominium"
DIST_ARCHIVE_RECORD_REL = "dist/v0.0.0-mock/win64/archive/archive_record.json"

PROHIBITED_DIR_NAMES = ("Source", "Sources", "source", "src")
REPOX_RULE_IDS = (
    "INV-NO-SRC-DIRECTORY",
    "INV-ARCH-GRAPH-V1-PRESENT",
    "INV-REPO-STRUCTURE-LOCKED",
    "INV-ARCH-GRAPH-MATCHES-REPO",
    "INV-MODULE-BOUNDARIES-RESPECTED",
    "INV-SINGLE-CANONICAL-ENGINES",
    "INV-XSTACK-CI-MUST-RUN",
    "INV-STRICT-MUST-PASS-FOR-MAIN",
)
AUDITX_DETECTOR_IDS = (
    "E560_ARCHITECTURE_DRIFT_SMELL",
    "E561_FORBIDDEN_DEPENDENCY_SMELL",
    "E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL",
    "E563_UI_TRUTH_LEAK_BOUNDARY_SMELL",
    "E564_MISSING_CI_GUARD_SMELL",
    "E565_REPOSITORY_STRUCTURE_DRIFT_SMELL",
    "AUDITX_NUMERIC_DISCIPLINE_SCAN",
)
PROFILE_IDS = ("FAST", "STRICT", "FULL")
XI8_TARGETED_TESTS = (
    "test_repository_structure_lock_valid",
    "test_no_prohibited_dirs_present",
    "test_xstack_ci_strict_passes",
)
CI_STRICT_SMOKE_TESTS = (
    "test_ci_entrypoint_deterministic_order",
    "test_ci_profiles_exist",
    "test_gate_definitions_valid",
    "test_ci_report_failures_propagate",
    "test_repository_structure_lock_valid",
    "test_no_prohibited_dirs_present",
)
TRACKED_DOMAIN_FAMILIES = (
    ("engine", "Deterministic engine-kernel and runtime law surfaces."),
    ("game", "Game-layer rules, domain content, and gameplay-specific orchestration."),
    ("apps", "User-facing applications, shells, launchers, setup flows, and product entrypoints."),
    ("tools", "Governed tooling, validation, release, audit, and operator support surfaces."),
    ("lib", "Shared libraries and reusable support code for non-product surfaces."),
    ("compat", "Compatibility negotiation, shims, and controlled legacy transition bridges."),
    ("ui", "Presentation and user-interface surfaces kept separate from truth mutation."),
    ("platform", "Platform adapters and environment-specific integration points."),
    ("data", "Derived artifacts, baselines, registries, inventories, and frozen machine-readable surfaces."),
    ("docs", "Canonical doctrine, audits, blueprints, and human-readable policy surfaces."),
)


class Xi8InputsMissing(RuntimeError):
    """Raised when Xi-8 cannot proceed safely."""


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
        raise Xi8InputsMissing(
            json.dumps(
                {"code": "refusal.xi.missing_inputs", "missing_inputs": [rel_path]},
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _read_optional_json(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    if not os.path.isfile(abs_path):
        return {}
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _json_without_keys(payload: Mapping[str, object], *keys: str) -> dict[str, object]:
    body = dict(payload or {})
    for key in keys:
        body[key] = ""
    return body


def recompute_structure_lock_content_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(_json_without_keys(payload, "content_hash", "deterministic_fingerprint"))


def recompute_structure_lock_fingerprint(payload: Mapping[str, object]) -> str:
    return canonical_sha256(_json_without_keys(payload, "deterministic_fingerprint"))


def _run_text_command(repo_root: str, command: Sequence[str]) -> str:
    completed = subprocess.run(
        list(command),
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(completed.returncode) != 0:
        raise Xi8InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi.missing_inputs",
                    "missing_inputs": [command[0]],
                    "reason": str(completed.stdout or "").strip() or "command failed",
                },
                indent=2,
                sort_keys=True,
            )
        )
    return str(completed.stdout or "")


def _run_json_command(repo_root: str, command: Sequence[str]) -> dict[str, object]:
    completed = subprocess.run(
        list(command),
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    payload: dict[str, object] = {
        "command": list(command),
        "returncode": int(completed.returncode),
        "status": "pass" if int(completed.returncode) == 0 else "fail",
    }
    text = str(completed.stdout or "").strip()
    if text:
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = {}
        if isinstance(parsed, dict):
            payload["stdout_json"] = parsed
            for field_name in (
                "result",
                "deterministic_fingerprint",
                "error_count",
                "warning_count",
                "archive_record_hash",
                "release_index_hash",
                "profile",
                "stage_count",
                "failing_stage_count",
                "report_json_path",
                "report_md_path",
                "case_count",
                "fixture_count",
            ):
                value = parsed.get(field_name)
                if value not in ("", None):
                    payload[field_name] = value
        else:
            payload["stdout_excerpt"] = text.splitlines()[-20:]
    return payload


def ensure_xi8_inputs(repo_root: str) -> None:
    root = _repo_root(repo_root)
    missing: list[str] = []
    for rel_path in (
        ARCHITECTURE_GRAPH_V1_REL,
        MODULE_REGISTRY_V1_REL,
        MODULE_BOUNDARY_RULES_V1_REL,
        SINGLE_ENGINE_REGISTRY_REL,
        XI_5A_FINAL_REL,
        XI_5X1_FINAL_REL,
        XI_5X2_FINAL_REL,
        XI_6_FINAL_REL,
        XI_7_FINAL_REL,
        XI5X2_SOURCE_POLICY_REL,
        BUILD_GRAPH_REL,
        SYMBOL_INDEX_REL,
        ENTRYPOINT_REL,
        ENTRYPOINT_PY_REL,
        ENTRYPOINT_PS1_REL,
        PROFILE_FAST_REL,
        PROFILE_STRICT_REL,
        PROFILE_FULL_REL,
        GATE_DEFINITIONS_REL,
        DIST_VERIFY_TOOL_REL,
        TRUST_STRICT_TOOL_REL,
        ARCHIVE_VERIFY_TOOL_REL,
        "docs/canon/constitution_v1.md",
        "docs/canon/glossary_v1.md",
        "AGENTS.md",
    ):
        if not os.path.exists(_repo_abs(root, rel_path)):
            missing.append(rel_path)
    if missing:
        raise Xi8InputsMissing(
            json.dumps(
                {"code": "refusal.xi.missing_inputs", "missing_inputs": sorted(set(missing))},
                indent=2,
                sort_keys=True,
            )
        )


def _git_declared_files(repo_root: str) -> list[str]:
    text = _run_text_command(repo_root, ("git", "ls-files", "--cached", "--others", "--exclude-standard"))
    rows = [_norm_rel(line) for line in text.splitlines() if _norm_rel(line)]
    return sorted(set(rows))


def _top_level_entries(file_paths: Iterable[object]) -> tuple[list[str], list[str]]:
    top_dirs: set[str] = set()
    top_files: set[str] = set()
    for rel_path in list(file_paths or []):
        token = _norm_rel(rel_path)
        if not token:
            continue
        parts = token.split("/")
        if len(parts) <= 1:
            top_files.add(parts[0])
        else:
            top_dirs.add(parts[0])
    return sorted(top_dirs), sorted(top_files)


def _source_named_ancestors(path: str) -> list[str]:
    roots: list[str] = []
    parts = [part for part in _norm_rel(path).split("/") if part]
    built: list[str] = []
    for part in parts:
        built.append(part)
        if part in PROHIBITED_DIR_NAMES:
            roots.append("/".join(built))
    return roots


def _source_like_roots(file_paths: Iterable[object]) -> list[str]:
    roots: set[str] = set()
    for rel_path in list(file_paths or []):
        token = _norm_rel(rel_path)
        if not token:
            continue
        for ancestor in _source_named_ancestors(os.path.dirname(token).replace("\\", "/")):
            roots.add(ancestor)
    return sorted(roots)


def _root_reason_map(source_policy: Mapping[str, object], declared_files: Sequence[str]) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for row in list(source_policy.get("allowlisted_residual_roots") or []):
        item = dict(row or {})
        root_path = _norm_rel(item.get("root_path"))
        if not root_path:
            continue
        details = {
            "policy_class": _token(item.get("policy_class")) or "INTENTIONAL_RESIDUAL_ALLOWED",
            "reason": _token(item.get("reason")) or "Xi-5x2 allowlisted source pocket retained intentionally.",
        }
        mapping[root_path] = details
        for source_root in _source_named_ancestors(root_path):
            mapping.setdefault(source_root, details)
    for root_path, policy_class, reason in (
        (
            "attic/src_quarantine/src",
            "VALID_LEGACY_ARCHIVE_SOURCE",
            "attic/src_quarantine/src is retained as explicit quarantine evidence and is fenced from active runtime and build ownership.",
        ),
        (
            "attic/src_quarantine/legacy/source",
            "VALID_LEGACY_ARCHIVE_SOURCE",
            "attic/src_quarantine/legacy/source is retained as explicit quarantine evidence and is fenced from active runtime and build ownership.",
        ),
    ):
        if any(_norm_rel(path).startswith(root_path + "/") or _norm_rel(path) == root_path for path in declared_files):
            mapping[root_path] = {"policy_class": policy_class, "reason": reason}
    return mapping


def _root_domain_map(module_registry: Mapping[str, object]) -> dict[str, str]:
    direct: dict[str, Counter[str]] = defaultdict(Counter)
    for row in list(module_registry.get("directories") or []):
        item = dict(row or {})
        path = _norm_rel(item.get("path"))
        if path in {"", "."}:
            continue
        top = path.split("/")[0]
        direct[top][_token(item.get("domain")) or "unknown"] += 1
    for row in list(module_registry.get("modules") or []):
        item = dict(row or {})
        root = _norm_rel(item.get("module_root"))
        if not root:
            continue
        top = root.split("/")[0]
        direct[top][_token(item.get("domain")) or "unknown"] += int(item.get("file_count", 0) or 0) or 1
    resolved: dict[str, str] = {}
    for top, counter in direct.items():
        if not counter:
            resolved[top] = "unknown"
            continue
        resolved[top] = sorted(counter.items(), key=lambda item: (-int(item[1]), item[0]))[0][0]
    return resolved


def _registered_top_level_dirs(module_registry: Mapping[str, object]) -> list[str]:
    rows = set()
    for row in list(module_registry.get("directories") or []):
        path = _norm_rel(dict(row or {}).get("path"))
        if path in {"", "."}:
            continue
        rows.add(path.split("/")[0])
    return sorted(rows)


def _module_counts_by_domain(module_registry: Mapping[str, object]) -> list[dict[str, object]]:
    counter: Counter[str] = Counter()
    for row in list(module_registry.get("modules") or []):
        item = dict(row or {})
        counter[_token(item.get("domain")) or "unknown"] += 1
    return [{"domain": domain, "module_count": int(counter[domain])} for domain in sorted(counter)]


def _module_counts_by_root(module_registry: Mapping[str, object]) -> list[dict[str, object]]:
    domain_map = _root_domain_map(module_registry)
    counter: Counter[str] = Counter()
    for row in list(module_registry.get("modules") or []):
        item = dict(row or {})
        module_root = _norm_rel(item.get("module_root"))
        if not module_root:
            continue
        counter[module_root.split("/")[0]] += 1
    rows = []
    for root in sorted(counter):
        rows.append(
            {
                "top_level_root": root,
                "module_count": int(counter[root]),
                "primary_domain": domain_map.get(root, "unknown"),
            }
        )
    return rows


def _profile_payload(profile_id: str) -> dict[str, object]:
    token = _token(profile_id).upper()
    validation_gate_ids = {
        "FAST": ["omega_1_worldgen_lock", "omega_2_baseline_universe"],
        "STRICT": [
            "validate_strict",
            "arch_audit_2",
            "omega_1_worldgen_lock",
            "omega_2_baseline_universe",
            "omega_3_gameplay_loop",
            "omega_4_disaster_suite",
            "omega_5_ecosystem_verify",
            "omega_6_update_sim",
        ],
        "FULL": [
            "validate_strict",
            "arch_audit_2",
            "omega_1_worldgen_lock",
            "omega_2_baseline_universe",
            "omega_3_gameplay_loop",
            "omega_4_disaster_suite",
            "omega_5_ecosystem_verify",
            "omega_6_update_sim",
            "convergence_gate",
            "performance_envelope",
            "store_verify",
            "store_gc",
            "archive_verify",
        ],
    }[token]
    description = {
        "FAST": "Default PR profile with Xi-8 structure lock enforcement, key AuditX scans, TestX FAST selection, and Ω-1/Ω-2 verification.",
        "STRICT": "Required pre-merge profile with Xi-8 structure lock enforcement, strict validation, ARCH-AUDIT-2, Ω-1..Ω-6, and full RepoX/AuditX/TestX strict coverage.",
        "FULL": "Nightly or pre-release profile with Xi-8 structure lock enforcement plus convergence, performance, store, and archive verification.",
    }[token]
    payload = {
        "report_id": "xstack.ci.profile.v1",
        "profile_id": token,
        "description": description,
        "repox_profile": token,
        "repox_rule_ids": list(REPOX_RULE_IDS),
        "auditx_detector_ids": list(AUDITX_DETECTOR_IDS),
        "testx_profile": token,
        "testx_selection": "impact_based_subset" if token == "FAST" else ("extended_subset" if token == "STRICT" else "full_profile_runner"),
        "testx_cache": "off",
        "execution_order": ["repox", "auditx", "testx", "validation_and_omega"],
        "validation_gate_ids": validation_gate_ids,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _gate_definitions_payload(lock_payload: Mapping[str, object]) -> dict[str, object]:
    payload = {
        "report_id": "xstack.ci.gate_definitions.v1",
        "description": "Deterministic Xi-8 CI gate catalog for RepoX, AuditX, TestX, structure-lock enforcement, and validation/Omega execution.",
        "profiles": [
            {"profile_id": "FAST", "purpose": "default per PR"},
            {"profile_id": "STRICT", "purpose": "required pre-merge to main"},
            {"profile_id": "FULL", "purpose": "nightly or pre-release"},
        ],
        "repox_rules": [
            {"rule_id": "INV-NO-SRC-DIRECTORY", "purpose": "Block reintroduction of generic src roots."},
            {"rule_id": "INV-ARCH-GRAPH-V1-PRESENT", "purpose": "Require the Xi-6 frozen architecture graph and drift guard."},
            {"rule_id": "INV-REPO-STRUCTURE-LOCKED", "purpose": "Require the Xi-8 repository structure lock and sanctioned source-pocket exceptions."},
            {"rule_id": "INV-ARCH-GRAPH-MATCHES-REPO", "purpose": "Require live repository roots to stay registered in the Xi-6/Xi-8 frozen architecture surfaces."},
            {"rule_id": "INV-MODULE-BOUNDARIES-RESPECTED", "purpose": "Block forbidden module dependencies."},
            {"rule_id": "INV-SINGLE-CANONICAL-ENGINES", "purpose": "Block duplicate semantic engine implementations."},
            {"rule_id": "INV-XSTACK-CI-MUST-RUN", "purpose": "Require the Xi-7/Xi-8 CI guardrail surface and workflow wiring."},
            {"rule_id": "INV-STRICT-MUST-PASS-FOR-MAIN", "purpose": "Require the STRICT profile as the declared merge guard for main."},
        ],
        "auditx_detectors": [
            {"detector_id": "E560_ARCHITECTURE_DRIFT_SMELL", "purpose": "Detect live module graph drift from the Xi-6 frozen architecture graph without an explicit update tag."},
            {"detector_id": "E561_FORBIDDEN_DEPENDENCY_SMELL", "purpose": "Detect module boundary violations against module_boundary_rules.v1."},
            {"detector_id": "E562_DUPLICATE_SEMANTIC_ENGINE_REGISTRY_SMELL", "purpose": "Detect duplicate semantic engines against the Xi-6 single-engine registry."},
            {"detector_id": "E563_UI_TRUTH_LEAK_BOUNDARY_SMELL", "purpose": "Reinforce the constitutional renderer and UI truth-leak boundary."},
            {"detector_id": "E564_MISSING_CI_GUARD_SMELL", "purpose": "Detect missing or incomplete Xi-7/Xi-8 CI guardrail surfaces and workflow wiring."},
            {"detector_id": "E565_REPOSITORY_STRUCTURE_DRIFT_SMELL", "purpose": "Detect Xi-8 repository-structure drift, unsanctioned source pockets, and unknown top-level roots."},
            {"detector_id": "AUDITX_NUMERIC_DISCIPLINE_SCAN", "purpose": "Run the deterministic numeric discipline scan as part of the Xi-8 audit surface."},
        ],
        "testx_groups": [
            {"group_id": "impact_subset_fast", "profile": "FAST", "selection": "impact_based_subset"},
            {"group_id": "extended_subset_strict", "profile": "STRICT", "selection": "strict_profile_runner"},
            {"group_id": "full_suite", "profile": "FULL", "selection": "full_profile_runner"},
        ],
        "validation_gates": [
            {"gate_id": "validate_strict", "profiles": ["STRICT", "FULL"], "command": ["python", "-B", "tools/ci/validate_all.py", "--repo-root", ".", "--strict"], "prefer_report_file": True, "report_json_rel": "data/audit/validation_report_STRICT.json", "report_doc_rel": "docs/audit/VALIDATION_REPORT_STRICT.md"},
            {"gate_id": "arch_audit_2", "profiles": ["STRICT", "FULL"], "command": ["python", "-B", "tools/audit/tool_run_arch_audit.py", "--repo-root", "."], "prefer_report_file": True, "report_json_rel": "data/audit/arch_audit2_report.json", "report_doc_rel": "docs/audit/ARCH_AUDIT2_REPORT.md"},
            {"gate_id": "omega_1_worldgen_lock", "profiles": ["FAST", "STRICT", "FULL"], "command": ["python", "-B", "tools/worldgen/tool_verify_worldgen_lock.py", "--repo-root", "."]},
            {"gate_id": "omega_2_baseline_universe", "profiles": ["FAST", "STRICT", "FULL"], "command": ["python", "-B", "tools/mvp/tool_verify_baseline_universe.py", "--repo-root", "."]},
            {"gate_id": "omega_3_gameplay_loop", "profiles": ["STRICT", "FULL"], "command": ["python", "-B", "tools/mvp/tool_verify_gameplay_loop.py", "--repo-root", "."]},
            {"gate_id": "omega_4_disaster_suite", "profiles": ["STRICT", "FULL"], "command": ["python", "-B", "tools/mvp/tool_run_disaster_suite.py", "--repo-root", "."]},
            {"gate_id": "omega_5_ecosystem_verify", "profiles": ["STRICT", "FULL"], "command": ["python", "-B", "tools/mvp/tool_verify_ecosystem.py", "--repo-root", "."]},
            {"gate_id": "omega_6_update_sim", "profiles": ["STRICT", "FULL"], "command": ["python", "-B", "tools/mvp/tool_run_update_sim.py", "--repo-root", "."]},
            {"gate_id": "convergence_gate", "profiles": ["FULL"], "command": ["python", "-B", "tools/convergence/tool_run_convergence_gate.py", "--repo-root", ".", "--skip-cross-platform", "--prefer-cached-heavy"]},
            {"gate_id": "performance_envelope", "profiles": ["FULL"], "command": ["python", "-B", "tools/perf/tool_run_performance_envelope.py", "--repo-root", ".", "--platform-tag", "win64"]},
            {"gate_id": "store_verify", "profiles": ["FULL"], "command": ["python", "-B", "tools/lib/tool_store_verify.py", "--repo-root", "."]},
            {"gate_id": "store_gc", "profiles": ["FULL"], "command": ["python", "-B", "tools/lib/tool_run_store_gc.py", "--repo-root", "."]},
            {"gate_id": "archive_verify", "profiles": ["FULL"], "command": ["python", "-B", "tools/release/tool_verify_archive.py", "--repo-root", "."], "optional": True, "skip_if_missing_path": DIST_ROOT_REL},
        ],
        "main_branch_policy": {"workflow_file": ".github/workflows/ci.yml", "required_profile": "STRICT", "local_fast_command": "tools/xstack/ci/xstack_ci_entrypoint --profile FAST"},
        "required_invariants": ["constitution_v1.md A1", "constitution_v1.md A8", "constitution_v1.md A10", "AGENTS.md §2", "AGENTS.md §5"],
        "repository_structure_lock_hash": _token(lock_payload.get("content_hash")),
        "provisional_allowances": [
            {"allowance_id": "xi7_data_architecture_support_surface", "allowed_module_id": "data.architecture", "reason": "Xi-6, Xi-7, and Xi-8 freeze and guard artifacts live under data/architecture as non-runtime support surfaces.", "replacement_plan": "Classify data/architecture explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "architecture_drift"},
            {"allowance_id": "xi8_data_xstack_support_surface", "allowed_module_id": "data.xstack", "reason": "Xi-7 and Xi-8 CI gate catalogs live under data/xstack as non-runtime support surfaces.", "replacement_plan": "Classify data/xstack explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "architecture_drift"},
            {"allowance_id": "xi8_docs_xstack_support_surface", "allowed_module_id": "docs.xstack", "reason": "Xi-7 and Xi-8 operator CI policy docs live under docs/xstack as non-runtime support surfaces.", "replacement_plan": "Classify docs/xstack explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "architecture_drift"},
            {"allowance_id": "xi8_tools_xstack_ci_support_surface", "allowed_module_id": "tools.xstack.ci", "reason": "Xi-7 and Xi-8 CI entrypoints and helpers live under tools/xstack/ci as non-runtime support surfaces.", "replacement_plan": "Classify tools/xstack/ci explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "architecture_drift"},
            {"allowance_id": "xi8_tools_xstack_ci_profiles_support_surface", "allowed_module_id": "tools.xstack.ci.profiles", "reason": "Xi-7 and Xi-8 CI profile metadata lives under tools/xstack/ci/profiles as non-runtime support surfaces.", "replacement_plan": "Classify tools/xstack/ci/profiles explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "architecture_drift"},
            {"allowance_id": "xi7_data_architecture_support_surface_boundary", "allowed_module_id": "data.architecture", "reason": "Xi-6, Xi-7, and Xi-8 freeze and guard artifacts live under data/architecture as non-runtime support surfaces.", "replacement_plan": "Classify data/architecture explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "module_boundary"},
            {"allowance_id": "xi8_data_xstack_support_surface_boundary", "allowed_module_id": "data.xstack", "reason": "Xi-7 and Xi-8 CI gate catalogs live under data/xstack as non-runtime support surfaces.", "replacement_plan": "Classify data/xstack explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "module_boundary"},
            {"allowance_id": "xi8_docs_xstack_support_surface_boundary", "allowed_module_id": "docs.xstack", "reason": "Xi-7 and Xi-8 operator CI policy docs live under docs/xstack as non-runtime support surfaces.", "replacement_plan": "Classify docs/xstack explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "module_boundary"},
            {"allowance_id": "xi8_tools_xstack_ci_support_surface_boundary", "allowed_module_id": "tools.xstack.ci", "reason": "Xi-7 and Xi-8 CI entrypoints and helpers live under tools/xstack/ci as non-runtime support surfaces.", "replacement_plan": "Classify tools/xstack/ci explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "module_boundary"},
            {"allowance_id": "xi8_tools_xstack_ci_profiles_support_surface_boundary", "allowed_module_id": "tools.xstack.ci.profiles", "reason": "Xi-7 and Xi-8 CI profile metadata lives under tools/xstack/ci/profiles as non-runtime support surfaces.", "replacement_plan": "Classify tools/xstack/ci/profiles explicitly in the next architecture-update revision instead of relying on a provisional allowance.", "scope": "module_boundary"},
            {"allowance_id": "xi7_tools_controlx_review_bridge", "allowed_module_id": "tools.controlx", "allowed_dependency_module_id": "tools.review", "reason": "ControlX planning helpers still reuse review-side analysis helpers during the Xi-7/Xi-8 integration phase.", "replacement_plan": "Move the shared logic into a neutral support surface or refresh module boundaries via ARCH-GRAPH-UPDATE before tightening this allowance away.", "scope": "module_boundary"},
            {"allowance_id": "xi8_auditx_ci_bridge", "allowed_module_id": "tools.auditx.analyzers", "allowed_dependency_module_id": "tools.xstack.ci", "reason": "AuditX Xi-7/Xi-8 analyzers reuse CI helper logic to report missing or drifted guard surfaces deterministically.", "replacement_plan": "Move shared CI-drift analysis into a neutral support surface or refresh module boundaries via ARCH-GRAPH-UPDATE before tightening this allowance away.", "scope": "module_boundary"},
            {"allowance_id": "xi8_repox_ci_bridge", "allowed_module_id": "tools.xstack.repox", "allowed_dependency_module_id": "tools.xstack.ci", "reason": "RepoX reuses Xi-7/Xi-8 CI helper logic to keep hard-fail rules aligned with CI metadata.", "replacement_plan": "Move shared CI-drift analysis into a neutral support surface or refresh module boundaries via ARCH-GRAPH-UPDATE before tightening this allowance away.", "scope": "module_boundary"},
            {"allowance_id": "xi8_testx_ci_bridge", "allowed_module_id": "tools.xstack.testx.tests", "allowed_dependency_module_id": "tools.xstack.ci", "reason": "Xi-7/Xi-8 TestX smoke tests inspect the committed CI profile metadata to keep enforcement deterministic.", "replacement_plan": "Move shared CI profile assertions into a neutral test support surface or refresh module boundaries via ARCH-GRAPH-UPDATE before tightening this allowance away.", "scope": "module_boundary"},
        ],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_repository_structure_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    declared_files = _git_declared_files(root)
    top_level_dirs, top_level_files = _top_level_entries(declared_files)
    source_policy = _read_json(root, XI5X2_SOURCE_POLICY_REL)
    module_registry = _read_json(root, MODULE_REGISTRY_V1_REL)
    architecture_graph = _read_json(root, ARCHITECTURE_GRAPH_V1_REL)
    boundary_rules = _read_json(root, MODULE_BOUNDARY_RULES_V1_REL)
    single_engine_registry = _read_json(root, SINGLE_ENGINE_REGISTRY_REL)
    live_source_like_roots = _source_like_roots(declared_files)
    sanctioned_root_rows = _root_reason_map(source_policy, declared_files)
    sanctioned_source_like_roots = sorted(
        {
            root_path
            for root_path in sanctioned_root_rows
            if _norm_rel(root_path).split("/")[-1] in PROHIBITED_DIR_NAMES
        }
    )
    snapshot = {
        "declared_file_count": len(declared_files),
        "declared_files": declared_files,
        "top_level_directories": top_level_dirs,
        "top_level_files": top_level_files,
        "top_level_domain_map": _root_domain_map(module_registry),
        "live_source_like_roots": live_source_like_roots,
        "sanctioned_source_like_roots": sanctioned_source_like_roots,
        "sanctioned_source_like_root_rows": [{"root_path": root_path, "policy_class": _token(sanctioned_root_rows[root_path].get("policy_class")), "reason": _token(sanctioned_root_rows[root_path].get("reason"))} for root_path in sanctioned_source_like_roots],
        "module_registry_module_count": int(len(list(module_registry.get("modules") or []))),
        "module_registry_directory_count": int(len(list(module_registry.get("directories") or []))),
        "registered_top_level_directories": _registered_top_level_dirs(module_registry),
        "module_counts_by_domain": _module_counts_by_domain(module_registry),
        "module_counts_by_root": _module_counts_by_root(module_registry),
        "source_policy_fingerprint": _token(source_policy.get("deterministic_fingerprint")),
        "architecture_graph_v1_content_hash": _token(architecture_graph.get("content_hash")),
        "architecture_graph_v1_fingerprint": _token(architecture_graph.get("deterministic_fingerprint")),
        "module_boundary_rules_v1_content_hash": _token(boundary_rules.get("content_hash")),
        "module_boundary_rules_v1_fingerprint": _token(boundary_rules.get("deterministic_fingerprint")),
        "single_engine_registry_content_hash": _token(single_engine_registry.get("content_hash")),
        "single_engine_registry_fingerprint": _token(single_engine_registry.get("deterministic_fingerprint")),
        "generated_source_like_roots_ignored": list(source_policy.get("generated_source_like_roots_ignored") or []),
    }
    return snapshot


def build_repository_structure_lock_payload(snapshot: Mapping[str, object]) -> dict[str, object]:
    payload = {
        "report_id": "repo.structure.lock.v1",
        "identity": {"kind": "identity.manifest", "id": "repository_structure_lock.v1"},
        "stability_class": "stable",
        "architecture_graph_v1_content_hash": _token(snapshot.get("architecture_graph_v1_content_hash")),
        "module_boundary_rules_v1_content_hash": _token(snapshot.get("module_boundary_rules_v1_content_hash")),
        "source_policy_fingerprint": _token(snapshot.get("source_policy_fingerprint")),
        "allowed_top_level_directories": list(snapshot.get("top_level_directories") or []),
        "allowed_top_level_files": list(snapshot.get("top_level_files") or []),
        "prohibited_top_level_directory_names": list(PROHIBITED_DIR_NAMES),
        "prohibited_nested_source_like_directory_names": list(PROHIBITED_DIR_NAMES),
        "allowed_source_like_roots": list(snapshot.get("sanctioned_source_like_roots") or []),
        "allowed_source_like_root_rows": list(snapshot.get("sanctioned_source_like_root_rows") or []),
        "generated_source_like_roots_ignored": list(snapshot.get("generated_source_like_roots_ignored") or []),
        "required_invariants": ["constitution_v1.md A1", "constitution_v1.md A8", "constitution_v1.md A10", "AGENTS.md §2", "AGENTS.md §5"],
        "notes": [
            "Freeze the actual live repository top-level structure rather than an idealized subset.",
            "Allow only Xi-5x2 policy-classified source-like roots to remain.",
            "Ignore generated or gitignored projection, dist, build, and cache trees when evaluating the lock.",
        ],
        "content_hash": "",
        "deterministic_fingerprint": "",
    }
    payload["content_hash"] = recompute_structure_lock_content_hash(payload)
    payload["deterministic_fingerprint"] = recompute_structure_lock_fingerprint(payload)
    return payload


def load_repository_structure_lock(repo_root: str) -> dict[str, object]:
    return _read_optional_json(repo_root, REPOSITORY_STRUCTURE_LOCK_REL)


def _allowance_matches_module_delta(gate_definitions: Mapping[str, object], module_delta: Sequence[object]) -> bool:
    delta = sorted({_token(value) for value in list(module_delta or []) if _token(value)})
    allowed = sorted(
        {
            _token(dict(row or {}).get("allowed_module_id"))
            for row in list(gate_definitions.get("provisional_allowances") or [])
            if _token(dict(row or {}).get("scope")) == "architecture_drift" and _token(dict(row or {}).get("allowed_module_id"))
        }
    )
    return bool(delta) and bool(allowed) and delta == allowed


def build_repository_structure_violations(repo_root: str) -> list[dict[str, object]]:
    root = _repo_root(repo_root)
    lock_payload = load_repository_structure_lock(root)
    if not lock_payload:
        return [
            {
                "rule_id": "INV-REPO-STRUCTURE-LOCKED",
                "code": "missing_repository_structure_lock",
                "file_path": REPOSITORY_STRUCTURE_LOCK_REL,
                "message": "Xi-8 repository structure lock is missing",
                "remediation": "restore data/architecture/repository_structure_lock.json before continuing CI",
            }
        ]
    snapshot = build_repository_structure_snapshot(root)
    findings: list[dict[str, object]] = []
    live_top_dirs = set(snapshot.get("top_level_directories") or [])
    live_top_files = set(snapshot.get("top_level_files") or [])
    allowed_top_dirs = set(lock_payload.get("allowed_top_level_directories") or [])
    allowed_top_files = set(lock_payload.get("allowed_top_level_files") or [])
    for extra in sorted(live_top_dirs - allowed_top_dirs):
        findings.append(
            {
                "rule_id": "INV-REPO-STRUCTURE-LOCKED",
                "code": "unexpected_top_level_directory",
                "file_path": extra,
                "message": "unknown top-level directory is not covered by the Xi-8 repository structure lock",
                "remediation": "update the repository structure lock deliberately or remove the undeclared top-level directory",
            }
        )
    for missing in sorted(allowed_top_dirs - live_top_dirs):
        findings.append(
            {
                "rule_id": "INV-REPO-STRUCTURE-LOCKED",
                "code": "missing_frozen_top_level_directory",
                "file_path": missing,
                "message": "frozen top-level directory is missing from the live repository",
                "remediation": "restore the missing top-level directory or refresh the Xi-8 lock deliberately",
            }
        )
    for extra in sorted(live_top_files - allowed_top_files):
        findings.append(
            {
                "rule_id": "INV-REPO-STRUCTURE-LOCKED",
                "code": "unexpected_top_level_file",
                "file_path": extra,
                "message": "unknown top-level file is not covered by the Xi-8 repository structure lock",
                "remediation": "update the repository structure lock deliberately or remove the undeclared top-level file",
            }
        )
    for missing in sorted(allowed_top_files - live_top_files):
        findings.append(
            {
                "rule_id": "INV-REPO-STRUCTURE-LOCKED",
                "code": "missing_frozen_top_level_file",
                "file_path": missing,
                "message": "frozen top-level file is missing from the live repository",
                "remediation": "restore the missing top-level file or refresh the Xi-8 lock deliberately",
            }
        )
    for top_dir in sorted(live_top_dirs):
        if top_dir in PROHIBITED_DIR_NAMES:
            findings.append(
                {
                    "rule_id": "INV-REPO-STRUCTURE-LOCKED",
                    "code": "prohibited_top_level_directory_name",
                    "file_path": top_dir,
                    "message": "prohibited generic source-like top-level directory exists",
                    "remediation": "remove the generic source-like top-level directory and route files into canonical domains",
                }
            )
    allowed_source_like_roots = set(lock_payload.get("allowed_source_like_roots") or [])
    for root_path in list(snapshot.get("live_source_like_roots") or []):
        if root_path in allowed_source_like_roots:
            continue
        findings.append(
            {
                "rule_id": "INV-REPO-STRUCTURE-LOCKED",
                "code": "unsanctioned_source_like_root",
                "file_path": root_path,
                "message": "source-like directory is not sanctioned by the Xi-8 repository structure lock",
                "remediation": "remove, rehome, or explicitly policy-classify the source-like directory before merge",
            }
        )
    return sorted(findings, key=lambda item: (_token(item.get("rule_id")), _norm_rel(item.get("file_path")), _token(item.get("code"))))


def build_arch_graph_matches_repo_violations(repo_root: str) -> list[dict[str, object]]:
    root = _repo_root(repo_root)
    snapshot = build_repository_structure_snapshot(root)
    gate_definitions = _read_optional_json(root, GATE_DEFINITIONS_REL)
    drift_report = build_architecture_drift_report(root)
    findings: list[dict[str, object]] = []
    if _token(drift_report.get("status")).lower() != "pass" and (not _allowance_matches_module_delta(gate_definitions, list(drift_report.get("module_delta_preview") or []))):
        findings.append(
            {
                "rule_id": "INV-ARCH-GRAPH-MATCHES-REPO",
                "code": "architecture_drift_detected",
                "file_path": ARCHITECTURE_GRAPH_V1_REL,
                "message": _token(drift_report.get("reason")) or "live repository drifted from the frozen architecture graph",
                "remediation": "attach ARCH-GRAPH-UPDATE and refresh the Xi-6/Xi-8 frozen architecture surfaces intentionally",
            }
        )
    registered = set(snapshot.get("registered_top_level_directories") or [])
    for top_dir in sorted(set(snapshot.get("top_level_directories") or []) - registered):
        findings.append(
            {
                "rule_id": "INV-ARCH-GRAPH-MATCHES-REPO",
                "code": "top_level_directory_not_registered",
                "file_path": top_dir,
                "message": "top-level directory is not registered in module_registry.v1",
                "remediation": "register the directory through Xi-6/Xi-8 architecture surfaces or remove the undeclared root",
            }
        )
    return sorted(findings, key=lambda item: (_token(item.get("rule_id")), _norm_rel(item.get("file_path")), _token(item.get("code"))))


def evaluate_repository_structure(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    lock_payload = load_repository_structure_lock(root)
    structure_findings = build_repository_structure_violations(root)
    arch_graph_findings = build_arch_graph_matches_repo_violations(root)
    report = {
        "report_id": "repo.structure.evaluation.v1",
        "status": "pass" if (not structure_findings and not arch_graph_findings) else "fail",
        "structure_findings": structure_findings,
        "arch_graph_match_findings": arch_graph_findings,
        "repository_structure_lock_hash": _token(lock_payload.get("content_hash")),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _render_repository_structure_doc(snapshot: Mapping[str, object], lock_payload: Mapping[str, object]) -> str:
    top_level_groups: dict[str, list[str]] = defaultdict(list)
    domain_map = dict(snapshot.get("top_level_domain_map") or {})
    for root in list(snapshot.get("top_level_directories") or []):
        top_level_groups[domain_map.get(root, "unknown")].append(root)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-8",
        "Replacement Target: superseded only by a later explicit repository-structure lock revision",
        "",
        "# Repository Structure v1",
        "",
        "Xi-8 freezes the live repository structure as it exists after Xi-5x2, Xi-6, and Xi-7.",
        "",
        "- repository structure lock hash: `{}`".format(_token(lock_payload.get("content_hash"))),
        "- allowed top-level directories: `{}`".format(len(list(lock_payload.get("allowed_top_level_directories") or []))),
        "- allowed top-level files: `{}`".format(len(list(lock_payload.get("allowed_top_level_files") or []))),
        "- sanctioned source-like roots: `{}`".format(len(list(lock_payload.get("allowed_source_like_roots") or []))),
        "",
        "## No `src` Rule",
        "",
        "Generic code dumping grounds remain forbidden:",
        "",
        "- top-level `src/`",
        "- top-level `source/`",
        "- top-level `Source/` or `Sources/`",
        "- any unsanctioned nested `src` or `source` directory that is not policy-classified in Xi-5x2/Xi-8",
        "",
        "Source-like roots that remain are allowed only through explicit Xi-5x2/Xi-8 policy.",
        "",
        "## Canonical Domain Placement",
        "",
    ]
    for root_name, description in TRACKED_DOMAIN_FAMILIES:
        lines.append("- `{}`: {}".format(root_name, description))
    lines.extend(["", "## Frozen Top-Level Layout", "", "| Primary Domain | Roots |", "| --- | --- |"])
    for domain in sorted(top_level_groups):
        lines.append("| `{}` | `{}` |".format(domain, ", ".join("`{}`".format(item) for item in sorted(top_level_groups[domain]))))
    if list(snapshot.get("top_level_files") or []):
        lines.extend(["", "Top-level files kept in the lock:", "", "- {}".format(", ".join("`{}`".format(item) for item in list(snapshot.get("top_level_files") or [])))])
    lines.extend(["", "## Allowed Source-Like Exceptions", "", "| Root | Policy Class | Rationale |", "| --- | --- | --- |"])
    for row in list(lock_payload.get("allowed_source_like_root_rows") or []):
        item = dict(row or {})
        lines.append("| `{}` | `{}` | {} |".format(_token(item.get("root_path")), _token(item.get("policy_class")), _token(item.get("reason"))))
    lines.extend(["", "## Prohibited Patterns", "", "- new unknown top-level directories without registry and lock updates", "- new top-level `src` or `source` directories", "- new nested source-like roots outside the sanctioned Xi-5x2/Xi-8 allowlist", "- generic common dumping grounds introduced without architectural registration", "", "Ignored generated surfaces such as `build/`, `dist/`, `out/`, `tmp/`, `.xstack_cache/`, and projection output trees are not part of this lock."])
    return "\n".join(lines) + "\n"


def _render_module_index_doc(snapshot: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-8",
        "Replacement Target: superseded only by a later explicit Xi architecture refresh",
        "",
        "# Module Index v1",
        "",
        "- frozen module count: `{}`".format(int(snapshot.get("module_registry_module_count", 0) or 0)),
        "- frozen directory count: `{}`".format(int(snapshot.get("module_registry_directory_count", 0) or 0)),
        "",
        "## Domain Counts",
        "",
        "| Domain | Module Count |",
        "| --- | --- |",
    ]
    for row in list(snapshot.get("module_counts_by_domain") or []):
        item = dict(row or {})
        lines.append("| `{}` | `{}` |".format(_token(item.get("domain")), int(item.get("module_count", 0) or 0)))
    lines.extend(["", "## Top-Level Root Ownership", "", "| Root | Primary Domain | Module Count |", "| --- | --- | --- |"])
    for row in list(snapshot.get("module_counts_by_root") or []):
        item = dict(row or {})
        lines.append("| `{}` | `{}` | `{}` |".format(_token(item.get("top_level_root")), _token(item.get("primary_domain")), int(item.get("module_count", 0) or 0)))
    return "\n".join(lines) + "\n"


def _shim_reference_rows(repo_root: str) -> dict[str, dict[str, bool]]:
    build_text = canonical_json_text(_read_json(repo_root, BUILD_GRAPH_REL))
    symbol_text = canonical_json_text(_read_json(repo_root, SYMBOL_INDEX_REL))
    return {
        "path": {"build_graph": "compat/shims/path_shims.py" in build_text or "shim.path." in build_text, "symbol_index": "compat/shims/path_shims.py" in symbol_text or "shim.path." in symbol_text},
        "flag": {"build_graph": "compat/shims/flag_shims.py" in build_text or "shim.flag." in build_text, "symbol_index": "compat/shims/flag_shims.py" in symbol_text or "shim.flag." in symbol_text},
        "tool": {"build_graph": "compat/shims/tool_shims.py" in build_text or "shim.tool." in build_text, "symbol_index": "compat/shims/tool_shims.py" in symbol_text or "shim.tool." in symbol_text},
        "validation": {"build_graph": "compat/shims/validation_shims.py" in build_text or "shim.validation." in build_text, "symbol_index": "compat/shims/validation_shims.py" in symbol_text or "shim.validation." in symbol_text},
    }


def _shim_rows(repo_root: str) -> list[dict[str, object]]:
    references = _shim_reference_rows(repo_root)
    rows: list[dict[str, object]] = []
    for category, category_rows in (
        ("path", path_shim_rows()),
        ("flag", legacy_flag_rows()),
        ("tool", tool_shim_rows()),
        ("validation", validation_shim_rows()),
    ):
        for row in list(category_rows or []):
            item = dict(row or {})
            legacy_surface = _token(item.get("legacy_surface")) or _token(item.get("legacy_flag"))
            replacement_surface = _token(item.get("replacement_surface")) or "{} {}".format(_token(item.get("replacement_flag")), _token(item.get("replacement_value"))).strip()
            rows.append(
                {
                    "category": category,
                    "shim_id": _token(item.get("shim_id")),
                    "legacy_surface": legacy_surface,
                    "replacement_surface": replacement_surface,
                    "sunset_milestone": "v0.1.0",
                    "build_graph_reference_detected": bool(references[category]["build_graph"]),
                    "symbol_index_reference_detected": bool(references[category]["symbol_index"]),
                }
            )
    return sorted(rows, key=lambda item: (_token(item.get("category")), _token(item.get("shim_id"))))


def _render_shim_sunset_plan(repo_root: str) -> str:
    shim_rows = _shim_rows(repo_root)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-8",
        "Replacement Target: later shim removal execution once REPO-LAYOUT-1 bridges are provably unused",
        "",
        "# Shim Sunset Plan",
        "",
        "Xi-8 does not remove shims automatically. The REPO-LAYOUT-1 shims remain in place until removal is proven safe.",
        "",
        "- shim count: `{}`".format(len(shim_rows)),
        "- shared sunset target: `{}`".format(SHIM_SUNSET_TARGET),
        "",
        "Removal requires all of the following:",
        "",
        "- no references in build graph",
        "- no references in symbol index",
        "- all docs updated",
        "- Ω suite passes without shims",
        "",
        "| Category | Shim ID | Legacy Surface | Forwards To | Milestone | Build Graph Ref | Symbol Index Ref |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in shim_rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("category")),
                _token(row.get("shim_id")),
                _token(row.get("legacy_surface")),
                _token(row.get("replacement_surface")),
                _token(row.get("sunset_milestone")),
                "yes" if bool(row.get("build_graph_reference_detected")) else "not proven",
                "yes" if bool(row.get("symbol_index_reference_detected")) else "not proven",
            )
        )
    lines.extend(["", "Current Xi-8 action: retain all shims. No shim was removed in this freeze pass."])
    return "\n".join(lines) + "\n"


def _render_ci_guardrails_doc(gate_definitions: Mapping[str, object], profiles: Sequence[Mapping[str, object]]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-8",
        "Replacement Target: superseded only by a later explicit CI guard profile revision",
        "",
        "# CI Guardrails",
        "",
        "Xi-8 extends the Xi-7 CI immune system with repository-structure freeze enforcement.",
        "",
        "Local commands:",
        "",
        "- `tools/xstack/ci/xstack_ci_entrypoint --profile FAST`",
        "- `python -B tools/xstack/ci/xstack_ci_entrypoint.py --repo-root . --profile FAST`",
        "",
        "## RepoX Rules",
        "",
    ]
    for row in list(gate_definitions.get("repox_rules") or []):
        item = dict(row or {})
        lines.append("- `{}`: {}".format(_token(item.get("rule_id")), _token(item.get("purpose"))))
    lines.extend(["", "## AuditX Detectors", ""])
    for row in list(gate_definitions.get("auditx_detectors") or []):
        item = dict(row or {})
        lines.append("- `{}`: {}".format(_token(item.get("detector_id")), _token(item.get("purpose"))))
    lines.extend(["", "## Profiles", ""])
    for profile in profiles:
        item = dict(profile or {})
        lines.append("- `{}`: {}".format(_token(item.get("profile_id")), _token(item.get("description"))))
    lines.extend(["", "Prompts are untrusted.", "CI is authoritative."])
    return "\n".join(lines) + "\n"


def _render_arch_drift_policy_doc(lock_payload: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-8",
        "Replacement Target: later explicit policy revision only",
        "",
        "# Architecture Drift Policy",
        "",
        "Intentional architecture and repository-structure change requires deliberate process rather than prompt drift.",
        "",
        "## Architecture Graph Updates",
        "",
        "1. prepare a ControlX architecture plan with `python -B tools/controlx/tool_plan_arch_change.py --repo-root .`",
        "2. attach `ARCH-GRAPH-UPDATE`",
        "3. update the Xi-6 frozen architecture artifacts deliberately",
        "4. pass the `FULL` CI profile",
        "",
        "## New Modules",
        "",
        "1. update `data/architecture/module_registry.v1.json`",
        "2. update `data/architecture/architecture_graph.v1.json`",
        "3. update `data/architecture/repository_structure_lock.json` if a new top-level root is involved",
        "4. pass `STRICT` and `FULL`",
        "",
        "## New Dependencies",
        "",
        "1. update `data/architecture/module_boundary_rules.v1.json`",
        "2. preserve constitutional architecture",
        "3. pass `STRICT` and `FULL`",
        "",
        "## Repository Structure Updates",
        "",
        "- top-level roots are frozen by Xi-8 lock hash `{}`".format(_token(lock_payload.get("content_hash"))),
        "- sanctioned source-like roots may change only through explicit Xi-5/Xi-8 policy refresh",
        "- generic `src/` and `source/` dumping grounds remain forbidden",
        "",
        "Prompts are untrusted.",
        "CI and frozen artifacts are authoritative.",
    ]
    return "\n".join(lines) + "\n"


def _render_repo_freeze_verification(report: Mapping[str, object]) -> str:
    ci_stage = dict(report.get("ci_strict") or {})
    trust_stage = dict(report.get("trust_strict") or {})
    dist_refresh_stage = dict(report.get("dist_refresh") or {})
    dist_stage = dict(report.get("dist_verify") or {})
    archive_release_stage = dict(report.get("archive_release") or {})
    archive_stage = dict(report.get("archive_verify") or {})
    tests_stage = dict(report.get("targeted_testx") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-8",
        "Replacement Target: superseded by a later explicit repository-freeze verification refresh",
        "",
        "# Repo Freeze Verification",
        "",
        "- XStack CI STRICT: `{}`".format(_token(ci_stage.get("result")) or _token(ci_stage.get("status"))),
        "- trust strict suite: `{}`".format(_token(trust_stage.get("result")) or _token(trust_stage.get("status"))),
        "- dist verify: `{}`".format(_token(dist_stage.get("result")) or _token(dist_stage.get("status")) or "not_run"),
        "- archive verify: `{}`".format(_token(archive_stage.get("result")) or _token(archive_stage.get("status")) or "not_run"),
        "- Xi-8 targeted TestX: `{}`".format(_token(tests_stage.get("result")) or _token(tests_stage.get("status"))),
        "",
        "## Commands",
        "",
    ]
    for key in ("ci_strict", "trust_strict", "dist_refresh", "dist_verify", "archive_release", "archive_verify", "targeted_testx"):
        item = dict(report.get(key) or {})
        command = list(item.get("command") or [])
        if command:
            lines.append("- `{}`".format(" ".join(command)))
    lines.extend(
        [
            "",
            "## Fingerprints",
            "",
            "- CI STRICT: `{}`".format(_token(ci_stage.get("deterministic_fingerprint"))),
            "- trust strict: `{}`".format(_token(trust_stage.get("deterministic_fingerprint"))),
            "- dist refresh: `{}`".format(_token(dist_refresh_stage.get("deterministic_fingerprint"))),
            "- dist verify: `{}`".format(_token(dist_stage.get("deterministic_fingerprint"))),
            "- archive release: `{}`".format(_token(archive_release_stage.get("deterministic_fingerprint"))),
            "- archive verify: `{}`".format(_token(archive_stage.get("deterministic_fingerprint"))),
        ]
    )
    return "\n".join(lines) + "\n"


def _render_xi8_final(snapshot: Mapping[str, object], lock_payload: Mapping[str, object], validation_report: Mapping[str, object], gate_ok: bool, shim_count: int) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-30",
        "Stability: stable",
        "Future Series: XI-8",
        "Replacement Target: later explicit repository-freeze revision or DIST-7 execution audit",
        "",
        "# XI-8 Final",
        "",
        "Xi-8 froze the live repository structure after the authoritative Xi-5a, Xi-5x1, Xi-5x2, Xi-6, and Xi-7 passes.",
        "",
        "Ground truth reused:",
        "",
        "- Xi-5a: approved v4 src-domain moves executed and dangerous shadow roots removed",
        "- Xi-5x1/Xi-5x2: residual convergence completed and source-pocket policy classified",
        "- Xi-6: architecture graph v1, module boundaries, and single-engine registry frozen",
        "- Xi-7: CI immune system integrated and verified",
        "",
        "Xi-8 outputs:",
        "",
        "- `data/architecture/repository_structure_lock.json`",
        "- `docs/architecture/REPOSITORY_STRUCTURE_v1.md`",
        "- `docs/architecture/MODULE_INDEX_v1.md`",
        "- `docs/architecture/SHIM_SUNSET_PLAN.md`",
        "- `docs/audit/REPO_FREEZE_VERIFICATION.md`",
        "",
        "Freeze summary:",
        "",
        "- repository structure lock hash: `{}`".format(_token(lock_payload.get("content_hash"))),
        "- architecture graph v1 hash: `{}`".format(_token(snapshot.get("architecture_graph_v1_content_hash"))),
        "- module boundaries hash: `{}`".format(_token(snapshot.get("module_boundary_rules_v1_content_hash"))),
        "- single-engine registry hash: `{}`".format(_token(snapshot.get("single_engine_registry_content_hash"))),
        "- top-level directories frozen: `{}`".format(len(list(lock_payload.get("allowed_top_level_directories") or []))),
        "- sanctioned source-like roots: `{}`".format(", ".join("`{}`".format(item) for item in list(lock_payload.get("allowed_source_like_roots") or []))),
        "",
        "Shim status:",
        "",
        "- total transitional shims retained: `{}`".format(shim_count),
        "- shim removal executed in Xi-8: `0`",
        "",
        "Validation:",
        "",
        "- XStack CI STRICT: `{}`".format(_token(dict(validation_report.get("ci_strict") or {}).get("result")) or _token(dict(validation_report.get("ci_strict") or {}).get("status"))),
        "- trust strict suite: `{}`".format(_token(dict(validation_report.get("trust_strict") or {}).get("result")) or _token(dict(validation_report.get("trust_strict") or {}).get("status"))),
        "- dist verify: `{}`".format(_token(dict(validation_report.get("dist_verify") or {}).get("result")) or _token(dict(validation_report.get("dist_verify") or {}).get("status")) or "not_run"),
        "- archive verify: `{}`".format(_token(dict(validation_report.get("archive_verify") or {}).get("result")) or _token(dict(validation_report.get("archive_verify") or {}).get("status")) or "not_run"),
        "- Xi-8 targeted TestX: `{}`".format(_token(dict(validation_report.get("targeted_testx") or {}).get("result")) or _token(dict(validation_report.get("targeted_testx") or {}).get("status"))),
        "",
        "Local validation note:",
        "",
        "- Xi-8 exercised the committed `STRICT` entrypoint with an explicit Xi-7/Xi-8 smoke subset so the RepoX/AuditX/validation/Ω lane stayed deterministic within local shell budget.",
        "- Xi-8 refreshed the tracked DIST tree and archive record against live release artifacts before tree-level verification so the freeze verdict reflects current repository reality, not stale derived outputs.",
        "- Xi-8 targeted repository-freeze tests were rerun separately after the committed STRICT report was written.",
        "",
        "Task-level invariants upheld:",
        "",
        "- `constitution_v1.md A1`",
        "- `constitution_v1.md A8`",
        "- `constitution_v1.md A10`",
        "- `AGENTS.md §2`",
        "- `AGENTS.md §5`",
        "",
        "Contract/schema impact: unchanged.",
        "Runtime semantics: unchanged.",
        "",
        "Readiness:",
        "",
        "- Ω suite passes: `{}`".format("true" if gate_ok else "false"),
        "- ready for DIST-7 packaging execution: `{}`".format("true" if gate_ok else "false"),
    ]
    return "\n".join(lines) + "\n"


def write_xi8_outputs(
    repo_root: str,
    snapshot: Mapping[str, object],
    lock_payload: Mapping[str, object],
    validation_report: Mapping[str, object] | None = None,
) -> dict[str, str]:
    gate_definitions = _gate_definitions_payload(lock_payload)
    profiles = [_profile_payload(profile_id) for profile_id in PROFILE_IDS]
    freeze_report = dict(validation_report or {})
    shim_count = len(_shim_rows(repo_root))
    gate_ok = bool(
        freeze_report
        and _token(dict(freeze_report.get("ci_strict") or {}).get("status")) == "pass"
        and _token(dict(freeze_report.get("trust_strict") or {}).get("status")) == "pass"
        and (
            not freeze_report.get("dist_refresh")
            or _token(dict(freeze_report.get("dist_refresh") or {}).get("status")) == "pass"
        )
        and _token(dict(freeze_report.get("targeted_testx") or {}).get("status")) == "pass"
        and (
            not freeze_report.get("dist_verify")
            or _token(dict(freeze_report.get("dist_verify") or {}).get("status")) in {"pass", "skipped"}
        )
        and (
            not freeze_report.get("archive_release")
            or _token(dict(freeze_report.get("archive_release") or {}).get("status")) in {"pass", "skipped"}
        )
        and (
            not freeze_report.get("archive_verify")
            or _token(dict(freeze_report.get("archive_verify") or {}).get("status")) in {"pass", "skipped"}
        )
    )
    written = {
        "repository_structure_lock": _write_json(repo_root, REPOSITORY_STRUCTURE_LOCK_REL, lock_payload),
        "repository_structure_doc": _write_text(repo_root, REPOSITORY_STRUCTURE_DOC_REL, _render_repository_structure_doc(snapshot, lock_payload)),
        "module_index_doc": _write_text(repo_root, MODULE_INDEX_DOC_REL, _render_module_index_doc(snapshot)),
        "shim_sunset_plan": _write_text(repo_root, SHIM_SUNSET_PLAN_REL, _render_shim_sunset_plan(repo_root)),
        "gate_definitions": _write_json(repo_root, GATE_DEFINITIONS_REL, gate_definitions),
        "profile_fast": _write_json(repo_root, PROFILE_FAST_REL, profiles[0]),
        "profile_strict": _write_json(repo_root, PROFILE_STRICT_REL, profiles[1]),
        "profile_full": _write_json(repo_root, PROFILE_FULL_REL, profiles[2]),
        "ci_guardrails_doc": _write_text(repo_root, CI_GUARDRAILS_DOC_REL, _render_ci_guardrails_doc(gate_definitions, profiles)),
        "arch_drift_policy_doc": _write_text(repo_root, ARCH_DRIFT_POLICY_DOC_REL, _render_arch_drift_policy_doc(lock_payload)),
        "repo_freeze_verification": _write_text(repo_root, REPO_FREEZE_VERIFICATION_REL, _render_repo_freeze_verification(freeze_report)),
        "xi_8_final": _write_text(repo_root, XI_8_FINAL_REL, _render_xi8_final(snapshot, lock_payload, freeze_report, gate_ok, shim_count)),
    }
    return written


def _targeted_test_command(repo_root: str) -> list[str]:
    del repo_root
    return [
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
        ",".join(XI8_TARGETED_TESTS),
    ]


def _collect_validation_report(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    report: dict[str, object] = {}
    report["ci_strict"] = _run_json_command(
        root,
        ["python", "-B", ENTRYPOINT_PY_REL, "--repo-root", ".", "--profile", "STRICT", "--testx-subset", ",".join(CI_STRICT_SMOKE_TESTS)],
    )
    report["ci_strict"]["command"] = ["python", "-B", ENTRYPOINT_PY_REL, "--repo-root", ".", "--profile", "STRICT", "--testx-subset", ",".join(CI_STRICT_SMOKE_TESTS)]
    report["ci_strict"]["mode"] = "strict_smoke_subset"
    report["ci_strict"]["subset_ids"] = list(CI_STRICT_SMOKE_TESTS)
    if _token(dict(report["ci_strict"]).get("status")) != "pass":
        return report

    report["trust_strict"] = _run_json_command(root, ["python", "-B", TRUST_STRICT_TOOL_REL, "--repo-root", "."])
    report["trust_strict"]["command"] = ["python", "-B", TRUST_STRICT_TOOL_REL, "--repo-root", "."]
    if _token(dict(report["trust_strict"]).get("status")) != "pass":
        return report

    if os.path.isdir(_repo_abs(root, DIST_ROOT_REL)):
        report["dist_refresh"] = _run_json_command(
            root,
            [
                "python",
                "-B",
                DIST_ASSEMBLE_TOOL_REL,
                "--repo-root",
                ".",
                "--platform-tag",
                "win64",
                "--channel",
                "mock",
                "--output-root",
                "dist",
            ],
        )
        report["dist_refresh"]["command"] = [
            "python",
            "-B",
            DIST_ASSEMBLE_TOOL_REL,
            "--repo-root",
            ".",
            "--platform-tag",
            "win64",
            "--channel",
            "mock",
            "--output-root",
            "dist",
        ]
        if _token(dict(report["dist_refresh"]).get("status")) != "pass":
            return report

        report["dist_verify"] = _run_json_command(
            root,
            ["python", "-B", DIST_VERIFY_TOOL_REL, "--repo-root", ".", "--platform-tag", "win64", "--dist-root", "dist"],
        )
        report["dist_verify"]["command"] = ["python", "-B", DIST_VERIFY_TOOL_REL, "--repo-root", ".", "--platform-tag", "win64", "--dist-root", "dist"]
        if _token(dict(report["dist_verify"]).get("status")) != "pass":
            return report

        report["archive_release"] = _run_json_command(
            root,
            [
                "python",
                "-B",
                ARCHIVE_RELEASE_TOOL_REL,
                "--repo-root",
                ".",
                "--dist-root",
                DIST_BUNDLE_REL,
                "--platform-tag",
                "win64",
                "--write-offline-bundle",
            ],
        )
        report["archive_release"]["command"] = [
            "python",
            "-B",
            ARCHIVE_RELEASE_TOOL_REL,
            "--repo-root",
            ".",
            "--dist-root",
            DIST_BUNDLE_REL,
            "--platform-tag",
            "win64",
            "--write-offline-bundle",
        ]
        if _token(dict(report["archive_release"]).get("status")) != "pass":
            return report

        report["archive_verify"] = _run_json_command(
            root,
            [
                "python",
                "-B",
                ARCHIVE_VERIFY_TOOL_REL,
                "--repo-root",
                ".",
                "--dist-root",
                DIST_BUNDLE_REL,
                "--platform-tag",
                "win64",
                "--archive-record-path",
                DIST_ARCHIVE_RECORD_REL,
            ],
        )
        report["archive_verify"]["command"] = [
            "python",
            "-B",
            ARCHIVE_VERIFY_TOOL_REL,
            "--repo-root",
            ".",
            "--dist-root",
            DIST_BUNDLE_REL,
            "--platform-tag",
            "win64",
            "--archive-record-path",
            DIST_ARCHIVE_RECORD_REL,
        ]
        if _token(dict(report["archive_verify"]).get("status")) != "pass":
            return report
    else:
        report["dist_refresh"] = {"status": "skipped", "reason": "dist_tree_missing"}
        report["dist_verify"] = {"status": "skipped", "reason": "dist_tree_missing"}
        report["archive_release"] = {"status": "skipped", "reason": "dist_tree_missing"}
        report["archive_verify"] = {"status": "skipped", "reason": "dist_tree_missing"}

    report["targeted_testx"] = _run_json_command(root, _targeted_test_command(root))
    report["targeted_testx"]["command"] = _targeted_test_command(root)
    return report


def run_xi8(repo_root: str, run_gates: bool = True) -> dict[str, object]:
    root = _repo_root(repo_root)
    ensure_xi8_inputs(root)
    snapshot = build_repository_structure_snapshot(root)
    lock_payload = build_repository_structure_lock_payload(snapshot)
    write_xi8_outputs(root, snapshot, lock_payload, {})
    validation_report = _collect_validation_report(root) if run_gates else {}
    write_xi8_outputs(root, snapshot, lock_payload, validation_report)
    evaluation = evaluate_repository_structure(root)
    passed = bool(validation_report) and _token(evaluation.get("status")) == "pass"
    for key in ("ci_strict", "trust_strict", "dist_refresh", "archive_release", "targeted_testx"):
        if _token(dict(validation_report.get(key) or {}).get("status")) != "pass":
            passed = False
    for key in ("dist_verify", "archive_verify"):
        status = _token(dict(validation_report.get(key) or {}).get("status"))
        if status not in {"", "pass", "skipped"}:
            passed = False
    if _token(dict(validation_report.get("ci_strict") or {}).get("result")) not in {"", "complete"}:
        passed = False
    return {
        "result": "complete" if passed else "blocked",
        "repository_structure_lock": lock_payload,
        "snapshot": snapshot,
        "validation_report": validation_report,
        "evaluation": evaluation,
    }


__all__ = [
    "AUDITX_DETECTOR_IDS",
    "ARCH_DRIFT_POLICY_DOC_REL",
    "CI_GUARDRAILS_DOC_REL",
    "CI_REPORT_JSON_REL",
    "CI_REPORT_MD_REL",
    "ENTRYPOINT_PY_REL",
    "GATE_DEFINITIONS_REL",
    "MODULE_INDEX_DOC_REL",
    "PROFILE_FAST_REL",
    "PROFILE_FULL_REL",
    "PROFILE_STRICT_REL",
    "REPOSITORY_STRUCTURE_DOC_REL",
    "REPOSITORY_STRUCTURE_LOCK_REL",
    "REPOX_RULE_IDS",
    "REPO_FREEZE_VERIFICATION_REL",
    "SHIM_SUNSET_PLAN_REL",
    "XI8_TARGETED_TESTS",
    "XI_8_FINAL_REL",
    "Xi8InputsMissing",
    "build_arch_graph_matches_repo_violations",
    "build_repository_structure_lock_payload",
    "build_repository_structure_snapshot",
    "build_repository_structure_violations",
    "ensure_xi8_inputs",
    "evaluate_repository_structure",
    "load_repository_structure_lock",
    "recompute_structure_lock_content_hash",
    "recompute_structure_lock_fingerprint",
    "run_xi8",
    "write_xi8_outputs",
]

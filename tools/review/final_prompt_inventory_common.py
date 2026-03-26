"""Deterministic PI-2 prompt inventory and snapshot-mapping helpers."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict, deque
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


SERIES_EXECUTION_STRATEGY_REL = "data/blueprint/series_execution_strategy.json"
FOUNDATION_PHASES_REL = "data/blueprint/foundation_phases.json"
STOP_CONDITIONS_REL = "data/blueprint/stop_conditions.json"
SERIES_DEP_GRAPH_REL = "data/blueprint/series_dependency_graph.json"

FINAL_PROMPT_INVENTORY_REL = "data/blueprint/final_prompt_inventory.json"
SNAPSHOT_MAPPING_TEMPLATE_REL = "data/blueprint/snapshot_mapping_template.json"
PROMPT_DEPENDENCY_TREE_REL = "data/blueprint/prompt_dependency_tree.json"
PROMPT_RISK_MATRIX_REL = "data/blueprint/prompt_risk_matrix.json"
RECONCILIATION_RULES_REL = "data/blueprint/repo_reality_reconciliation_rules.json"

FINAL_PROMPT_INVENTORY_DOC_REL = "docs/blueprint/FINAL_PROMPT_INVENTORY.md"
SNAPSHOT_MAPPING_TEMPLATE_DOC_REL = "docs/blueprint/SNAPSHOT_MAPPING_TEMPLATE.md"
PROMPT_EXECUTION_CHECKLIST_DOC_REL = "docs/blueprint/PROMPT_EXECUTION_CHECKLIST.md"
PROMPT_DEPENDENCY_TREE_DOC_REL = "docs/blueprint/PROMPT_DEPENDENCY_TREE.md"
PROMPT_RISK_MATRIX_DOC_REL = "docs/blueprint/PROMPT_RISK_MATRIX.md"
RECONCILIATION_GUIDE_DOC_REL = "docs/blueprint/REPO_REALITY_RECONCILIATION_GUIDE.md"
PI_2_FINAL_REL = "docs/audit/PI_2_FINAL.md"

OUTPUT_REL_PATHS = {
    FINAL_PROMPT_INVENTORY_REL,
    SNAPSHOT_MAPPING_TEMPLATE_REL,
    PROMPT_DEPENDENCY_TREE_REL,
    PROMPT_RISK_MATRIX_REL,
    RECONCILIATION_RULES_REL,
    FINAL_PROMPT_INVENTORY_DOC_REL,
    SNAPSHOT_MAPPING_TEMPLATE_DOC_REL,
    PROMPT_EXECUTION_CHECKLIST_DOC_REL,
    PROMPT_DEPENDENCY_TREE_DOC_REL,
    PROMPT_RISK_MATRIX_DOC_REL,
    RECONCILIATION_GUIDE_DOC_REL,
    PI_2_FINAL_REL,
}

REQUIRED_INPUTS = {
    "foundation_phases": FOUNDATION_PHASES_REL,
    "series_dependency_graph": SERIES_DEP_GRAPH_REL,
    "series_execution_strategy": SERIES_EXECUTION_STRATEGY_REL,
    "stop_conditions": STOP_CONDITIONS_REL,
}

DOC_REPORT_DATE = "2026-03-26"
SERIES_KEY_ORDER = {"SIGMA": 0, "PHI": 1, "UPSILON": 2, "ZETA": 3}
SERIES_GLYPH = {"SIGMA": "Σ", "PHI": "Φ", "UPSILON": "Υ", "ZETA": "Ζ"}
SERIES_NAME = {
    "SIGMA": "Human / Agent Interface & Governance",
    "PHI": "Runtime Componentization & Service Kernel",
    "UPSILON": "Build, Release, Distribution, Control Plane",
    "ZETA": "Live Runtime Operations & Extreme Replaceability",
}
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "extreme": 3}
GATE_ORDER = {"FAST": 0, "STRICT": 1, "FULL": 2}
EXECUTION_CLASS_ORDER = {
    "docs_only": 0,
    "schema_registry": 1,
    "tooling": 2,
    "implementation": 3,
    "refactor": 4,
    "operations": 5,
}
SNAPSHOT_ORDER = {"pre_snapshot_safe": 0, "post_snapshot_required": 1}
FOUNDATION_NODE_IDS = ("XI-8", "OMEGA-FREEZE", "SNAPSHOT-MAP")


class PiInputMissingError(RuntimeError):
    """Raised when required PI inputs are missing."""

    def __init__(self, missing_paths: Sequence[str]):
        super().__init__("missing PI inputs")
        self.missing_paths = sorted({_norm_rel(path) for path in missing_paths if _token(path)})
        self.refusal_code = "refusal.pi.missing_inputs"


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


def _doc_header(title: str, replacement_target: str) -> str:
    return "\n".join(
        [
            "Status: DERIVED",
            f"Last Reviewed: {DOC_REPORT_DATE}",
            "Supersedes: none",
            "Superseded By: none",
            "Stability: provisional",
            "Future Series: PI",
            f"Replacement Target: {replacement_target}",
            "",
            f"# {title}",
            "",
        ]
    )


def _required_inputs(repo_root: str) -> dict[str, dict]:
    root = _repo_root(repo_root)
    payloads: dict[str, dict] = {}
    missing = []
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
    if missing:
        raise PiInputMissingError(missing)
    return payloads


def _prompt_number(prompt_id: str) -> int:
    try:
        return int(_token(prompt_id).split("-", 1)[1])
    except (IndexError, ValueError):
        return 999


def _series_from_prompt_id(prompt_id: str) -> str:
    return {"Σ": "SIGMA", "Φ": "PHI", "Υ": "UPSILON", "Ζ": "ZETA"}.get(_token(prompt_id)[:1], "")


def _prompt_sort_key(prompt_id: str) -> tuple[int, int, str]:
    series_key = _series_from_prompt_id(prompt_id)
    return (SERIES_KEY_ORDER.get(series_key, 99), _prompt_number(prompt_id), _token(prompt_id))


def _fingerprinted(payload: Mapping[str, object]) -> dict[str, object]:
    row = dict(payload)
    row["deterministic_fingerprint"] = canonical_sha256(row)
    return row


def _make_prompt_seed(
    series_key: str,
    number: int,
    title: str,
    short_goal: str,
    execution_class: str,
    snapshot_requirement: str,
    risk_level: str,
    gate_profile_required: str,
    rollback_strategy_required: bool,
    manual_review_required: bool,
    category: str,
    family: str,
    prerequisites: Sequence[str],
) -> dict[str, object]:
    prompt_id = f"{SERIES_GLYPH[series_key]}-{number}"
    return {
        "category": category,
        "execution_class": execution_class,
        "family": family,
        "gate_profile_required": gate_profile_required,
        "manual_review_required": bool(manual_review_required),
        "prerequisites": sorted({_token(item) for item in prerequisites if _token(item)}, key=lambda item: (_prompt_sort_key(item) if _series_from_prompt_id(item) else (98, 0, item))),
        "prompt_id": prompt_id,
        "risk_level": risk_level,
        "rollback_strategy_required": bool(rollback_strategy_required),
        "series_id": SERIES_GLYPH[series_key],
        "series_key": series_key,
        "short_goal": short_goal,
        "snapshot_requirement": snapshot_requirement,
        "title": title,
    }


SIGMA_PROMPT_SEEDS = [
    _make_prompt_seed("SIGMA", 0, "AGENT-GOVERNANCE-0", "Freeze the human and agent governance contract, authority boundaries, and review doctrine.", "docs_only", "pre_snapshot_safe", "low", "FAST", False, True, "governance", "foundation", ["XI-8", "OMEGA-FREEZE"]),
    _make_prompt_seed("SIGMA", 1, "AGENT-MIRRORS-0", "Define mirrored human and agent surfaces so every governed action has an inspectable counterpart.", "docs_only", "pre_snapshot_safe", "low", "FAST", False, False, "governance", "foundation", ["Σ-0"]),
    _make_prompt_seed("SIGMA", 2, "NATURAL-LANGUAGE-TASK-BRIDGE-0", "Bind natural-language intent to deterministic task classes, validation levels, and refusals.", "schema_registry", "pre_snapshot_safe", "medium", "STRICT", False, True, "governance", "foundation", ["Σ-0", "Σ-1"]),
    _make_prompt_seed("SIGMA", 3, "XSTACK-TASK-CATALOG-0", "Publish the canonical XStack task catalog that future humans and agents must target.", "schema_registry", "pre_snapshot_safe", "medium", "STRICT", False, False, "governance", "foundation", ["Σ-2"]),
    _make_prompt_seed("SIGMA", 4, "MCP-INTERFACE-0", "Define the governed MCP interface surface for prompt execution, inspection, and refusal handling.", "tooling", "pre_snapshot_safe", "medium", "STRICT", False, True, "interfaces", "foundation", ["Σ-3"]),
    _make_prompt_seed("SIGMA", 5, "AGENT-SAFETY-POLICY-0", "Lock safety policy, manual review gates, and escalation rules for future automation.", "schema_registry", "pre_snapshot_safe", "medium", "STRICT", False, True, "governance", "foundation", ["Σ-0", "Σ-2", "Σ-4"]),
    _make_prompt_seed("SIGMA", 6, "AGENT-PERFORMANCE-0", "Measure and tune governed agent throughput only after the live repository snapshot is mapped to real workflows.", "tooling", "post_snapshot_required", "medium", "STRICT", False, False, "operations", "optimization", ["Σ-3", "Σ-4", "Σ-5", "SNAPSHOT-MAP"]),
]


PHI_PROMPT_SEEDS = [
    _make_prompt_seed("PHI", 0, "RUNTIME-KERNEL-MODEL-0", "Define the deterministic runtime kernel doctrine, service boundaries, and lawful state movement.", "docs_only", "pre_snapshot_safe", "medium", "STRICT", False, True, "kernel", "foundation", ["XI-8", "OMEGA-FREEZE"]),
    _make_prompt_seed("PHI", 1, "COMPONENT-MODEL-0", "Define the component contract, ownership boundaries, and lifecycle vocabulary for runtime services.", "docs_only", "pre_snapshot_safe", "medium", "STRICT", False, True, "kernel", "foundation", ["Φ-0"]),
    _make_prompt_seed("PHI", 2, "MODULE-LOADER-0", "Insert a governed, capability-negotiated module loader into the live runtime after snapshot mapping.", "implementation", "post_snapshot_required", "high", "STRICT", True, True, "loading", "runtime", ["Φ-1", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 3, "RUNTIME-SERVICES-0", "Separate runtime services from the kernel without violating process-only mutation.", "implementation", "post_snapshot_required", "high", "STRICT", True, True, "services", "runtime", ["Φ-1", "Φ-2", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 4, "STATE-EXTERNALIZATION-0", "Define export/import, ownership, and replay-safe state movement before live cutovers.", "schema_registry", "pre_snapshot_safe", "high", "STRICT", True, True, "state", "foundation", ["Φ-0", "Φ-1"]),
    _make_prompt_seed("PHI", 5, "LIFECYCLE-MANAGER-0", "Implement governed startup, shutdown, handoff, and rollback choreography for runtime services.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "services", "runtime", ["Φ-3", "Φ-4", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 6, "FRAMEGRAPH-0", "Introduce a framegraph-style render plan layer that separates render intent from backend execution.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "rendering", "replaceability", ["Φ-1", "Φ-3", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 7, "RENDER-DEVICE-0", "Define the render device abstraction required for backend swap, validation renderers, and mirrored execution.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "rendering", "replaceability", ["Φ-1", "Φ-6", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 8, "HOTSWAP-BOUNDARIES-0", "Freeze lawful replacement boundaries, state handoff points, and rollback obligations for hot-replaceable services.", "schema_registry", "post_snapshot_required", "high", "FULL", True, True, "replaceability", "replaceability", ["Φ-5", "Φ-6", "Φ-7", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 9, "ASSET-PIPELINE-0", "Build the governed asset and shader pipeline that live mount, streaming, and validation features depend on.", "implementation", "post_snapshot_required", "high", "STRICT", True, False, "assets", "runtime", ["Φ-1", "Φ-6", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 10, "SANDBOXING-0", "Add governed sandboxing and isolation boundaries for untrusted runtime extensions and mods.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "security", "runtime", ["Φ-1", "Φ-2", "Φ-3", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 11, "MULTI-VERSION-COEXISTENCE-0", "Define how multiple runtime, protocol, and module versions coexist during controlled migration windows.", "schema_registry", "pre_snapshot_safe", "high", "STRICT", True, True, "compatibility", "foundation", ["Φ-1", "Φ-4"]),
    _make_prompt_seed("PHI", 12, "EVENT-LOG-0", "Create the deterministic event-log substrate required for replay, cutover, and distributed execution.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "state", "distributed", ["Φ-4", "Φ-5", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 13, "SNAPSHOT-SERVICE-0", "Create the snapshot service and handoff format required for save migration, rollback, and distributed recovery.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "state", "distributed", ["Φ-4", "Φ-5", "Φ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("PHI", 14, "DISTRIBUTED-AUTHORITY-0", "Define the lawful distributed authority model, handoff semantics, and proof obligations.", "schema_registry", "post_snapshot_required", "extreme", "FULL", True, True, "distributed", "distributed", ["Φ-11", "Φ-12", "Φ-13", "Σ-5", "SNAPSHOT-MAP"]),
]


UPSILON_PROMPT_SEEDS = [
    _make_prompt_seed("UPSILON", 0, "BUILD-GRAPH-LOCK-0", "Lock the live build graph after snapshot mapping so future tooling runs against a stable substrate.", "tooling", "post_snapshot_required", "medium", "STRICT", True, True, "build", "foundation", ["XI-8", "OMEGA-FREEZE", "SNAPSHOT-MAP"]),
    _make_prompt_seed("UPSILON", 1, "PRESET-CONSOLIDATION-0", "Consolidate presets and toolchains against the actual live repository layout.", "refactor", "post_snapshot_required", "medium", "STRICT", True, False, "build", "foundation", ["Υ-0", "SNAPSHOT-MAP"]),
    _make_prompt_seed("UPSILON", 2, "VERSIONING-POLICY-0", "Freeze versioning, migration, and compatibility discipline for the post-XI control plane.", "docs_only", "pre_snapshot_safe", "medium", "STRICT", False, True, "policy", "foundation", ["XI-8", "OMEGA-FREEZE"]),
    _make_prompt_seed("UPSILON", 3, "RELEASE-INDEX-POLICY-1", "Refine release index policy, publication semantics, and rollback lineage before pipeline work.", "docs_only", "pre_snapshot_safe", "medium", "STRICT", False, False, "policy", "foundation", ["Υ-2"]),
    _make_prompt_seed("UPSILON", 4, "MANUAL-AUTOMATION-PARITY-0", "Map manual operator workflows to automation steps so every automated release action has a human mirror.", "tooling", "post_snapshot_required", "medium", "STRICT", True, False, "operations", "foundation", ["Σ-3", "Υ-0", "SNAPSHOT-MAP"]),
    _make_prompt_seed("UPSILON", 5, "BUILD-REPRO-MATRIX-0", "Establish the reproducibility matrix for supported toolchains, profiles, and artifact classes.", "tooling", "post_snapshot_required", "high", "STRICT", True, False, "build", "foundation", ["Υ-0", "Υ-1", "SNAPSHOT-MAP"]),
    _make_prompt_seed("UPSILON", 6, "RELEASE-PIPELINE-0", "Build the deterministic release pipeline once the live toolchain graph and parity map are known.", "implementation", "post_snapshot_required", "high", "STRICT", True, True, "release", "runtime", ["Υ-3", "Υ-4", "Υ-5", "SNAPSHOT-MAP"]),
    _make_prompt_seed("UPSILON", 7, "ARCHIVE-MIRROR-0", "Build the governed archive mirror workflow and offline bundle publication path.", "implementation", "post_snapshot_required", "medium", "STRICT", True, False, "release", "runtime", ["Υ-3", "Υ-6", "SNAPSHOT-MAP"]),
    _make_prompt_seed("UPSILON", 8, "PUBLICATION-MODELS-0", "Define publication models, promotion paths, and compatibility classes for release distribution.", "docs_only", "pre_snapshot_safe", "medium", "STRICT", False, False, "policy", "foundation", ["Υ-2", "Υ-3"]),
    _make_prompt_seed("UPSILON", 9, "LICENSE-CAPABILITY-0", "Define how license, entitlement, and capability policy constrain distribution and operator workflows.", "schema_registry", "pre_snapshot_safe", "high", "STRICT", False, True, "policy", "foundation", ["Υ-8"]),
    _make_prompt_seed("UPSILON", 10, "RELEASE-OPS-0", "Create the governed release-operations controller and operator workflow surface.", "operations", "post_snapshot_required", "high", "FULL", True, True, "operations", "runtime", ["Σ-5", "Υ-6", "Υ-7", "Υ-8", "Υ-11", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("UPSILON", 11, "DISASTER-DOWNGRADE-POLICY-0", "Lock downgrade, yank, and degraded-survival policy before live cutovers or automated rollback.", "schema_registry", "pre_snapshot_safe", "high", "STRICT", True, True, "policy", "foundation", ["OMEGA-FREEZE", "Υ-2", "Υ-12"]),
    _make_prompt_seed("UPSILON", 12, "OPERATOR-TRANSACTION-LOG-0", "Define the operator transaction log and explainable action ledger for cutovers, rollback, and rehearsal.", "schema_registry", "pre_snapshot_safe", "high", "STRICT", True, True, "operations", "foundation", ["Σ-0", "Σ-3", "Υ-2"]),
]


ZETA_PROMPT_SEEDS = [
    _make_prompt_seed("ZETA", 0, "HOTSWAP-RENDERERS-0", "Make renderers hot-swappable only after render boundaries, lifecycle control, and transaction logging are frozen.", "operations", "post_snapshot_required", "high", "FULL", True, True, "replaceability", "replaceability", ["Φ-5", "Φ-6", "Φ-7", "Φ-8", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 1, "SERVICE-RESTARTS-0", "Enable governed service restarts with rollback and replay-safe recovery.", "operations", "post_snapshot_required", "high", "FULL", True, True, "replaceability", "replaceability", ["Φ-3", "Φ-5", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 2, "PARTIAL-MODULE-RELOAD-0", "Support partial module reload only within frozen ABI, lifecycle, and rollback boundaries.", "operations", "post_snapshot_required", "high", "FULL", True, True, "replaceability", "replaceability", ["Φ-2", "Φ-5", "Φ-8", "Φ-11", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 3, "BACKEND-SWAP-AUDIO-INPUT-STORAGE-NET-0", "Allow backend swap for non-render services only after service boundaries and transaction logging are governed.", "operations", "post_snapshot_required", "high", "FULL", True, True, "replaceability", "replaceability", ["Φ-3", "Φ-5", "Φ-8", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 4, "LIVE-UI-SHELL-REPLACEMENT-0", "Allow shell replacement without bypassing authority, law, or rollback discipline.", "operations", "post_snapshot_required", "high", "FULL", True, True, "replaceability", "replaceability", ["Σ-2", "Φ-5", "Φ-8", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 5, "LIVE-SAVE-MIGRATION-0", "Perform live save migration with snapshot safety, rollback, and baseline verification discipline.", "operations", "post_snapshot_required", "high", "FULL", True, True, "state_migration", "state", ["OMEGA-FREEZE", "Φ-4", "Φ-13", "Υ-11", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 6, "LIVE-STATE-SCHEMA-EVOLUTION-0", "Evolve runtime state schemas live only after save migration, coexistence, and manual review gates are satisfied.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "state_migration", "state", ["Σ-5", "Φ-11", "Ζ-5", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 7, "NONBLOCKING-SAVES-0", "Enable non-blocking save capture using lifecycle control and snapshot service boundaries.", "operations", "post_snapshot_required", "high", "FULL", True, True, "state_migration", "state", ["Φ-4", "Φ-5", "Φ-13", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 8, "PARTIAL-WORLD-RESTORE-0", "Restore selected world slices without violating snapshot isolation or replay equivalence.", "operations", "post_snapshot_required", "high", "FULL", True, True, "state_migration", "state", ["Ζ-5", "Ζ-7", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 9, "FORKABLE-SAVES-AND-BRANCHABLE-UNIVERSES-0", "Allow governed save forks and branchable universe lines without breaking provenance.", "operations", "post_snapshot_required", "high", "FULL", True, True, "state_migration", "state", ["Φ-13", "Υ-12", "Ζ-7", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 10, "CANARY-RELEASES-0", "Run canary releases with explicit exposure policy, rollback receipts, and operator signoff.", "operations", "post_snapshot_required", "high", "FULL", True, True, "rollout", "operations", ["Σ-5", "Υ-10", "Υ-11", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 11, "INCREMENTAL-CUTOVERS-0", "Perform cutovers incrementally with explainable checkpoints and reversible steps.", "operations", "post_snapshot_required", "high", "FULL", True, True, "rollout", "operations", ["Ζ-10", "Φ-5", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 12, "SAFE-MODE-DEGRADED-BOOT-0", "Operationalize safe-mode degraded boot as a governed release and recovery path.", "operations", "post_snapshot_required", "medium", "STRICT", True, True, "rollout", "operations", ["OMEGA-FREEZE", "Σ-5", "Υ-11", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 13, "OPERATOR-REVERSIBLE-RELEASES-0", "Require every operator-driven release to carry a governed reversal path before promotion.", "operations", "post_snapshot_required", "high", "FULL", True, True, "rollout", "operations", ["Ζ-10", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 14, "EXPLAINABLE-UPGRADE-PLANS-0", "Emit explainable upgrade plans instead of imperative black-box rollout scripts.", "tooling", "post_snapshot_required", "medium", "STRICT", True, False, "rollout", "operations", ["Σ-2", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 15, "DETERMINISTIC-OPERATOR-PLAYBOOKS-0", "Build deterministic operator playbooks that map directly onto XStack validations and rollback hooks.", "tooling", "post_snapshot_required", "medium", "STRICT", True, False, "rollout", "operations", ["Σ-3", "Ζ-14", "Υ-10", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 16, "LIVE-TRUST-ROOT-ROTATION-0", "Rotate trust roots live without creating unverifiable upgrade windows.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "trust_security", "security", ["OMEGA-FREEZE", "Σ-5", "Υ-10", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 17, "LIVE-REVOCATION-PROPAGATION-0", "Propagate trust and capability revocations live with deterministic client and operator responses.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "trust_security", "security", ["Σ-5", "Ζ-16", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 18, "RUNTIME-SIGNATURE-POLICY-0", "Enforce runtime signature policy for replaceable services, live content, and release operations.", "schema_registry", "post_snapshot_required", "high", "STRICT", True, True, "trust_security", "security", ["Σ-5", "Υ-9", "Υ-10", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 19, "LIVE-PRIVILEGE-ESCALATION-REVOCATION-0", "Control live privilege escalation and revocation without bypassing law-gated authority.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "trust_security", "security", ["Σ-5", "Ζ-17", "Ζ-18", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 20, "UNTRUSTED-MOD-ISOLATION-0", "Isolate untrusted mods behind sandbox, signature, and capability policy boundaries.", "implementation", "post_snapshot_required", "extreme", "FULL", True, True, "trust_security", "security", ["Σ-5", "Φ-2", "Φ-10", "Υ-9", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 21, "ATTESTED-SERVICE-REPLACEMENT-0", "Require attested service replacement so cutovers can be proven, reviewed, and rolled back.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "trust_security", "security", ["Σ-5", "Ζ-1", "Ζ-18", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 22, "SEALED-EXECUTION-PROFILES-0", "Create sealed execution profiles that constrain live operations to reviewed and signed capability sets.", "schema_registry", "post_snapshot_required", "high", "FULL", True, True, "trust_security", "security", ["Σ-5", "Υ-9", "Ζ-18", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 23, "TWO-PERSON-APPROVAL-WORKFLOWS-0", "Require dual approval for the highest-risk live operations and trust changes.", "schema_registry", "post_snapshot_required", "medium", "STRICT", True, True, "trust_security", "security", ["Σ-5", "Υ-10", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 24, "LIVE-TOPOLOGY-VISUALIZATION-0", "Visualize the live service and dependency topology for operators and reviewers.", "tooling", "post_snapshot_required", "medium", "STRICT", False, False, "observability", "operations", ["Φ-3", "Σ-1", "Υ-10", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 25, "SERVICE-DEPENDENCY-GRAPH-INSPECTION-0", "Inspect service dependency graphs live so cutovers and failures remain explainable.", "tooling", "post_snapshot_required", "medium", "STRICT", False, False, "observability", "operations", ["Ζ-24", "Φ-3", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 26, "CUTOVER-PLAN-VISUALIZATION-0", "Visualize cutover plans and rollback branches before operator approval.", "tooling", "post_snapshot_required", "medium", "STRICT", False, False, "observability", "operations", ["Ζ-14", "Ζ-24", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 27, "CONTINUOUS-INVARIANT-MONITOR-0", "Continuously watch the non-negotiable invariants that live operations must never violate.", "tooling", "post_snapshot_required", "high", "STRICT", True, True, "observability", "operations", ["OMEGA-FREEZE", "Σ-3", "Υ-10", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 28, "RUNTIME-DRIFT-DETECTION-0", "Detect runtime drift against the frozen architecture and baseline expectations.", "tooling", "post_snapshot_required", "high", "STRICT", True, True, "observability", "operations", ["Ζ-27", "Υ-0", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 29, "PROOF-ANCHOR-HEALTH-MONITOR-0", "Monitor proof-anchor health and cutover viability during live operations.", "tooling", "post_snapshot_required", "high", "STRICT", True, True, "observability", "operations", ["Ζ-27", "Φ-12", "Φ-13", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 30, "TRACE-AND-REPLAY-PAIRING-0", "Pair live traces with deterministic replay verification so operator action remains explainable.", "tooling", "post_snapshot_required", "high", "STRICT", True, False, "observability", "operations", ["OMEGA-FREEZE", "Φ-12", "Υ-12", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 31, "HUMAN-AND-MACHINE-HEALTH-SURFACES-0", "Surface runtime health in forms both humans and agents can inspect without ambiguity.", "tooling", "post_snapshot_required", "medium", "STRICT", False, False, "observability", "operations", ["Σ-1", "Ζ-24", "Ζ-27", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 32, "POLICY-DRIVEN-AUTO-REMEDIATION-0", "Allow bounded auto-remediation only where policy, rollback, and review thresholds are explicit.", "operations", "post_snapshot_required", "high", "FULL", True, True, "observability", "operations", ["Σ-5", "Υ-10", "Ζ-27", "Ζ-28", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 33, "MIRRORED-RENDER-EXECUTION-0", "Run mirrored render execution so backend changes can be validated side-by-side before promotion.", "operations", "post_snapshot_required", "high", "FULL", True, True, "render_sidecars", "rendering", ["Ζ-0", "Φ-6", "Φ-7", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 34, "OFFSCREEN-VALIDATION-RENDERER-0", "Run an offscreen validation renderer to verify frame correctness without driving the live shell.", "implementation", "post_snapshot_required", "high", "FULL", True, False, "render_sidecars", "rendering", ["Φ-6", "Φ-7", "Φ-9", "Υ-5", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 35, "DEBUG-RENDERER-SIDECAR-0", "Attach a debug renderer sidecar without mutating truth or breaking replay equivalence.", "operations", "post_snapshot_required", "high", "FULL", True, True, "render_sidecars", "rendering", ["Σ-1", "Ζ-33", "Ζ-34", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 36, "HEADLESS-VISIBLE-COEXECUTION-0", "Run headless and visible render paths together to compare results before cutover.", "operations", "post_snapshot_required", "high", "FULL", True, False, "render_sidecars", "rendering", ["Ζ-33", "Ζ-34", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 37, "LIVE-FRAMEGRAPH-MIGRATION-0", "Migrate framegraph plans live only within frozen replacement and rollback boundaries.", "operations", "post_snapshot_required", "high", "FULL", True, True, "render_sidecars", "rendering", ["Ζ-0", "Ζ-33", "Φ-6", "Φ-8", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 38, "GPU-RESOURCE-REBINDING-0", "Rebind GPU resources during cutover without breaking render state guarantees or rollback plans.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "render_sidecars", "rendering", ["Ζ-0", "Ζ-37", "Φ-7", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 39, "RENDERER-STATE-CHECKPOINTING-0", "Checkpoint renderer state so backend cutovers and validation reruns can be replayed safely.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "render_sidecars", "rendering", ["Ζ-37", "Φ-13", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 40, "LIVE-SHADER-BACKEND-SWITCH-0", "Switch shader backends live only after the asset and render device surfaces are frozen.", "operations", "post_snapshot_required", "high", "FULL", True, True, "render_sidecars", "rendering", ["Ζ-0", "Φ-7", "Φ-9", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 41, "VIRTUAL-DISPLAY-TARGETS-0", "Create virtual display targets for validation, remote execution, and rehearsal.", "implementation", "post_snapshot_required", "medium", "STRICT", True, False, "render_sidecars", "rendering", ["Φ-7", "Φ-9", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 42, "REMOTE-RENDER-SERVICE-0", "Externalize rendering as a remote service only after render isolation and rollback controls are proven.", "operations", "post_snapshot_required", "high", "FULL", True, True, "render_sidecars", "rendering", ["Φ-3", "Φ-7", "Υ-10", "Ζ-33", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 43, "TIERED-RENDER-DEGRADATION-0", "Degrade rendering tiers explicitly under operator policy instead of silently diverging.", "operations", "post_snapshot_required", "medium", "STRICT", True, False, "render_sidecars", "rendering", ["Υ-11", "Ζ-34", "Ζ-42", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 44, "LIVE-PACK-MOUNT-UNMOUNT-0", "Mount and unmount packs live only through governed compatibility, rollback, and quarantine flows.", "operations", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Σ-5", "Φ-2", "Φ-11", "Υ-10", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 45, "LIVE-MOD-ACTIVATION-0", "Activate mods live only after isolation, capability, and rollback controls are present.", "operations", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Φ-10", "Υ-9", "Ζ-44", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 46, "MOD-QUARANTINE-AND-ROLLBACK-0", "Quarantine and roll back faulty mods without rebuilding the rest of the runtime from scratch.", "operations", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Υ-11", "Υ-12", "Ζ-45", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 47, "CONTENT-NAMESPACE-REBINDING-0", "Rebind content namespaces live while preserving pack identity and deterministic resolution order.", "operations", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Φ-11", "Ζ-44", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 48, "LIVE-ASSET-STREAMING-0", "Stream assets live only after asset pipeline, lifecycle, and pack mount boundaries are frozen.", "operations", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Φ-5", "Φ-9", "Ζ-44", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 49, "LIVE-LOGIC-RECOMPILATION-0", "Recompile live logic only through module loader, coexistence, and rollback-safe cutover surfaces.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "content_ops", "content", ["Φ-2", "Φ-11", "Ζ-45", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 50, "COMPATIBILITY-SCORED-MOD-INSERTION-0", "Score mods for live insertion against compatibility, policy, and rollback readiness.", "tooling", "post_snapshot_required", "high", "STRICT", True, True, "content_ops", "content", ["Σ-5", "Υ-10", "Ζ-44", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 51, "SIGNED-CAPABILITY-MODS-0", "Require signed capability-bearing mods before live activation or privileged content operations.", "schema_registry", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Υ-9", "Ζ-18", "Ζ-45", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 52, "MOD-ABI-LAYERS-0", "Create ABI compatibility layers so controlled mod version overlap can exist without blind breakage.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Φ-2", "Φ-11", "Ζ-45", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 53, "HOT-PATCH-NONCORE-DATA-0", "Allow hot patching of non-core data only through governed staging and rollback flows.", "operations", "post_snapshot_required", "medium", "STRICT", True, False, "content_ops", "content", ["Υ-10", "Ζ-44", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 54, "MOD-STAGING-BEFORE-ACTIVATION-0", "Stage mods before activation so compatibility, signatures, and rollback checks complete first.", "tooling", "post_snapshot_required", "medium", "STRICT", True, False, "content_ops", "content", ["Υ-10", "Ζ-44", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 55, "CANARY-MOD-DEPLOYMENT-0", "Roll mods out through canary cohorts before broad activation.", "operations", "post_snapshot_required", "high", "FULL", True, True, "content_ops", "content", ["Ζ-10", "Ζ-50", "Ζ-54", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 56, "PER-INSTANCE-MOD-GRAPHS-0", "Maintain per-instance mod graphs so live content choices remain explicit and auditable.", "implementation", "post_snapshot_required", "high", "STRICT", True, False, "content_ops", "content", ["Φ-11", "Υ-12", "Ζ-45", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 57, "DETERMINISTIC-REPLICATED-SIM-0", "Replicate simulation deterministically only after event logs, snapshots, authority, and operator controls are frozen.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["OMEGA-FREEZE", "Φ-12", "Φ-13", "Φ-14", "Υ-12", "Ζ-27", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 58, "AUTHORITY-HANDOFF-WITHOUT-DISCONNECT-0", "Hand authority off live without disconnects only after replicated simulation and authority proofs exist.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Ζ-24", "Ζ-57", "Φ-14", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 59, "SHARD-RELOCATION-0", "Relocate shards only after replication, authority handoff, and snapshot transfer are proven.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Ζ-57", "Ζ-58", "Φ-13", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 60, "EVENT-TAIL-SYNCHRONIZATION-0", "Synchronize event tails deterministically so replica catch-up and replay remain lawful.", "implementation", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Φ-12", "Φ-13", "Ζ-57", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 61, "INTEREST-MANAGEMENT-0", "Govern distributed interest management without changing authoritative truth outcomes.", "implementation", "post_snapshot_required", "high", "FULL", True, True, "distributed_runtime", "distributed", ["Φ-3", "Ζ-57", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 62, "MULTI-SITE-FAILOVER-0", "Fail over between sites only after replicated simulation and downgrade policy are proven.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Υ-11", "Ζ-57", "Ζ-60", "Ζ-63", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 63, "QUORUM-SHARD-OWNERSHIP-0", "Define quorum-based shard ownership before live distributed failover or migration.", "schema_registry", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Φ-14", "Ζ-57", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 64, "DETERMINISTIC-CONFLICT-RESOLUTION-0", "Resolve distributed conflicts deterministically so replay and rollback remain equivalent.", "implementation", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Ζ-57", "Ζ-63", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 65, "FEDERATED-WORLDS-0", "Coordinate federated worlds only after distributed authority and trust policy are stable.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Σ-5", "Ζ-57", "Ζ-63", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 66, "CROSS-SHARD-ENTITY-MIGRATION-0", "Migrate entities across shards only after relocation and conflict resolution are proven.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Ζ-59", "Ζ-64", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 67, "SEAMLESS-PLAYER-TRANSFER-0", "Transfer players seamlessly only after interest management and entity migration remain deterministic.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Ζ-58", "Ζ-61", "Ζ-66", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 68, "DISTRIBUTED-REPLAY-VERIFY-0", "Verify distributed replay equivalence before any replicated runtime is considered trustworthy.", "tooling", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Ζ-30", "Ζ-57", "Ζ-60", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 69, "PARTIAL-CLUSTER-RESTART-0", "Restart cluster slices only after replication, failover, and downgrade policy are stable.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Υ-11", "Ζ-57", "Ζ-62", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 70, "NETWORK-PARTITION-MODES-0", "Define lawful partition behavior before distributed survival or rejoin logic is enabled.", "schema_registry", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Υ-11", "Ζ-57", "Ζ-63", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 71, "DISTRIBUTED-DEGRADED-SURVIVAL-0", "Survive distributed degradation only through explicit downgrade and quorum-aware policy.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Υ-11", "Ζ-62", "Ζ-70", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 72, "DETERMINISTIC-REJOIN-0", "Rejoin distributed partitions only after replay verification and partition policy are proven.", "operations", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Ζ-57", "Ζ-68", "Ζ-70", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 73, "PROOF-ANCHOR-QUORUM-VERIFY-0", "Verify proof anchors by quorum before distributed authority is trusted for promotion.", "tooling", "post_snapshot_required", "extreme", "FULL", True, True, "distributed_runtime", "distributed", ["Φ-14", "Ζ-29", "Ζ-57", "SNAPSHOT-MAP"]),
    _make_prompt_seed("ZETA", 74, "WHAT-IF-SIM-ON-UPDATES-0", "Run what-if simulation on updates only after distributed replay, release ops, and downgrade paths are proven.", "operations", "post_snapshot_required", "high", "FULL", True, True, "distributed_runtime", "distributed", ["Υ-10", "Υ-11", "Υ-12", "Ζ-57", "SNAPSHOT-MAP"]),
]


GLOBAL_EXECUTION_DOCTRINE = [
    "architecture docs and schemas first",
    "registries and validators second",
    "runtime implementation third",
    "live operations only after runtime foundations frozen",
    "packaging and publication only after convergence gates pass",
    "any AI execution is advisory and XStack-gated",
]


GLOBAL_STOP_CONDITIONS = [
    {"stop_id": "global.architecture_graph_changed", "condition": "If the architecture graph changes unexpectedly, stop.", "escalation": "Regenerate the snapshot mapping, reconcile drift, and require manual review."},
    {"stop_id": "global.semantic_contract_bump", "condition": "If a semantic contract bump is required, stop and escalate.", "escalation": "Route through contract review, migration or refusal planning, and CompatX review."},
    {"stop_id": "global.conflicting_live_subsystem", "condition": "If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.", "escalation": "Apply keep/merge/replace/quarantine rules before implementation continues."},
    {"stop_id": "global.baseline_drift", "condition": "If deterministic baselines drift, stop.", "escalation": "Re-run OMEGA verification, identify the drift source, and do not continue live-runtime work."},
    {"stop_id": "global.runtime_boundaries_unclear", "condition": "If runtime or module boundaries are unclear, stop before PHI-series implementation.", "escalation": "Convert the uncertainty into architecture review and snapshot remapping."},
    {"stop_id": "global.unstated_zeta_foundation", "condition": "If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning.", "escalation": "Split the missing foundation into an earlier prompt and rerun dependency planning."},
]


RECONCILIATION_RULE_ROWS = [
    {"rule_id": "reality.extend_existing", "statement": "If the live repo already has a subsystem that satisfies the blueprint, prefer extending it.", "action": "keep"},
    {"rule_id": "reality.route_duplicates_through_xi", "statement": "If duplicate implementations exist, route through XI-series convergence logic first.", "action": "merge"},
    {"rule_id": "reality.code_beats_docs", "statement": "If documentation contradicts code, code is authoritative until reconciled.", "action": "reconcile"},
    {"rule_id": "reality.unknown_boundary_means_post_snapshot", "statement": "If the blueprint assumes a module boundary not present in repo, mark it as post-snapshot-required.", "action": "replace"},
    {"rule_id": "reality.extend_before_invent", "statement": "Never invent new modules if an existing module can be extended safely.", "action": "keep"},
    {"rule_id": "reality.uncertainty_quarantines", "statement": "If uncertain, quarantine and escalate to manual review.", "action": "quarantine"},
]


CRITICAL_PATH_PROMPT_IDS = {
    "Σ-0", "Σ-1", "Σ-2", "Σ-3", "Σ-5",
    "Φ-0", "Φ-1", "Φ-2", "Φ-3", "Φ-4", "Φ-5", "Φ-12", "Φ-13", "Φ-14",
    "Υ-0", "Υ-2", "Υ-3", "Υ-6", "Υ-10", "Υ-11", "Υ-12",
    "Ζ-10", "Ζ-14", "Ζ-16", "Ζ-18", "Ζ-24", "Ζ-27", "Ζ-28", "Ζ-29", "Ζ-30", "Ζ-33", "Ζ-44",
    "Ζ-57", "Ζ-58", "Ζ-59", "Ζ-60", "Ζ-62", "Ζ-63", "Ζ-68", "Ζ-73",
}


def _prompt_inputs(seed: Mapping[str, object]) -> list[str]:
    series_key = _token(seed.get("series_key"))
    family = _token(seed.get("family"))
    inputs = [
        "docs/blueprint/SERIES_EXECUTION_STRATEGY.md",
        "docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md",
        "data/blueprint/series_execution_strategy.json",
    ]
    if _token(seed.get("snapshot_requirement")) == "post_snapshot_required":
        inputs.append("snapshot-mapping rows for the target prompt")
    if series_key == "SIGMA":
        inputs.extend(["AGENTS.md", "docs/canon/constitution_v1.md", "tools/xstack"])
    elif series_key == "PHI":
        inputs.extend(["docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md", "engine/", "server/", "client/"])
    elif series_key == "UPSILON":
        inputs.extend(["data/audit/build_graph.json", "dist/", "tools/xstack/"])
    elif series_key == "ZETA":
        inputs.extend(["OMEGA baseline artifacts", "PHI runtime foundation outputs", "UPSILON control-plane outputs"])
        if family == "distributed":
            inputs.extend(["distributed replay verify reports", "proof-anchor health reports"])
    return sorted({_token(item) for item in inputs if _token(item)})


def _prompt_outputs(seed: Mapping[str, object]) -> list[str]:
    title = _token(seed.get("title"))
    series_key = _token(seed.get("series_key"))
    outputs = [f"design package for {title.lower()}", "validation report", "rollback notes" if bool(seed.get("rollback_strategy_required")) else "execution notes"]
    if series_key == "SIGMA":
        outputs.append("governance or catalog artifact update")
    elif series_key == "PHI":
        outputs.append("runtime boundary artifact or componentization change")
    elif series_key == "UPSILON":
        outputs.append("control-plane or release artifact update")
    elif series_key == "ZETA":
        outputs.append("operations playbook or cutover artifact")
    return sorted({_token(item) for item in outputs if _token(item)})


def _gates_after_execution(seed: Mapping[str, object]) -> list[str]:
    gate = _token(seed.get("gate_profile_required"))
    if gate == "FAST":
        return ["RepoX FAST", "AuditX FAST", "TestX impacted subset"]
    if gate == "STRICT":
        return ["RepoX STRICT", "AuditX STRICT", "validate --all STRICT", "TestX extended subset"]
    return ["XStack CI FULL", "RepoX FULL", "AuditX FULL", "Omega verification suite", "trust strict suite when relevant"]


def _gates_before_execution(seed: Mapping[str, object]) -> list[str]:
    gates = ["blueprint consistency check"]
    if _token(seed.get("snapshot_requirement")) == "post_snapshot_required":
        gates.append("snapshot mapping review")
        gates.append("RepoX FAST")
    if bool(seed.get("manual_review_required")):
        gates.append("manual review packet ready")
    return gates


def _prompt_stop_conditions(seed: Mapping[str, object]) -> list[str]:
    conditions = [row["condition"] for row in GLOBAL_STOP_CONDITIONS]
    if _token(seed.get("snapshot_requirement")) == "post_snapshot_required":
        conditions.append("If snapshot mapping for this prompt is incomplete or low-confidence, stop.")
    if bool(seed.get("manual_review_required")):
        conditions.append("If required human review is unavailable or unresolved, stop.")
    if bool(seed.get("rollback_strategy_required")):
        conditions.append("If rollback strategy is absent or unverified, stop.")
    return sorted({item for item in conditions if _token(item)})


def _planned_module_targets(seed: Mapping[str, object]) -> list[str]:
    series_key = _token(seed.get("series_key"))
    category = _token(seed.get("category"))
    family = _token(seed.get("family"))
    targets = ["docs/blueprint"]
    if series_key == "SIGMA":
        targets.extend(["AGENTS.md", "tools/xstack", "tools/controlx"])
    elif series_key == "PHI":
        targets.extend(["engine", "server", "client"])
        if category in {"rendering", "replaceability"}:
            targets.append("client")
    elif series_key == "UPSILON":
        targets.extend(["tools/xstack", "cmake", "dist", "docs"])
    elif series_key == "ZETA":
        targets.extend(["engine", "server", "client", "tools/xstack"])
        if family == "distributed":
            targets.extend(["server", "tools/xstack"])
        if category == "content_ops":
            targets.extend(["packs", "data"])
    return sorted({_token(item) for item in targets if _token(item)})


PROMPT_SEEDS = list(SIGMA_PROMPT_SEEDS) + list(PHI_PROMPT_SEEDS) + list(UPSILON_PROMPT_SEEDS) + list(ZETA_PROMPT_SEEDS)

FOUNDATION_NODES = [
    {
        "description": "Repository convergence, architecture freeze, and structure lock are complete enough to anchor post-XI planning.",
        "node_id": "XI-8",
        "node_type": "foundation",
        "title": "Repository Freeze Complete",
    },
    {
        "description": "OMEGA verification baselines and distribution freeze artifacts exist and remain authoritative.",
        "node_id": "OMEGA-FREEZE",
        "node_type": "foundation",
        "title": "Omega Runtime Freeze",
    },
    {
        "description": "A fresh repository snapshot has been mapped against the blueprint and reconciled before implementation planning proceeds.",
        "node_id": "SNAPSHOT-MAP",
        "node_type": "gate",
        "title": "Snapshot Mapping Complete",
    },
]

PROMPT_REQUIRED_FIELDS = (
    "prompt_id",
    "series_id",
    "title",
    "short_goal",
    "prerequisites",
    "dependent_prompts",
    "risk_level",
    "execution_class",
    "snapshot_requirement",
    "gate_profile_required",
    "rollback_strategy_required",
    "manual_review_required",
    "stop_conditions",
)


def _risk_label_from_level(level: int) -> str:
    reverse = {value: key for key, value in RISK_ORDER.items()}
    return reverse.get(max(0, min(3, int(level))), "medium")


def _series_summary_counts(rows: Sequence[Mapping[str, object]], key: str, label_name: str) -> list[dict[str, object]]:
    counts = Counter(_token(row.get(key)) for row in rows if _token(row.get(key)))
    if key == "series_id":
        ordered_keys = [SERIES_GLYPH[item] for item in ("SIGMA", "PHI", "UPSILON", "ZETA")]
    elif key == "risk_level":
        ordered_keys = sorted(counts, key=lambda item: (RISK_ORDER.get(item, 99), item))
    elif key == "snapshot_requirement":
        ordered_keys = sorted(counts, key=lambda item: (SNAPSHOT_ORDER.get(item, 99), item))
    elif key == "execution_class":
        ordered_keys = sorted(counts, key=lambda item: (EXECUTION_CLASS_ORDER.get(item, 99), item))
    else:
        ordered_keys = sorted(counts)
    return [
        {label_name: item, "count": int(counts.get(item, 0))}
        for item in ordered_keys
        if int(counts.get(item, 0)) > 0
    ]


def _is_prompt_id(value: object) -> bool:
    return bool(_series_from_prompt_id(_token(value)))


def _phase_for_prompt(seed: Mapping[str, object]) -> str:
    series_key = _token(seed.get("series_key"))
    family = _token(seed.get("family"))
    if series_key == "SIGMA":
        return "A"
    if series_key == "UPSILON":
        return "C"
    if series_key == "PHI":
        if family == "distributed":
            return "E"
        if family in {"replaceability", "runtime"} and _token(seed.get("category")) in {"rendering", "replaceability", "assets", "security"}:
            return "D"
        return "B"
    if family == "distributed":
        return "E"
    return "D"


def _phase_label(phase_id: str) -> str:
    return {
        "A": "Phase A - Governance & Interface Foundations",
        "B": "Phase B - Runtime Component Foundations",
        "C": "Phase C - Build / Release / Control Plane Foundations",
        "D": "Phase D - Advanced Replaceability",
        "E": "Phase E - Distributed Live Operations",
    }.get(_token(phase_id), "Unknown phase")


def _series_label(series_key: str) -> str:
    return f"{SERIES_GLYPH.get(series_key, _token(series_key))}-Series - {SERIES_NAME.get(series_key, _token(series_key))}"


def _prompt_prereq_sort_key(prereq: str) -> tuple[int, int, str]:
    return _prompt_sort_key(prereq) if _is_prompt_id(prereq) else (98, 0, _token(prereq))


def _build_dependent_map(seeds: Sequence[Mapping[str, object]]) -> dict[str, list[str]]:
    dependent_map: dict[str, set[str]] = defaultdict(set)
    for seed in seeds:
        prompt_id = _token(seed.get("prompt_id"))
        for prereq in seed.get("prerequisites") or []:
            prereq_id = _token(prereq)
            if _is_prompt_id(prereq_id):
                dependent_map[prereq_id].add(prompt_id)
    return {
        prompt_id: sorted(values, key=_prompt_sort_key)
        for prompt_id, values in sorted(dependent_map.items(), key=lambda item: _prompt_sort_key(item[0]))
    }


def _risk_axes(seed: Mapping[str, object]) -> dict[str, str]:
    base = RISK_ORDER.get(_token(seed.get("risk_level")), 1)
    series_key = _token(seed.get("series_key"))
    category = _token(seed.get("category"))
    execution_class = _token(seed.get("execution_class"))
    family = _token(seed.get("family"))
    gate = _token(seed.get("gate_profile_required"))

    determinism = base + (1 if series_key in {"PHI", "ZETA"} else 0)
    if category in {"state", "distributed", "replaceability", "rendering", "content_ops"}:
        determinism += 1
    compatibility = base + (1 if category in {"compatibility", "state_migration", "content_ops", "distributed_runtime"} else 0)
    architecture_drift = base + (1 if execution_class in {"implementation", "refactor", "operations"} else 0)
    distribution = base + (1 if series_key == "UPSILON" or category in {"release", "rollout", "content_ops"} else 0)
    operator_safety = base + (1 if gate == "FULL" or execution_class == "operations" else 0)
    trust_security = base + (
        2 if category in {"trust_security", "security"} else 1 if series_key == "ZETA" and family in {"distributed", "security"} else 0
    )
    axis_levels = {
        "risk_to_architecture_drift": _risk_label_from_level(min(3, architecture_drift)),
        "risk_to_compatibility": _risk_label_from_level(min(3, compatibility)),
        "risk_to_determinism": _risk_label_from_level(min(3, determinism)),
        "risk_to_distribution": _risk_label_from_level(min(3, distribution)),
        "risk_to_operator_safety": _risk_label_from_level(min(3, operator_safety)),
        "risk_to_trust_security": _risk_label_from_level(min(3, trust_security)),
    }
    aggregate = max(RISK_ORDER.get(value, 1) for value in axis_levels.values())
    axis_levels["aggregate_risk_rating"] = _risk_label_from_level(aggregate)
    return axis_levels


def _parallelizable(seed: Mapping[str, object], prompt_id: str) -> bool:
    if prompt_id in CRITICAL_PATH_PROMPT_IDS:
        return False
    if bool(seed.get("manual_review_required")):
        return False
    return _token(seed.get("execution_class")) in {"docs_only", "schema_registry", "tooling"}


def _build_prompt_rows(seeds: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    dependent_map = _build_dependent_map(seeds)
    rows: list[dict[str, object]] = []
    for seed in sorted(seeds, key=lambda item: _prompt_sort_key(_token(item.get("prompt_id")))):
        prompt_id = _token(seed.get("prompt_id"))
        row = dict(seed)
        row["dependent_prompts"] = list(dependent_map.get(prompt_id, []))
        row["gates_required_after_execution"] = _gates_after_execution(seed)
        row["gates_required_before_execution"] = _gates_before_execution(seed)
        row["inputs"] = _prompt_inputs(seed)
        row["outputs"] = _prompt_outputs(seed)
        row["phase_id"] = _phase_for_prompt(seed)
        row["phase_label"] = _phase_label(row["phase_id"])
        row["planned_module_targets"] = _planned_module_targets(seed)
        row["purpose"] = _token(seed.get("short_goal"))
        row["series_name"] = SERIES_NAME.get(_token(seed.get("series_key")), "")
        row["should_never_run_before_snapshot_mapping"] = _token(seed.get("snapshot_requirement")) == "post_snapshot_required"
        row["parallelizable"] = _parallelizable(seed, prompt_id)
        row["critical_path"] = prompt_id in CRITICAL_PATH_PROMPT_IDS
        row["stop_conditions"] = _prompt_stop_conditions(seed)
        row.update(_risk_axes(seed))
        missing = [field for field in PROMPT_REQUIRED_FIELDS if field not in row]
        if missing:
            raise ValueError(f"prompt '{prompt_id}' missing required fields: {', '.join(missing)}")
        rows.append(_fingerprinted(row))
    return rows


def _validate_prompt_graph(rows: Sequence[Mapping[str, object]]) -> None:
    prompt_ids = {_token(row.get("prompt_id")) for row in rows}
    known_ids = set(prompt_ids) | set(FOUNDATION_NODE_IDS)
    for row in rows:
        prompt_id = _token(row.get("prompt_id"))
        if not prompt_id:
            raise ValueError("encountered prompt without prompt_id")
        if _token(row.get("snapshot_requirement")) == "post_snapshot_required" and "SNAPSHOT-MAP" not in set(row.get("prerequisites") or []):
            raise ValueError(f"post-snapshot prompt '{prompt_id}' must depend on SNAPSHOT-MAP")
        for prereq in row.get("prerequisites") or []:
            prereq_id = _token(prereq)
            if prereq_id not in known_ids:
                raise ValueError(f"prompt '{prompt_id}' references unknown prerequisite '{prereq_id}'")

    indegree = {prompt_id: 0 for prompt_id in prompt_ids}
    graph: dict[str, set[str]] = {prompt_id: set() for prompt_id in prompt_ids}
    for row in rows:
        prompt_id = _token(row.get("prompt_id"))
        for prereq in row.get("prerequisites") or []:
            prereq_id = _token(prereq)
            if prereq_id in prompt_ids and prompt_id not in graph[prereq_id]:
                graph[prereq_id].add(prompt_id)
                indegree[prompt_id] += 1
    queue = deque(sorted((prompt_id for prompt_id, degree in indegree.items() if degree == 0), key=_prompt_sort_key))
    visited: list[str] = []
    while queue:
        current = queue.popleft()
        visited.append(current)
        for child in sorted(graph[current], key=_prompt_sort_key):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if len(visited) != len(prompt_ids):
        raise ValueError("prompt dependency graph contains a cycle")


def _build_final_prompt_inventory(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    payload = {
        "execution_doctrine": list(GLOBAL_EXECUTION_DOCTRINE),
        "global_stop_conditions": [_fingerprinted(row) for row in GLOBAL_STOP_CONDITIONS],
        "prompts": list(rows),
        "report_id": "pi.2.final_prompt_inventory.v1",
        "summary": {
            "critical_path_prompt_count": len([row for row in rows if bool(row.get("critical_path"))]),
            "execution_class_counts": _series_summary_counts(rows, "execution_class", "execution_class"),
            "manual_review_required_count": len([row for row in rows if bool(row.get("manual_review_required"))]),
            "parallelizable_prompt_count": len([row for row in rows if bool(row.get("parallelizable"))]),
            "prompt_count": len(rows),
            "risk_counts": _series_summary_counts(rows, "risk_level", "risk_level"),
            "series_counts": _series_summary_counts(rows, "series_id", "series_id"),
            "snapshot_requirement_counts": _series_summary_counts(rows, "snapshot_requirement", "snapshot_requirement"),
        },
    }
    return _fingerprinted(payload)


def _build_snapshot_mapping_template(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    template_rows = []
    for row in rows:
        template_row = {
            "actual_repo_locations": [],
            "confidence_score": 0.0,
            "drift_found": [],
            "gaps_found": [],
            "keep_merge_replace_recommendation": "undetermined",
            "obsolete_assumptions": [],
            "planned_module_targets": list(row.get("planned_module_targets") or []),
            "prompt_id": _token(row.get("prompt_id")),
            "requires_manual_review": bool(row.get("manual_review_required")),
            "series_id": _token(row.get("series_id")),
            "snapshot_requirement": _token(row.get("snapshot_requirement")),
            "title": _token(row.get("title")),
        }
        template_rows.append(_fingerprinted(template_row))
    payload = {
        "report_id": "pi.2.snapshot_mapping_template.v1",
        "rows": template_rows,
        "summary": {
            "post_snapshot_prompt_count": len([row for row in rows if _token(row.get("snapshot_requirement")) == "post_snapshot_required"]),
            "prompt_count": len(rows),
            "requires_manual_review_count": len([row for row in rows if bool(row.get("manual_review_required"))]),
        },
        "template_fields": [
            "planned_module_targets",
            "actual_repo_locations",
            "gaps_found",
            "drift_found",
            "obsolete_assumptions",
            "keep_merge_replace_recommendation",
            "confidence_score",
            "requires_manual_review",
        ],
    }
    return _fingerprinted(payload)


def _build_prompt_dependency_tree(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    prompt_nodes = []
    edges = []
    parallelizable_prompt_ids = []
    blocked_until_snapshot_mapping = []
    for row in rows:
        prompt_id = _token(row.get("prompt_id"))
        prompt_node = {
            "critical_path": bool(row.get("critical_path")),
            "dependent_prompts": list(row.get("dependent_prompts") or []),
            "gate_profile_required": _token(row.get("gate_profile_required")),
            "manual_review_required": bool(row.get("manual_review_required")),
            "parallelizable": bool(row.get("parallelizable")),
            "phase_id": _token(row.get("phase_id")),
            "prompt_id": prompt_id,
            "prerequisites": list(row.get("prerequisites") or []),
            "series_id": _token(row.get("series_id")),
            "should_never_run_before_snapshot_mapping": bool(row.get("should_never_run_before_snapshot_mapping")),
            "snapshot_requirement": _token(row.get("snapshot_requirement")),
            "title": _token(row.get("title")),
        }
        prompt_nodes.append(_fingerprinted(prompt_node))
        if bool(row.get("parallelizable")):
            parallelizable_prompt_ids.append(prompt_id)
        if bool(row.get("should_never_run_before_snapshot_mapping")):
            blocked_until_snapshot_mapping.append(prompt_id)
        for prereq in row.get("prerequisites") or []:
            edges.append({"edge_type": "depends_on", "from": _token(prereq), "to": prompt_id})
    payload = {
        "critical_path_prompts": sorted(CRITICAL_PATH_PROMPT_IDS, key=_prompt_sort_key),
        "edges": sorted(edges, key=lambda item: (_prompt_prereq_sort_key(_token(item.get("from"))), _prompt_sort_key(_token(item.get("to"))))),
        "foundation_nodes": [_fingerprinted(row) for row in FOUNDATION_NODES],
        "parallelizable_prompt_ids": sorted(set(parallelizable_prompt_ids), key=_prompt_sort_key),
        "prompt_nodes": prompt_nodes,
        "report_id": "pi.2.prompt_dependency_tree.v1",
        "should_never_run_before_snapshot_mapping": sorted(set(blocked_until_snapshot_mapping), key=_prompt_sort_key),
        "summary": {
            "critical_path_prompt_count": len(CRITICAL_PATH_PROMPT_IDS),
            "edge_count": len(edges),
            "foundation_node_count": len(FOUNDATION_NODES),
            "parallelizable_prompt_count": len(set(parallelizable_prompt_ids)),
            "prompt_count": len(rows),
        },
    }
    return _fingerprinted(payload)


def _build_prompt_risk_matrix(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    risk_rows = []
    for row in rows:
        risk_row = {
            "aggregate_risk_rating": _token(row.get("aggregate_risk_rating")),
            "manual_review_required": bool(row.get("manual_review_required")),
            "prompt_id": _token(row.get("prompt_id")),
            "risk_to_architecture_drift": _token(row.get("risk_to_architecture_drift")),
            "risk_to_compatibility": _token(row.get("risk_to_compatibility")),
            "risk_to_determinism": _token(row.get("risk_to_determinism")),
            "risk_to_distribution": _token(row.get("risk_to_distribution")),
            "risk_to_operator_safety": _token(row.get("risk_to_operator_safety")),
            "risk_to_trust_security": _token(row.get("risk_to_trust_security")),
            "series_id": _token(row.get("series_id")),
            "snapshot_requirement": _token(row.get("snapshot_requirement")),
            "title": _token(row.get("title")),
        }
        risk_rows.append(_fingerprinted(risk_row))
    payload = {
        "prompts": risk_rows,
        "report_id": "pi.2.prompt_risk_matrix.v1",
        "summary": {
            "aggregate_risk_counts": _series_summary_counts(risk_rows, "aggregate_risk_rating", "risk_level"),
            "prompt_count": len(risk_rows),
            "series_counts": _series_summary_counts(risk_rows, "series_id", "series_id"),
        },
    }
    return _fingerprinted(payload)


def _build_reconciliation_rules() -> dict[str, object]:
    rules = []
    for row in RECONCILIATION_RULE_ROWS:
        rendered = dict(row)
        rendered["escalation"] = {
            "discard": "Retire the assumption or path only after review confirms it is obsolete.",
            "keep": "Extend the existing subsystem instead of rebuilding the idea from scratch.",
            "merge": "Use XI evidence to converge duplicate or overlapping implementations before future work starts.",
            "quarantine": "Create a manual review packet and stop implementation planning until the ambiguity is resolved.",
            "reconcile": "Update docs, registries, or blueprint assumptions so the code and plan agree again.",
            "replace": "Mark the blueprint assumption as post-snapshot-required and derive a repo-specific replacement strategy.",
        }.get(_token(row.get("action")), "Escalate to manual review.")
        rules.append(_fingerprinted(rendered))
    payload = {
        "decision_outcomes": ["keep", "merge", "replace", "discard", "quarantine"],
        "report_id": "pi.2.repo_reality_reconciliation_rules.v1",
        "rules": rules,
    }
    return _fingerprinted(payload)


def _build_stop_conditions_payload(existing: Mapping[str, object]) -> dict[str, object]:
    payload = dict(existing)
    payload["execution_doctrine"] = list(GLOBAL_EXECUTION_DOCTRINE)
    payload["global_stop_conditions"] = [_fingerprinted(row) for row in GLOBAL_STOP_CONDITIONS]
    payload["inventory_guardrails"] = [
        "If any prompt lacks metadata, stop and repair the inventory before execution planning continues.",
        "If snapshot mapping confidence remains low for a post-snapshot prompt, stop and escalate to manual review.",
        "If a prompt depends on an unstated foundation, stop and move the missing work into an earlier series.",
    ]
    payload["pi_2_extension_report_id"] = "pi.2.stop_conditions_extension.v1"
    return _fingerprinted(payload)


def _joined(values: Iterable[object]) -> str:
    rendered = [str(value).strip() for value in values if str(value).strip()]
    return ", ".join(rendered) if rendered else "none"


def _markdown_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def _render_inventory_doc(rows: Sequence[Mapping[str, object]], inventory: Mapping[str, object]) -> str:
    lines = [
        _doc_header("Final Prompt Inventory", "snapshot-anchored prompt execution inventory after fresh repository mapping"),
        "## Current Boundary",
        "",
        "This is the canonical prompt catalog for all post-XI series work.",
        "It is planning only and must be reconciled against a fresh repository snapshot before any post-snapshot prompt executes.",
        "",
        "## Safest Execution Doctrine",
        "",
    ]
    lines.extend(f"{index}. {item}." for index, item in enumerate(inventory.get("execution_doctrine") or [], start=1))
    lines.extend(
        [
            "",
            "The matching execution doctrine is also anchored in `docs/blueprint/SERIES_EXECUTION_STRATEGY.md`.",
            "",
            "## Global Stop Conditions",
            "",
        ]
    )
    for row in inventory.get("global_stop_conditions") or []:
        current = dict(row)
        lines.append(f"- `{_token(current.get('stop_id'))}`: {_token(current.get('condition'))} Escalation: {_token(current.get('escalation'))}")
    lines.extend(
        [
            "",
            "## Inventory Summary",
            "",
            _markdown_table(
                ["Series", "Count"],
                [
                    [item.get("series_id"), item.get("count")]
                    for item in dict(inventory.get("summary") or {}).get("series_counts") or []
                ],
            ),
            "",
        ]
    )
    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[_token(row.get("series_key"))].append(row)
    for series_key in ("SIGMA", "PHI", "UPSILON", "ZETA"):
        lines.extend([f"## {_series_label(series_key)}", ""])
        for row in grouped.get(series_key, []):
            prompt_id = _token(row.get("prompt_id"))
            lines.extend(
                [
                    f"### `{prompt_id}` `{_token(row.get('title'))}`",
                    "",
                    f"- Purpose: {_token(row.get('purpose'))}",
                    f"- Inputs: {_joined(row.get('inputs') or [])}",
                    f"- Outputs: {_joined(row.get('outputs') or [])}",
                    f"- Prerequisites: {_joined(row.get('prerequisites') or [])}",
                    f"- Dependent Prompts: {_joined(row.get('dependent_prompts') or [])}",
                    f"- Snapshot Requirement: `{_token(row.get('snapshot_requirement'))}`",
                    f"- Risk Level: `{_token(row.get('risk_level'))}`",
                    f"- Execution Class: `{_token(row.get('execution_class'))}`",
                    f"- Gate Profile Required: `{_token(row.get('gate_profile_required'))}`",
                    f"- Gates Required After Execution: {_joined(row.get('gates_required_after_execution') or [])}",
                    f"- Manual Review Required: `{'yes' if bool(row.get('manual_review_required')) else 'no'}`",
                    f"- Rollback Strategy Required: `{'yes' if bool(row.get('rollback_strategy_required')) else 'no'}`",
                    f"- Stop Conditions: {_joined(row.get('stop_conditions') or [])}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def _render_snapshot_mapping_doc(rows: Sequence[Mapping[str, object]], template: Mapping[str, object]) -> str:
    table_rows = []
    for row in template.get("rows") or []:
        current = dict(row)
        table_rows.append(
            [
                _token(current.get("prompt_id")),
                _token(current.get("series_id")),
                _joined(current.get("planned_module_targets") or []),
                _token(current.get("keep_merge_replace_recommendation")),
                "yes" if bool(current.get("requires_manual_review")) else "no",
            ]
        )
    lines = [
        _doc_header("Snapshot Mapping Template", "filled snapshot-to-blueprint reconciliation packet after fresh repository archaeology"),
        "## Template Fields",
        "",
        "Each row must be completed against the fresh repository snapshot before post-snapshot prompts execute.",
        "",
        _markdown_table(
            ["Field", "Purpose"],
            [
                ["planned_module_targets", "Expected architectural targets from the blueprint."],
                ["actual_repo_locations", "Observed files, modules, or docs in the live repository."],
                ["gaps_found", "Missing foundations or artifacts that block the prompt."],
                ["drift_found", "Conflicts between the blueprint and live repo state."],
                ["obsolete_assumptions", "Blueprint assumptions invalidated by the live repo."],
                ["keep_merge_replace_recommendation", "Current recommendation before implementation planning."],
                ["confidence_score", "Mapping confidence from 0.0 to 1.0."],
                ["requires_manual_review", "Whether a human review gate is mandatory."],
            ],
        ),
        "",
        "## Prompt Rows",
        "",
        _markdown_table(["Prompt", "Series", "Planned Module Targets", "Default Recommendation", "Manual Review"], table_rows),
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_checklist_doc(rows: Sequence[Mapping[str, object]]) -> str:
    lines = [
        _doc_header("Prompt Execution Checklist", "prompt-by-prompt operational checklist after snapshot mapping"),
        "## Execution Checklist",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### `{_token(row.get('prompt_id'))}` `{_token(row.get('title'))}`",
                "",
                f"- Preconditions: {_joined(row.get('prerequisites') or [])}",
                f"- Gate Before Execution: {_joined(row.get('gates_required_before_execution') or [])}",
                f"- Gate After Execution: {_joined(row.get('gates_required_after_execution') or [])}",
                f"- Required Artifacts To Inspect: {_joined(row.get('inputs') or [])}",
                f"- Human Review Mandatory: `{'yes' if bool(row.get('manual_review_required')) else 'no'}`",
                f"- Rollback Plan Must Be Prepared First: `{'yes' if bool(row.get('rollback_strategy_required')) else 'no'}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_dependency_tree_doc(tree: Mapping[str, object]) -> str:
    lines = [
        _doc_header("Prompt Dependency Tree", "snapshot-anchored execution graph after live repository mapping"),
        "## Critical Path",
        "",
    ]
    for prompt_id in tree.get("critical_path_prompts") or []:
        lines.append(f"- `{_token(prompt_id)}`")
    lines.extend(["", "## Foundation Nodes", ""])
    for row in tree.get("foundation_nodes") or []:
        current = dict(row)
        lines.append(f"- `{_token(current.get('node_id'))}`: {_token(current.get('title'))}. {_token(current.get('description'))}")
    lines.extend(
        [
            "",
            "## Dependency Edges",
            "",
            _markdown_table(
                ["From", "To", "Type"],
                [[_token(row.get("from")), _token(row.get("to")), _token(row.get("edge_type"))] for row in tree.get("edges") or []],
            ),
            "",
            "## Parallelizable Prompts",
            "",
        ]
    )
    for prompt_id in tree.get("parallelizable_prompt_ids") or []:
        lines.append(f"- `{_token(prompt_id)}`")
    lines.extend(["", "## Should Never Run Before Snapshot Mapping", ""])
    for prompt_id in tree.get("should_never_run_before_snapshot_mapping") or []:
        lines.append(f"- `{_token(prompt_id)}`")
    return "\n".join(lines).rstrip() + "\n"


def _render_risk_matrix_doc(risk_matrix: Mapping[str, object]) -> str:
    rows = []
    for row in risk_matrix.get("prompts") or []:
        current = dict(row)
        rows.append(
            [
                _token(current.get("prompt_id")),
                _token(current.get("risk_to_determinism")),
                _token(current.get("risk_to_compatibility")),
                _token(current.get("risk_to_architecture_drift")),
                _token(current.get("risk_to_distribution")),
                _token(current.get("risk_to_operator_safety")),
                _token(current.get("risk_to_trust_security")),
                _token(current.get("aggregate_risk_rating")),
            ]
        )
    lines = [
        _doc_header("Prompt Risk Matrix", "prompt-specific automation risk matrix after snapshot mapping"),
        "## Aggregate Risk Table",
        "",
        _markdown_table(
            ["Prompt", "Determinism", "Compatibility", "Architecture Drift", "Distribution", "Operator Safety", "Trust / Security", "Aggregate"],
            rows,
        ),
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_reconciliation_guide_doc(rules: Mapping[str, object]) -> str:
    lines = [
        _doc_header("Repo Reality Reconciliation Guide", "snapshot reconciliation guidance after fresh repository archaeology"),
        "## Reconciliation Rules",
        "",
        _markdown_table(
            ["Rule", "Statement", "Preferred Action", "Escalation"],
            [
                [
                    _token(row.get("rule_id")),
                    _token(row.get("statement")),
                    _token(row.get("action")),
                    _token(row.get("escalation")),
                ]
                for row in rules.get("rules") or []
            ],
        ),
        "",
        "## Decision Outcomes",
        "",
    ]
    for value in rules.get("decision_outcomes") or []:
        lines.append(f"- `{_token(value)}`")
    return "\n".join(lines).rstrip() + "\n"


def _render_pi_2_final_doc(
    inventory: Mapping[str, object],
    tree: Mapping[str, object],
    template: Mapping[str, object],
    risk_matrix: Mapping[str, object],
) -> str:
    summary = dict(inventory.get("summary") or {})
    lines = [
        _doc_header("PI 2 Final Report", "final snapshot-driven execution planning after live repository mapping"),
        "## Generated Artifacts",
        "",
        "- `docs/blueprint/FINAL_PROMPT_INVENTORY.md`",
        "- `docs/blueprint/SNAPSHOT_MAPPING_TEMPLATE.md`",
        "- `docs/blueprint/PROMPT_EXECUTION_CHECKLIST.md`",
        "- `docs/blueprint/PROMPT_DEPENDENCY_TREE.md`",
        "- `docs/blueprint/PROMPT_RISK_MATRIX.md`",
        "- `docs/blueprint/REPO_REALITY_RECONCILIATION_GUIDE.md`",
        "- `data/blueprint/final_prompt_inventory.json`",
        "- `data/blueprint/snapshot_mapping_template.json`",
        "- `data/blueprint/prompt_dependency_tree.json`",
        "- `data/blueprint/prompt_risk_matrix.json`",
        "- `data/blueprint/repo_reality_reconciliation_rules.json`",
        "",
        "## Summary",
        "",
        f"- Prompt count: `{int(summary.get('prompt_count', 0) or 0)}`",
        f"- Critical path prompts: `{int(summary.get('critical_path_prompt_count', 0) or 0)}`",
        f"- Parallelizable prompts: `{int(summary.get('parallelizable_prompt_count', 0) or 0)}`",
        f"- Manual review required prompts: `{int(summary.get('manual_review_required_count', 0) or 0)}`",
        f"- Snapshot mapping rows: `{int(dict(template.get('summary') or {}).get('prompt_count', 0) or 0)}`",
        f"- Dependency edges: `{int(dict(tree.get('summary') or {}).get('edge_count', 0) or 0)}`",
        f"- Risk rows: `{int(dict(risk_matrix.get('summary') or {}).get('prompt_count', 0) or 0)}`",
        "",
        "## Readiness",
        "",
        "The prompt inventory is complete, the dependency graph is coherent, the snapshot mapping scaffold is ready, and the risk matrix plus stop conditions are explicit enough to drive the next fresh-repo-snapshot planning pass.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build_final_prompt_inventory_snapshot(repo_root: str) -> dict[str, object]:
    root = _repo_root(repo_root)
    inputs = _required_inputs(root)
    prompt_rows = _build_prompt_rows(PROMPT_SEEDS)
    _validate_prompt_graph(prompt_rows)

    final_prompt_inventory = _build_final_prompt_inventory(prompt_rows)
    snapshot_mapping_template = _build_snapshot_mapping_template(prompt_rows)
    prompt_dependency_tree = _build_prompt_dependency_tree(prompt_rows)
    prompt_risk_matrix = _build_prompt_risk_matrix(prompt_rows)
    reconciliation_rules = _build_reconciliation_rules()
    stop_conditions = _build_stop_conditions_payload(dict(inputs.get("stop_conditions") or {}))

    return {
        "final_prompt_inventory": final_prompt_inventory,
        "prompt_dependency_tree": prompt_dependency_tree,
        "prompt_risk_matrix": prompt_risk_matrix,
        "repo_reality_reconciliation_rules": reconciliation_rules,
        "snapshot_mapping_template": snapshot_mapping_template,
        "stop_conditions": stop_conditions,
        "docs": {
            FINAL_PROMPT_INVENTORY_DOC_REL: _render_inventory_doc(prompt_rows, final_prompt_inventory),
            PI_2_FINAL_REL: _render_pi_2_final_doc(final_prompt_inventory, prompt_dependency_tree, snapshot_mapping_template, prompt_risk_matrix),
            PROMPT_DEPENDENCY_TREE_DOC_REL: _render_dependency_tree_doc(prompt_dependency_tree),
            PROMPT_EXECUTION_CHECKLIST_DOC_REL: _render_checklist_doc(prompt_rows),
            PROMPT_RISK_MATRIX_DOC_REL: _render_risk_matrix_doc(prompt_risk_matrix),
            RECONCILIATION_GUIDE_DOC_REL: _render_reconciliation_guide_doc(reconciliation_rules),
            SNAPSHOT_MAPPING_TEMPLATE_DOC_REL: _render_snapshot_mapping_doc(prompt_rows, snapshot_mapping_template),
        },
    }


def write_final_prompt_inventory_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> None:
    root = _repo_root(repo_root)
    _write_canonical_json(_repo_abs(root, FINAL_PROMPT_INVENTORY_REL), dict(snapshot.get("final_prompt_inventory") or {}))
    _write_canonical_json(_repo_abs(root, SNAPSHOT_MAPPING_TEMPLATE_REL), dict(snapshot.get("snapshot_mapping_template") or {}))
    _write_canonical_json(_repo_abs(root, PROMPT_DEPENDENCY_TREE_REL), dict(snapshot.get("prompt_dependency_tree") or {}))
    _write_canonical_json(_repo_abs(root, PROMPT_RISK_MATRIX_REL), dict(snapshot.get("prompt_risk_matrix") or {}))
    _write_canonical_json(_repo_abs(root, RECONCILIATION_RULES_REL), dict(snapshot.get("repo_reality_reconciliation_rules") or {}))
    _write_canonical_json(_repo_abs(root, STOP_CONDITIONS_REL), dict(snapshot.get("stop_conditions") or {}))
    docs = dict(snapshot.get("docs") or {})
    for rel_path, text in sorted(docs.items()):
        _write_text(_repo_abs(root, rel_path), str(text))


__all__ = [
    "FINAL_PROMPT_INVENTORY_DOC_REL",
    "FINAL_PROMPT_INVENTORY_REL",
    "PI_2_FINAL_REL",
    "PROMPT_DEPENDENCY_TREE_DOC_REL",
    "PROMPT_DEPENDENCY_TREE_REL",
    "PROMPT_EXECUTION_CHECKLIST_DOC_REL",
    "PROMPT_RISK_MATRIX_DOC_REL",
    "PROMPT_RISK_MATRIX_REL",
    "RECONCILIATION_GUIDE_DOC_REL",
    "RECONCILIATION_RULES_REL",
    "SNAPSHOT_MAPPING_TEMPLATE_DOC_REL",
    "SNAPSHOT_MAPPING_TEMPLATE_REL",
    "STOP_CONDITIONS_REL",
    "build_final_prompt_inventory_snapshot",
    "write_final_prompt_inventory_snapshot",
]

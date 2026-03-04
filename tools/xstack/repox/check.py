#!/usr/bin/env python3
"""Minimal deterministic RepoX policy scan for XStack profile runs."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from typing import Dict, Iterable, List, Set, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


FORBIDDEN_IDENTIFIERS = (
    "survival_mode",
    "creative_mode",
    "hardcore_mode",
    "spectator_mode",
    "debug_mode",
    "godmode",
    "sandbox",
)

RESERVED_WORDS = (
    "deterministic",
    "law",
    "authority",
    "lens",
    "canonical",
    "identity",
    "collapse",
    "expand",
    "macro",
    "micro",
    "process",
    "refusal",
)

SCAN_ROOTS = (
    "client/observability",
    "client/presentation",
    "worldgen",
    "tools/xstack/compatx",
    "tools/xstack/pack_loader",
    "tools/xstack/pack_contrib",
    "tools/xstack/registry_compile",
    "tools/xstack/controlx",
    "tools/xstack/repox",
    "tools/xstack/auditx",
    "tools/xstack/testx",
    "tools/xstack/performx",
    "tools/xstack/securex",
    "tools/xstack/sessionx",
    "tools/domain",
    "tools/xstack/bundle_list.py",
    "tools/xstack/bundle_validate.py",
    "tools/xstack/session_create.py",
    "tools/xstack/session_boot.py",
    "tools/worldgen_offline",
    "schemas",
    "schema/worldgen",
    "data/registries/domain_registry.json",
    "data/registries/domain_contract_registry.json",
    "data/registries/solver_registry.json",
    "data/registries/net_replication_policy_registry.json",
    "data/registries/net_resync_strategy_registry.json",
    "data/registries/anti_cheat_policy_registry.json",
    "data/registries/anti_cheat_module_registry.json",
    "data/registries/worldgen_constraints_registry.json",
    "data/registries/worldgen_module_registry.json",
    "packs",
    "bundles",
    "docs/contracts",
    "docs/net",
    "docs/testing",
    "docs/worldgen",
    "docs/architecture/registry_compile.md",
    "docs/architecture/lockfile.md",
    "docs/architecture/pack_system.md",
    "docs/architecture/session_lifecycle.md",
)

TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hh",
    ".hpp",
    ".cmd",
    ".json",
    ".md",
    ".py",
    ".schema.json",
    ".schema",
    ".txt",
    ".yaml",
    ".yml",
}

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')
RENDERER_TRUTH_INCLUDE_FORBIDDEN = {
    "domino/truth_model_v1.h",
    "domino/truth_model.h",
}

SESSION_PIPELINE_REQUIRED_FILES = (
    "schemas/session_spec.schema.json",
    "schemas/session_stage.schema.json",
    "schemas/session_pipeline.schema.json",
    "data/registries/session_stage_registry.json",
    "data/registries/session_pipeline_registry.json",
)

DOMAIN_FOUNDATION_REQUIRED_FILES = (
    "data/registries/domain_registry.json",
    "data/registries/domain_contract_registry.json",
    "data/registries/solver_registry.json",
)

CONTRACT_STABILITY_BASELINE_IDS = (
    "dom.contract.mass_conservation",
    "dom.contract.energy_conservation",
    "dom.contract.charge_conservation",
    "dom.contract.ledger_balance",
    "dom.contract.epistemic_non_omniscience",
    "dom.contract.deterministic_transition",
    "dom.contract.port_contract_preservation",
)

DOMAIN_TOKEN_ALLOWED_PATH_PREFIXES = (
    "data/registries/domain_registry.json",
    "data/registries/solver_registry.json",
    "docs/scale/",
    "schema/scale/",
    "schemas/domain_",
    "schemas/solver_registry.schema.json",
    "tools/domain/",
)

CONTRACT_TOKEN_ALLOWED_PATH_PREFIXES = (
    "data/registries/domain_registry.json",
    "data/registries/domain_contract_registry.json",
    "data/registries/solver_registry.json",
    "docs/scale/",
    "schema/scale/",
    "schemas/domain_foundation_registry.schema.json",
    "schemas/domain_contract_registry.schema.json",
    "schemas/solver_registry.schema.json",
    "tools/domain/",
    "tools/xstack/testx/tests/",
)

NEGATIVE_SCAN_ROOTS = (
    "engine",
    "game",
    "client",
    "server",
    "tools",
    "launcher",
    "setup",
)

NEGATIVE_SCAN_EXCLUDED_PREFIXES = (
    "tools/xstack/out/",
    "tools/xstack/testdata/",
    "tools/xstack/testx/tests/",
    "tools/auditx/cache/",
    "build/",
    "dist/",
    "docs/",
    "data/",
)

NEGATIVE_SCAN_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hh",
    ".hpp",
    ".py",
    ".cmd",
}

SCHEMA_READ_ALLOWED_PREFIXES = (
    "tools/xstack/compatx/",
    "tools/xstack/schema_validate.py",
    "tools/domain/",
)

SESSION_PIPELINE_ALLOWED_PREFIXES = (
    "tools/xstack/sessionx/",
    "tools/xstack/session_boot.py",
    "tools/xstack/session_control.py",
    "tools/xstack/session_server.py",
    "tools/xstack/session_surface.py",
)

CONTROL_MUTATION_ALLOWED_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/sessionx/creator.py",
    "tools/xstack/testx/tests/",
)

BODY_MUTATION_ALLOWED_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/sessionx/creator.py",
    "tools/xstack/testx/tests/",
)

CIV_MUTATION_ALLOWED_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/sessionx/creator.py",
    "tools/xstack/testx/tests/",
)

REPRESENTATION_RENDER_ONLY_FILES = (
    "src/client/render/render_model_adapter.py",
    "src/client/render/representation_resolver.py",
    "tools/xstack/sessionx/render_model.py",
)

RENDERER_RENDERMODEL_ONLY_FILES = (
    "src/client/render/render_model_adapter.py",
    "src/client/render/representation_resolver.py",
    "src/client/render/snapshot_capture.py",
    "src/client/render/renderers/null_renderer.py",
    "src/client/render/renderers/software_renderer.py",
    "tools/xstack/sessionx/render_model.py",
    "tools/render/tool_render_capture.py",
    "tools/render/render_cli.py",
)

RENDER_SNAPSHOT_DERIVED_FILES = (
    "src/client/render/snapshot_capture.py",
    "src/client/render/renderers/null_renderer.py",
    "src/client/render/renderers/software_renderer.py",
    "tools/render/tool_render_capture.py",
)

INTENT_DISPATCH_WHITELIST_REGISTRY_REL = "data/registries/intent_dispatch_whitelist.json"
DEPRECATIONS_REGISTRY_REL = "data/governance/deprecations.json"
DEFAULT_INTENT_DISPATCH_ALLOWED_PATTERNS = (
    "src/net/**",
    "src/control/**",
    "tools/xstack/testx/tests/**",
)

BOUNDARY_ALIAS_RULES = {
    "INV-NO-DUPLICATE-GRAPH-SUBSTRATE": {
        "INV-NO-DUPLICATE-GRAPH",
        "INV-NO-DUPLICATE-GRAPH-SUBSTRATES",
    },
    "INV-NO-DUPLICATE-FLOW-SUBSTRATE": {
        "INV-NO-DUPLICATE-FLOW",
        "INV-NO-DUPLICATE-FLOW-LOGIC",
    },
    "INV-RENDER-TRUTH-ISOLATION": {
        "INV-RENDERER-TRUTH-ISOLATION",
        "repox.renderer_truth_import",
        "repox.renderer_truth_symbol",
    },
    "INV-NO-PRODUCTION-LEGACY-IMPORT": {
        "INV-NO-LEGACY-REFERENCE",
    },
    "INV-CONTROL-PLANE-ONLY-DISPATCH": {
        "INV-NO-DIRECT-INTENT-ENVELOPE-CONSTRUCTION",
        "INV-NO-DIRECT-INTENT-DISPATCH",
    },
    "INV-DECISION-LOG-MANDATORY": {
        "INV-DECISION-LOG-REQUIRED",
    },
    "INV-NO-MODE-FLAGS": {
        "repox.forbidden_identifier",
        "repox.mode_flag_heuristic",
    },
    "INV-NO-TRUTH-ACCESS-IN-RENDER": {
        "INV-RENDERER-TRUTH-ISOLATION",
        "INV-RENDERER-CONSUMES-RENDERMODEL-ONLY",
    },
    "INV-LOSS-MAPPED-TO-HEAT": {
        "INV-LOSS-MUST-DECLARE-TARGET",
    },
    "INV-PHYS-PROFILE-DECLARED": {
        "INV-PHYSICS-PROFILE-IN-IDENTITY",
    },
    "INV-FIELD-MUTATION-THROUGH-PROCESS": {
        "INV-FIELD-MUTATION-PROCESS-ONLY",
    },
}

BOUNDARY_BLOCKER_RULE_IDS = (
    "INV-NO-DUPLICATE-GRAPH-SUBSTRATE",
    "INV-NO-DUPLICATE-FLOW-SUBSTRATE",
    "INV-NO-ADHOC-STATE-FLAG",
    "INV-NO-ADHOC-TEMP-MODIFIERS",
    "INV-NO-ADHOC-SCHEDULER",
    "INV-PLATFORM-ISOLATION",
    "INV-RENDER-TRUTH-ISOLATION",
    "INV-NO-TOOLS-IN-RUNTIME",
    "INV-NO-DIRECT-INTENT-ENVELOPE-CONSTRUCTION",
    "INV-CONTROL-PLANE-ONLY-DISPATCH",
    "INV-CONTROL-INTENT-REQUIRED",
    "INV-NO-PRODUCTION-LEGACY-IMPORT",
    "INV-NO-MACRO-BEHAVIOR-WITHOUT-IR",
    "INV-NO-DYNAMIC-EVAL",
    "INV-NO-DOMAIN-DOWNGRADE-LOGIC",
    "INV-DECISION-LOG-MANDATORY",
    "INV-NO-DOMAIN-FIDELITY-DOWNGRADE",
    "INV-FIDELITY-USES-ENGINE",
    "INV-NO-DIRECT-STRUCTURE-INSTALL",
    "INV-GHOST-IS-DERIVED",
    "INV-VIEW-CHANGES-THROUGH-CONTROL",
    "INV-NO-DIRECT-CAMERA-TOGGLE",
    "INV-NO-TRUTH-ACCESS-IN-RENDER",
    "INV-NO-TYPE-BRANCHING",
    "INV-CAPABILITY-REGISTRY-REQUIRED",
    "INV-DOMAIN-CONTROL-REGISTERED",
    "INV-NO-HARDCODED-GAUGE-WIDTH-SPECS",
    "INV-SPECSHEET-OPTIONAL",
    "INV-INFERENCE-DERIVED-ONLY",
    "INV-FORMALIZATION-THROUGH-CONTROL",
    "INV-NO-ADHOC-LOAD-CHECK",
    "INV-STRUCTURAL-FAILURE-THROUGH-MECH",
    "INV-NO-ADHOC-WEATHER-FLAGS",
    "INV-FIELD-QUERIES-ONLY",
    "INV-FIELD-TYPE-REGISTERED",
    "INV-FIELD-MUTATION-THROUGH-PROCESS",
    "INV-NO-ADHOC-SAFETY-LOGIC",
    "INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL",
    "INV-PHYS-PROFILE-DECLARED",
    "INV-UNREGISTERED-QUANTITY-FORBIDDEN",
    "INV-LOSS-MAPPED-TO-HEAT",
    "INV-LOSS-MUST-DECLARE-TARGET",
    "INV-INFO-ARTIFACT-MUST-HAVE-FAMILY",
    "INV-TIER-CONTRACT-REQUIRED",
    "INV-COUPLING-CONTRACT-REQUIRED",
    "INV-EXPLAIN-CONTRACT-REQUIRED",
    "INV-NO-UNDECLARED-COUPLING",
    "INV-REALISM-DETAIL-MUST-BE-MODEL",
    "INV-NO-VEHICLE-SPECIALCASE",
    "INV-VEHICLES-AS-ASSEMBLIES",
    "INV-SPEC-COMPATIBILITY-REQUIRED",
    "INV-TRAVEL-THROUGH-COMMITMENTS",
    "INV-NO-SILENT-POSITION-UPDATES",
    "INV-NO-DIRECT-VELOCITY-MUTATION",
    "INV-FORCE-THROUGH-PROCESS",
    "INV-MOMENTUM-STATE-DECLARED",
    "INV-ENERGY-TRANSFORM-REGISTERED",
    "INV-NO-DIRECT-ENERGY-MUTATION",
    "INV-ENTROPY-UPDATE-THROUGH-ENGINE",
    "INV-NO-SILENT-EFFICIENCY-DROP",
)

PLATFORM_ABSTRACTION_FILES = (
    "src/platform/__init__.py",
    "src/platform/platform_window.py",
    "src/platform/platform_input.py",
    "src/platform/platform_gfx.py",
    "src/platform/platform_audio.py",
    "src/platform/platform_input_routing.py",
)

HW_RENDERER_RENDERMODEL_ONLY_FILES = (
    "src/client/render/renderers/hw_renderer_gl.py",
    "src/client/render/snapshot_capture.py",
)

REPRESENTATION_DATA_DRIVEN_FILE = "src/client/render/representation_resolver.py"
REPRESENTATION_DATA_DRIVEN_REQUIRED_TOKENS = (
    "representation_rule_registry",
    "_rule_rows(",
    "_select_rule(",
)

COSMETIC_SEMANTIC_FORBIDDEN_TOKENS = (
    "collision_layer",
    "shape_type",
    "shape_parameters",
    "body_move_attempt",
    "speed_scalar",
    "velocity_mm_per_tick",
)

INTERACTION_UI_SURFACE_FILES = (
    "src/client/interaction/affordance_generator.py",
    "src/client/interaction/interaction_dispatch.py",
    "src/client/interaction/preview_generator.py",
    "src/client/interaction/inspection_overlays.py",
    "src/client/interaction/interaction_panel.py",
    "tools/xstack/sessionx/interaction.py",
    "tools/interaction/interaction_cli.py",
)

PUBLIC_INTERACTION_ENTRYPOINT_REQUIREMENTS = {
    "src/client/interaction/interaction_dispatch.py": (
        "def run_interaction_command(",
        "def build_interaction_control_intent(",
        "build_control_intent(",
        "build_control_resolution(",
    ),
    "tools/interaction/interaction_cli.py": (
        "run_interaction_command(",
    ),
    "tools/xstack/sessionx/interaction.py": (
        "run_interaction_command(",
    ),
}

UI_DIRECT_PROCESS_SCAN_ROOTS = (
    "src/client/interaction/",
    "tools/interaction/",
    "tools/xstack/sessionx/interaction.py",
)

UI_DIRECT_PROCESS_ALLOWED_FILES = (
    "src/client/interaction/interaction_dispatch.py",
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/testx/tests/",
    "tools/auditx/analyzers/",
)

INTERACTION_DISPATCH_ALLOWED_DIRECT_PROCESS_FILE = "src/client/interaction/interaction_dispatch.py"
INTERACTION_AFFORDANCE_FILE = "src/client/interaction/affordance_generator.py"
ACTION_SURFACE_ENGINE_FILE = "src/interaction/action_surface_engine.py"
ACTION_SURFACE_REGISTRY_FILES = (
    "data/registries/surface_type_registry.json",
    "data/registries/tool_tag_registry.json",
    "data/registries/surface_visibility_policy_registry.json",
)
TOOL_REGISTRY_FILES = (
    "data/registries/tool_type_registry.json",
    "data/registries/tool_effect_model_registry.json",
)
MACHINE_REGISTRY_FILES = (
    "data/registries/port_type_registry.json",
    "data/registries/machine_type_registry.json",
    "data/registries/machine_operation_registry.json",
    "data/registries/port_visibility_policy_registry.json",
)
INTERACTION_TRUTH_MUTATION_FORBIDDEN_KEYS = (
    "agent_states",
    "world_assemblies",
    "active_law_references",
    "session_references",
    "history_anchors",
    "camera_assemblies",
    "time_control",
    "process_log",
    "faction_assemblies",
    "affiliations",
    "territory_assemblies",
    "diplomatic_relations",
    "cohort_assemblies",
    "body_assemblies",
    "interest_regions",
    "macro_capsules",
    "micro_regions",
    "performance_state",
)

PLAYER_LITERAL_ALLOWED_PATH_PREFIXES = (
    "data/",
    "docs/",
    "schemas/",
    "tools/auditx/",
    "tools/xstack/testx/tests/",
    "tools/xstack/repox/check.py",
)

PLAYER_FACTION_LITERAL_ALLOWED_PATH_PREFIXES = (
    "data/",
    "docs/",
    "schemas/",
    "tools/auditx/",
    "tools/xstack/testx/tests/",
    "tools/xstack/repox/check.py",
)

PLAYER_DIEGETIC_REQUIRED_FILES = (
    "packs/law/law.player.diegetic_default/data/law_profile.player.diegetic_default.json",
    "packs/experience/profile.player.default/data/experience_profile.player.default.json",
    "packs/tool/workspace.player.diegetic_default/pack.json",
)

PLAYER_DEBUG_WINDOW_PREFIXES = (
    "window.tool.",
    "window.observer.",
)

PLAYER_DEBUG_WINDOW_IDS = (
    "window.spectator.follow_controls",
    "window.spectator.scoreboard_stub",
)

PLAYER_DEFAULT_FORBIDDEN_PROCESSES = (
    "process.camera_teleport",
    "process.control_set_view_lens",
    "process.observe.telemetry",
    "process.time_control_set_rate",
    "process.time_pause",
    "process.time_resume",
)

PLAYER_DEBUG_FORBIDDEN_ENTITLEMENTS = (
    "entitlement.control.admin",
    "entitlement.debug_view",
    "entitlement.inspect",
    "entitlement.teleport",
    "entitlement.time_control",
    "lens.nondiegetic.access",
)

WORLDGEN_CONSTRAINT_REQUIRED_FILES = (
    "schemas/worldgen_constraints.schema.json",
    "schemas/worldgen_search_plan.schema.json",
    "data/registries/worldgen_constraints_registry.json",
)

WORLDGEN_CONSTRAINT_LITERAL_ALLOWED_PATH_PREFIXES = (
    "packs/",
    "bundles/",
    "data/registries/worldgen_constraints_registry.json",
    "docs/worldgen/",
    "schema/worldgen/",
    "schemas/",
    "schemas/worldgen_constraints.schema.json",
    "schemas/worldgen_search_plan.schema.json",
    "schemas/worldgen_constraints_registry.schema.json",
    "tools/xstack/testx/tests/",
    "tools/worldgen_offline/",
    "worldgen/core/constraint_solver.py",
    "worldgen/core/constraint_commands.py",
)

WORLDGEN_SEED_POLICY_FORBIDDEN_TOKENS = (
    "import random",
    "from random import",
    "random.",
    "import secrets",
    "from secrets import",
    "secrets.",
    "uuid.uuid4(",
    "time.time(",
    "datetime.now(",
)

MULTIPLAYER_NET_SCHEMA_NAMES = (
    "net_intent_envelope",
    "net_tick_intent_list",
    "net_hash_anchor_frame",
    "net_snapshot",
    "net_delta",
    "net_perceived_delta",
    "net_handshake",
    "net_anti_cheat_event",
)

MULTIPLAYER_POLICY_REGISTRY_FILES = (
    "data/registries/net_replication_policy_registry.json",
    "data/registries/net_resync_strategy_registry.json",
    "data/registries/net_server_policy_registry.json",
    "data/registries/securex_policy_registry.json",
    "data/registries/server_profile_registry.json",
    "data/registries/shard_map_registry.json",
    "data/registries/perception_interest_policy_registry.json",
    "data/registries/anti_cheat_policy_registry.json",
    "data/registries/anti_cheat_module_registry.json",
)

ANTI_CHEAT_REQUIRED_POLICY_IDS = (
    "policy.ac.detect_only",
    "policy.ac.casual_default",
    "policy.ac.rank_strict",
    "policy.ac.private_relaxed",
)
ANTI_CHEAT_ALLOWED_ACTIONS = (
    "audit",
    "refuse",
    "throttle",
    "terminate",
    "require_attestation",
)

NET_POLICY_LITERAL_ALLOWED_PATH_PREFIXES = (
    "data/registries/",
    "docs/net/",
    "docs/contracts/",
    "schemas/",
    "tools/xstack/testx/tests/",
    "tools/auditx/",
    "tools/xstack/registry_compile/",
    "tools/xstack/sessionx/",
    "tools/xstack/repox/",
)

PHYSICS_LITERAL_ALLOWED_PATH_PREFIXES = (
    "packs/",
    "data/registries/",
    "docs/",
    "schemas/",
    "tools/auditx/",
    "tools/xstack/testx/tests/",
    "tools/xstack/repox/check.py",
)

BLUEPRINT_LITERAL_ALLOWED_PATH_PREFIXES = (
    "packs/",
    "data/registries/",
    "docs/",
    "schemas/",
    "schema/",
    "tools/auditx/",
    "tools/xstack/testx/tests/",
    "tools/xstack/repox/check.py",
)

AUDITX_FINDINGS_PATH = "docs/audit/auditx/FINDINGS.json"
AUDITX_RUNTIME_PROBE_OUTPUT_ROOT = ".xstack_cache/auditx/repox_probe"
AUDITX_HIGH_RISK_CONFIDENCE = 0.85
AUDITX_HIGH_RISK_THRESHOLD = 15
AUDITX_HARD_FAIL_CONFIDENCE = 0.8
AUDITX_HARD_FAIL_ANALYZER_RULES = {
    "E129_CONTROL_PLANE_BYPASS_SMELL": "INV-CONTROL-PLANE-ONLY-DISPATCH",
}

CI_LANE_WORKFLOW_PATH = ".github/workflows/xstack_lanes.yml"
CI_LANE_REQUIRED_JOBS = (
    "ci-dev",
    "ci-verify",
    "ci-dist",
)
CI_DEV_FORBIDDEN_PACKAGING_TOKENS = (
    "tools/setup/build",
    "tools/setup/build.py",
    "build_dist_layout",
    "packaging.verify",
    "dist/",
    "build/dist",
)

REGRESSION_LOCK_PATH = "data/regression/observer_baseline.json"
REGRESSION_LOCK_REQUIRED_FIELDS = (
    "baseline_id",
    "bundle_id",
    "composite_hash_anchor",
    "pack_lock_hash",
    "registry_hashes",
    "update_policy",
)

MULTIPLAYER_REGRESSION_LOCK_PATH = "data/regression/multiplayer_baseline.json"
MULTIPLAYER_REGRESSION_LOCK_REQUIRED_FIELDS = (
    "baseline_id",
    "bundle_id",
    "policy_baselines",
    "ranked_handshake_matrix_hash",
    "anti_cheat_fingerprint_hashes",
    "update_policy",
)

CONTROL_DECISION_REGRESSION_LOCK_PATH = "data/regression/control_decision_baseline.json"
CONTROL_DECISION_REGRESSION_LOCK_REQUIRED_FIELDS = (
    "baseline_id",
    "sequence_id",
    "fingerprint_cases",
    "sequence_fingerprint",
    "update_policy",
)

CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH = "data/regression/control_plane_full_baseline.json"
CONTROL_PLANE_FULL_REGRESSION_LOCK_REQUIRED_FIELDS = (
    "baseline_id",
    "scenario_id",
    "composite_control_plane_hash_anchor",
    "proof_bundle_fingerprint",
    "fidelity_allocation_fingerprint",
    "view_negotiation_fingerprint",
    "update_policy",
)

MAT_SCALE_REGRESSION_LOCK_PATH = "data/regression/mat_scale_baseline.json"
MAT_SCALE_REGRESSION_LOCK_REQUIRED_FIELDS = (
    "baseline_id",
    "scenario_id",
    "degradation_order_fingerprint",
    "hash_anchor_stream",
    "inspection_cache_hit_pattern",
    "update_policy",
)

CONSISTENCY_MATRIX_PATH = "docs/audit/CROSS_SYSTEM_CONSISTENCY_MATRIX.md"
CONSISTENCY_MATRIX_REQUIRED_SYSTEMS = (
    "Engine",
    "Game",
    "Client",
    "Server",
    "Launcher",
    "Setup",
    "Tools",
    "Packs",
    "Schemas",
    "Registries",
    "UI IR",
    "Worldgen",
    "SRZ",
    "XStack (RepoX/TestX/AuditX/PerformX/CompatX/SecureX)",
)
CONSISTENCY_MATRIX_REQUIRED_COLUMNS = (
    "State mutation authority",
    "Artifact generation",
    "Registry consumption",
    "Schema validation",
    "Capability enforcement",
    "Determinism enforcement",
    "Refusal emission",
    "Packaging interaction",
    "Versioning/BII stamping",
    "Logging/run-meta",
    "Derived artifact production",
)

STATUS_NOW_PATH = "docs/STATUS_NOW.md"
STATUS_NOW_REQUIRED_SECTIONS = (
    "## REAL",
    "## SOON",
    "## STUB",
    "## DEFERRED",
)

RUNTIME_PATH_PREFIXES = (
    "engine/",
    "game/",
    "client/",
    "server/",
    "launcher/",
    "setup/",
    "libs/",
)

DERIVED_PROVENANCE_REQUIRED_FIELDS = (
    "artifact_type_id",
    "source_pack_id",
    "source_hash",
    "generator_tool_id",
    "generator_tool_version",
    "schema_version",
    "input_merkle_hash",
    "pack_lock_hash",
    "deterministic",
)

DERIVED_JSON_PATH_PREFIX = "packs/derived/"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _severity_rank(value: str) -> int:
    token = str(value or "").strip().lower()
    if token == "warn":
        return 0
    if token == "fail":
        return 1
    if token == "refusal":
        return 2
    return 9


def _finding_id(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _finding(
    severity: str,
    file_path: str,
    line_number: int,
    snippet: str,
    message: str,
    rule_id: str,
) -> Dict[str, object]:
    token = "{}|{}|{}|{}|{}".format(rule_id, file_path, line_number, severity, message)
    return {
        "finding_id": _finding_id(token),
        "rule_id": str(rule_id),
        "severity": str(severity),
        "file_path": _norm(file_path),
        "line_number": int(line_number),
        "snippet": str(snippet),
        "message": str(message),
    }


def _scan_files(repo_root: str) -> List[str]:
    out: List[str] = []
    for root in SCAN_ROOTS:
        abs_path = os.path.join(repo_root, root.replace("/", os.sep))
        if os.path.isdir(abs_path):
            for walk_root, _dirs, files in os.walk(abs_path):
                for name in files:
                    rel = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                    lower = rel.lower()
                    _, ext = os.path.splitext(name.lower())
                    if lower.endswith(".schema.json"):
                        out.append(rel)
                        continue
                    if ext in TEXT_EXTENSIONS:
                        out.append(rel)
        elif os.path.isfile(abs_path):
            out.append(_norm(os.path.relpath(abs_path, repo_root)))
    return sorted(set(out))


def _iter_negative_code_files(repo_root: str) -> List[str]:
    out: List[str] = []
    for root in NEGATIVE_SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(dirs)
            files = sorted(files)
            for name in files:
                _, ext = os.path.splitext(name.lower())
                if ext not in NEGATIVE_SCAN_EXTENSIONS:
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith(NEGATIVE_SCAN_EXCLUDED_PREFIXES):
                    continue
                out.append(rel_path)
    return sorted(set(out))


def _iter_lines(repo_root: str, rel_path: str) -> Iterable[Tuple[int, str]]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle, start=1):
                yield idx, line.rstrip("\n")
    except (OSError, UnicodeDecodeError):
        return


def _status_from_findings(findings: List[Dict[str, object]]) -> str:
    severities = set(str(row.get("severity", "")) for row in findings)
    if "refusal" in severities:
        return "refusal"
    if "fail" in severities:
        return "fail"
    return "pass"


def _load_json_object(repo_root: str, rel_path: str) -> Tuple[dict, str]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _invariant_severity(profile: str) -> str:
    return "refusal" if str(profile).strip().upper() in ("STRICT", "FULL") else "fail"


def _strict_only_severity(profile: str) -> str:
    token = str(profile).strip().upper()
    return _invariant_severity(token) if token in ("STRICT", "FULL") else "warn"


def _deprecated_inline_response_curve_sites(repo_root: str) -> Set[Tuple[str, int]]:
    rel_path = "data/registries/deprecation_registry.json"
    payload, err = _load_json_object(repo_root, rel_path)
    if err:
        return set()
    rows = list((dict(payload.get("record") or {})).get("deprecations") or [])
    out: Set[Tuple[str, int]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).strip().lower()
        if status and status not in {"active", "warning"}:
            continue
        ext = dict(row.get("extensions") or {})
        invariant_id = str(ext.get("invariant_id", "")).strip()
        if invariant_id not in {"INV-REALISM-DETAIL-MUST-BE-MODEL", "INV-RESPONSE-CURVES-MUST-BE-MODELS"}:
            continue
        source_path = _norm(str(ext.get("source_path", "")).strip())
        line_start = int(max(0, int(ext.get("line_start", 0) or 0)))
        if source_path and line_start:
            out.add((source_path, line_start))
    return out


def _append_session_pipeline_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    missing = []
    for rel_path in SESSION_PIPELINE_REQUIRED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
    for rel_path in sorted(missing):
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required session pipeline contract file is missing",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
    if missing:
        return

    stage_registry, stage_err = _load_json_object(repo_root, "data/registries/session_stage_registry.json")
    pipeline_registry, pipeline_err = _load_json_object(repo_root, "data/registries/session_pipeline_registry.json")
    if stage_err or pipeline_err:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="session stage/pipeline registry JSON is invalid",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
        return

    stage_rows = (stage_registry.get("record") or {}).get("stages")
    pipeline_rows = (pipeline_registry.get("record") or {}).get("pipelines")
    if not isinstance(stage_rows, list) or not isinstance(pipeline_rows, list):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="session stage/pipeline registry record lists are missing",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
        return

    stage_map = {}
    for row in stage_rows:
        if not isinstance(row, dict):
            continue
        stage_id = str(row.get("stage_id", "")).strip()
        if stage_id:
            stage_map[stage_id] = row
    default_pipeline = {}
    for row in pipeline_rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("pipeline_id", "")).strip() == "pipeline.client.default":
            default_pipeline = row
            break
    if not default_pipeline:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="default pipeline.client.default is missing",
                rule_id="INV-SESSION-PIPELINE-DECLARED",
            )
        )
        return

    resolve_stage = dict(stage_map.get("stage.resolve_session") or {})
    allowed_from_resolve = sorted(
        set(str(item).strip() for item in (resolve_stage.get("allowed_next_stage_ids") or []) if str(item).strip())
    )
    if "stage.session_running" in allowed_from_resolve:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_stage_registry.json",
                line_number=1,
                snippet="",
                message="stage.resolve_session cannot directly transition to stage.session_running",
                rule_id="INV-NO-STAGE-SKIP",
            )
        )

    ready_stage = dict(stage_map.get("stage.session_ready") or {})
    allowed_from_ready = sorted(
        set(str(item).strip() for item in (ready_stage.get("allowed_next_stage_ids") or []) if str(item).strip())
    )
    if "stage.session_running" not in allowed_from_ready:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_stage_registry.json",
                line_number=1,
                snippet="",
                message="stage.session_ready must allow transition to stage.session_running",
                rule_id="INV-NO-STAGE-SKIP",
            )
        )

    order = [str(item).strip() for item in (default_pipeline.get("stages") or []) if str(item).strip()]
    required_order = ["stage.resolve_session", "stage.verify_world", "stage.session_ready", "stage.session_running"]
    if any(stage_id not in order for stage_id in required_order):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_pipeline_registry.json",
                line_number=1,
                snippet="",
                message="pipeline.client.default is missing required canonical stages",
                rule_id="INV-NO-STAGE-SKIP",
            )
        )
    else:
        indices = [int(order.index(stage_id)) for stage_id in required_order]
        if indices != sorted(indices):
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/session_pipeline_registry.json",
                    line_number=1,
                    snippet="",
                    message="pipeline.client.default stage order allows skip relative to running transition",
                    rule_id="INV-NO-STAGE-SKIP",
                )
            )

    ready_extensions = dict(ready_stage.get("extensions") or {})
    ready_tick = ready_extensions.get("ready_time_must_equal_tick")
    if int(ready_tick if ready_tick is not None else -1) != 0:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/session_stage_registry.json",
                line_number=1,
                snippet="",
                message="stage.session_ready must enforce simulation_time.tick == 0",
                rule_id="INV-SESSION-READY-TIME-ZERO",
            )
        )


def _append_multiplayer_contract_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    missing = []
    for rel_path in MULTIPLAYER_POLICY_REGISTRY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
    for rel_path in sorted(missing):
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required multiplayer policy registry file is missing",
                rule_id="INV-NET-POLICY-REGISTRIES-VALID",
            )
        )

    try:
        from tools.xstack.compatx.validator import validate_schema_example
    except Exception:
        validate_schema_example = None

    if validate_schema_example is None:
        findings.append(
            _finding(
                severity=severity,
                file_path="tools/xstack/compatx/validator.py",
                line_number=1,
                snippet="",
                message="unable to import schema validator for multiplayer schema checks",
                rule_id="INV-NET-SCHEMAS-VALID",
            )
        )
    else:
        for schema_name in MULTIPLAYER_NET_SCHEMA_NAMES:
            checked = validate_schema_example(repo_root=repo_root, schema_name=schema_name)
            if not bool(checked.get("valid", False)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="schemas/{}.schema.json".format(schema_name),
                        line_number=1,
                        snippet="",
                        message="multiplayer schema example validation failed for '{}'".format(schema_name),
                        rule_id="INV-NET-SCHEMAS-VALID",
                    )
                )

    if missing:
        return

    replication_payload, replication_err = _load_json_object(repo_root, "data/registries/net_replication_policy_registry.json")
    resync_payload, resync_err = _load_json_object(repo_root, "data/registries/net_resync_strategy_registry.json")
    server_policy_payload, server_policy_err = _load_json_object(repo_root, "data/registries/net_server_policy_registry.json")
    shard_map_payload, shard_map_err = _load_json_object(repo_root, "data/registries/shard_map_registry.json")
    perception_interest_payload, perception_interest_err = _load_json_object(
        repo_root,
        "data/registries/perception_interest_policy_registry.json",
    )
    anti_cheat_policy_payload, anti_cheat_policy_err = _load_json_object(repo_root, "data/registries/anti_cheat_policy_registry.json")
    anti_cheat_module_payload, anti_cheat_module_err = _load_json_object(repo_root, "data/registries/anti_cheat_module_registry.json")
    securex_policy_payload, securex_policy_err = _load_json_object(repo_root, "data/registries/securex_policy_registry.json")
    server_profile_payload, server_profile_err = _load_json_object(repo_root, "data/registries/server_profile_registry.json")
    if (
        replication_err
        or resync_err
        or server_policy_err
        or shard_map_err
        or perception_interest_err
        or anti_cheat_policy_err
        or anti_cheat_module_err
        or securex_policy_err
        or server_profile_err
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/net_replication_policy_registry.json",
                line_number=1,
                snippet="",
                message="one or more multiplayer policy registries are invalid JSON",
                rule_id="INV-NET-POLICY-REGISTRIES-VALID",
            )
        )
        return

    replication_rows = (((replication_payload.get("record") or {}).get("policies")) or [])
    resync_rows = (((resync_payload.get("record") or {}).get("strategies")) or [])
    server_policy_rows = (((server_policy_payload.get("record") or {}).get("policies")) or [])
    shard_map_rows = (((shard_map_payload.get("record") or {}).get("shard_maps")) or [])
    perception_interest_rows = (((perception_interest_payload.get("record") or {}).get("policies")) or [])
    anti_cheat_policy_rows = (((anti_cheat_policy_payload.get("record") or {}).get("policies")) or [])
    anti_cheat_module_rows = (((anti_cheat_module_payload.get("record") or {}).get("modules")) or [])
    securex_policy_rows = (((securex_policy_payload.get("record") or {}).get("policies")) or [])
    server_profile_rows = (((server_profile_payload.get("record") or {}).get("profiles")) or [])
    if (
        not isinstance(replication_rows, list)
        or not isinstance(resync_rows, list)
        or not isinstance(server_policy_rows, list)
        or not isinstance(shard_map_rows, list)
        or not isinstance(perception_interest_rows, list)
        or not isinstance(anti_cheat_policy_rows, list)
        or not isinstance(anti_cheat_module_rows, list)
        or not isinstance(securex_policy_rows, list)
        or not isinstance(server_profile_rows, list)
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/net_replication_policy_registry.json",
                line_number=1,
                snippet="",
                message="multiplayer policy registry record lists are missing",
                rule_id="INV-NET-POLICY-REGISTRIES-VALID",
            )
        )
        return

    shard_map_ids = set(
        str(row.get("shard_map_id", "")).strip()
        for row in shard_map_rows
        if isinstance(row, dict) and str(row.get("shard_map_id", "")).strip()
    )
    perception_policy_ids = set(
        str(row.get("policy_id", "")).strip()
        for row in perception_interest_rows
        if isinstance(row, dict) and str(row.get("policy_id", "")).strip()
    )

    resync_ids = set()
    for row in resync_rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("strategy_id", "")).strip()
        if token:
            resync_ids.add(token)

    replication_ids = set()
    for row in replication_rows:
        if not isinstance(row, dict):
            continue
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        replication_ids.add(policy_id)
        strategy_id = str(row.get("resync_strategy_id", "")).strip()
        if strategy_id and strategy_id not in resync_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/net_replication_policy_registry.json",
                    line_number=1,
                    snippet=policy_id,
                    message="replication policy '{}' references missing resync strategy '{}'".format(policy_id, strategy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )

    for row in resync_rows:
        if not isinstance(row, dict):
            continue
        strategy_id = str(row.get("strategy_id", "")).strip()
        for policy_id in sorted(set(str(item).strip() for item in (row.get("supported_policies") or []) if str(item).strip())):
            if policy_id not in replication_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_resync_strategy_registry.json",
                        line_number=1,
                        snippet=strategy_id,
                        message="resync strategy '{}' references missing replication policy '{}'".format(strategy_id, policy_id),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )

    module_ids = set()
    for row in anti_cheat_module_rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("module_id", "")).strip()
        if token:
            module_ids.add(token)

    anti_cheat_ids = set()
    for row in anti_cheat_policy_rows:
        if not isinstance(row, dict):
            continue
        policy_id = str(row.get("policy_id", "")).strip()
        if policy_id:
            anti_cheat_ids.add(policy_id)
        else:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/anti_cheat_policy_registry.json",
                    line_number=1,
                    snippet="",
                    message="anti-cheat policy entry is missing policy_id",
                    rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                )
            )
            continue
        modules_enabled = sorted(set(str(item).strip() for item in (row.get("modules_enabled") or []) if str(item).strip()))
        if not modules_enabled:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/anti_cheat_policy_registry.json",
                    line_number=1,
                    snippet=policy_id,
                    message="anti-cheat policy '{}' must declare non-empty modules_enabled".format(policy_id),
                    rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                )
            )
        for module_id in modules_enabled:
            if module_id not in module_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/anti_cheat_policy_registry.json",
                        line_number=1,
                        snippet=policy_id,
                        message="anti-cheat policy '{}' references missing module '{}'".format(policy_id, module_id),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        default_actions = row.get("default_actions")
        if isinstance(default_actions, dict):
            for module_id in sorted(default_actions.keys()):
                token = str(module_id).strip()
                if token and token not in module_ids:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/anti_cheat_policy_registry.json",
                            line_number=1,
                            snippet=policy_id,
                            message="anti-cheat policy '{}' default_actions references missing module '{}'".format(
                                policy_id,
                                token,
                            ),
                            rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                        )
                    )
                action_token = str(default_actions.get(module_id, "")).strip()
                if action_token and action_token not in ANTI_CHEAT_ALLOWED_ACTIONS:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/anti_cheat_policy_registry.json",
                            line_number=1,
                            snippet="{}={}".format(token, action_token),
                            message="anti-cheat policy '{}' default action '{}' is not allowed".format(policy_id, action_token),
                            rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                        )
                    )
            for module_id in modules_enabled:
                if module_id not in default_actions:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/anti_cheat_policy_registry.json",
                            line_number=1,
                            snippet=policy_id,
                            message="anti-cheat policy '{}' is missing default action for enabled module '{}'".format(
                                policy_id,
                                module_id,
                            ),
                            rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                        )
                    )
        else:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/anti_cheat_policy_registry.json",
                    line_number=1,
                    snippet=policy_id,
                    message="anti-cheat policy '{}' default_actions must be an object".format(policy_id),
                    rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
                )
            )

    for policy_id in sorted(set(ANTI_CHEAT_REQUIRED_POLICY_IDS) - set(anti_cheat_ids)):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/anti_cheat_policy_registry.json",
                line_number=1,
                snippet=policy_id,
                message="required anti-cheat policy '{}' is missing".format(policy_id),
                rule_id="INV-ANTI_CHEAT-POLICY-REGISTRY-VALID",
            )
        )

    securex_policy_ids = set(
        str(row.get("securex_policy_id", "")).strip()
        for row in securex_policy_rows
        if isinstance(row, dict) and str(row.get("securex_policy_id", "")).strip()
    )

    for row in server_policy_rows:
        if not isinstance(row, dict):
            continue
        server_policy_id = str(row.get("policy_id", "")).strip()
        for policy_id in row.get("allowed_replication_policy_ids") or []:
            token = str(policy_id).strip()
            if token and token not in replication_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' references missing replication policy '{}'".format(server_policy_id, token),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        allowed_anti_cheat_ids = []
        for policy_id in row.get("allowed_anti_cheat_policy_ids") or []:
            token = str(policy_id).strip()
            if token:
                allowed_anti_cheat_ids.append(token)
            if token and token not in anti_cheat_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' references missing anti-cheat policy '{}'".format(server_policy_id, token),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        required_anti_cheat_policy_id = str(row.get("required_anti_cheat_policy_id", "")).strip()
        if required_anti_cheat_policy_id and required_anti_cheat_policy_id not in allowed_anti_cheat_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/net_server_policy_registry.json",
                    line_number=1,
                    snippet=server_policy_id,
                    message="server policy '{}' required anti-cheat policy is not present in allowed_anti_cheat_policy_ids".format(
                        server_policy_id
                    ),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        securex_policy_id = str(row.get("securex_policy_id", "")).strip()
        if securex_policy_id and securex_policy_id not in securex_policy_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/net_server_policy_registry.json",
                    line_number=1,
                    snippet=server_policy_id,
                    message="server policy '{}' references missing securex policy '{}'".format(server_policy_id, securex_policy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        allowed_replication_ids = sorted(
            set(str(item).strip() for item in (row.get("allowed_replication_policy_ids") or []) if str(item).strip())
        )
        if "policy.net.srz_hybrid" in allowed_replication_ids:
            extensions = dict(row.get("extensions") or {})
            shard_map_id = str(extensions.get("default_shard_map_id", "")).strip()
            if not shard_map_id or shard_map_id not in shard_map_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' must declare a valid extensions.default_shard_map_id when srz_hybrid is allowed".format(
                            server_policy_id
                        ),
                        rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
                    )
                )
            perception_policy_id = str(extensions.get("perception_interest_policy_id", "")).strip()
            if not perception_policy_id or perception_policy_id not in perception_policy_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/net_server_policy_registry.json",
                        line_number=1,
                        snippet=server_policy_id,
                        message="server policy '{}' must declare a valid extensions.perception_interest_policy_id when srz_hybrid is allowed".format(
                            server_policy_id
                        ),
                        rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
                )
            )

    for row in server_profile_rows:
        if not isinstance(row, dict):
            continue
        server_profile_id = str(row.get("server_profile_id", "")).strip()
        securex_policy_id = str(row.get("securex_policy_id", "")).strip()
        anti_cheat_policy_id = str(row.get("anti_cheat_policy_id", "")).strip()
        allowed_replication_ids = sorted(
            set(str(item).strip() for item in (row.get("allowed_replication_policy_ids") or []) if str(item).strip())
        )
        required_replication_ids = sorted(
            set(str(item).strip() for item in (row.get("required_replication_policy_ids") or []) if str(item).strip())
        )
        allowed_law_profile_ids = sorted(
            set(str(item).strip() for item in (row.get("allowed_law_profile_ids") or []) if str(item).strip())
        )
        if securex_policy_id not in securex_policy_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/server_profile_registry.json",
                    line_number=1,
                    snippet=server_profile_id,
                    message="server profile '{}' references missing securex policy '{}'".format(server_profile_id, securex_policy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        if anti_cheat_policy_id not in anti_cheat_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/server_profile_registry.json",
                    line_number=1,
                    snippet=server_profile_id,
                    message="server profile '{}' references missing anti-cheat policy '{}'".format(server_profile_id, anti_cheat_policy_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )
        for policy_id in allowed_replication_ids + required_replication_ids:
            if policy_id not in replication_ids:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/server_profile_registry.json",
                        line_number=1,
                        snippet=server_profile_id,
                        message="server profile '{}' references missing replication policy '{}'".format(server_profile_id, policy_id),
                        rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                    )
                )
        if not allowed_law_profile_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/server_profile_registry.json",
                    line_number=1,
                    snippet=server_profile_id,
                    message="server profile '{}' must declare non-empty allowed_law_profile_ids".format(server_profile_id),
                    rule_id="INV-NET-POLICY-REGISTRIES-VALID",
                )
            )

    required_registry_refs = (
        (
            "tools/xstack/sessionx/net_handshake.py",
            (
                "replication_registry",
                "anti_cheat_registry",
                "server_policy_registry",
                "securex_policy_registry",
                "server_profile_registry",
            ),
        ),
    )
    for rel_path, required_tokens in required_registry_refs:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="net handshake implementation file is missing",
                    rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="unable to read net handshake implementation for registry-usage invariant",
                    rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                )
            )
            continue
        for token in required_tokens:
            if token not in text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="net handshake implementation is missing required registry reference token '{}'".format(token),
                        rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                    )
                )

    token_severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    hardcoded_policy_literal_pattern = re.compile(r"(policy\.net\.[a-z0-9_.-]+|policy\.ac\.[a-z0-9_.-]+)", re.IGNORECASE)
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if any(rel_norm.startswith(prefix) for prefix in NET_POLICY_LITERAL_ALLOWED_PATH_PREFIXES):
            continue
        _, ext = os.path.splitext(rel_norm.lower())
        if ext not in {".py", ".c", ".cc", ".cpp", ".h", ".hpp", ".hh", ".cxx", ".hxx"}:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            if hardcoded_policy_literal_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=token_severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="hardcoded network policy literal detected outside registry-governed paths",
                        rule_id="INV-NET-HANDSHAKE-USES-REGISTRIES",
                    )
                )

    flag_pattern = re.compile(r"\bif\s*\([^)]*(lockstep|server_authoritative|srz_hybrid)[^)]*\)", re.IGNORECASE)
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if any(rel_norm.startswith(prefix) for prefix in NET_POLICY_LITERAL_ALLOWED_PATH_PREFIXES):
            continue
        _, ext = os.path.splitext(rel_norm.lower())
        if ext not in {".py", ".c", ".cc", ".cpp", ".h", ".hpp", ".hh", ".cxx", ".hxx"}:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            if flag_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=token_severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="hardcoded network policy branch detected; select replication policy by policy_id",
                        rule_id="INV-NO-HARDCODED-NET-POLICY-FLAGS",
                    )
                )

    truth_net_pattern = re.compile(
        r"(truthmodel|truth_model).*(serialize|json|packet|socket|network|replication|delta|snapshot)"
        r"|"
        r"(serialize|json|packet|socket|network|replication|delta|snapshot).*(truthmodel|truth_model)",
        re.IGNORECASE,
    )
    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        if rel_norm.startswith(("tools/xstack/testx/tests/", "tools/auditx/", "tools/xstack/auditx/")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "truth_snapshot_hash" in lower:
                continue
            if truth_net_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="TruthModel network serialization smell detected; transmit PerceivedModel/snapshot hashes only",
                        rule_id="INV-NO-TRUTH-OVER-NET",
                    )
                )
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="network payload path must remain PerceivedModel-only and avoid TruthModel serialization",
                        rule_id="INV-NET-PERCEIVED-ONLY",
                    )
                )

    perceived_required = (
        ("src/net/policies/policy_server_authoritative.py", ("observe_truth(", "schema_name=\"net_perceived_delta\"")),
        ("src/net/srz/shard_coordinator.py", ("observe_truth(", "schema_name=\"net_perceived_delta\"")),
    )
    for rel_path, required_tokens in perceived_required:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="network perceived-only invariant target file is missing",
                    rule_id="INV-NET-PERCEIVED-ONLY",
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="unable to read file for perceived-only invariant",
                    rule_id="INV-NET-PERCEIVED-ONLY",
                )
            )
            continue
        for token in required_tokens:
            if token not in text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="network path missing required perceived-only token '{}'".format(token),
                        rule_id="INV-NET-PERCEIVED-ONLY",
                    )
                )

    law_registry_path = "data/registries/law_profiles.json"
    law_registry_payload, law_registry_err = _load_json_object(repo_root, law_registry_path)
    law_rows = []
    if not law_registry_err:
        law_rows = (((law_registry_payload.get("record") or {}).get("profiles")) or [])
        if isinstance(law_rows, list):
            for idx, row in enumerate(law_rows):
                if not isinstance(row, dict):
                    continue
                law_profile_id = str(row.get("law_profile_id", "")).strip() or "<unknown>"
                if not str(row.get("epistemic_policy_id", "")).strip():
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=law_registry_path,
                            line_number=1,
                            snippet=law_profile_id,
                            message="law profile '{}' is missing epistemic_policy_id".format(law_profile_id),
                            rule_id="INV-EPISTEMIC-POLICY-REQUIRED",
                        )
                    )
                if "survival" in law_profile_id.lower():
                    allowed_lenses = sorted(
                        set(str(item).strip().lower() for item in (row.get("allowed_lenses") or []) if str(item).strip())
                    )
                    if any("nondiegetic" in token for token in allowed_lenses):
                        findings.append(
                            _finding(
                                severity="warn",
                                file_path=law_registry_path,
                                line_number=1,
                                snippet=law_profile_id,
                                message="survival profile '{}' should default to diegetic lenses only".format(law_profile_id),
                                rule_id="INV-DIEGETIC-DEFAULTS-SURVIVAL",
                            )
                        )

    packs_law_root = os.path.join(repo_root, "packs", "law")
    if os.path.isdir(packs_law_root):
        for walk_root, dirs, files in os.walk(packs_law_root):
            dirs[:] = sorted(dirs)
            if "pack.json" not in files:
                continue
            data_root = os.path.join(walk_root, "data")
            if not os.path.isdir(data_root):
                continue
            for name in sorted(os.listdir(data_root)):
                if not str(name).lower().endswith(".json"):
                    continue
                abs_file = os.path.join(data_root, name)
                rel_file = _norm(os.path.relpath(abs_file, repo_root))
                payload, err = _load_json_object(repo_root, rel_file)
                if err:
                    continue
                if not str(payload.get("law_profile_id", "")).strip():
                    continue
                law_profile_id = str(payload.get("law_profile_id", "")).strip()
                if not str(payload.get("epistemic_policy_id", "")).strip():
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_file,
                            line_number=1,
                            snippet=law_profile_id,
                            message="pack law profile '{}' is missing epistemic_policy_id".format(law_profile_id),
                            rule_id="INV-EPISTEMIC-POLICY-REQUIRED",
                        )
                    )

    authoritative_rel = "src/net/policies/policy_server_authoritative.py"
    authoritative_abs = os.path.join(repo_root, authoritative_rel.replace("/", os.sep))
    if not os.path.isfile(authoritative_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=authoritative_rel,
                line_number=1,
                snippet="",
                message="server-authoritative policy implementation file is missing",
                rule_id="INV-AUTHORITATIVE-USES-PERCEIVED-ONLY",
            )
        )
    else:
        try:
            authoritative_lines = open(authoritative_abs, "r", encoding="utf-8").read().splitlines()
        except OSError:
            authoritative_lines = []
        authoritative_text = "\n".join(authoritative_lines)
        if "observe_truth(" not in authoritative_text or "schema_name=\"net_perceived_delta\"" not in authoritative_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=authoritative_rel,
                    line_number=1,
                    snippet="observe_truth/net_perceived_delta",
                    message="server-authoritative policy must derive outbound state through Observation Kernel perceived deltas",
                    rule_id="INV-AUTHORITATIVE-USES-PERCEIVED-ONLY",
                )
            )
        authoritative_truth_leak_pattern = re.compile(
            r"(send|socket|packet|transport|wire|payload_ref).*(truth_model|truthmodel|universe_state)"
            r"|"
            r"(truth_model|truthmodel|universe_state).*(send|socket|packet|transport|wire)",
            re.IGNORECASE,
        )
        for line_no, line in enumerate(authoritative_lines, start=1):
            lower = str(line).lower()
            if "truth_snapshot_hash" in lower:
                continue
            if authoritative_truth_leak_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=authoritative_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="server-authoritative policy must not transmit TruthModel/universe_state payload over net path",
                        rule_id="INV-AUTHORITATIVE-NO-TRUTH-TRANSMISSION",
                    )
                )

    srz_routing_rel = "src/net/srz/routing.py"
    srz_routing_abs = os.path.join(repo_root, srz_routing_rel.replace("/", os.sep))
    if not os.path.isfile(srz_routing_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=srz_routing_rel,
                line_number=1,
                snippet="",
                message="SRZ routing module is missing",
                rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
            )
        )
    else:
        try:
            srz_routing_text = open(srz_routing_abs, "r", encoding="utf-8").read()
        except OSError:
            srz_routing_text = ""
        required_tokens = ("def route_intent_envelope", "shard_index(", "shard_map", "site_registry")
        for token in required_tokens:
            if token not in srz_routing_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=srz_routing_rel,
                        line_number=1,
                        snippet=token,
                        message="SRZ routing must resolve targets from shard_map-driven metadata",
                        rule_id="INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP",
                    )
                )

    srz_coordinator_rel = "src/net/srz/shard_coordinator.py"
    srz_coordinator_abs = os.path.join(repo_root, srz_coordinator_rel.replace("/", os.sep))
    if not os.path.isfile(srz_coordinator_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=srz_coordinator_rel,
                line_number=1,
                snippet="",
                message="SRZ shard coordinator module is missing",
                rule_id="INV-NO-CROSS-SHARD-DIRECT-WRITES",
            )
        )
    else:
        try:
            srz_coordinator_text = open(srz_coordinator_abs, "r", encoding="utf-8").read()
        except OSError:
            srz_coordinator_text = ""
        if "owner_shard_id != target_shard_id" not in srz_coordinator_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=srz_coordinator_rel,
                    line_number=1,
                    snippet="owner_shard_id != target_shard_id",
                    message="SRZ coordinator must enforce owner-target shard mismatch checks before commit",
                    rule_id="INV-NO-CROSS-SHARD-DIRECT-WRITES",
                )
            )
        if "refusal.net.cross_shard_unsupported" not in srz_coordinator_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=srz_coordinator_rel,
                    line_number=1,
                    snippet="refusal.net.cross_shard_unsupported",
                    message="SRZ coordinator must refuse unsupported cross-shard direct writes deterministically",
                    rule_id="INV-NO-CROSS-SHARD-DIRECT-WRITES",
                )
            )


def _append_domain_foundation_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    missing = []
    for rel_path in DOMAIN_FOUNDATION_REQUIRED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
    for rel_path in sorted(missing):
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required domain foundation registry file is missing",
                rule_id="INV-DOMAIN-REGISTRY-VALID",
            )
        )
    if missing:
        return

    try:
        from tools.domain.tool_domain_validate import validate_domain_foundation
    except Exception:
        findings.append(
            _finding(
                severity=severity,
                file_path="tools/domain/tool_domain_validate.py",
                line_number=1,
                snippet="",
                message="unable to import domain foundation validator",
                rule_id="INV-DOMAIN-REGISTRY-VALID",
            )
        )
        return

    checked = validate_domain_foundation(repo_root=repo_root)
    if str(checked.get("result", "")) != "complete":
        for row in checked.get("errors") or []:
            if not isinstance(row, dict):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=str(row.get("path", "data/registries/domain_registry.json")),
                    line_number=1,
                    snippet="",
                    message=str(row.get("message", "")),
                    rule_id="INV-DOMAIN-REGISTRY-VALID",
                )
            )

    solver_payload, solver_err = _load_json_object(repo_root, "data/registries/solver_registry.json")
    if solver_err:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/solver_registry.json",
                line_number=1,
                snippet="",
                message="solver registry JSON is invalid",
                rule_id="INV-SOLVER-DOMAIN-BINDING",
            )
        )
    else:
        rows = solver_payload.get("records")
        if not isinstance(rows, list):
            findings.append(
                _finding(
                    severity=severity,
                    file_path="data/registries/solver_registry.json",
                    line_number=1,
                    snippet="",
                    message="solver registry records list is missing",
                    rule_id="INV-SOLVER-DOMAIN-BINDING",
                )
            )
        else:
            for idx, row in enumerate(rows):
                if not isinstance(row, dict):
                    continue
                solver_id = str(row.get("solver_id", "")).strip()
                domain_ids = [str(item).strip() for item in (row.get("domain_ids") or []) if str(item).strip()]
                contract_ids = [str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip()]
                if not domain_ids or not contract_ids:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="data/registries/solver_registry.json",
                            line_number=1,
                            snippet="",
                            message="solver '{}' at records[{}] must declare non-empty domain_ids and contract_ids".format(
                                solver_id or "<unknown>",
                                idx,
                            ),
                            rule_id="INV-SOLVER-DOMAIN-BINDING",
                        )
                    )

    contract_payload, contract_err = _load_json_object(repo_root, "data/registries/domain_contract_registry.json")
    if contract_err:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/domain_contract_registry.json",
                line_number=1,
                snippet="",
                message="domain contract registry JSON is invalid",
                rule_id="INV-CONTRACT-ID-STABILITY",
            )
        )
        return
    contract_rows = contract_payload.get("records")
    if not isinstance(contract_rows, list):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/domain_contract_registry.json",
                line_number=1,
                snippet="",
                message="domain contract registry records list is missing",
                rule_id="INV-CONTRACT-ID-STABILITY",
            )
        )
        return
    current_ids = set(
        str(row.get("contract_id", "")).strip()
        for row in contract_rows
        if isinstance(row, dict) and str(row.get("contract_id", "")).strip()
    )
    schema_version = str(contract_payload.get("schema_version", "")).strip()
    missing_baseline = sorted(set(CONTRACT_STABILITY_BASELINE_IDS) - current_ids)
    if schema_version == "1.0.0" and missing_baseline:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/domain_contract_registry.json",
                line_number=1,
                snippet="",
                message="contract IDs removed/renamed without schema version bump: {}".format(",".join(missing_baseline)),
                rule_id="INV-CONTRACT-ID-STABILITY",
            )
        )


def _worldgen_constraint_contributions(repo_root: str) -> List[Dict[str, str]]:
    packs_root = os.path.join(repo_root, "packs")
    if not os.path.isdir(packs_root):
        return []

    rows: List[Dict[str, str]] = []
    for walk_root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(dirs)
        if "pack.json" not in files:
            continue
        rel_manifest = _norm(os.path.relpath(os.path.join(walk_root, "pack.json"), repo_root))
        payload, err = _load_json_object(repo_root, rel_manifest)
        if err:
            continue
        pack_id = str(payload.get("pack_id", "")).strip()
        contributions = payload.get("contributions")
        if not isinstance(contributions, list):
            continue
        for idx, row in enumerate(contributions):
            if not isinstance(row, dict):
                continue
            if str(row.get("type", "")).strip() != "worldgen_constraints":
                continue
            contribution_id = str(row.get("id", "")).strip()
            contribution_path = str(row.get("path", "")).strip()
            rows.append(
                {
                    "manifest": rel_manifest,
                    "pack_id": pack_id,
                    "contribution_id": contribution_id,
                    "contribution_path": contribution_path,
                    "contribution_index": str(idx),
                }
            )
    return sorted(
        rows,
        key=lambda item: (
            str(item.get("pack_id", "")),
            str(item.get("contribution_id", "")),
            str(item.get("contribution_path", "")),
            str(item.get("manifest", "")),
        ),
    )


def _append_worldgen_constraint_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    for rel_path in WORLDGEN_CONSTRAINT_REQUIRED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required worldgen constraints contract file is missing",
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )

    try:
        from tools.xstack.compatx.validator import validate_instance
    except Exception:
        validate_instance = None

    registry_payload, registry_error = _load_json_object(repo_root, "data/registries/worldgen_constraints_registry.json")
    registry_entries = (((registry_payload.get("record") or {}).get("entries")) or []) if not registry_error else []
    registry_by_id: Dict[str, Dict[str, object]] = {}
    if registry_error:
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/worldgen_constraints_registry.json",
                line_number=1,
                snippet="",
                message="worldgen constraints registry JSON is invalid",
                rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
            )
        )
    elif not isinstance(registry_entries, list):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/worldgen_constraints_registry.json",
                line_number=1,
                snippet="",
                message="worldgen constraints registry entries list is missing",
                rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
            )
        )
    else:
        for idx, row in enumerate(registry_entries):
            if not isinstance(row, dict):
                continue
            constraints_id = str(row.get("constraints_id", "")).strip()
            if not constraints_id:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/worldgen_constraints_registry.json",
                        line_number=1,
                        snippet="",
                        message="entry[{}] missing constraints_id".format(idx),
                        rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                    )
                )
                continue
            if constraints_id in registry_by_id:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/worldgen_constraints_registry.json",
                        line_number=1,
                        snippet=constraints_id,
                        message="duplicate constraints_id '{}' in registry".format(constraints_id),
                        rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                    )
                )
                continue
            registry_by_id[constraints_id] = row

    contributions = _worldgen_constraint_contributions(repo_root)
    contribution_ids = set()
    for row in contributions:
        manifest = str(row.get("manifest", ""))
        pack_id = str(row.get("pack_id", ""))
        constraints_id = str(row.get("contribution_id", ""))
        contribution_path = str(row.get("contribution_path", ""))
        contribution_ids.add(constraints_id)
        if constraints_id not in registry_by_id:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=manifest,
                    line_number=1,
                    snippet=constraints_id,
                    message="worldgen constraints contribution id is missing from registry",
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )
            continue
        registry_entry = dict(registry_by_id.get(constraints_id) or {})
        expected_pack_id = str(registry_entry.get("pack_id", "")).strip()
        if expected_pack_id and pack_id and expected_pack_id != pack_id:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=manifest,
                    line_number=1,
                    snippet=constraints_id,
                    message="constraints registry pack_id mismatch for '{}'".format(constraints_id),
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )

        pack_manifest_dir = os.path.dirname(manifest)
        payload_rel_path = _norm(os.path.join(pack_manifest_dir, contribution_path))
        payload_abs_path = os.path.join(repo_root, payload_rel_path.replace("/", os.sep))
        if not os.path.isfile(payload_abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=manifest,
                    line_number=1,
                    snippet=contribution_path,
                    message="worldgen constraints contribution path does not exist",
                    rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
                )
            )
            continue

        payload, payload_error = _load_json_object(repo_root, payload_rel_path)
        if payload_error:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet="",
                    message="worldgen constraints payload JSON is invalid",
                    rule_id="INV-CONSTRAINT-SCHEMA-VALID",
                )
            )
            continue

        if validate_instance is None:
            findings.append(
                _finding(
                    severity=severity,
                    file_path="tools/xstack/compatx/validator.py",
                    line_number=1,
                    snippet="",
                    message="unable to import schema validator for worldgen constraints",
                    rule_id="INV-CONSTRAINT-SCHEMA-VALID",
                )
            )
        else:
            checked = validate_instance(
                repo_root=repo_root,
                schema_name="worldgen_constraints",
                payload=payload,
                strict_top_level=True,
            )
            if not bool(checked.get("valid", False)):
                for err in list(checked.get("errors") or [])[:10]:
                    if not isinstance(err, dict):
                        continue
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=payload_rel_path,
                            line_number=1,
                            snippet=str(err.get("path", "")),
                            message="worldgen constraints schema violation: {}".format(str(err.get("message", ""))),
                            rule_id="INV-CONSTRAINT-SCHEMA-VALID",
                        )
                    )

        policy = str(payload.get("deterministic_seed_policy", "")).strip()
        try:
            candidate_count = int(payload.get("candidate_count", 0))
        except (TypeError, ValueError):
            candidate_count = 0
        refusal_codes = sorted(
            set(str(item).strip() for item in (payload.get("refusal_codes") or []) if str(item).strip())
        )
        if policy not in ("single", "multi"):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet=policy,
                    message="deterministic_seed_policy must be single or multi",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )
        if policy == "single" and candidate_count != 1:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet="candidate_count={}".format(candidate_count),
                    message="single deterministic_seed_policy requires candidate_count == 1",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )
        if candidate_count < 1:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet="candidate_count={}".format(candidate_count),
                    message="candidate_count must be >= 1 for deterministic search",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )
        missing_refusals = sorted(
            set(("refusal.constraints_unsatisfiable", "refusal.search_exhausted")) - set(refusal_codes)
        )
        if missing_refusals:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=payload_rel_path,
                    line_number=1,
                    snippet=",".join(missing_refusals),
                    message="constraints artifact missing required refusal_codes",
                    rule_id="INV-DETERMINISTIC-SEED-POLICY",
                )
            )

    for constraints_id in sorted(set(registry_by_id.keys()) - set(contribution_ids)):
        findings.append(
            _finding(
                severity=severity,
                file_path="data/registries/worldgen_constraints_registry.json",
                line_number=1,
                snippet=constraints_id,
                message="registry constraints_id has no matching worldgen_constraints pack contribution",
                rule_id="INV-WORLDGEN-CONSTRAINTS-REGISTERED",
            )
        )

    constraint_solver_rel = "worldgen/core/constraint_solver.py"
    for line_no, line in _iter_lines(repo_root, constraint_solver_rel):
        lower = str(line).lower()
        for token in WORLDGEN_SEED_POLICY_FORBIDDEN_TOKENS:
            if token in lower:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=constraint_solver_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="forbidden nondeterministic seed source token '{}' detected".format(token),
                        rule_id="INV-DETERMINISTIC-SEED-POLICY",
                    )
                )


def _append_constraint_hardcode_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    rel_norm = _norm(rel_path)
    if any(rel_norm.startswith(prefix) for prefix in WORLDGEN_CONSTRAINT_LITERAL_ALLOWED_PATH_PREFIXES):
        return
    match = re.search(r'["\'](constraints\.[A-Za-z0-9_.-]+)["\']', line)
    if not match:
        return
    token = str(match.group(1))
    if token.startswith("constraints.worldgen."):
        return
    lower = line.lower()
    if "constraints_id" not in lower and "constraints-id" not in lower:
        return
    severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="hardcoded worldgen constraints_id literal detected outside registry/pack declarations",
            rule_id="INV-NO-HARDCODED-CONSTRAINT-LOGIC",
        )
    )


def _git_status_paths(repo_root: str) -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "-uall"],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return []
    if int(proc.returncode) != 0:
        return []
    rows = []
    for line in (proc.stdout or "").splitlines():
        token = str(line[3:] if len(line) >= 3 else line).strip()
        if token:
            rows.append(_norm(token))
    return sorted(set(rows))


def _runtime_status_paths(repo_root: str) -> List[str]:
    return sorted(path for path in _git_status_paths(repo_root) if path.startswith(RUNTIME_PATH_PREFIXES))


def _derived_artifact_files(repo_root: str) -> List[str]:
    root = os.path.join(repo_root, "packs", "derived")
    rows: List[str] = []
    if not os.path.isdir(root):
        return rows
    for walk_root, dirs, files in os.walk(root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not str(name).lower().endswith(".json"):
                continue
            if str(name).lower() == "pack.json":
                continue
            abs_path = os.path.join(walk_root, name)
            rows.append(_norm(os.path.relpath(abs_path, repo_root)))
    return sorted(set(rows))


def _append_derived_provenance_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    for rel_path in _derived_artifact_files(repo_root):
        payload, err = _load_json_object(repo_root, rel_path)
        if err:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="derived artifact payload must be valid JSON object",
                    rule_id="INV-DERIVED-HAS-PROVENANCE",
                )
            )
            continue
        provenance = payload.get("provenance")
        if not isinstance(provenance, dict):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="derived artifact is missing required provenance object",
                    rule_id="INV-DERIVED-HAS-PROVENANCE",
                )
            )
            continue
        for field in DERIVED_PROVENANCE_REQUIRED_FIELDS:
            token = provenance.get(field)
            if token is None or (isinstance(token, str) and not str(token).strip()):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=str(field),
                        message="derived provenance missing required field '{}'".format(field),
                        rule_id="INV-DERIVED-HAS-PROVENANCE",
                    )
                )
        if bool(provenance.get("deterministic", False)) is not True:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="deterministic={}".format(str(provenance.get("deterministic"))),
                    message="derived provenance deterministic flag must be true",
                    rule_id="INV-DERIVED-HAS-PROVENANCE",
                )
            )

        source_hash = str(provenance.get("source_hash", "")).strip()
        input_merkle_hash = str(provenance.get("input_merkle_hash", "")).strip()
        if source_hash.startswith("placeholder.") or input_merkle_hash.startswith("placeholder."):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="source_hash={} input_merkle_hash={}".format(source_hash, input_merkle_hash)[:140],
                    message="derived artifact appears hand-edited (placeholder provenance hashes)",
                    rule_id="INV-NO-HAND_EDITED-DERIVED",
                )
            )

        generator_tool = str(provenance.get("generator_tool_id", "")).strip()
        if generator_tool and not os.path.isfile(os.path.join(repo_root, generator_tool.replace("/", os.sep))):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=generator_tool,
                    message="derived provenance references missing generator tool path",
                    rule_id="INV-NO-HAND_EDITED-DERIVED",
                )
            )


def _append_auditx_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    abs_path = os.path.join(repo_root, AUDITX_FINDINGS_PATH.replace("/", os.sep))
    if os.path.isfile(abs_path):
        payload, err = _load_json_object(repo_root, AUDITX_FINDINGS_PATH)
        if err:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=AUDITX_FINDINGS_PATH,
                    line_number=1,
                    snippet="",
                    message="AuditX findings payload is invalid JSON",
                    rule_id="INV-AUDITX-REPORT-STRUCTURE",
                )
            )
        else:
            records = payload.get("findings")
            if not isinstance(records, list):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=AUDITX_FINDINGS_PATH,
                        line_number=1,
                        snippet="",
                        message="AuditX findings payload missing 'findings' list",
                        rule_id="INV-AUDITX-REPORT-STRUCTURE",
                    )
                )
            else:
                try:
                    from tools.auditx.model import validate_finding_record
                except Exception:
                    validate_finding_record = None
                if validate_finding_record is None:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path="tools/auditx/model/finding.py",
                            line_number=1,
                            snippet="",
                            message="unable to import AuditX finding validator",
                            rule_id="INV-AUDITX-REPORT-STRUCTURE",
                        )
                    )
                else:
                    for idx, row in enumerate(records):
                        if not isinstance(row, dict):
                            findings.append(
                                _finding(
                                    severity=severity,
                                    file_path=AUDITX_FINDINGS_PATH,
                                    line_number=1,
                                    snippet="",
                                    message="finding at index {} is not an object".format(idx),
                                    rule_id="INV-AUDITX-REPORT-STRUCTURE",
                                )
                            )
                            continue
                        for message in validate_finding_record(row):
                            findings.append(
                                _finding(
                                    severity=severity,
                                    file_path=AUDITX_FINDINGS_PATH,
                                    line_number=1,
                                    snippet="",
                                    message="finding[{}]: {}".format(idx, message),
                                    rule_id="INV-AUDITX-REPORT-STRUCTURE",
                                )
                            )
                            if len(findings) >= 250:
                                break
                        if len(findings) >= 250:
                            break

                high_risk = 0
                for row in records:
                    if not isinstance(row, dict):
                        continue
                    severity_token = str(row.get("severity", "")).strip().upper()
                    if severity_token not in ("RISK", "VIOLATION"):
                        continue
                    try:
                        confidence = float(row.get("confidence", 0.0))
                    except (TypeError, ValueError):
                        confidence = 0.0
                    if confidence >= AUDITX_HIGH_RISK_CONFIDENCE:
                        high_risk += 1

                hard_fail_rows = 0
                for row in records:
                    if not isinstance(row, dict):
                        continue
                    analyzer_id = str(row.get("analyzer_id", "")).strip()
                    rule_id = str(AUDITX_HARD_FAIL_ANALYZER_RULES.get(analyzer_id, "")).strip()
                    if not rule_id:
                        continue
                    severity_token = str(row.get("severity", "")).strip().upper()
                    if severity_token not in ("RISK", "VIOLATION"):
                        continue
                    try:
                        confidence = float(row.get("confidence", 0.0))
                    except (TypeError, ValueError):
                        confidence = 0.0
                    if confidence < AUDITX_HARD_FAIL_CONFIDENCE:
                        continue
                    location = dict(row.get("location") or {})
                    file_path = str(location.get("file_path", "")).strip() or AUDITX_FINDINGS_PATH
                    line_number = int(location.get("line_start", 1) or 1)
                    evidence_rows = [str(item).strip() for item in list(row.get("evidence") or []) if str(item).strip()]
                    snippet = str((evidence_rows[0] if evidence_rows else "")).strip()[:140]
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=file_path,
                            line_number=max(1, line_number),
                            snippet=snippet,
                            message="AuditX hard-fail analyzer {} reported {} (confidence={:.2f})".format(
                                analyzer_id,
                                severity_token.lower(),
                                confidence,
                            ),
                            rule_id=rule_id,
                        )
                    )
                    hard_fail_rows += 1
                    if hard_fail_rows >= 50:
                        break

                if high_risk >= AUDITX_HIGH_RISK_THRESHOLD:
                    findings.append(
                        _finding(
                            severity="warn",
                            file_path=AUDITX_FINDINGS_PATH,
                            line_number=1,
                            snippet="",
                            message="high-confidence AuditX risk findings exceed threshold ({} >= {})".format(
                                high_risk,
                                AUDITX_HIGH_RISK_THRESHOLD,
                            ),
                            rule_id="INV-AUDITX-REPORT-STRUCTURE",
                        )
                    )

    pre_runtime = _runtime_status_paths(repo_root)
    command = [
        sys.executable,
        "tools/auditx/auditx.py",
        "scan",
        "--repo-root",
        repo_root,
        "--changed-only",
        "--format",
        "json",
        "--output-root",
        AUDITX_RUNTIME_PROBE_OUTPUT_ROOT,
    ]
    try:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError:
        findings.append(
            _finding(
                severity="warn",
                file_path="tools/auditx/auditx.py",
                line_number=1,
                snippet="",
                message="AuditX probe scan unavailable in current environment",
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )
        return

    scan_output = str(proc.stdout or "")
    if int(proc.returncode) not in (0, 2):
        findings.append(
            _finding(
                severity=severity,
                file_path="tools/auditx/auditx.py",
                line_number=1,
                snippet=scan_output.strip()[:140],
                message="AuditX probe scan failed unexpectedly (exit={})".format(int(proc.returncode)),
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )
        return
    if "\"refusal_code\": \"refusal.git_unavailable\"" in scan_output:
        findings.append(
            _finding(
                severity="warn",
                file_path="tools/auditx/auditx.py",
                line_number=1,
                snippet="refusal.git_unavailable",
                message="AuditX changed-only probe reported git unavailable",
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )
        return

    post_runtime = _runtime_status_paths(repo_root)
    new_runtime_paths = sorted(set(post_runtime) - set(pre_runtime))
    for rel_path in new_runtime_paths:
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="AuditX scan modified tracked runtime path",
                rule_id="INV-AUDITX-RUN-DETERMINISTIC",
            )
        )


def _append_ci_lane_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    workflow_path = os.path.join(repo_root, CI_LANE_WORKFLOW_PATH.replace("/", os.sep))
    if not os.path.isfile(workflow_path):
        findings.append(
            _finding(
                severity=severity,
                file_path=CI_LANE_WORKFLOW_PATH,
                line_number=1,
                snippet="",
                message="required CI lane workflow is missing",
                rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
            )
        )
        return

    try:
        lines = open(workflow_path, "r", encoding="utf-8").read().splitlines()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=CI_LANE_WORKFLOW_PATH,
                line_number=1,
                snippet="",
                message="unable to read CI lane workflow",
                rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
            )
        )
        return

    lowered = "\n".join(lines).lower()
    for job_id in CI_LANE_REQUIRED_JOBS:
        marker = "\n  {}:".format(job_id)
        if marker not in ("\n" + lowered):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CI_LANE_WORKFLOW_PATH,
                    line_number=1,
                    snippet=job_id,
                    message="missing required CI lane job '{}'".format(job_id),
                    rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
                )
            )

    start = -1
    end = len(lines)
    for idx, line in enumerate(lines):
        if line.strip().lower() == "ci-dev:" and line.startswith("  "):
            start = idx
            break
    if start == -1:
        return
    for idx in range(start + 1, len(lines)):
        line = lines[idx]
        if re.match(r"^\s{2}[A-Za-z0-9_-]+:\s*$", line):
            end = idx
            break
    dev_block = "\n".join(lines[start:end]).lower()
    for token in CI_DEV_FORBIDDEN_PACKAGING_TOKENS:
        if str(token).lower() in dev_block:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CI_LANE_WORKFLOW_PATH,
                    line_number=start + 1,
                    snippet=str(token),
                    message="ci-dev lane must not invoke packaging token '{}'".format(token),
                    rule_id="INV-NO-PACKAGING-FROM-DEV-LANE",
                )
            )


def _append_regression_lock_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    payload, err = _load_json_object(repo_root, REGRESSION_LOCK_PATH)
    if err:
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="",
                message="observer regression baseline lock file is missing or invalid",
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )
        return
    for field in REGRESSION_LOCK_REQUIRED_FIELDS:
        value = payload.get(field)
        if value is None or (isinstance(value, str) and not str(value).strip()):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=str(field),
                    message="regression lock missing required field '{}'".format(field),
                    rule_id="INV-REGRESSION-LOCK-PRESENT",
                )
            )
    registry_hashes = payload.get("registry_hashes")
    if not isinstance(registry_hashes, dict):
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="registry_hashes",
                message="regression lock registry_hashes must be an object",
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )
    else:
        for key in ("ephemeris_registry_hash", "terrain_tile_registry_hash"):
            if not str(registry_hashes.get(key, "")).strip():
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=key,
                        message="regression lock missing required registry hash '{}'".format(key),
                        rule_id="INV-REGRESSION-LOCK-PRESENT",
                    )
                )

    update_policy = payload.get("update_policy")
    required_tag = ""
    if isinstance(update_policy, dict):
        required_tag = str(update_policy.get("required_commit_tag", "")).strip()
    if not required_tag:
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="update_policy.required_commit_tag",
                message="regression lock must declare update_policy.required_commit_tag",
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--pretty=%s", "--", REGRESSION_LOCK_PATH],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return
    if int(proc.returncode) != 0:
        return
    subject = str(proc.stdout or "").strip()
    if subject and required_tag not in subject:
        findings.append(
            _finding(
                severity=severity,
                file_path=REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=subject[:140],
                message="latest baseline commit message must include '{}'".format(required_tag),
                rule_id="INV-REGRESSION-LOCK-PRESENT",
            )
        )

    mp_payload, mp_err = _load_json_object(repo_root, MULTIPLAYER_REGRESSION_LOCK_PATH)
    if mp_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="",
                message="multiplayer regression baseline lock file is missing or invalid",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    for field in MULTIPLAYER_REGRESSION_LOCK_REQUIRED_FIELDS:
        value = mp_payload.get(field)
        if value is None or (isinstance(value, str) and not str(value).strip()):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=str(field),
                    message="multiplayer regression lock missing required field '{}'".format(field),
                    rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                )
            )

    policy_rows = mp_payload.get("policy_baselines")
    if not isinstance(policy_rows, dict):
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="policy_baselines",
                message="multiplayer regression lock policy_baselines must be an object",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
    else:
        for policy_id in (
            "policy.net.lockstep",
            "policy.net.server_authoritative",
            "policy.net.srz_hybrid",
        ):
            row = policy_rows.get(policy_id)
            if not isinstance(row, dict):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=policy_id,
                        message="multiplayer regression lock missing policy baseline '{}'".format(policy_id),
                        rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                    )
                )
                continue
            final_hash = str(row.get("final_composite_hash", "")).strip()
            if not final_hash:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=policy_id,
                        message="multiplayer regression lock requires final_composite_hash for '{}'".format(policy_id),
                        rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                    )
                )

    fp_rows = mp_payload.get("anti_cheat_fingerprint_hashes")
    if not isinstance(fp_rows, dict):
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="anti_cheat_fingerprint_hashes",
                message="multiplayer regression lock anti_cheat_fingerprint_hashes must be an object",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
    else:
        for key in (
            "detect_only_event_fingerprint_hash",
            "rank_strict_event_fingerprint_hash",
            "rank_strict_action_fingerprint_hash",
        ):
            if not str(fp_rows.get(key, "")).strip():
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                        line_number=1,
                        snippet=key,
                        message="multiplayer regression lock missing anti-cheat fingerprint hash '{}'".format(key),
                        rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
                    )
                )

    mp_update_policy = mp_payload.get("update_policy")
    mp_required_tag = ""
    if isinstance(mp_update_policy, dict):
        mp_required_tag = str(mp_update_policy.get("required_commit_tag", "")).strip()
    if not mp_required_tag:
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="update_policy.required_commit_tag",
                message="multiplayer regression lock must declare update_policy.required_commit_tag",
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    try:
        mp_proc = subprocess.run(
            ["git", "log", "-1", "--pretty=%s", "--", MULTIPLAYER_REGRESSION_LOCK_PATH],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return
    if int(mp_proc.returncode) != 0:
        return
    mp_subject = str(mp_proc.stdout or "").strip()
    if mp_subject and mp_required_tag not in mp_subject:
        findings.append(
            _finding(
                severity=severity,
                file_path=MULTIPLAYER_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=mp_subject[:140],
                message="latest multiplayer baseline commit message must include '{}'".format(mp_required_tag),
                rule_id="INV-MULTIPLAYER-REGRESSION-LOCK-PRESENT",
            )
        )

    ctrl_payload, ctrl_err = _load_json_object(repo_root, CONTROL_DECISION_REGRESSION_LOCK_PATH)
    if ctrl_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_DECISION_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="",
                message="control decision regression baseline lock file is missing or invalid",
                rule_id="INV-CONTROL-DECISION-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    for field in CONTROL_DECISION_REGRESSION_LOCK_REQUIRED_FIELDS:
        value = ctrl_payload.get(field)
        if value is None or (isinstance(value, str) and not str(value).strip()):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CONTROL_DECISION_REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=str(field),
                    message="control decision regression lock missing required field '{}'".format(field),
                    rule_id="INV-CONTROL-DECISION-REGRESSION-LOCK-PRESENT",
                )
            )

    fingerprint_cases = ctrl_payload.get("fingerprint_cases")
    if not isinstance(fingerprint_cases, list) or not fingerprint_cases:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_DECISION_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="fingerprint_cases",
                message="control decision regression lock requires non-empty fingerprint_cases list",
                rule_id="INV-CONTROL-DECISION-REGRESSION-LOCK-PRESENT",
            )
        )
    else:
        for row in (item for item in fingerprint_cases if isinstance(item, dict)):
            case_id = str(row.get("case_id", "")).strip()
            has_decision_fp = bool(str(row.get("decision_log_fingerprint", "")).strip())
            has_sequence_fp = bool(str(row.get("sequence_fingerprint", "")).strip())
            if case_id and (has_decision_fp or has_sequence_fp):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CONTROL_DECISION_REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=case_id or "fingerprint_case",
                    message="each fingerprint case must declare case_id and decision or sequence fingerprint",
                    rule_id="INV-CONTROL-DECISION-REGRESSION-LOCK-PRESENT",
                )
            )
            break

    ctrl_update_policy = ctrl_payload.get("update_policy")
    ctrl_required_tag = ""
    if isinstance(ctrl_update_policy, dict):
        ctrl_required_tag = str(ctrl_update_policy.get("required_commit_tag", "")).strip()
    if not ctrl_required_tag:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_DECISION_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="update_policy.required_commit_tag",
                message="control decision regression lock must declare update_policy.required_commit_tag",
                rule_id="INV-CONTROL-DECISION-REGRESSION-LOCK-PRESENT",
            )
        )
        return

    try:
        ctrl_proc = subprocess.run(
            ["git", "log", "-1", "--pretty=%s", "--", CONTROL_DECISION_REGRESSION_LOCK_PATH],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return
    if int(ctrl_proc.returncode) != 0:
        return
    ctrl_subject = str(ctrl_proc.stdout or "").strip()
    if ctrl_subject and ctrl_required_tag not in ctrl_subject:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_DECISION_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=ctrl_subject[:140],
                message="latest control decision baseline commit message must include '{}'".format(ctrl_required_tag),
                rule_id="INV-CONTROL-DECISION-REGRESSION-LOCK-PRESENT",
            )
        )

    full_payload, full_err = _load_json_object(repo_root, CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH)
    if full_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="",
                message="control-plane full regression baseline lock file is missing or invalid",
                rule_id="INV-CONTROL-PLANE-FULL-REGRESSION-LOCK-PRESENT",
            )
        )
        return
    for field in CONTROL_PLANE_FULL_REGRESSION_LOCK_REQUIRED_FIELDS:
        value = full_payload.get(field)
        if value is None or (isinstance(value, str) and not str(value).strip()):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=str(field),
                    message="control-plane full regression lock missing required field '{}'".format(field),
                    rule_id="INV-CONTROL-PLANE-FULL-REGRESSION-LOCK-PRESENT",
                )
            )

    full_update_policy = full_payload.get("update_policy")
    full_required_tag = ""
    if isinstance(full_update_policy, dict):
        full_required_tag = str(full_update_policy.get("required_commit_tag", "")).strip()
    if not full_required_tag:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="update_policy.required_commit_tag",
                message="control-plane full regression lock must declare update_policy.required_commit_tag",
                rule_id="INV-CONTROL-PLANE-FULL-REGRESSION-LOCK-PRESENT",
            )
        )
        return
    if full_required_tag != "CTRL-PLANE-REGRESSION-UPDATE":
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=full_required_tag,
                message="control-plane full regression lock required_commit_tag must be CTRL-PLANE-REGRESSION-UPDATE",
                rule_id="INV-CONTROL-PLANE-FULL-REGRESSION-LOCK-PRESENT",
            )
        )

    try:
        full_proc = subprocess.run(
            ["git", "log", "-1", "--pretty=%s", "--", CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return
    if int(full_proc.returncode) != 0:
        return
    full_subject = str(full_proc.stdout or "").strip()
    if full_subject and full_required_tag not in full_subject:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONTROL_PLANE_FULL_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=full_subject[:140],
                message="latest control-plane full baseline commit message must include '{}'".format(full_required_tag),
                rule_id="INV-CONTROL-PLANE-FULL-REGRESSION-LOCK-PRESENT",
            )
        )


def _append_cross_system_matrix_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    matrix_abs = os.path.join(repo_root, CONSISTENCY_MATRIX_PATH.replace("/", os.sep))
    if not os.path.isfile(matrix_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=CONSISTENCY_MATRIX_PATH,
                line_number=1,
                snippet="",
                message="cross-system consistency matrix is missing",
                rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
            )
        )
        return
    try:
        content = open(matrix_abs, "r", encoding="utf-8").read()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=CONSISTENCY_MATRIX_PATH,
                line_number=1,
                snippet="",
                message="unable to read cross-system consistency matrix",
                rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
            )
        )
        return
    for system_name in CONSISTENCY_MATRIX_REQUIRED_SYSTEMS:
        if str(system_name) not in content:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CONSISTENCY_MATRIX_PATH,
                    line_number=1,
                    snippet=str(system_name),
                    message="matrix is missing required system row '{}'".format(system_name),
                    rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
                )
            )
    for column_name in CONSISTENCY_MATRIX_REQUIRED_COLUMNS:
        if str(column_name) not in content:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=CONSISTENCY_MATRIX_PATH,
                    line_number=1,
                    snippet=str(column_name),
                    message="matrix is missing required responsibility column '{}'".format(column_name),
                    rule_id="INV-CROSS-SYSTEM-MATRIX-PRESENT",
                )
            )


def _append_status_now_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    status_now_abs = os.path.join(repo_root, STATUS_NOW_PATH.replace("/", os.sep))
    if not os.path.isfile(status_now_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=STATUS_NOW_PATH,
                line_number=1,
                snippet="",
                message="status snapshot file is missing",
                rule_id="INV-STATUS-NOW-PRESENT",
            )
        )
        return
    try:
        content = open(status_now_abs, "r", encoding="utf-8").read()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=STATUS_NOW_PATH,
                line_number=1,
                snippet="",
                message="unable to read status snapshot file",
                rule_id="INV-STATUS-NOW-PRESENT",
            )
        )
        return
    for header in STATUS_NOW_REQUIRED_SECTIONS:
        if header not in content:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=STATUS_NOW_PATH,
                    line_number=1,
                    snippet=header,
                    message="status snapshot missing required section '{}'".format(header),
                    rule_id="INV-STATUS-NOW-PRESENT",
                )
            )


def _append_forbidden_identifier_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    lower = line.lower()
    severity = _invariant_severity(profile)
    for token in FORBIDDEN_IDENTIFIERS:
        pattern = r"\b{}\b".format(re.escape(token))
        if re.search(pattern, lower):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=line.strip()[:140],
                    message="forbidden identifier '{}' detected".format(token),
                    rule_id="INV-NO-MODE-FLAGS",
                )
            )


def _append_mode_flag_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    match = re.search(r"\b([a-zA-Z_][a-zA-Z0-9_]*_mode)\b", line)
    if not match:
        return
    lhs = str(match.group(1))
    lower = line.lower()
    is_toggle = any(flag in lower for flag in ("= true", "= false", ": true", ": false", "=0", "=1", ":0", ":1"))
    if not is_toggle:
        return
    severity = _invariant_severity(profile)
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="mode-flag heuristic matched '{}'".format(lhs),
            rule_id="INV-NO-MODE-FLAGS",
        )
    )


def _append_reserved_misuse_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    # Fidelity level maps use canonical enum keys ("micro|meso|macro") and are
    # not generic mode/config flags.
    if any(
        token in line
        for token in (
            "fidelity_cost_by_level",
            "inspection_cost_by_level",
            "reenactment_cost_by_level",
            "_FIDELITY_LEVEL_RANK",
            "_FIDELITY_RANK",
            "_FIDELITY_LEVELS",
        )
    ):
        return
    rel_norm = _norm(rel_path)
    exempt_roots = (
        "schemas/",
        "schema/",
        "docs/",
        "packs/derived/",
    )
    exempt_files = (
        "data/registries/session_stage_registry.json",
        "data/registries/session_pipeline_registry.json",
    )
    if rel_norm.startswith(exempt_roots) or rel_norm in exempt_files:
        return
    for token in RESERVED_WORDS:
        pattern = r'"{}"\s*:\s*(true|false|0|1)'.format(re.escape(token))
        if re.search(pattern, line, flags=re.IGNORECASE):
            severity = "warn" if profile == "FAST" else "fail"
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=line.strip()[:140],
                    message="reserved word '{}' used as generic config flag".format(token),
                    rule_id="repox.reserved_word_flag_misuse",
                )
            )


def _append_domain_token_hardcode_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    rel_norm = _norm(rel_path)
    if any(rel_norm.startswith(prefix) for prefix in DOMAIN_TOKEN_ALLOWED_PATH_PREFIXES):
        return
    pattern = r'["\']dom\.domain\.[A-Za-z0-9_.-]+["\']'
    if not re.search(pattern, line):
        return
    severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="hardcoded domain token literal detected outside registry-governed paths",
            rule_id="INV-NO-HARDCODED-DOMAIN-TOKENS",
        )
    )


def _append_contract_token_hardcode_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if rel_path == "tools/xstack/repox/check.py":
        return
    rel_norm = _norm(rel_path)
    if any(rel_norm.startswith(prefix) for prefix in CONTRACT_TOKEN_ALLOWED_PATH_PREFIXES):
        return
    pattern = r'["\']dom\.contract\.[A-Za-z0-9_.-]+["\']'
    if not re.search(pattern, line):
        return
    severity = "warn" if profile == "FAST" else _invariant_severity(profile)
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="hardcoded contract token literal detected outside registry-governed paths",
            rule_id="INV-NO-HARDCODED-CONTRACT-TOKENS",
        )
    )


def _append_strict_placeholder_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if profile not in ("STRICT", "FULL"):
        return
    if rel_path == "tools/xstack/repox/check.py":
        return
    lower = line.lower()
    placeholder_hits = (
        "renderer_truth_include",
        "truth_renderer_include",
        "include_renderer_truth",
    )
    if any(hit in lower for hit in placeholder_hits):
        findings.append(
            _finding(
                severity="refusal",
                file_path=rel_path,
                line_number=line_no,
                snippet=line.strip()[:140],
                message="forbidden renderer/truth include placeholder detected",
                rule_id="repox.renderer_truth_placeholder",
            )
        )


def _append_renderer_truth_boundary_findings(
    findings: List[Dict[str, object]],
    rel_path: str,
    line_no: int,
    line: str,
    profile: str,
) -> None:
    if profile not in ("STRICT", "FULL"):
        return
    rel_norm = _norm(rel_path).lower()
    if not rel_norm.startswith("client/presentation/"):
        return
    match = INCLUDE_RE.match(line)
    if match:
        include_path = str(match.group(1)).replace("\\", "/").lower()
        if include_path in RENDERER_TRUTH_INCLUDE_FORBIDDEN:
            findings.append(
                _finding(
                    severity="refusal",
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=line.strip()[:140],
                    message="renderer include/import of TruthModel header is forbidden",
                    rule_id="repox.renderer_truth_import",
                )
            )
            return
    if "dom_truth_model_v1" in line:
        findings.append(
            _finding(
                severity="refusal",
                file_path=rel_path,
                line_number=line_no,
                snippet=line.strip()[:140],
                message="renderer usage of TruthModel symbol is forbidden",
                rule_id="repox.renderer_truth_symbol",
            )
        )


def _append_negative_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    io_read_tokens = ("open(", "fopen(", "ifstream", "std::ifstream", "json.load(")
    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()

            if rel_norm.startswith(("engine/", "game/")):
                if ("packs/" in lower or "packs\\" in lower) and any(token in lower for token in io_read_tokens):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="runtime code must not directly read pack files",
                            rule_id="INV-NO-DIRECT-PACK-READS-IN-RUNTIME",
                        )
                    )

            has_schema_token = ("schemas/" in lower) or ("schema/" in lower) or (".schema.json" in lower)
            if has_schema_token and any(token in lower for token in io_read_tokens):
                if not rel_norm.startswith(SCHEMA_READ_ALLOWED_PREFIXES):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="schema file parsing must route through validation layer",
                            rule_id="INV-NO-DIRECT-SCHEMA-PARSE-OUTSIDE-VALIDATION",
                        )
                    )

            if rel_norm.startswith(("client/presentation/", "client/ui/")):
                ui_bypass_tokens = (
                    "boot_session_spec(",
                    "create_session_spec(",
                    "run_intent_script(",
                    "run_process(",
                    "execute_process(",
                )
                if any(token in lower for token in ui_bypass_tokens):
                    if "command_graph" not in lower and "intent" not in lower:
                        findings.append(
                            _finding(
                                severity=severity,
                                file_path=rel_norm,
                                line_number=line_no,
                                snippet=str(line).strip()[:140],
                                message="ui logic invocation must route through command graph/intents",
                                rule_id="INV-UI-COMMAND-GRAPH-ONLY",
                            )
                        )

            if rel_norm.startswith(("tools/launcher/", "tools/setup/", "launcher/", "setup/")):
                if "add_argument(" in lower and re.search(r"--(from-stage|to-stage|stage-id)\b", lower):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="session stage jump arguments are forbidden on launcher/setup surfaces",
                            rule_id="INV-NO-SESSION-PIPELINE-BYPASS",
                        )
                    )

            if not rel_norm.startswith(CONTROL_MUTATION_ALLOWED_PREFIXES):
                control_state_write = re.search(
                    r"state\s*\[\s*[\"'](control_bindings|controller_assemblies)[\"']\s*\]\s*=",
                    str(line),
                )
                control_collection_mutation = re.search(
                    r"\b(control_bindings|controller_assemblies)\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                if control_state_write or control_collection_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="control bindings/controller assemblies must mutate only through control processes",
                            rule_id="INV-CONTROL-PROCESSES-ONLY",
                        )
                    )

            if not rel_norm.startswith(BODY_MUTATION_ALLOWED_PREFIXES):
                body_state_write = re.search(
                    r"state\s*\[\s*[\"']body_assemblies[\"']\s*\]\s*=",
                    str(line),
                )
                body_collection_mutation = re.search(
                    r"\bbody_assemblies\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                body_transform_mutation = re.search(
                    r"\bbody\w*\s*\[\s*[\"']transform_mm[\"']\s*\]\s*=",
                    str(line),
                )
                if body_state_write or body_collection_mutation or body_transform_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="body assemblies and body transforms must mutate only through deterministic processes",
                            rule_id="INV-BODY-MUTATION-PROCESS-ONLY",
                        )
                    )

            if not rel_norm.startswith(CIV_MUTATION_ALLOWED_PREFIXES):
                civ_state_write = re.search(
                    r"state\s*\[\s*[\"'](faction_assemblies|affiliations|territory_assemblies|diplomatic_relations)[\"']\s*\]\s*=",
                    str(line),
                )
                civ_collection_mutation = re.search(
                    r"\b(faction_assemblies|affiliations|territory_assemblies|diplomatic_relations)\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                if civ_state_write or civ_collection_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="civilisation state must mutate only through deterministic CIV processes",
                            rule_id="INV-CIV-PROCESSES-ONLY-MUTATION",
                        )
                    )
                order_state_write = re.search(
                    r"state\s*\[\s*[\"'](order_assemblies|order_queue_assemblies)[\"']\s*\]\s*=",
                    str(line),
                )
                order_collection_mutation = re.search(
                    r"\b(order_assemblies|order_queue_assemblies)\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                if order_state_write or order_collection_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="orders must be created/cancelled/executed through deterministic order intents and process handlers",
                            rule_id="INV-ORDERS-AS-INTENTS",
                        )
                    )
                role_state_write = re.search(
                    r"state\s*\[\s*[\"'](institution_assemblies|role_assignment_assemblies)[\"']\s*\]\s*=",
                    str(line),
                )
                role_collection_mutation = re.search(
                    r"\b(institution_assemblies|role_assignment_assemblies)\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                if role_state_write or role_collection_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="institution/role delegation state must mutate only through gated role assignment processes",
                            rule_id="INV-ROLE-DELEGATION-GATED",
                        )
                    )
                cohort_state_write = re.search(
                    r"state\s*\[\s*[\"']cohort_assemblies[\"']\s*\]\s*=",
                    str(line),
                )
                cohort_collection_mutation = re.search(
                    r"\bcohort_assemblies\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                    str(line),
                )
                if cohort_state_write or cohort_collection_mutation:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="cohort expand/collapse state must mutate only through deterministic cohort processes",
                            rule_id="INV-COHORT-EXPAND-COLLAPSE-PROCESS-ONLY",
                        )
                    )

            if not any(rel_norm.startswith(prefix) for prefix in PLAYER_LITERAL_ALLOWED_PATH_PREFIXES):
                if re.search(r"[\"']player(?:\.[a-z0-9_.-]+)?[\"']", lower):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="hardcoded single-player literal detected; control substrate must stay controller-agnostic",
                            rule_id="INV-NO-HARDCODED-PLAYER",
                        )
                    )

            if not any(rel_norm.startswith(prefix) for prefix in PLAYER_FACTION_LITERAL_ALLOWED_PATH_PREFIXES):
                if re.search(
                    r"(player[_\s\.-]*faction|faction[_\s\.-]*player|faction\.player|player\.faction)",
                    lower,
                ):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="hardcoded player-faction special casing is forbidden; faction handling must stay registry/process driven",
                            rule_id="INV-NO-PLAYER-FACTION-SPECIALCASE",
                        )
                    )

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""
    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="control process runtime is missing; entitlement gate checks cannot be verified",
                rule_id="INV-CONTROL-ENTITLEMENT-GATED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="movement runtime is missing; cannot verify agent_move dispatches through process.body_move_attempt",
                rule_id="INV-MOVE-USES-BODY_MOVE_ATTEMPT",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="movement ownership guards are missing; cannot verify ownership enforcement for embodied movement",
                rule_id="INV-OWNERSHIP-CHECK-REQUIRED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="camera/view runtime is missing; cannot verify registry-driven view mode selection",
                rule_id="INV-VIEW-MODES-REGISTRY-DRIVEN",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="camera/view runtime is missing; cannot verify observer watermark enforcement",
                rule_id="INV-WATERMARK-ENFORCED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify process-only civilisation mutation invariant",
                rule_id="INV-CIV-PROCESSES-ONLY-MUTATION",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify deterministic faction id generation contract",
                rule_id="INV-FACTION-ID-STABLE",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify cohort expand/collapse process-only mutation invariant",
                rule_id="INV-COHORT-EXPAND-COLLAPSE-PROCESS-ONLY",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify cohort mapping policy declaration invariant",
                rule_id="INV-COHORT-MAPPING-POLICY-DECLARED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify orders execute strictly via intent/process pipeline",
                rule_id="INV-ORDERS-AS-INTENTS",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify role delegation law-gating",
                rule_id="INV-ROLE-DELEGATION-GATED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify demography process policy/model resolution invariants",
                rule_id="INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="CIV process runtime is missing; cannot verify no individual-level sex simulation scope guard",
                rule_id="INV-NO-INDIVIDUAL_SEX_SIM_YET",
            )
        )
    else:
        required_control_entitlements = (
            ("process.control_bind_camera", "entitlement.control.camera"),
            ("process.control_unbind_camera", "entitlement.control.camera"),
            ("process.control_possess_agent", "entitlement.control.possess"),
            ("process.control_release_agent", "entitlement.control.possess"),
            ("process.control_set_view_lens", "entitlement.control.lens_override"),
        )
        for process_id, entitlement_id in required_control_entitlements:
            if process_id not in process_runtime_text or entitlement_id not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet="{} -> {}".format(process_id, entitlement_id),
                        message="control process entitlement mapping is missing or incomplete",
                        rule_id="INV-CONTROL-ENTITLEMENT-GATED",
                    )
                )
        deterministic_pair_tokens = (
            "def _broadphase_pairs(",
            "for cell_key in sorted(grid.keys()):",
            "return sorted(list(pair_set)",
        )
        for token in deterministic_pair_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="collision broadphase must preserve deterministic pair ordering",
                        rule_id="INV-DETERMINISTIC-PAIR-ORDER",
                    )
                )

        movement_tokens = (
            "elif process_id == \"process.agent_move\":",
            "moved = _apply_body_move_attempt(",
        )
        for token in movement_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="agent movement must route through process.body_move_attempt and avoid direct transform mutation",
                        rule_id="INV-MOVE-USES-BODY_MOVE_ATTEMPT",
                    )
                )

        civ_process_tokens = (
            "elif process_id == \"process.faction_create\":",
            "elif process_id == \"process.faction_dissolve\":",
            "elif process_id == \"process.affiliation_join\":",
            "elif process_id == \"process.affiliation_leave\":",
            "elif process_id == \"process.territory_claim\":",
            "elif process_id == \"process.territory_release\":",
            "elif process_id == \"process.diplomacy_set_relation\":",
            "_persist_civ_state(",
        )
        for token in civ_process_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="civilisation runtime mutations must be implemented through deterministic CIV process handlers",
                    rule_id="INV-CIV-PROCESSES-ONLY-MUTATION",
                )
            )

        order_process_tokens = (
            "elif process_id == \"process.order_create\":",
            "elif process_id == \"process.order_cancel\":",
            "elif process_id == \"process.order_tick\":",
            "_run_order_tick(",
            "_order_type_rows(",
        )
        for token in order_process_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="order execution must remain process-driven (orders as intents) with registry-backed type resolution",
                    rule_id="INV-ORDERS-AS-INTENTS",
                )
            )

        role_delegation_tokens = (
            "elif process_id == \"process.role_assign\":",
            "elif process_id == \"process.role_revoke\":",
            "allow_role_delegation",
            "delegable_entitlements",
            "_role_rows(",
            "_institution_type_rows(",
        )
        for token in role_delegation_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="role delegation must be law/profile-gated and registry-driven",
                    rule_id="INV-ROLE-DELEGATION-GATED",
                )
            )

        cohort_process_tokens = (
            "elif process_id == \"process.cohort_create\":",
            "elif process_id == \"process.cohort_expand_to_micro\":",
            "elif process_id == \"process.cohort_collapse_from_micro\":",
            "_ensure_cohort_assemblies(",
            "_expand_cohort_to_micro_internal(",
            "_collapse_cohort_from_micro_internal(",
        )
        for token in cohort_process_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="cohort runtime mutations must be implemented through deterministic expand/collapse process handlers",
                    rule_id="INV-COHORT-EXPAND-COLLAPSE-PROCESS-ONLY",
                )
            )

        cohort_policy_tokens = (
            "_cohort_mapping_policy_rows(",
            "cohort_mapping_policy_registry",
            "mapping_policy_id",
        )
        for token in cohort_policy_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="cohort mapping policy must be resolved from declared registry data",
                    rule_id="INV-COHORT-MAPPING-POLICY-DECLARED",
                )
            )

        demography_tokens = (
            "elif process_id == \"process.demography_tick\":",
            "_demography_policy_rows(",
            "_birth_model_rows(",
            "_death_model_rows(",
            "refusal.civ.births_forbidden_by_law",
        )
        for token in demography_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="demography execution must remain registry-driven with explicit birth/death model gating",
                    rule_id="INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                )
            )

        sex_scope_forbidden_tokens = (
            "pregnancy",
            "pregnant",
            "sexual_intercourse",
            "insemination",
            "fertility_cycle",
        )
        for line_no, line in _iter_lines(repo_root, process_runtime_rel):
            lowered = str(line).lower()
            if not any(token in lowered for token in sex_scope_forbidden_tokens):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="individual-level sex simulation semantics are out of scope for CIV-4 demography scaffold",
                    rule_id="INV-NO-INDIVIDUAL_SEX_SIM_YET",
                )
            )

        faction_id_tokens = (
            "def _deterministic_faction_id(",
            "\"founder_agent_id\"",
            "\"created_tick\"",
            "_deterministic_faction_id(",
        )
        for token in faction_id_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="faction identity generation must remain deterministic and founder/tick stable",
                    rule_id="INV-FACTION-ID-STABLE",
                )
            )

        ownership_tokens = (
            "def _movement_context(",
            "refusal.agent.ownership_violation",
        )
        for token in ownership_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="embodied movement must enforce deterministic ownership checks in multiplayer contexts",
                        rule_id="INV-OWNERSHIP-CHECK-REQUIRED",
                    )
                )

        required_view_tokens = (
            "_view_mode_entries(navigation_indices)",
            "view mode '{}' is not declared in view mode registry",
            "control_policy.allowed_view_modes",
        )
        for token in required_view_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="camera/view validation must resolve view modes from registry payloads and control policy",
                        rule_id="INV-VIEW-MODES-REGISTRY-DRIVEN",
                    )
                )

        required_view_control_tokens = (
            "elif process_id == \"process.view_bind\":",
            "process_id = \"process.view_bind\"",
            "apply_view_binding(",
        )
        for token in required_view_control_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="camera/view changes must route through control-plane process.view_bind handler",
                    rule_id="INV-VIEW-CHANGES-THROUGH-CONTROL",
                )
            )

        legacy_camera_tokens = (
            "\"process.camera_bind_target\"",
            "\"process.camera_unbind_target\"",
            "\"process.camera_set_view_mode\"",
        )
        has_view_bind_adapter = (
            "if process_id in (" in process_runtime_text
            and "process_id = \"process.view_bind\"" in process_runtime_text
            and all(token in process_runtime_text for token in legacy_camera_tokens)
        )
        if not has_view_bind_adapter:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet="process_id = \"process.view_bind\"",
                    message="legacy camera toggles must be adapter-routed through process.view_bind",
                    rule_id="INV-NO-DIRECT-CAMERA-TOGGLE",
                )
            )

        control_action_rel = "data/registries/control_action_registry.json"
        control_action_payload, control_action_err = _load_json_object(repo_root, control_action_rel)
        if control_action_err:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=control_action_rel,
                    line_number=1,
                    snippet="",
                    message="control action registry missing; cannot verify view policy action routing",
                    rule_id="INV-VIEW-CHANGES-THROUGH-CONTROL",
                )
            )
        else:
            action_rows = (((control_action_payload.get("record") or {}).get("actions")) or [])
            if isinstance(action_rows, list):
                view_change_policy_row = {}
                for row in sorted((item for item in action_rows if isinstance(item, dict)), key=lambda item: str(item.get("action_id", ""))):
                    if str(row.get("action_id", "")).strip() == "action.view.change_policy":
                        view_change_policy_row = dict(row)
                        break
                produced_process_id = str((dict(view_change_policy_row.get("produces") or {})).get("process_id", "")).strip()
                if produced_process_id != "process.view_bind":
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=control_action_rel,
                            line_number=1,
                            snippet="action.view.change_policy -> {}".format(produced_process_id or "<missing>"),
                            message="action.view.change_policy must dispatch to process.view_bind",
                            rule_id="INV-VIEW-CHANGES-THROUGH-CONTROL",
                        )
                    )

        if "refusal.view.watermark_required" not in process_runtime_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet="refusal.view.watermark_required",
                    message="observer truth-capable view modes must enforce watermark entitlement refusal",
                    rule_id="INV-WATERMARK-ENFORCED",
                )
            )

        lod_transition_tokens = (
            "process.region_expand",
            "process.region_collapse",
            "_run_region_transition_with_lod_invariance(",
            "refusal.ep.lod_information_gain",
        )
        for token in lod_transition_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="solver tier transitions must execute LOD epistemic invariance checks through redaction-aware process paths",
                    rule_id="INV-SOLVER-TIER-REDACTION-REQUIRED",
                )
            )

        hardcoded_view_branch = re.compile(
            r"if\s+.*(?:==|!=|in\s*\()\s*[\"']view\.[a-z0-9_.-]+[\"']",
            re.IGNORECASE,
        )
        for line_no, line in _iter_lines(repo_root, process_runtime_rel):
            if hardcoded_view_branch.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="hardcoded view mode branch detected; resolve view rules through view_mode registry data",
                        rule_id="INV-VIEW-MODES-REGISTRY-DRIVEN",
                    )
                )

    cohort_policy_registry_rel = "data/registries/cohort_mapping_policy_registry.json"
    cohort_policy_registry_payload, cohort_policy_registry_err = _load_json_object(repo_root, cohort_policy_registry_rel)
    if cohort_policy_registry_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=cohort_policy_registry_rel,
                line_number=1,
                snippet="",
                message="cohort mapping policy registry is missing or invalid JSON",
                rule_id="INV-COHORT-MAPPING-POLICY-DECLARED",
            )
        )
    else:
        policy_rows = (((cohort_policy_registry_payload.get("record") or {}).get("policies")) or [])
        if not isinstance(policy_rows, list) or not policy_rows:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=cohort_policy_registry_rel,
                    line_number=1,
                    snippet="record.policies",
                    message="cohort mapping policy registry must declare at least one mapping policy",
                    rule_id="INV-COHORT-MAPPING-POLICY-DECLARED",
                )
            )
        else:
            for row in policy_rows:
                if not isinstance(row, dict):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=cohort_policy_registry_rel,
                            line_number=1,
                            snippet="record.policies[]",
                            message="cohort mapping policy entries must be object rows",
                            rule_id="INV-COHORT-MAPPING-POLICY-DECLARED",
                        )
                    )
                    continue
                mapping_policy_id = str(row.get("mapping_policy_id", "")).strip()
                if not mapping_policy_id:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=cohort_policy_registry_rel,
                            line_number=1,
                            snippet="mapping_policy_id",
                            message="cohort mapping policy entries must declare mapping_policy_id",
                            rule_id="INV-COHORT-MAPPING-POLICY-DECLARED",
                        )
                    )
                try:
                    max_micro_agents = int(row.get("max_micro_agents_per_cohort", -1))
                except (TypeError, ValueError):
                    max_micro_agents = -1
                if max_micro_agents < 0:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=cohort_policy_registry_rel,
                            line_number=1,
                            snippet=mapping_policy_id or "max_micro_agents_per_cohort",
                            message="cohort mapping policy must declare non-negative max_micro_agents_per_cohort",
                            rule_id="INV-COHORT-MAPPING-POLICY-DECLARED",
                        )
                    )

    demography_policy_registry_rel = "data/registries/demography_policy_registry.json"
    demography_policy_payload, demography_policy_err = _load_json_object(repo_root, demography_policy_registry_rel)
    if demography_policy_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=demography_policy_registry_rel,
                line_number=1,
                snippet="",
                message="demography policy registry is missing or invalid JSON",
                rule_id="INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
            )
        )
    else:
        policy_rows = (((demography_policy_payload.get("record") or {}).get("policies")) or [])
        if not isinstance(policy_rows, list) or not policy_rows:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=demography_policy_registry_rel,
                    line_number=1,
                    snippet="record.policies",
                    message="demography policy registry must declare at least one policy entry",
                    rule_id="INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                )
            )
        else:
            observed_policy_ids = sorted(
                set(
                    str(item.get("demography_policy_id", "")).strip()
                    for item in policy_rows
                    if isinstance(item, dict) and str(item.get("demography_policy_id", "")).strip()
                )
            )
            for required_policy_id in (
                "demo.policy.none",
                "demo.policy.stable_no_birth",
                "demo.policy.basic_births",
            ):
                if required_policy_id in set(observed_policy_ids):
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=demography_policy_registry_rel,
                        line_number=1,
                        snippet=required_policy_id,
                        message="demography policy registry is missing required baseline policy '{}'".format(required_policy_id),
                        rule_id="INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                    )
                )

    parameter_bundle_registry_rel = "data/registries/parameter_bundles.json"
    parameter_bundle_payload, parameter_bundle_err = _load_json_object(repo_root, parameter_bundle_registry_rel)
    if parameter_bundle_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=parameter_bundle_registry_rel,
                line_number=1,
                snippet="",
                message="parameter bundle registry is missing or invalid JSON",
                rule_id="INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
            )
        )
    else:
        bundle_rows = (((parameter_bundle_payload.get("record") or {}).get("bundles")) or [])
        bundle_ids = sorted(
            set(
                str(item.get("parameter_bundle_id", "")).strip()
                for item in bundle_rows
                if isinstance(item, dict) and str(item.get("parameter_bundle_id", "")).strip()
            )
        )
        for required_bundle_id in ("params.civ.nobirths", "params.civ.basic_births"):
            if required_bundle_id in set(bundle_ids):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=parameter_bundle_registry_rel,
                    line_number=1,
                    snippet=required_bundle_id,
                    message="demography parameter bundle '{}' is missing".format(required_bundle_id),
                    rule_id="INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                )
            )

    demography_doc_rel = "docs/civilisation/DEMOGRAPHY_OPTIONALITY.md"
    demography_doc_abs = os.path.join(repo_root, demography_doc_rel.replace("/", os.sep))
    try:
        demography_doc_text = open(demography_doc_abs, "r", encoding="utf-8").read().lower()
    except OSError:
        demography_doc_text = ""
    if not demography_doc_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=demography_doc_rel,
                line_number=1,
                snippet="",
                message="demography doctrine doc is missing; CIV-4 scope guard cannot be verified",
                rule_id="INV-NO-INDIVIDUAL_SEX_SIM_YET",
            )
        )
    else:
        if "no explicit sex" not in demography_doc_text and "no individual-level reproduction" not in demography_doc_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=demography_doc_rel,
                    line_number=1,
                    snippet="no explicit sex simulation",
                    message="demography doctrine must explicitly state no individual-level sex simulation scope in CIV-4",
                    rule_id="INV-NO-INDIVIDUAL_SEX_SIM_YET",
                )
            )

    observation_rel = "tools/xstack/sessionx/observation.py"
    observation_abs = os.path.join(repo_root, observation_rel.replace("/", os.sep))
    try:
        observation_text = open(observation_abs, "r", encoding="utf-8").read()
    except OSError:
        observation_text = ""
    if not observation_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=observation_rel,
                line_number=1,
                snippet="",
                message="observation kernel is missing; cannot verify observer watermark channel enforcement",
                rule_id="INV-WATERMARK-ENFORCED",
            )
        )
    else:
        watermark_tokens = (
            "_observer_watermark_payload(",
            "ch.watermark.observer_mode",
            "refusal.ep.entitlement_missing",
        )
        for token in watermark_tokens:
            if token not in observation_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=observation_rel,
                        line_number=1,
                        snippet=token,
                        message="observer truth view path must emit watermark channel and enforce entitlement checks",
                    rule_id="INV-WATERMARK-ENFORCED",
                )
            )

        lod_observation_tokens = (
            "def _apply_lod_invariance_redaction(",
            "perceived_model = _apply_lod_invariance_redaction(",
            "lod_redaction_rule_id",
        )
        for token in lod_observation_tokens:
            if token in observation_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=observation_rel,
                    line_number=1,
                    snippet=token,
                    message="observation kernel must apply deterministic LOD redaction before perceived output emission",
                    rule_id="INV-SOLVER-TIER-REDACTION-REQUIRED",
                )
            )

        micro_leak_pattern = re.compile(
            r"\b(micro_regions?|micro_solver|hidden_inventory|internal_state)\b",
            re.IGNORECASE,
        )
        micro_scan_paths = (
            observation_rel,
            "src/net/policies/policy_server_authoritative.py",
            "src/net/srz/shard_coordinator.py",
        )
        for rel_path in micro_scan_paths:
            for line_no, line in _iter_lines(repo_root, rel_path):
                lowered = str(line).lower()
                if not micro_leak_pattern.search(str(line)):
                    continue
                if "lod_redaction" in lowered or "refusal.ep.lod_information_gain" in lowered:
                    continue
                if "test_force_lod_information_gain" in lowered:
                    continue
                if rel_path == observation_rel and "_lod_redaction_" in lowered:
                    continue
                stripped = str(line).strip()
                if rel_path == observation_rel and stripped.startswith(("'", '"')):
                    token = stripped.strip().strip(",").strip("'").strip('"').strip().lower()
                    if token in ("hidden_inventory", "internal_state", "micro_solver", "native_precision"):
                        continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="micro/internal solver state must not flow directly into perceived/network payloads without redaction",
                        rule_id="INV-NO-DIRECT-MICRO-TO-PERCEIVED",
                    )
                )

    memory_kernel_rel = "src/epistemics/memory/memory_kernel.py"
    memory_kernel_abs = os.path.join(repo_root, memory_kernel_rel.replace("/", os.sep))
    if not os.path.isfile(memory_kernel_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=memory_kernel_rel,
                line_number=1,
                snippet="",
                message="memory kernel is missing; cannot verify memory truth-separation invariants",
                rule_id="INV-MEMORY-NO-TRUTH",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=memory_kernel_rel,
                line_number=1,
                snippet="",
                message="memory kernel is missing; cannot verify tick-based decay invariants",
                rule_id="INV-MEMORY-TICK-BASED",
            )
        )
    else:
        try:
            memory_kernel_text = open(memory_kernel_abs, "r", encoding="utf-8").read()
        except OSError:
            memory_kernel_text = ""
        if not memory_kernel_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=memory_kernel_rel,
                    line_number=1,
                    snippet="",
                    message="memory kernel is unreadable; cannot verify invariants",
                    rule_id="INV-MEMORY-NO-TRUTH",
                )
            )
        else:
            truth_token_pattern = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
            for line_no, line in _iter_lines(repo_root, memory_kernel_rel):
                if truth_token_pattern.search(str(line)):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=memory_kernel_rel,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="memory subsystem must not reference TruthModel/universe state payloads",
                            rule_id="INV-MEMORY-NO-TRUTH",
                        )
                    )

            wall_clock_pattern = re.compile(
                r"(time\.time|time\.perf_counter|time\.monotonic|datetime\.|utcnow\(|now\()",
                re.IGNORECASE,
            )
            for line_no, line in _iter_lines(repo_root, memory_kernel_rel):
                if wall_clock_pattern.search(str(line)):
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=memory_kernel_rel,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="memory decay/eviction must be tick-based and must not use wall-clock APIs",
                            rule_id="INV-MEMORY-TICK-BASED",
                        )
                    )

            tick_tokens = (
                "tick_delta",
                "ttl_ticks",
                "last_refresh_tick",
            )
            for token in tick_tokens:
                if token not in memory_kernel_text:
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=memory_kernel_rel,
                            line_number=1,
                            snippet=token,
                            message="memory kernel must use deterministic tick-based ttl accounting",
                            rule_id="INV-MEMORY-TICK-BASED",
                        )
                    )

    instrument_kernel_rel = "src/diegetics/instrument_kernel.py"
    instrument_kernel_abs = os.path.join(repo_root, instrument_kernel_rel.replace("/", os.sep))
    if not os.path.isfile(instrument_kernel_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=instrument_kernel_rel,
                line_number=1,
                snippet="",
                message="diegetic instrument kernel is missing; cannot verify perceived-only invariant",
                rule_id="INV-INSTRUMENTS-PERCEIVED-ONLY",
            )
        )
    else:
        try:
            instrument_kernel_text = open(instrument_kernel_abs, "r", encoding="utf-8").read()
        except OSError:
            instrument_kernel_text = ""
        truth_token_pattern = re.compile(r"\b(truth_model|truthmodel|universe_state|registry_payloads)\b", re.IGNORECASE)
        for line_no, line in _iter_lines(repo_root, instrument_kernel_rel):
            if truth_token_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=instrument_kernel_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="diegetic instrument kernel must derive from Perceived.now/memory only",
                        rule_id="INV-INSTRUMENTS-PERCEIVED-ONLY",
                    )
                )
        if "compute_diegetic_instruments(" not in instrument_kernel_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=instrument_kernel_rel,
                    line_number=1,
                    snippet="compute_diegetic_instruments(",
                    message="diegetic kernel entrypoint is missing",
                    rule_id="INV-INSTRUMENTS-PERCEIVED-ONLY",
                )
            )

    observation_text = ""
    if os.path.isfile(observation_abs):
        try:
            observation_text = open(observation_abs, "r", encoding="utf-8").read()
        except OSError:
            observation_text = ""
    required_instrument_tokens = (
        "compute_diegetic_instruments(",
        "perceived_now=perceived_model",
        "memory_store=memory_block",
    )
    for token in required_instrument_tokens:
        if token in observation_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=observation_rel,
                line_number=1,
                snippet=token,
                message="observation kernel must route instrument derivation from Perceived.now and Perceived.memory",
                rule_id="INV-INSTRUMENTS-PERCEIVED-ONLY",
            )
        )

    instrument_registry_rel = "data/registries/instrument_type_registry.json"
    instrument_registry_payload, instrument_registry_err = _load_json_object(repo_root, instrument_registry_rel)
    declared_diegetic_channels = set()
    required_runtime_channels = set()
    if instrument_registry_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=instrument_registry_rel,
                line_number=1,
                snippet="",
                message="instrument type registry is missing/invalid; cannot validate diegetic channel declarations",
                rule_id="INV-DIEGETIC-CHANNELS-REGISTRY-DRIVEN",
            )
        )
    else:
        rows = (((instrument_registry_payload.get("record") or {}).get("instrument_types")) or [])
        if not isinstance(rows, list):
            rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            produced = row.get("produced_channels_out")
            if not isinstance(produced, list):
                continue
            runtime_status = str((dict(row.get("extensions") or {})).get("runtime_status", "")).strip().lower()
            is_stub = runtime_status == "stub"
            for channel_id in produced:
                token = str(channel_id).strip()
                if not token.startswith("ch.diegetic."):
                    continue
                declared_diegetic_channels.add(token)
                if not is_stub:
                    required_runtime_channels.add(token)

    if required_runtime_channels:
        for channel_id in sorted(required_runtime_channels):
            if channel_id in observation_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=observation_rel,
                    line_number=1,
                    snippet=channel_id,
                    message="non-stub diegetic channel declared in registry is not surfaced in observation pipeline",
                    rule_id="INV-DIEGETIC-CHANNELS-REGISTRY-DRIVEN",
                )
            )

    channel_token_pattern = re.compile(r"\bch\.diegetic\.[a-z0-9_.-]+\b")
    discovered_tokens = set(channel_token_pattern.findall(str(observation_text or "")))
    policy_registry_rel = "data/registries/epistemic_policy_registry.json"
    policy_registry_payload, _policy_registry_err = _load_json_object(repo_root, policy_registry_rel)
    policy_text = ""
    if isinstance(policy_registry_payload, dict):
        try:
            policy_text = json.dumps(policy_registry_payload, sort_keys=True)
        except (TypeError, ValueError):
            policy_text = ""
    discovered_tokens.update(channel_token_pattern.findall(str(policy_text)))

    lens_registry_rel = "packs/domain/pack.domain.navigation/data/lens.sensor.json"
    lens_abs = os.path.join(repo_root, lens_registry_rel.replace("/", os.sep))
    lens_text = ""
    if os.path.isfile(lens_abs):
        try:
            lens_text = open(lens_abs, "r", encoding="utf-8").read()
        except OSError:
            lens_text = ""
    discovered_tokens.update(channel_token_pattern.findall(str(lens_text)))

    if declared_diegetic_channels:
        for token in sorted(discovered_tokens):
            if token in declared_diegetic_channels:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=observation_rel,
                    line_number=1,
                    snippet=token,
                    message="diegetic channel token is used outside instrument registry declarations",
                    rule_id="INV-DIEGETIC-CHANNELS-REGISTRY-DRIVEN",
                )
            )

    missing_player_diegetic_files = []
    for rel_path in PLAYER_DIEGETIC_REQUIRED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        missing_player_diegetic_files.append(rel_path)
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required diegetic-first player baseline artifact is missing",
                rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
            )
        )
    if missing_player_diegetic_files:
        return

    player_law_rel = "packs/law/law.player.diegetic_default/data/law_profile.player.diegetic_default.json"
    player_law_payload, player_law_err = _load_json_object(repo_root, player_law_rel)
    if player_law_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=player_law_rel,
                line_number=1,
                snippet="",
                message="player diegetic default law profile is missing or invalid JSON",
                rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
            )
        )
    else:
        law_profile_id = str(player_law_payload.get("law_profile_id", "")).strip()
        if law_profile_id != "law.player.diegetic_default":
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_law_rel,
                    line_number=1,
                    snippet=law_profile_id,
                    message="player law profile id must be law.player.diegetic_default",
                    rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
                )
            )
        allowed_lenses = sorted(set(str(item).strip() for item in (player_law_payload.get("allowed_lenses") or []) if str(item).strip()))
        if any(token.startswith("lens.nondiegetic.") for token in allowed_lenses):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_law_rel,
                    line_number=1,
                    snippet="allowed_lenses",
                    message="player diegetic default law must not allow nondiegetic lenses",
                    rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                )
            )
        debug_allowances = dict(player_law_payload.get("debug_allowances") or {})
        if bool(debug_allowances.get("allow_nondiegetic_overlays", False)):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_law_rel,
                    line_number=1,
                    snippet="allow_nondiegetic_overlays",
                    message="player diegetic default law must keep allow_nondiegetic_overlays disabled",
                    rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                )
            )
        forbidden_processes = set(
            str(item).strip()
            for item in (player_law_payload.get("forbidden_processes") or [])
            if str(item).strip()
        )
        for process_id in PLAYER_DEFAULT_FORBIDDEN_PROCESSES:
            if process_id in forbidden_processes:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_law_rel,
                    line_number=1,
                    snippet=process_id,
                    message="player diegetic default law must forbid debug/non-diegetic process surfaces",
                    rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                )
            )

    player_experience_rel = "packs/experience/profile.player.default/data/experience_profile.player.default.json"
    player_experience_payload, player_experience_err = _load_json_object(repo_root, player_experience_rel)
    if player_experience_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=player_experience_rel,
                line_number=1,
                snippet="",
                message="player default experience profile is missing or invalid JSON",
                rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
            )
        )
    else:
        experience_id = str(player_experience_payload.get("experience_id", "")).strip()
        if experience_id != "profile.player.default":
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_experience_rel,
                    line_number=1,
                    snippet=experience_id,
                    message="player default experience id must be profile.player.default",
                    rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
                )
            )
        default_law_profile_id = str(player_experience_payload.get("default_law_profile_id", "")).strip()
        if default_law_profile_id != "law.player.diegetic_default":
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_experience_rel,
                    line_number=1,
                    snippet=default_law_profile_id,
                    message="player default experience must bind law.player.diegetic_default",
                    rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
                )
            )
        default_lens_id = str((dict(player_experience_payload.get("presentation_defaults") or {})).get("default_lens_id", "")).strip()
        if default_lens_id.startswith("lens.nondiegetic."):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_experience_rel,
                    line_number=1,
                    snippet=default_lens_id,
                    message="player default experience must not default to nondiegetic lens",
                    rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                )
            )

    player_workspace_rel = "packs/tool/workspace.player.diegetic_default/pack.json"
    player_workspace_payload, player_workspace_err = _load_json_object(repo_root, player_workspace_rel)
    if player_workspace_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=player_workspace_rel,
                line_number=1,
                snippet="",
                message="player diegetic workspace pack is missing or invalid JSON",
                rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
            )
        )
    else:
        workspace_pack_id = str(player_workspace_payload.get("pack_id", "")).strip()
        if workspace_pack_id != "workspace.player.diegetic_default":
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_workspace_rel,
                    line_number=1,
                    snippet=workspace_pack_id,
                    message="player workspace pack id must be workspace.player.diegetic_default",
                    rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
                )
            )
        contributions = list(player_workspace_payload.get("contributions") or [])
        if not contributions:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=player_workspace_rel,
                    line_number=1,
                    snippet="contributions",
                    message="player diegetic workspace pack must declare instrument window contributions",
                    rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
                )
            )
        for row in sorted((item for item in contributions if isinstance(item, dict)), key=lambda item: str(item.get("id", ""))):
            window_id = str(row.get("id", "")).strip()
            if not window_id.startswith("window.player.instrument."):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=player_workspace_rel,
                        line_number=1,
                        snippet=window_id,
                        message="player diegetic workspace must expose only window.player.instrument.* entries",
                        rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                    )
                )
            if window_id in PLAYER_DEBUG_WINDOW_IDS or any(window_id.startswith(prefix) for prefix in PLAYER_DEBUG_WINDOW_PREFIXES):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=player_workspace_rel,
                        line_number=1,
                        snippet=window_id,
                        message="player workspace includes forbidden debug/non-diegetic window",
                        rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                    )
                )
            rel_path = str(row.get("path", "")).strip()
            if not rel_path:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=player_workspace_rel,
                        line_number=1,
                        snippet=window_id,
                        message="player workspace contribution is missing path",
                        rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
                    )
                )
                continue
            window_rel = "packs/tool/workspace.player.diegetic_default/{}".format(rel_path)
            window_payload, window_err = _load_json_object(repo_root, window_rel)
            if window_err:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=window_rel,
                        line_number=1,
                        snippet=window_id,
                        message="player workspace window descriptor is missing or invalid JSON",
                        rule_id="INV-DIEGETIC-DEFAULT-PROFILE-PRESENT",
                    )
                )
                continue
            required_lenses = sorted(set(str(item).strip() for item in (window_payload.get("required_lenses") or []) if str(item).strip()))
            if any(token.startswith("lens.nondiegetic.") for token in required_lenses):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=window_rel,
                        line_number=1,
                        snippet="required_lenses",
                        message="player workspace windows must not require nondiegetic lenses",
                        rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                    )
                )
            required_entitlements = sorted(
                set(str(item).strip() for item in (window_payload.get("required_entitlements") or []) if str(item).strip())
            )
            forbidden_entitlements = [token for token in required_entitlements if token in PLAYER_DEBUG_FORBIDDEN_ENTITLEMENTS]
            if forbidden_entitlements:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=window_rel,
                        line_number=1,
                        snippet=forbidden_entitlements[0],
                        message="player workspace window requires forbidden debug entitlement",
                        rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                    )
                )

    ui_host_rel = "tools/xstack/sessionx/ui_host.py"
    ui_host_abs = os.path.join(repo_root, ui_host_rel.replace("/", os.sep))
    if not os.path.isfile(ui_host_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=ui_host_rel,
                line_number=1,
                snippet="",
                message="ui host is missing; cannot verify diegetic player debug-surface gating",
                rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
            )
        )
    else:
        try:
            ui_host_text = open(ui_host_abs, "r", encoding="utf-8").read()
        except OSError:
            ui_host_text = ""
        required_ui_tokens = (
            "def _is_nondiegetic_window(",
            "allow_nondiegetic_overlays",
            "window_is_nondiegetic",
        )
        for token in required_ui_tokens:
            if token in ui_host_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=ui_host_rel,
                    line_number=1,
                    snippet=token,
                    message="ui host must gate non-diegetic windows for player default laws",
                    rule_id="INV-NO-PLAYER_DEBUG_SURFACES",
                )
            )


def _append_representation_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""

    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime is missing; cosmetic process-only representation checks cannot be verified",
                rule_id="INV-NO-COSMETIC-SEMANTICS",
            )
        )
    else:
        required_cosmetic_tokens = (
            "elif process_id == \"process.cosmetic_assign\":",
            "representation_state = _representation_state(policy_context)",
            "skip_state_log = True",
        )
        for token in required_cosmetic_tokens:
            if token not in process_runtime_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet=token,
                        message="cosmetic assignment must remain representation-side and process-driven",
                        rule_id="INV-NO-COSMETIC-SEMANTICS",
                    )
                )

        for line_no, line in _iter_lines(repo_root, process_runtime_rel):
            lower = str(line).lower()
            if "cosmetic" not in lower:
                continue
            if "refusal.cosmetic" in lower:
                continue
            if "representation_state" in lower:
                continue
            if any(token in lower for token in COSMETIC_SEMANTIC_FORBIDDEN_TOKENS):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="cosmetic path must not touch authoritative movement/collision fields",
                        rule_id="INV-NO-COSMETIC-SEMANTICS",
                    )
                )

    truth_render_pattern = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
    for rel_path in REPRESENTATION_RENDER_ONLY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="render adapter/resolver file is missing",
                    rule_id="INV-RENDERER-TRUTH-ISOLATION",
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            if truth_render_pattern.search(str(line)):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="render adapter/resolver must not import or reference TruthModel/universe state",
                        rule_id="INV-RENDERER-TRUTH-ISOLATION",
                    )
                )

    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if rel_norm.startswith(("tools/xstack/testx/tests/", "tools/auditx/", "docs/")):
            continue
        if "representation" not in rel_norm and "render_model.py" not in rel_norm:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "truth_model" in lower or "truthmodel" in lower:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="representation code path references TruthModel symbol",
                        rule_id="INV-RENDERER-TRUTH-ISOLATION",
                    )
                )

    resolver_abs = os.path.join(repo_root, REPRESENTATION_DATA_DRIVEN_FILE.replace("/", os.sep))
    resolver_text = ""
    try:
        resolver_text = open(resolver_abs, "r", encoding="utf-8").read()
    except OSError:
        resolver_text = ""
    if not resolver_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=REPRESENTATION_DATA_DRIVEN_FILE,
                line_number=1,
                snippet="",
                message="representation resolver is missing; cannot verify data-driven rule mapping",
                rule_id="INV-REPRESENTATION-RULES-DATA-DRIVEN",
            )
        )
    else:
        for token in REPRESENTATION_DATA_DRIVEN_REQUIRED_TOKENS:
            if token in resolver_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=REPRESENTATION_DATA_DRIVEN_FILE,
                    line_number=1,
                    snippet=token,
                    message="representation resolver must consume registry-driven rules, not hardcoded maps",
                    rule_id="INV-REPRESENTATION-RULES-DATA-DRIVEN",
                )
            )

    renderer_truth_pattern = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
    renderer_mutation_pattern = re.compile(r"\b(process_runtime|apply_intent|authority_context|process_id)\b", re.IGNORECASE)
    for rel_path in RENDERER_RENDERMODEL_ONLY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="renderer contract file is missing",
                    rule_id="INV-RENDERER-CONSUMES-RENDERMODEL-ONLY",
                )
            )
            continue
        has_render_model_token = False
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line)
            lower_token = token.lower()
            if "render_model" in lower_token or "rendermodel" in lower_token:
                has_render_model_token = True
            if renderer_truth_pattern.search(token):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="renderer path references forbidden truth symbol",
                        rule_id="INV-RENDERER-CONSUMES-RENDERMODEL-ONLY",
                    )
                )
            if renderer_mutation_pattern.search(token):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="renderer path must not couple to process mutation surfaces",
                        rule_id="INV-RENDERER-CONSUMES-RENDERMODEL-ONLY",
                    )
                )
        if not has_render_model_token:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="render_model",
                    message="renderer path must consume RenderModel payloads",
                    rule_id="INV-RENDERER-CONSUMES-RENDERMODEL-ONLY",
                )
            )

    no_truth_access_pattern = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
    for rel_path in RENDERER_RENDERMODEL_ONLY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="renderer contract file is missing for truth-access boundary verification",
                    rule_id="INV-NO-TRUTH-ACCESS-IN-RENDER",
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            if not no_truth_access_pattern.search(str(line)):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="renderer path must not access truth-model symbols; consume Perceived/Render models only",
                    rule_id="INV-NO-TRUTH-ACCESS-IN-RENDER",
                )
            )

    derived_anchor_found = False
    for rel_path in RENDER_SNAPSHOT_DERIVED_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="render snapshot derived artifact file is missing",
                    rule_id="INV-RENDER_SNAPSHOTS_DERIVED_ONLY",
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            lower = str(line).lower()
            if "run_meta" in lower and "render_snapshots" in lower:
                derived_anchor_found = True
            if "process_runtime" in lower or "truth_model" in lower or "truthmodel" in lower:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="render snapshot pipeline must remain derived-only and truth-isolated",
                        rule_id="INV-RENDER_SNAPSHOTS_DERIVED_ONLY",
                    )
                )
    if not derived_anchor_found:
        findings.append(
            _finding(
                severity=severity,
                file_path="tools/render/tool_render_capture.py",
                line_number=1,
                snippet="run_meta/render_snapshots",
                message="render snapshot pipeline must define deterministic derived storage root",
                rule_id="INV-RENDER_SNAPSHOTS_DERIVED_ONLY",
            )
        )


def _append_ranked_governance_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    registry_rel = "data/registries/server_profile_registry.json"
    registry_payload, registry_err = _load_json_object(repo_root, registry_rel)
    if registry_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=registry_rel,
                line_number=1,
                snippet="",
                message="server profile registry is missing or invalid JSON",
                rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
            )
        )
    else:
        profile_rows = (((registry_payload.get("record") or {}).get("profiles")) or [])
        if not isinstance(profile_rows, list):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=registry_rel,
                    line_number=1,
                    snippet="",
                    message="server profile registry record.profiles is missing",
                    rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                )
            )
        else:
            ranked_profile = {}
            for row in profile_rows:
                if not isinstance(row, dict):
                    continue
                if str(row.get("server_profile_id", "")).strip() == "server.profile.rank_strict":
                    ranked_profile = dict(row)
                    break
            if not ranked_profile:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=registry_rel,
                        line_number=1,
                        snippet="server.profile.rank_strict",
                        message="ranked server profile is missing",
                        rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                    )
                )
            else:
                securex_policy_id = str(ranked_profile.get("securex_policy_id", "")).strip()
                anti_cheat_policy_id = str(ranked_profile.get("anti_cheat_policy_id", "")).strip()
                if securex_policy_id != "securex.policy.rank_strict":
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=registry_rel,
                            line_number=1,
                            snippet=securex_policy_id,
                            message="ranked server profile must reference securex.policy.rank_strict",
                            rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                        )
                    )
                if anti_cheat_policy_id != "policy.ac.rank_strict":
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=registry_rel,
                            line_number=1,
                            snippet=anti_cheat_policy_id,
                            message="ranked server profile must reference policy.ac.rank_strict",
                            rule_id="INV-RANKED-REQUIRES-SECUREX-STRICT",
                        )
                    )

    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        if rel_norm.startswith(("tools/xstack/testx/tests/", "tools/auditx/")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "ranked_mode" not in lower:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="ranked governance must be data-driven; ranked_mode flags are forbidden",
                    rule_id="INV-NO-RANKED-FLAGS",
                )
            )


def _append_hidden_ban_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    anti_engine_rel = "src/net/anti_cheat/anti_cheat_engine.py"
    anti_engine_abs = os.path.join(repo_root, anti_engine_rel.replace("/", os.sep))
    if not os.path.isfile(anti_engine_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=anti_engine_rel,
                line_number=1,
                snippet="",
                message="anti-cheat engine is missing",
                rule_id="INV-NO-HIDDEN-BAN",
            )
        )
        return
    try:
        anti_engine_text = open(anti_engine_abs, "r", encoding="utf-8").read()
    except OSError:
        findings.append(
            _finding(
                severity=severity,
                file_path=anti_engine_rel,
                line_number=1,
                snippet="",
                message="unable to read anti-cheat engine for hidden-ban invariant",
                rule_id="INV-NO-HIDDEN-BAN",
            )
        )
        return

    required_tokens = (
        "anti_cheat_events",
        "anti_cheat_enforcement_actions",
        "_record_refusal_injection(",
        "terminated_peers",
    )
    for token in required_tokens:
        if token not in anti_engine_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=anti_engine_rel,
                    line_number=1,
                    snippet=token,
                    message="anti-cheat termination path must emit event/action/refusal artifacts",
                    rule_id="INV-NO-HIDDEN-BAN",
                )
            )

    termination_paths = (
        "src/net/policies/policy_server_authoritative.py",
        "src/net/srz/shard_coordinator.py",
        "src/net/policies/policy_lockstep.py",
    )
    for rel_path in termination_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            continue
        if "terminate" not in text:
            continue
        if rel_path.endswith("policy_lockstep.py"):
            required = ("refusal_from_decision(",)
        else:
            required = ("_apply_enforcement_result(", "anti_cheat_enforcement_actions")
        for token in required:
            if token not in text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="terminate handling must route through explicit anti-cheat enforcement pipeline",
                        rule_id="INV-NO-HIDDEN-BAN",
                    )
                )

    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.startswith("src/net/"):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lower = str(line).lower()
            if "terminated_peers" not in lower:
                continue
            if rel_norm == anti_engine_rel:
                continue
            if '"terminated_peers": []' in lower or "'terminated_peers': []" in lower:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="peer termination must be emitted by anti-cheat engine with policy action log",
                    rule_id="INV-NO-HIDDEN-BAN",
                )
            )


def _append_reality_profile_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_files = {
        "schemas/universe_identity.schema.json": (
            "physics_profile_id",
            "immutable_after_create",
            "initial_pack_set_hash_expectation",
        ),
        "tools/xstack/sessionx/creator.py": (
            "physics_profile_id",
            "select_physics_profile(",
            "write_null_boot_artifacts(",
        ),
        "tools/xstack/sessionx/runner.py": (
            "select_physics_profile(",
            "refusal.physics_profile_mismatch",
            "server_physics_profile_id=",
        ),
        "tools/xstack/sessionx/net_handshake.py": (
            "refusal.physics_profile_missing",
            "refusal.physics_profile_mismatch",
            "server_physics_profile_id",
        ),
        "tools/xstack/sessionx/universe_physics.py": (
            "NULL_PHYSICS_PROFILE_ID",
            "write_null_boot_artifacts(",
            "default_null_lockfile_payload(",
        ),
    }
    for rel_path, tokens in required_files.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required RS-1 physics profile runtime file is missing",
                    rule_id="INV-PHYSICS-PROFILE-IN-IDENTITY",
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required RS-1 physics profile runtime file is unreadable",
                    rule_id="INV-PHYSICS-PROFILE-IN-IDENTITY",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="physics profile identity/handshake invariant token is missing",
                    rule_id="INV-PHYSICS-PROFILE-IN-IDENTITY",
                )
            )

    runtime_scan_roots = (
        "tools/xstack/sessionx/",
        "src/",
        "worldgen/",
    )
    for rel_path in _iter_negative_code_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.startswith(runtime_scan_roots):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            lowered = str(line).lower()
            if "physics.default.realistic" not in lowered:
                continue
            if rel_norm.startswith(PHYSICS_LITERAL_ALLOWED_PATH_PREFIXES):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="runtime must not hardcode the optional realistic profile id; profile selection must remain pack-driven",
                    rule_id="INV-NO-HARDCODED-PHYSICS-ASSUMPTIONS",
                )
            )


def _append_phys_profile_declared_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    rule_id = "INV-PHYS-PROFILE-DECLARED"

    session_schema_rel = "schemas/session_spec.schema.json"
    payload, payload_error = _load_json_object(repo_root, session_schema_rel)
    if payload_error:
        findings.append(
            _finding(
                severity=severity,
                file_path=session_schema_rel,
                line_number=1,
                snippet="",
                message="session spec schema is missing or invalid; physics profile declaration cannot be enforced",
                rule_id=rule_id,
            )
        )
    else:
        required = list(payload.get("required") or [])
        if "physics_profile_id" not in required:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=session_schema_rel,
                    line_number=1,
                    snippet="required.physics_profile_id",
                    message="session specs must declare top-level physics_profile_id",
                    rule_id=rule_id,
                )
            )
        properties = payload.get("properties")
        physics_property = {}
        if isinstance(properties, dict):
            physics_property = dict(properties.get("physics_profile_id") or {})
        if str(physics_property.get("type", "")).strip() != "string":
            findings.append(
                _finding(
                    severity=severity,
                    file_path=session_schema_rel,
                    line_number=1,
                    snippet="properties.physics_profile_id",
                    message="session spec physics_profile_id must be typed as string",
                    rule_id=rule_id,
                )
            )

    required_tokens = {
        "schema/session/session_spec.schema": (
            "physics_profile_id",
        ),
        "schemas/examples/session_spec.example.json": (
            "\"physics_profile_id\"",
        ),
        "tools/xstack/testdata/session/session_spec.fixture.json": (
            "\"physics_profile_id\"",
        ),
        "tools/xstack/sessionx/creator.py": (
            "\"physics_profile_id\": str(identity_payload.get(\"physics_profile_id\", \"\")).strip()",
        ),
    }
    for rel_path, tokens in required_tokens.items():
        text = _file_text(repo_root, rel_path)
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required physics-profile declaration surface is missing",
                    rule_id=rule_id,
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="physics profile declaration token is missing",
                    rule_id=rule_id,
                )
            )


def _append_unregistered_quantity_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    rule_id = "INV-UNREGISTERED-QUANTITY-FORBIDDEN"
    quantity_registry_rel = "data/registries/quantity_registry.json"

    payload, payload_error = _load_json_object(repo_root, quantity_registry_rel)
    rows = list(((payload.get("record") or {}).get("quantities") or []) if not payload_error else [])
    registered_quantities = set(
        str(row.get("quantity_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("quantity_id", "")).strip()
    )

    if payload_error or not registered_quantities:
        findings.append(
            _finding(
                severity=severity,
                file_path=quantity_registry_rel,
                line_number=1,
                snippet="quantities",
                message="quantity registry is missing or empty; cannot enforce registered quantity usage",
                rule_id=rule_id,
            )
        )
        return

    token_pattern = re.compile(r"\bquantity\.[A-Za-z0-9_.-]+\b")
    scan_prefixes = (
        "src/",
        "tools/xstack/sessionx/",
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    skip_files = {
        "tools/xstack/repox/check.py",
    }
    allowed_placeholder_quantities = {
        "quantity.unknown",
    }

    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in skip_files:
            continue
        if not rel_norm.endswith((".py", ".json", ".schema", ".schema.json", ".md", ".txt")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            unknown_tokens: List[str] = []
            for token in token_pattern.findall(snippet):
                candidate = str(token).strip().rstrip(".,:;")
                lowered = candidate.lower()
                if lowered.endswith(".json") or lowered.endswith(".schema") or lowered.endswith(".schema.json"):
                    continue
                if candidate in allowed_placeholder_quantities:
                    continue
                if candidate in registered_quantities:
                    continue
                unknown_tokens.append(candidate)
            if not unknown_tokens:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="quantity identifier is not registered in data/registries/quantity_registry.json: {}".format(
                        ",".join(sorted(set(unknown_tokens)))
                    ),
                    rule_id=rule_id,
                )
            )
            break


def _append_conservation_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    contract_required_files = {
        "tools/xstack/sessionx/runner.py": (
            "conservation_contract_set_registry_hash",
            "conservation_contract_set_id",
            "identity_conservation_contract_set_id",
        ),
        "tools/xstack/sessionx/script_runner.py": (
            "conservation_contract_set_registry_hash",
            "conservation_contract_set_id",
        ),
        "tools/xstack/sessionx/net_handshake.py": (
            "conservation_contract_set_id",
            "refusal.conservation_contract_set_mismatch",
        ),
        "src/reality/ledger/ledger_engine.py": (
            "finalize_process_accounting(",
            "record_unaccounted_delta(",
        ),
    }
    for rel_path, tokens in contract_required_files.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required conservation contract runtime file is missing",
                    rule_id="INV-CONSERVATION-CONTRACT-SET-REQUIRED",
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required conservation contract runtime file is unreadable",
                    rule_id="INV-CONSERVATION-CONTRACT-SET-REQUIRED",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="conservation contract set integration token is missing",
                    rule_id="INV-CONSERVATION-CONTRACT-SET-REQUIRED",
                )
            )

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""
    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime is missing; cannot verify conservation accounting emission hooks",
                rule_id="INV-NO-SILENT-VIOLATIONS",
            )
        )
        return

    required_accounting_tokens = (
        "_ledger_emit_exception(",
        "_record_unaccounted_conservation_delta(",
        "_finalize_conservation_process(",
        "refusal.conservation_unaccounted",
    )
    for token in required_accounting_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet=token,
                message="conservation mutation paths must route through deterministic ledger accounting hooks",
                rule_id="INV-NO-SILENT-VIOLATIONS",
            )
        )

    if "CONSERVATION_VIOLATION" in process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="CONSERVATION_VIOLATION",
                message="legacy hardcoded conservation violation refusals detected; use contract-ledger refusal paths instead",
                rule_id="INV-NO-SILENT-VIOLATIONS",
            )
        )


def _append_material_dimension_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    quantity_type_registry_rel = "data/registries/quantity_type_registry.json"
    quantity_type_abs = os.path.join(repo_root, quantity_type_registry_rel.replace("/", os.sep))
    if not os.path.isfile(quantity_type_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=quantity_type_registry_rel,
                line_number=1,
                snippet="",
                message="quantity_type_registry is missing",
                rule_id="INV-QUANTITY-TYPE-DECLARED",
            )
        )
    else:
        payload, payload_error = _load_json_object(repo_root, quantity_type_registry_rel)
        rows = list(((payload.get("record") or {}).get("quantity_types") or []) if not payload_error else [])
        if payload_error or not rows:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=quantity_type_registry_rel,
                    line_number=1,
                    snippet="quantity_types",
                    message="quantity_type_registry must define quantity_types entries",
                    rule_id="INV-QUANTITY-TYPE-DECLARED",
                )
            )

    compatibility_required = {
        "tools/xstack/registry_compile/compiler.py": (
            "\"quantity_type_registry\"",
            "\"dimension_registry\"",
            "\"unit_registry\"",
            "\"base_dimension_registry\"",
        ),
        "src/reality/ledger/ledger_engine.py": (
            "_REFUSAL_DIMENSION_MISMATCH",
            "quantity_dimensions",
            "refusal.dimension.mismatch",
        ),
        "src/materials/dimension_engine.py": (
            "dimension_add(",
            "dimension_mul(",
            "dimension_div(",
            "quantity_add(",
            "quantity_convert(",
            "refusal.unit.invalid_conversion",
        ),
    }
    for rel_path, tokens in compatibility_required.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required material dimension enforcement file is missing",
                    rule_id="INV-DIMENSION-COMPATIBILITY-ENFORCED",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required material dimension compatibility token is missing",
                    rule_id="INV-DIMENSION-COMPATIBILITY-ENFORCED",
                )
            )

    invariant_math_files = (
        "src/materials/dimension_engine.py",
        "src/reality/ledger/ledger_engine.py",
    )
    for rel_path in invariant_math_files:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="invariant math file missing; cannot verify raw-float prohibition",
                    rule_id="INV-NO-RAW-FLOAT-IN-INVARIANT-MATH",
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            lowered = token.lower()
            if "deterministic_float" in lowered:
                continue
            if (
                "float(" not in lowered
                and ": float" not in lowered
                and "-> float" not in lowered
                and "float " not in lowered
            ):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="invariant quantity math must not use raw float types",
                    rule_id="INV-NO-RAW-FLOAT-IN-INVARIANT-MATH",
                )
            )


def _append_material_taxonomy_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    material_registry_paths = (
        "data/registries/element_registry.json",
        "data/registries/compound_registry.json",
        "data/registries/mixture_registry.json",
        "data/registries/material_class_registry.json",
        "data/registries/quality_distribution_registry.json",
    )
    for rel_path in material_registry_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="material definitions must remain data-only registry artifacts",
                rule_id="INV-MATERIAL-DEFINITIONS-DATA-ONLY",
            )
        )

    for rel_path in _scan_files(repo_root):
        if not rel_path.startswith("src/"):
            continue
        if not rel_path.endswith((".py", ".c", ".h", ".cpp", ".hpp")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            lowered = token.lower()
            if "material registry" in lowered:
                continue
            if "element." not in token:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="runtime source must not hardcode concrete element ids",
                    rule_id="INV-NO-HARDCODED-ELEMENTS",
                )
            )

    required_tokens = {
        "src/materials/composition_engine.py": (
            "validate_compound_composition(",
            "validate_mixture_composition(",
            "validate_material_class(",
            "REFUSAL_MATERIAL_INVALID_COMPOSITION",
            "REFUSAL_MATERIAL_MASS_FRACTION_MISMATCH",
            "REFUSAL_MATERIAL_DIMENSION_MISMATCH",
        ),
        "tools/xstack/registry_compile/compiler.py": (
            "_material_taxonomy_registry_rows(",
            "refuse.material.invalid_composition",
            "refuse.material.mass_fraction_mismatch",
            "refuse.material.dimension_mismatch",
        ),
    }
    for rel_path, tokens in required_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="material composition validation implementation file is missing",
                    rule_id="INV-COMPOSITION-VALIDATED",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required composition validation token is missing",
                    rule_id="INV-COMPOSITION-VALIDATED",
                )
            )


def _append_material_structure_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_registry_paths = (
        "data/registries/part_class_registry.json",
        "data/registries/connection_type_registry.json",
        "data/registries/blueprint_registry.json",
    )
    for rel_path in required_registry_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="blueprint/assembly definitions must remain data-only registry artifacts",
                rule_id="INV-BLUEPRINTS-DATA-ONLY",
            )
        )

    structure_literals = (
        "blueprint.house.basic",
        "blueprint.lathe.basic",
        "blueprint.road.segment.basic",
        "blueprint.simple_bridge.basic",
        "blueprint.space_elevator.template",
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith((".py", ".c", ".h", ".cpp", ".hpp", ".json", ".md")):
            continue
        if rel_path.startswith(BLUEPRINT_LITERAL_ALLOWED_PATH_PREFIXES):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if not any(literal in token for literal in structure_literals):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="runtime/source must not hardcode baseline blueprint structure identifiers",
                    rule_id="INV-NO-HARDCODED-STRUCTURES",
                )
            )

    required_tokens = {
        "src/materials/blueprint_engine.py": (
            "compile_blueprint_artifacts(",
            "blueprint_compile_cache_key(",
            "REFUSAL_BLUEPRINT_MISSING_PART_CLASS",
            "REFUSAL_BLUEPRINT_INVALID_GRAPH",
            "REFUSAL_BLUEPRINT_PARAMETER_INVALID",
        ),
        "tools/materials/tool_blueprint_compile.py": (
            "compile_blueprint_artifacts(",
            "cache_key",
            "pack_lock_hash",
        ),
        "src/client/interaction/preview_generator.py": (
            "_blueprint_preview_payload(",
            "process.blueprint_inspect",
            "build_blueprint_ghost_overlay(",
        ),
        "src/client/interaction/inspection_overlays.py": (
            "_blueprint_overlay_payload(",
            "build_blueprint_ghost_overlay(",
            "blueprint_bom_summary(",
        ),
        "tools/xstack/registry_compile/compiler.py": (
            "_materials_structure_registry_rows(",
            "allowed_target_kinds = {",
            "\"blueprint\"",
            "\"logistics_node\"",
        ),
    }
    for rel_path, tokens in required_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required blueprint deterministic compilation/runtime file is missing",
                    rule_id="INV-DETERMINISTIC-BLUEPRINT-COMPILATION",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required blueprint deterministic compilation token is missing",
                    rule_id="INV-DETERMINISTIC-BLUEPRINT-COMPILATION",
                )
            )


def _append_material_logistics_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_registry_paths = (
        "data/registries/logistics_routing_rule_registry.json",
        "data/registries/logistics_graph_registry.json",
    )
    for rel_path in required_registry_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="logistics registry artifacts must be declared as data-only inputs",
                rule_id="INV-MANIFESTS-PROCESS-ONLY",
            )
        )

    process_only_fields = (
        "state[\"logistics_manifests\"]",
        "state[\"shipment_commitments\"]",
        "state[\"logistics_node_inventories\"]",
        "state[\"logistics_provenance_events\"]",
    )
    process_only_allowed_prefixes = (
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(process_only_allowed_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if not any(field in token for field in process_only_fields):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="logistics state mutation must occur only through process runtime commit paths",
                    rule_id="INV-MANIFESTS-PROCESS-ONLY",
                )
            )

    required_no_silent_transfer_tokens = {
        "src/logistics/logistics_engine.py": (
            "create_manifest_and_commitment(",
            "tick_manifests(",
            "shipment_depart",
            "shipment_arrive",
            "shipment_lost",
            "REFUSAL_LOGISTICS_INSUFFICIENT_STOCK",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.manifest_create",
            "process.manifest_tick",
            "_persist_logistics_state(",
            "_ledger_emit_exception(",
        ),
    }
    for rel_path, tokens in required_no_silent_transfer_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required logistics transfer/refusal implementation file is missing",
                    rule_id="INV-NO-SILENT-TRANSFER",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required logistics transfer token is missing",
                    rule_id="INV-NO-SILENT-TRANSFER",
                )
            )

    required_routing_tokens = {
        "src/logistics/logistics_engine.py": (
            "_best_route(",
            "sorted(",
            "heapq",
            "route.shortest_delay",
            "route.min_cost_units",
            "edge_id",
        ),
        "tools/xstack/sessionx/scheduler.py": (
            "process.manifest_create",
            "process.manifest_tick",
        ),
    }
    for rel_path, tokens in required_routing_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required deterministic logistics routing file is missing",
                    rule_id="INV-LOGISTICS-DETERMINISTIC-ROUTING",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required deterministic logistics routing token is missing",
                    rule_id="INV-LOGISTICS-DETERMINISTIC-ROUTING",
                )
            )


def _append_material_construction_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_registry_paths = (
        "data/registries/provenance_event_type_registry.json",
        "data/registries/construction_policy_registry.json",
    )
    for rel_path in required_registry_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="construction/provenance registries must be declared as data-only inputs",
                rule_id="INV-PROVENANCE-EVENTS-REQUIRED",
            )
        )

    process_only_fields = (
        "state[\"construction_projects\"]",
        "state[\"construction_steps\"]",
        "state[\"construction_commitments\"]",
        "state[\"construction_provenance_events\"]",
        "state[\"installed_structure_instances\"]",
    )
    process_only_allowed_prefixes = (
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(process_only_allowed_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if not any(field in token for field in process_only_fields):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="construction/install state mutation must occur only through process runtime commit paths",
                    rule_id="INV-NO-SILENT-INSTALL",
                )
            )

    required_commitment_tokens = {
        "src/materials/construction/construction_engine.py": (
            "_construction_commitment_row(",
            "milestone_commitment_ids",
            "start_commitment_id",
            "end_commitment_id",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.construction_project_create",
            "process.construction_project_tick",
            "_persist_construction_state(",
        ),
    }
    for rel_path, tokens in required_commitment_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required construction commitment implementation file is missing",
                    rule_id="INV-CONSTRUCTION-REQUIRES-COMMITMENTS",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required construction commitment token is missing",
                    rule_id="INV-CONSTRUCTION-REQUIRES-COMMITMENTS",
                )
            )

    required_provenance_tokens = {
        "src/materials/construction/construction_engine.py": (
            "_event_row(",
            "event.construct_project_created",
            "event.construct_step_started",
            "event.construct_step_completed",
            "event.install_part",
            "event.material_consumed",
            "event.batch_created",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "construction_provenance_events",
            "_persist_construction_state(",
        ),
    }
    for rel_path, tokens in required_provenance_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required construction provenance implementation file is missing",
                    rule_id="INV-PROVENANCE-EVENTS-REQUIRED",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required construction provenance token is missing",
                    rule_id="INV-PROVENANCE-EVENTS-REQUIRED",
                )
            )

    required_ledger_tokens = {
        "src/materials/construction/construction_engine.py": (
            "ledger_deltas={\"quantity.mass\": -1 * int(total_mass_raw)}",
            "ledger_deltas={\"quantity.mass\": int(total_mass_raw)}",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "_finalize_conservation_or_refusal(",
        ),
    }
    for rel_path, tokens in required_ledger_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required construction ledger accounting file is missing",
                    rule_id="INV-LEDGER-DEBIT-CREDIT-REQUIRED",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required construction ledger debit/credit token is missing",
                    rule_id="INV-LEDGER-DEBIT-CREDIT-REQUIRED",
                )
            )


def _append_material_maintenance_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_registry_paths = (
        "data/registries/failure_mode_registry.json",
        "data/registries/maintenance_policy_registry.json",
        "data/registries/backlog_growth_rule_registry.json",
    )
    for rel_path in required_registry_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="maintenance/failure registries must be declared as data-only inputs",
                rule_id="INV-FAILURE-MODES-REGISTRY-DRIVEN",
            )
        )

    required_registry_tokens = {
        "src/materials/maintenance/decay_engine.py": (
            "failure_mode_rows_by_id(",
            "maintenance_policy_rows_by_id(",
            "backlog_growth_rule_rows_by_id(",
            "tick_decay(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "_policy_payload(policy_context, \"failure_mode_registry\")",
            "_policy_payload(policy_context, \"maintenance_policy_registry\")",
            "_policy_payload(policy_context, \"backlog_growth_rule_registry\")",
            "process.decay_tick",
        ),
    }
    for rel_path, tokens in required_registry_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required maintenance/failure registry-driven implementation file is missing",
                    rule_id="INV-FAILURE-MODES-REGISTRY-DRIVEN",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required maintenance/failure registry token is missing",
                    rule_id="INV-FAILURE-MODES-REGISTRY-DRIVEN",
                )
            )

    process_only_fields = (
        "state[\"asset_health_states\"]",
        "state[\"failure_events\"]",
        "state[\"maintenance_commitments\"]",
        "state[\"maintenance_provenance_events\"]",
    )
    process_only_allowed_prefixes = (
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(process_only_allowed_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if not any(field in token for field in process_only_fields):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="failure/maintenance state mutation must occur only through process runtime commit paths",
                    rule_id="INV-NO-SILENT-FAILURES",
                )
            )

    required_no_silent_failure_tokens = {
        "src/materials/maintenance/decay_engine.py": (
            "_failure_event(",
            "_provenance_event(",
            "failed_mode_ids",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.decay_tick",
            "_persist_maintenance_state(",
            "failure_events",
            "maintenance_provenance_events",
        ),
    }
    for rel_path, tokens in required_no_silent_failure_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required explicit failure/provenance implementation file is missing",
                    rule_id="INV-NO-SILENT-FAILURES",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required explicit failure/provenance token is missing",
                    rule_id="INV-NO-SILENT-FAILURES",
                )
            )

    required_commitment_tokens = {
        "src/materials/maintenance/decay_engine.py": (
            "schedule_maintenance_commitments(",
            "perform_inspection(",
            "perform_maintenance(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.maintenance_schedule",
            "process.inspection_perform",
            "process.maintenance_perform",
            "maintenance_commitments",
        ),
    }
    for rel_path, tokens in required_commitment_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required maintenance commitment implementation file is missing",
                    rule_id="INV-MAINTENANCE-IS-COMMITMENT-DRIVEN",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required maintenance commitment token is missing",
                    rule_id="INV-MAINTENANCE-IS-COMMITMENT-DRIVEN",
                )
            )


def _append_material_materialization_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_schema_paths = (
        "schemas/micro_part_instance.schema.json",
        "schemas/materialization_state.schema.json",
        "schemas/distribution_aggregate.schema.json",
        "schemas/reenactment_descriptor.schema.json",
    )
    for rel_path in required_schema_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="materialization schema artifact missing",
                rule_id="INV-MACRO-STOCK-CANONICAL",
            )
        )

    process_only_fields = (
        "state[\"micro_part_instances\"]",
        "state[\"materialization_states\"]",
        "state[\"distribution_aggregates\"]",
        "state[\"materialization_reenactment_descriptors\"]",
    )
    process_only_allowed_prefixes = (
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(process_only_allowed_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if not any(field in token for field in process_only_fields):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="materialization state mutation must occur only through process runtime commit paths",
                    rule_id="INV-MACRO-STOCK-CANONICAL",
                )
            )

    no_global_tokens = {
        "src/materials/materialization/materialization_engine.py": (
            "max_micro_parts",
            "REFUSAL_MATERIALIZATION_BUDGET_EXCEEDED",
            "materialize_structure_roi(",
            "dematerialize_structure_roi(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.materialize_structure_roi",
            "process.dematerialize_structure_roi",
            "_persist_materialization_state(",
        ),
        "tools/xstack/sessionx/scheduler.py": (
            "process.materialize_structure_roi",
            "process.dematerialize_structure_roi",
        ),
    }
    for rel_path, tokens in no_global_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required materialization budget/process file is missing",
                    rule_id="INV-NO-GLOBAL-MICRO-PARTS",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required materialization budget/process token is missing",
                    rule_id="INV-NO-GLOBAL-MICRO-PARTS",
                )
            )

    deterministic_tokens = {
        "src/materials/materialization/materialization_engine.py": (
            "canonical_sha256",
            "\"stream\": \"materialization\"",
            "_stable_materialization_seed(",
            "_micro_part_id(",
            "sorted(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "inv.transition.expand_materialization",
            "inv.transition.collapse_materialization",
            "exception.numeric_error_budget",
        ),
    }
    for rel_path, tokens in deterministic_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required deterministic materialization file is missing",
                    rule_id="INV-MATERIALIZATION-DETERMINISTIC",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required deterministic materialization token is missing",
                    rule_id="INV-MATERIALIZATION-DETERMINISTIC",
                )
            )


def _append_material_commitment_reenactment_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_schema_paths = (
        "schemas/commitment.schema.json",
        "schemas/event_stream_index.schema.json",
        "schemas/reenactment_request.schema.json",
        "schemas/reenactment_artifact.schema.json",
    )
    for rel_path in required_schema_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="commitment/reenactment schema artifact missing",
                rule_id="INV-REENACTMENT_DERIVED_ONLY",
            )
        )

    process_only_fields = (
        "state[\"material_commitments\"]",
        "state[\"event_stream_indices\"]",
        "state[\"reenactment_requests\"]",
        "state[\"reenactment_artifacts\"]",
    )
    process_only_allowed_prefixes = (
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(process_only_allowed_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if not any(field in token for field in process_only_fields):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token[:140],
                    message="commitment/reenactment state mutation must occur only through process runtime commit paths",
                    rule_id="INV-REENACTMENT_DERIVED_ONLY",
                )
            )

    causality_tokens = {
        "src/materials/commitments/commitment_engine.py": (
            "strictness_requires_commitment(",
            "REFUSAL_COMMITMENT_REQUIRED_MISSING",
            "resolve_causality_strictness_row(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "_enforce_causality_commitment_requirement(",
            "process.commitment_create",
            "process.event_stream_index_rebuild",
            "process.reenactment_generate",
            "process.reenactment_play",
        ),
    }
    for rel_path, tokens in causality_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required causality strictness implementation file is missing",
                    rule_id="INV-NO_SILENT_MACRO_CHANGE",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required causality strictness token is missing",
                    rule_id="INV-NO_SILENT_MACRO_CHANGE",
                )
            )

    derived_only_tokens = {
        "src/materials/commitments/commitment_engine.py": (
            "\"derived_only\": True",
            "build_reenactment_artifact(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.reenactment_generate",
            "process.reenactment_play",
            "skip_state_log = True",
        ),
        "tools/materials/tool_reenact_generate.py": (
            "tool.materials.tool_reenact_generate",
            "build_reenactment_artifact(",
            "\"derived_only\"",
        ),
    }
    for rel_path, tokens in derived_only_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required reenactment derived-only implementation file is missing",
                    rule_id="INV-REENACTMENT_DERIVED_ONLY",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required reenactment derived-only token is missing",
                    rule_id="INV-REENACTMENT_DERIVED_ONLY",
                )
            )


def _append_material_scale_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    strategy_rel = "docs/materials/PERFORMANCE_AND_SCALE_STRATEGY.md"
    strategy_abs = os.path.join(repo_root, strategy_rel.replace("/", os.sep))
    try:
        strategy_text = open(strategy_abs, "r", encoding="utf-8").read()
    except OSError:
        strategy_text = ""
    if not strategy_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=strategy_rel,
                line_number=1,
                snippet="",
                message="MAT scale strategy doctrine is missing",
                rule_id="INV-MAT-SCALE-POLICY-DECLARED",
            )
        )
    else:
        for token in (
            "No Lag Spikes Contract",
            "Deterministic Degradation Priorities",
            "cache snapshots by deterministic input hash anchors",
            "Regression Locks",
        ):
            if token in strategy_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=strategy_rel,
                    line_number=1,
                    snippet=token,
                    message="MAT scale strategy missing required doctrine token",
                    rule_id="INV-MAT-SCALE-POLICY-DECLARED",
                )
            )

    required_tokens = {
        "src/materials/performance/mat_scale_engine.py": (
            "DEFAULT_MAT_DEGRADATION_ORDER",
            "compute_mat_cost_usage(",
            "apply_mat_degradation_policy(",
            "run_stress_simulation(",
            "_inspection_cache_key(",
        ),
        "tools/materials/tool_generate_factory_planet_scenario.py": (
            "default_factory_planet_scenario(",
            "deterministic_fingerprint",
        ),
        "tools/materials/tool_run_stress.py": (
            "run_stress_simulation(",
            "stress_report",
            "inspection_cache_hit_rate_permille",
        ),
    }
    for rel_path, tokens in required_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required MAT scale deterministic implementation file is missing",
                    rule_id="INV-DEGRADE-NOT-MELTDOWN",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required MAT scale deterministic token is missing",
                    rule_id="INV-DEGRADE-NOT-MELTDOWN",
                )
            )

    wallclock_patterns = (
        "time.time(",
        "time.perf_counter(",
        "time.monotonic(",
        "datetime.now(",
    )
    for rel_path in (
        "src/materials/performance/mat_scale_engine.py",
        "tools/materials/tool_generate_factory_planet_scenario.py",
        "tools/materials/tool_run_stress.py",
    ):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        lowered = text.lower()
        for token in wallclock_patterns:
            if token not in lowered:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="MAT stress paths must not use wall-clock APIs",
                    rule_id="INV-NO-WALLCLOCK-IN-STRESS",
                )
            )

    payload, err = _load_json_object(repo_root, MAT_SCALE_REGRESSION_LOCK_PATH)
    if err:
        findings.append(
            _finding(
                severity=severity,
                file_path=MAT_SCALE_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="",
                message="MAT scale regression baseline lock file is missing or invalid",
                rule_id="INV-MAT-SCALE-REGRESSION-LOCK-PRESENT",
            )
        )
        return
    for field in MAT_SCALE_REGRESSION_LOCK_REQUIRED_FIELDS:
        value = payload.get(field)
        if value is None or (isinstance(value, str) and not str(value).strip()):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=MAT_SCALE_REGRESSION_LOCK_PATH,
                    line_number=1,
                    snippet=field,
                    message="MAT scale regression lock missing required field '{}'".format(field),
                    rule_id="INV-MAT-SCALE-REGRESSION-LOCK-PRESENT",
                )
            )
    hashes = payload.get("hash_anchor_stream")
    if not isinstance(hashes, list) or not hashes:
        findings.append(
            _finding(
                severity=severity,
                file_path=MAT_SCALE_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="hash_anchor_stream",
                message="MAT scale regression lock requires non-empty hash_anchor_stream",
                rule_id="INV-MAT-SCALE-REGRESSION-LOCK-PRESENT",
            )
        )
    hit_pattern = payload.get("inspection_cache_hit_pattern")
    if not isinstance(hit_pattern, dict):
        findings.append(
            _finding(
                severity=severity,
                file_path=MAT_SCALE_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="inspection_cache_hit_pattern",
                message="MAT scale regression lock requires inspection_cache_hit_pattern object",
                rule_id="INV-MAT-SCALE-REGRESSION-LOCK-PRESENT",
            )
        )
    required_tag = ""
    update_policy = payload.get("update_policy")
    if isinstance(update_policy, dict):
        required_tag = str(update_policy.get("required_commit_tag", "")).strip()
    if not required_tag:
        findings.append(
            _finding(
                severity=severity,
                file_path=MAT_SCALE_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet="update_policy.required_commit_tag",
                message="MAT scale regression lock must declare update_policy.required_commit_tag",
                rule_id="INV-MAT-SCALE-REGRESSION-LOCK-PRESENT",
            )
        )
        return
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--pretty=%s", "--", MAT_SCALE_REGRESSION_LOCK_PATH],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return
    if int(proc.returncode) != 0:
        return
    subject = str(proc.stdout or "").strip()
    if subject and required_tag not in subject:
        findings.append(
            _finding(
                severity=severity,
                file_path=MAT_SCALE_REGRESSION_LOCK_PATH,
                line_number=1,
                snippet=subject[:140],
                message="latest MAT scale baseline commit message must include '{}'".format(required_tag),
                rule_id="INV-MAT-SCALE-REGRESSION-LOCK-PRESENT",
            )
        )


def _append_core_abstraction_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_files = {
        "src/core/graph/network_graph_engine.py": (
            "INV-NO-DUPLICATE-GRAPH-SUBSTRATES",
            ("normalize_network_graph(", "route_query(", "heapq.heappush("),
            "core graph substrate file missing deterministic graph tokens",
        ),
        "src/core/graph/routing_engine.py": (
            "INV-NETWORKGRAPH-ONLY",
            ("query_route_result(", "route_query_edges(", "build_route_cache_key("),
            "core routing substrate file missing deterministic NetworkGraph routing tokens",
        ),
        "src/core/schedule/schedule_engine.py": (
            "INV-NO-DUPLICATE-SCHEDULERS",
            ("normalize_schedule(", "advance_schedule(", "recurrence_rule"),
            "core schedule substrate file missing deterministic schedule tokens",
        ),
        "src/core/state/state_machine_engine.py": (
            "INV-NO-ADHOC-STATE-MACHINES",
            ("normalize_state_machine(", "apply_transition(", "trigger_process_id"),
            "core state-machine substrate file missing deterministic transition tokens",
        ),
        "src/core/constraints/constraint_engine.py": (
            "INV-CONSTRAINTS-USE-COMPONENT",
            ("normalize_constraint_component(", "tick_constraints(", "build_constraint_enforcement_hooks("),
            "core constraint substrate file missing deterministic constraint component tokens",
        ),
        "src/core/hazards/hazard_engine.py": (
            "INV-NO-ADHOC-HAZARD-LOOPS",
            ("normalize_hazard_model(", "tick_hazard_models(", "consequence_process_id"),
            "core hazard substrate file missing deterministic hazard component tokens",
        ),
        "src/core/flow/flow_engine.py": (
            "INV-NO-DUPLICATE-FLOW-LOGIC",
            ("normalize_flow_channel(", "tick_flow_channels(", "normalize_flow_transfer_event(", "quantity_id"),
            "core flow substrate file missing deterministic flow tokens",
        ),
    }
    for rel_path, (rule_id, tokens, message) in required_files.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message=message,
                    rule_id=rule_id,
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message=message,
                    rule_id=rule_id,
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/graph/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        if (
            "heapq.heappush(" in text
            and "from_node_id" in text
            and "to_node_id" in text
            and "edge_id" in text
        ):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="heapq.heappush(",
                    message="graph traversal/path search must be implemented in src/core/graph only",
                    rule_id="INV-NO-DUPLICATE-GRAPH-SUBSTRATES",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/graph/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        has_custom_routing_tokens = (
            "heapq.heappush(" in text
            and "route_policy_id" in text
            and "path_edge_ids" in text
            and "path_node_ids" in text
        )
        imports_core_graph = (
            "from src.core.graph" in text
            or "import src.core.graph" in text
            or "src.core.graph." in text
        )
        if has_custom_routing_tokens and (not imports_core_graph):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="heapq.heappush(",
                    message="NetworkGraph routing implementations must live in src/core/graph or wrap it explicitly",
                    rule_id="INV-NETWORKGRAPH-ONLY",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/schedule/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        if "recurrence_rule" in text and "next_due_tick" in text and "def " in text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="recurrence_rule",
                    message="schedule recurrence logic must use src/core/schedule substrate",
                    rule_id="INV-NO-DUPLICATE-SCHEDULERS",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/state/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        if "from_state_id" in text and "to_state_id" in text and "trigger_process_id" in text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="trigger_process_id",
                    message="state transition models must use src/core/state substrate",
                    rule_id="INV-NO-ADHOC-STATE-MACHINES",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/flow/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        if "def flow_transfer(" in text or "def tick_flow_channels(" in text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="def flow_transfer(" if "def flow_transfer(" in text else "def tick_flow_channels(",
                    message="flow math engines must be implemented only in src/core/flow",
                    rule_id="INV-NO-DUPLICATE-FLOW-LOGIC",
                )
            )

    flow_required_tokens = {
        "src/logistics/logistics_engine.py": ("tick_flow_channels(", "_best_route(", "flow_channel_id"),
        "tools/xstack/sessionx/process_runtime.py": ("_ledger_emit_exception(", "process.manifest_tick", "flow_transfer_events"),
    }
    for rel_path, tokens in flow_required_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="flow subsystem integration file missing for ledger coupling checks",
                    rule_id="INV-FLOW-USES-LEDGER-FOR-CONSERVED",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="flow paths must remain process-driven and ledger-accounted",
                    rule_id="INV-FLOW-USES-LEDGER-FOR-CONSERVED",
                )
            )

    behavior_required_tokens = {
        "src/materials/maintenance/decay_engine.py": {
            "INV-NO-ADHOC-STATE-FLAGS": ("apply_transition(", "state_machine", "_STATE_MACHINE_TYPE_ID"),
            "INV-NO-ADHOC-SCHEDULERS": ("tick_schedules(", "_schedule_id(", "schedule_component"),
            "INV-NO-ADHOC-HAZARD-LOOPS": ("tick_hazard_models(", "_hazard_id(", "hazard_type_id"),
        }
    }
    for rel_path, rule_map in behavior_required_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            for rule_id in sorted(rule_map.keys()):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet="",
                        message="behavioral component migration file missing for ABS-4 invariants",
                        rule_id=rule_id,
                    )
                )
            continue
        lowered = text.lower()
        if "import random" in lowered or "from random import" in lowered or "random." in lowered:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="random",
                    message="hazard behavior must remain deterministic and component-driven",
                    rule_id="INV-NO-ADHOC-HAZARD-LOOPS",
                )
            )
        for rule_id, tokens in sorted(rule_map.items(), key=lambda item: str(item[0])):
            for token in tokens:
                if token in text:
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="behavioral component invariants require component-engine usage tokens",
                        rule_id=rule_id,
                    )
                )

    interior_required_tokens = {
        "src/interior/interior_engine.py": {
            "INV-PORTAL-USES-STATE-MACHINE": (
                "apply_portal_transition(",
                "normalize_state_machine(",
                "apply_transition(",
                "state_machine_id",
            ),
        },
        "tools/xstack/sessionx/observation.py": {
            "INV-NO-ADHOC-OCCLUSION": (
                "_apply_interior_occlusion(",
                "path_exists(",
                "interior_portal_state_machines",
            ),
            "INV-NO-TRUTH-LEAK-IN-INSTRUMENTS": (
                "_instrument_channel_view(",
                "instrument.interior.pressure",
                "instrument.interior.alarm",
            ),
            "INV-INTERIOR-STATE-DIEGETIC-GATED": (
                "ch.diegetic.pressure_status",
                "ch.diegetic.oxygen_status",
                "ch.diegetic.door_indicator",
            ),
            "INV-NO-OMNISCIENT-INTERIOR-UI": (
                "_viewer_graph_portal_entity_ids(",
                "viewer_graph_id",
                "interior.portal.",
            ),
        },
        "src/interior/compartment_flow_builder.py": {
            "INV-INTERIOR-FLOWS-USE-FLOWSYSTEM": (
                "normalize_flow_channel(",
                "build_compartment_flow_channels(",
                "channel.interior.",
            ),
            "INV-NO-ADHOC-CFD": (
                "conductance_air",
                "conductance_water",
                "conductance_smoke",
            ),
        },
        "src/interior/compartment_flow_engine.py": {
            "INV-INTERIOR-FLOWS-USE-FLOWSYSTEM": (
                "tick_flow_channels(",
                "build_compartment_flow_channels(",
                "flow_solver_policy_registry",
            ),
            "INV-NO-ADHOC-CFD": (
                "_pressure_from_air_mass(",
                "_substeps_for_dt(",
                "_flow_balance_for_medium(",
            ),
        },
        "src/inspection/inspection_engine.py": {
            "INV-INTERIOR-STATE-DIEGETIC-GATED": (
                "section.interior.connectivity_summary",
                "section.interior.flow_summary",
                "allow_hidden_state",
            ),
            "INV-NO-OMNISCIENT-INTERIOR-UI": (
                "epistemic_redaction_level",
                "quant_step",
                "target_kind",
            ),
        },
        "src/client/interaction/inspection_overlays.py": {
            "INV-NO-OMNISCIENT-INTERIOR-UI": (
                "_interior_overlay_payload(",
                "section.interior.pressure_summary",
                "inspection_snapshot",
            ),
        },
    }
    for rel_path, rule_map in sorted(interior_required_tokens.items(), key=lambda item: str(item[0])):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            for rule_id in sorted(rule_map.keys()):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet="",
                        message="interior subsystem invariant file missing",
                        rule_id=rule_id,
                    )
                )
            continue
        for rule_id, tokens in sorted(rule_map.items(), key=lambda item: str(item[0])):
            for token in tokens:
                if token in text:
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                    message="interior subsystem invariants require deterministic occlusion/state-machine tokens",
                    rule_id=rule_id,
                )
            )

    pose_mount_required_tokens = {
        "tools/xstack/sessionx/process_runtime.py": {
            "INV-POSE-REQUIRES-PROCESS": (
                "process.pose_enter",
                "process.pose_exit",
                "process.meta_pose_override",
                "enter_pose_slot(",
                "exit_pose_slot(",
                "_persist_pose_mount_state(",
            ),
            "INV-MOUNT-REQUIRES-PROCESS": (
                "process.mount_attach",
                "process.mount_detach",
                "attach_mount_points(",
                "detach_mount_point(",
                "_persist_pose_mount_state(",
            ),
            "INV-NO-TELEPORT-OCCUPY": (
                "_pose_slot_accessible_by_path(",
                "path_exists(",
                "REFUSAL_POSE_NO_ACCESS_PATH",
            ),
        },
        "src/interaction/pose/pose_engine.py": {
            "INV-POSE-REQUIRES-PROCESS": (
                "def enter_pose_slot(",
                "def exit_pose_slot(",
                "REFUSAL_POSE_OCCUPIED",
                "REFUSAL_POSE_NOT_OCCUPANT",
            ),
        },
        "src/interaction/mount/mount_engine.py": {
            "INV-MOUNT-REQUIRES-PROCESS": (
                "def attach_mount_points(",
                "def detach_mount_point(",
                "REFUSAL_MOUNT_INCOMPATIBLE",
                "REFUSAL_MOUNT_ALREADY_ATTACHED",
            ),
        },
    }
    for rel_path, rule_map in sorted(pose_mount_required_tokens.items(), key=lambda item: str(item[0])):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            for rule_id in sorted(rule_map.keys()):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet="",
                        message="POSE/Mount invariant file missing",
                        rule_id=rule_id,
                    )
                )
            continue
        for rule_id, tokens in sorted(rule_map.items(), key=lambda item: str(item[0])):
            for token in tokens:
                if token in text:
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet=token,
                        message="POSE/Mount invariants require deterministic process-driven occupancy/attachment tokens",
                        rule_id=rule_id,
                    )
                )

    pose_mount_mutation_allowed_prefixes = (
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(pose_mount_mutation_allowed_prefixes):
            continue
        if rel_path == "tools/xstack/repox/check.py":
            continue
        if rel_path.startswith(("tools/xstack/out/", "tools/auditx/cache/")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if any(
                marker in token
                for marker in (
                    'state["pose_slots"]',
                    "state['pose_slots']",
                    'state["mount_points"]',
                    "state['mount_points']",
                    'state["pose_mount_provenance_events"]',
                    "state['pose_mount_provenance_events']",
                )
            ):
                rule_id = "INV-POSE-REQUIRES-PROCESS"
                if "mount_points" in token:
                    rule_id = "INV-MOUNT-REQUIRES-PROCESS"
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token[:140],
                        message="pose/mount state mutation must occur only through deterministic process runtime commit paths",
                        rule_id=rule_id,
                    )
                )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/interior/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        ad_hoc_occlusion_tokens = (
            "interior_volume_id" in text
            and "portal" in text
            and ("path_exists(" in text or "reachable_volumes(" in text)
        )
        uses_interior_substrate = (
            "from src.interior" in text
            or "import src.interior" in text
            or "src.interior." in text
        )
        if ad_hoc_occlusion_tokens and not uses_interior_substrate:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="interior_volume_id",
                    message="interior occlusion/path logic must be centralized in src/interior and observation integration",
                    rule_id="INV-NO-ADHOC-OCCLUSION",
                )
            )
        ad_hoc_compartment_flow_tokens = (
            "air_mass" in text
            and "water_volume" in text
            and "portal" in text
            and ("tick_flow_channels(" not in text and "build_compartment_flow_channels(" not in text)
        )
        if ad_hoc_compartment_flow_tokens and not uses_interior_substrate:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="air_mass",
                    message="interior compartment flows must use src/interior + FlowSystem substrate; ad-hoc CFD/flow loops are forbidden",
                    rule_id="INV-NO-ADHOC-CFD",
                )
            )

    observation_rel = "tools/xstack/sessionx/observation.py"
    observation_abs = os.path.join(repo_root, observation_rel.replace("/", os.sep))
    try:
        observation_text = open(observation_abs, "r", encoding="utf-8").read()
    except OSError:
        observation_text = ""
    if observation_text:
        forbidden_truth_tokens = ("compartment_states", "interior_leak_hazards", "portal_flow_params")
        for token in forbidden_truth_tokens:
            if token not in observation_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=observation_rel,
                    line_number=1,
                    snippet=token,
                    message="diegetic interior instrument channels must remain derived from instrument assemblies/perceived model",
                    rule_id="INV-NO-TRUTH-LEAK-IN-INSTRUMENTS",
                )
            )


def _load_intent_dispatch_whitelist_patterns(repo_root: str) -> Tuple[List[str], str]:
    rel_path = INTENT_DISPATCH_WHITELIST_REGISTRY_REL
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return list(DEFAULT_INTENT_DISPATCH_ALLOWED_PATTERNS), "missing or invalid whitelist registry"
    if not isinstance(payload, dict):
        return list(DEFAULT_INTENT_DISPATCH_ALLOWED_PATTERNS), "invalid whitelist root object"
    record = payload.get("record")
    if not isinstance(record, dict):
        return list(DEFAULT_INTENT_DISPATCH_ALLOWED_PATTERNS), "missing whitelist record object"
    rows = record.get("allowed_file_patterns")
    if not isinstance(rows, list):
        return list(DEFAULT_INTENT_DISPATCH_ALLOWED_PATTERNS), "missing allowed_file_patterns list"
    patterns = sorted(
        set(_norm(str(item).strip()) for item in rows if str(item).strip())
    )
    if not patterns:
        return list(DEFAULT_INTENT_DISPATCH_ALLOWED_PATTERNS), "empty allowed_file_patterns list"
    return patterns, ""


def _path_matches_glob_pattern(rel_path: str, patterns: List[str]) -> bool:
    token = _norm(rel_path)
    for pattern in list(patterns or []):
        matcher = _norm(pattern)
        if not matcher:
            continue
        if fnmatch.fnmatch(token, matcher):
            return True
    return False


def _read_json_object(path: str) -> Dict[str, object]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_deprecation_entries(repo_root: str) -> Tuple[List[Dict[str, object]], str]:
    registry_abs = os.path.join(repo_root, DEPRECATIONS_REGISTRY_REL.replace("/", os.sep))
    payload = _read_json_object(registry_abs)
    if not payload:
        return [], "missing or invalid deprecations registry JSON"
    rows = payload.get("entries")
    if not isinstance(rows, list):
        return [], "deprecations registry missing entries list"
    out = [row for row in rows if isinstance(row, dict)]
    return out, ""


def _collect_changed_paths(repo_root: str) -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "-uall"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return []
    if int(proc.returncode) != 0:
        return []
    out: List[str] = []
    for line in str(proc.stdout or "").splitlines():
        token = str(line[3:] if len(line) >= 3 else line).strip()
        if not token:
            continue
        out.append(_norm(token))
    return sorted(set(out))


def _file_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_boundary_blocker_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    existing_keys = set(
        (
            str(row.get("rule_id", "")),
            str(row.get("file_path", "")),
            int(row.get("line_number", 0) or 0),
            str(row.get("snippet", "")),
            str(row.get("message", "")),
        )
        for row in list(findings or [])
        if isinstance(row, dict)
    )
    for row in list(findings or []):
        if not isinstance(row, dict):
            continue
        src_rule_id = str(row.get("rule_id", "")).strip()
        for alias_rule_id, source_rule_ids in BOUNDARY_ALIAS_RULES.items():
            if src_rule_id not in source_rule_ids:
                continue
            key = (
                alias_rule_id,
                str(row.get("file_path", "")),
                int(row.get("line_number", 0) or 0),
                str(row.get("snippet", "")),
                str(row.get("message", "")),
            )
            if key in existing_keys:
                continue
            existing_keys.add(key)
            findings.append(
                _finding(
                    severity=severity,
                    file_path=str(row.get("file_path", "")),
                    line_number=int(row.get("line_number", 0) or 0),
                    snippet=str(row.get("snippet", "")),
                    message=str(row.get("message", "")),
                    rule_id=alias_rule_id,
                )
            )

    runtime_roots = ("src/", "engine/", "game/", "client/", "server/")
    runtime_skip_prefixes = (
        "tools/",
        "docs/",
        "build/",
        "dist/",
        "legacy/",
        ".xstack_cache/",
    )
    tool_include_patterns = (
        re.compile(r"^\s*from\s+tools\.auditx\b", re.IGNORECASE),
        re.compile(r"^\s*import\s+tools\.auditx\b", re.IGNORECASE),
        re.compile(r"^\s*from\s+tools\.governance\b", re.IGNORECASE),
        re.compile(r"^\s*import\s+tools\.governance\b", re.IGNORECASE),
        re.compile(r"^\s*from\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
        re.compile(r"^\s*import\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
        re.compile(r'^\s*#\s*include\s*[<"]tools/', re.IGNORECASE),
        re.compile(r'^\s*#\s*include\s*[<"]\.\./tools/', re.IGNORECASE),
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.startswith(runtime_roots):
            continue
        if rel_norm.startswith(runtime_skip_prefixes):
            continue
        _, ext = os.path.splitext(rel_norm.lower())
        if ext not in (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp"):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            token = str(line).strip()
            if not token:
                continue
            if not any(pattern.search(token) for pattern in tool_include_patterns):
                continue
            key = (
                "INV-NO-TOOLS-IN-RUNTIME",
                rel_norm,
                int(line_no),
                token[:140],
                "runtime modules must not import/include tool-suite paths",
            )
            if key in existing_keys:
                continue
            existing_keys.add(key)
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=int(line_no),
                    snippet=token[:140],
                    message="runtime modules must not import/include tool-suite paths",
                    rule_id="INV-NO-TOOLS-IN-RUNTIME",
                )
            )

    whitelist_patterns, whitelist_error = _load_intent_dispatch_whitelist_patterns(repo_root)
    if whitelist_error:
        key = (
            "INV-CONTROL-PLANE-ONLY-DISPATCH",
            INTENT_DISPATCH_WHITELIST_REGISTRY_REL,
            1,
            "",
            "intent dispatch whitelist registry is missing or invalid",
        )
        if key not in existing_keys:
            existing_keys.add(key)
            findings.append(
                _finding(
                    severity=severity,
                    file_path=INTENT_DISPATCH_WHITELIST_REGISTRY_REL,
                    line_number=1,
                    snippet="",
                    message="intent dispatch whitelist registry is missing or invalid",
                    rule_id="INV-CONTROL-PLANE-ONLY-DISPATCH",
                )
            )

    envelope_file_roots = ("src/",)
    envelope_skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/xstack/out/",
        "tools/auditx/analyzers/",
        "tests/",
    )
    required_envelope_markers = (
        '"envelope_id"',
        '"payload_schema_id"',
        '"pack_lock_hash"',
        '"authority_summary"',
    )
    explicit_builder_tokens = (
        "build_client_intent_envelope(",
        "_build_envelope(",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(envelope_file_roots):
            continue
        if rel_norm.startswith(envelope_skip_prefixes):
            continue
        abs_path = os.path.join(repo_root, rel_norm.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        has_envelope_literal = all(marker in text for marker in required_envelope_markers)
        has_builder_token = any(marker in text for marker in explicit_builder_tokens)
        if (not has_envelope_literal) and (not has_builder_token):
            continue
        if _path_matches_glob_pattern(rel_norm, whitelist_patterns):
            continue
        snippet = "intent envelope construction markers"
        if has_builder_token:
            snippet = (
                "build_client_intent_envelope("
                if "build_client_intent_envelope(" in text
                else "_build_envelope("
            )
        key = (
            "INV-CONTROL-PLANE-ONLY-DISPATCH",
            rel_norm,
            1,
            snippet,
            "intent envelope construction is restricted to whitelist-registry paths",
        )
        if key in existing_keys:
            continue
        existing_keys.add(key)
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_norm,
                line_number=1,
                snippet=snippet,
                message="intent envelope construction is restricted to whitelist-registry paths",
                rule_id="INV-CONTROL-PLANE-ONLY-DISPATCH",
            )
        )

    for rel_path, required_tokens in sorted(
        PUBLIC_INTERACTION_ENTRYPOINT_REQUIREMENTS.items(),
        key=lambda item: str(item[0]),
    ):
        text = _file_text(repo_root, rel_path)
        if not text:
            key = (
                "INV-CONTROL-INTENT-REQUIRED",
                rel_path,
                1,
                "",
                "public interaction entrypoint file is missing",
            )
            if key not in existing_keys:
                existing_keys.add(key)
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=1,
                        snippet="",
                        message="public interaction entrypoint file is missing",
                        rule_id="INV-CONTROL-INTENT-REQUIRED",
                    )
                )
            continue
        for token in list(required_tokens or []):
            if str(token) in text:
                continue
            key = (
                "INV-CONTROL-INTENT-REQUIRED",
                rel_path,
                1,
                str(token),
                "public-facing interaction entrypoints must route through ControlIntent and control-plane resolution",
            )
            if key in existing_keys:
                continue
            existing_keys.add(key)
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=str(token),
                    message="public-facing interaction entrypoints must route through ControlIntent and control-plane resolution",
                    rule_id="INV-CONTROL-INTENT-REQUIRED",
                )
            )

    direct_process_call_pattern = re.compile(r"\b(?:run_process|execute_process|execute_intent|runtime_execute_intent)\s*\(")
    process_literal_pattern = re.compile(r"[\"']process\.[a-zA-Z0-9_.-]+[\"']")
    process_id_literal_pattern = re.compile(r"[\"']process_id[\"']\s*:\s*[\"']process\.[a-zA-Z0-9_.-]+[\"']")
    ui_scan_paths: List[str] = []
    for root in UI_DIRECT_PROCESS_SCAN_ROOTS:
        abs_root = os.path.join(repo_root, str(root).replace("/", os.sep))
        if os.path.isfile(abs_root):
            ui_scan_paths.append(_norm(os.path.relpath(abs_root, repo_root)))
            continue
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                ui_scan_paths.append(_norm(os.path.relpath(os.path.join(walk_root, name), repo_root)))
    for rel_norm in sorted(set(ui_scan_paths)):
        if not rel_norm.endswith(".py"):
            continue
        if any(
            rel_norm.startswith(prefix) if prefix.endswith("/") else rel_norm == prefix
            for prefix in UI_DIRECT_PROCESS_ALLOWED_FILES
        ):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            direct_call = bool(direct_process_call_pattern.search(snippet) and process_literal_pattern.search(snippet))
            direct_process_id_literal = bool(process_id_literal_pattern.search(snippet))
            if (not direct_call) and (not direct_process_id_literal):
                continue
            key = (
                "INV-CONTROL-INTENT-REQUIRED",
                rel_norm,
                int(line_no),
                snippet[:140],
                "UI interaction modules must not invoke process.* directly; build ControlIntent and route through control-plane dispatch",
            )
            if key in existing_keys:
                continue
            existing_keys.add(key)
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=int(line_no),
                    snippet=snippet[:140],
                    message="UI interaction modules must not invoke process.* directly; build ControlIntent and route through control-plane dispatch",
                    rule_id="INV-CONTROL-INTENT-REQUIRED",
                )
            )
            break


def _append_deprecation_framework_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    try:
        from tools.governance.tool_deprecation_check import validate_deprecation_registry
    except Exception as exc:
        findings.append(
            _finding(
                severity=severity,
                file_path=DEPRECATIONS_REGISTRY_REL,
                line_number=1,
                snippet="",
                message="unable to import deprecation validator: {}".format(str(exc)),
                rule_id="INV-DEPRECATION-REGISTRY-VALID",
            )
        )
        return

    validation = validate_deprecation_registry(
        repo_root=repo_root,
        deprecations_rel=DEPRECATIONS_REGISTRY_REL,
        topology_map_rel="docs/audit/TOPOLOGY_MAP.json",
    )
    if str(validation.get("result", "")) != "pass":
        for row in list(validation.get("errors") or []):
            if not isinstance(row, dict):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=DEPRECATIONS_REGISTRY_REL,
                    line_number=1,
                    snippet=str(row.get("path", "")),
                    message="{} ({})".format(str(row.get("message", "")), str(row.get("code", ""))),
                    rule_id="INV-DEPRECATION-REGISTRY-VALID",
                )
            )

    entries, load_err = _load_deprecation_entries(repo_root)
    if load_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=DEPRECATIONS_REGISTRY_REL,
                line_number=1,
                snippet="",
                message=load_err,
                rule_id="INV-DEPRECATION-REGISTRY-VALID",
            )
        )
        return

    adapter_paths = sorted(
        set(
            _norm(str(row.get("adapter_path", "")).strip())
            for row in entries
            if isinstance(row, dict) and str(row.get("adapter_path", "")).strip()
        )
    )
    deprecated_ids = sorted(
        set(
            str(row.get("deprecated_id", "")).strip()
            for row in entries
            if isinstance(row, dict)
            and str(row.get("deprecated_id", "")).strip()
            and str(row.get("status", "")).strip() in {"deprecated", "quarantined", "removed"}
        )
    )

    runtime_prefixes = ("src/", "engine/", "game/", "client/", "server/", "platform/")
    runtime_file_exts = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp")
    all_code_prefixes = runtime_prefixes + ("tools/",)
    legacy_import_patterns = (
        re.compile(r"^\s*from\s+(legacy|quarantine)\b"),
        re.compile(r"^\s*import\s+(legacy|quarantine)\b"),
        re.compile(r'^\s*#\s*include\s*[<"](?:\.\./)*(legacy|quarantine)/', re.IGNORECASE),
        re.compile(r'^\s*#\s*include\s*[<"](?:\.\./)*(legacy|quarantine)\\', re.IGNORECASE),
    )

    for root in runtime_prefixes:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(runtime_file_exts):
                    continue
                rel_norm = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                for line_no, line in _iter_lines(repo_root, rel_norm):
                    token = str(line)
                    if not any(pattern.search(token) for pattern in legacy_import_patterns):
                        continue
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=str(line).strip()[:140],
                            message="production/runtime code must not import/reference legacy or quarantine paths",
                            rule_id="INV-NO-PRODUCTION-LEGACY-IMPORT",
                        )
                    )

    for root in all_code_prefixes:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(runtime_file_exts):
                    continue
                rel_norm = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_norm.startswith(("tools/xstack/testx/tests/", "tools/xstack/out/", "build/", "dist/")):
                    continue
                for line_no, line in _iter_lines(repo_root, rel_norm):
                    token = str(line)
                    if not any(pattern.search(token) for pattern in legacy_import_patterns):
                        continue
                    if rel_norm in adapter_paths:
                        continue
                    findings.append(
                        _finding(
                            severity=severity,
                            file_path=rel_norm,
                            line_number=line_no,
                            snippet=token.strip()[:140],
                            message="legacy/quarantine access is allowed only from declared adapter paths",
                            rule_id="INV-ADAPTER-ONLY-ACCESS",
                        )
                    )
                    break

    changed_paths = _collect_changed_paths(repo_root)
    for rel_norm in changed_paths:
        if not rel_norm.startswith(all_code_prefixes):
            continue
        if rel_norm.startswith(("docs/", "data/", "schema/", "schemas/", "tools/xstack/testx/tests/", "tests/")):
            continue
        text = _file_text(repo_root, rel_norm)
        if not text:
            continue
        for deprecated_id in deprecated_ids:
            if deprecated_id not in text:
                continue
            if rel_norm in {DEPRECATIONS_REGISTRY_REL, "tools/xstack/repox/check.py"}:
                continue
            if rel_norm in adapter_paths:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=1,
                    snippet=deprecated_id[:140],
                    message="new code paths must not introduce deprecated identifier references",
                    rule_id="INV-NO-NEW-USE-OF-DEPRECATED",
                )
            )
            break


def _append_retro_consistency_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    retro_required_files = {
        "src/core/graph/network_graph_engine.py": (
            "INV-NO-DUPLICATE-GRAPH",
            ("normalize_network_graph(", "route_query("),
            "retro-consistency requires canonical core graph substrate",
        ),
        "src/core/flow/flow_engine.py": (
            "INV-NO-DUPLICATE-FLOW",
            ("normalize_flow_channel(", "tick_flow_channels("),
            "retro-consistency requires canonical core flow substrate",
        ),
        "src/core/state/state_machine_engine.py": (
            "INV-NO-ADHOC-STATE-FLAG",
            ("normalize_state_machine(", "apply_transition("),
            "retro-consistency requires canonical state-machine substrate",
        ),
        "src/core/schedule/schedule_engine.py": (
            "INV-NO-ADHOC-SCHEDULER",
            ("normalize_schedule(", "tick_schedules("),
            "retro-consistency requires canonical schedule substrate",
        ),
        "src/core/hazards/hazard_engine.py": (
            "INV-NO-ADHOC-HAZARD",
            ("normalize_hazard_model(", "tick_hazard_models("),
            "retro-consistency requires canonical hazard substrate",
        ),
    }
    for rel_path, (rule_id, tokens, message) in sorted(retro_required_files.items(), key=lambda item: str(item[0])):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message=message,
                    rule_id=rule_id,
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message=message,
                    rule_id=rule_id,
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/graph/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if (
            text
            and "heapq.heappush(" in text
            and "from_node_id" in text
            and "to_node_id" in text
            and "edge_id" in text
        ):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="heapq.heappush(",
                    message="graph traversal/path search must stay in src/core/graph substrate",
                    rule_id="INV-NO-DUPLICATE-GRAPH",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/flow/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if (not text) or ("def " not in text):
            continue
        if "def flow_transfer(" in text or "def tick_flow_channels(" in text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="def flow_transfer(" if "def flow_transfer(" in text else "def tick_flow_channels(",
                    message="flow transfer logic must stay in src/core/flow substrate",
                    rule_id="INV-NO-DUPLICATE-FLOW",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/state/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if text and "from_state_id" in text and "to_state_id" in text and "trigger_process_id" in text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="trigger_process_id",
                    message="state transition logic must use StateMachine substrate",
                    rule_id="INV-NO-ADHOC-STATE-FLAG",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/schedule/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if text and "recurrence_rule" in text and "next_due_tick" in text and "def " in text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="recurrence_rule",
                    message="recurrence/scheduling logic must use Schedule substrate",
                    rule_id="INV-NO-ADHOC-SCHEDULER",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(("src/core/hazards/", "tools/xstack/testx/tests/", "tests/")):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if (
            text
            and "base_hazard_rate_per_tick" in text
            and "accumulation" in text
            and "threshold" in text
            and "consequence_process_id" in text
        ):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="base_hazard_rate_per_tick",
                    message="hazard accumulation/threshold logic must use Hazard substrate",
                    rule_id="INV-NO-ADHOC-HAZARD",
                )
            )

    allowed_intent_dispatch_paths = {
        "src/control/control_plane_engine.py",
        "src/client/interaction/interaction_dispatch.py",
        "src/net/srz/shard_coordinator.py",
        "src/net/policies/policy_server_authoritative.py",
    }
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if not rel_path.startswith("src/"):
            continue
        if rel_path.startswith(
            (
                "tools/xstack/testx/tests/",
                "tests/",
                "tools/xstack/out/",
                "tools/auditx/analyzers/",
            )
        ):
            continue
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            continue
        has_execute_call = ("execute_intent(" in text) and ("def execute_intent(" not in text)
        has_envelope_builder = ("build_client_intent_envelope(" in text) or ("_build_envelope(" in text)
        if rel_path not in allowed_intent_dispatch_paths and (has_execute_call or has_envelope_builder):
            snippet = (
                "execute_intent("
                if has_execute_call
                else ("build_client_intent_envelope(" if "build_client_intent_envelope(" in text else "_build_envelope(")
            )
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=snippet,
                    message="direct intent dispatch is restricted to canonical control/interaction pipeline files",
                    rule_id="INV-CONTROL-PLANE-ONLY-DISPATCH",
                )
            )

    control_plane_path = "src/control/control_plane_engine.py"
    control_plane_text = _file_text(repo_root, control_plane_path)
    if (not control_plane_text) or ("_write_decision_log(" not in control_plane_text) or ('"decision_log_ref"' not in control_plane_text):
        findings.append(
            _finding(
                severity=severity,
                file_path=control_plane_path,
                line_number=1,
                snippet="_write_decision_log(",
                message="control plane resolutions must emit deterministic decision logs",
                rule_id="INV-DECISION-LOG-MANDATORY",
            )
        )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith((".py", ".cpp", ".h", ".hpp", ".c", ".cc")):
            continue
        if not rel_path.startswith(("src/", "engine/", "game/", "server/", "client/")):
            continue
        if rel_path.startswith(
            (
                "legacy/",
                "docs/",
                "tools/xstack/testx/tests/",
                "tools/xstack/out/",
            )
        ):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line)
            if (
                "legacy/" not in token
                and "legacy\\" not in token
                and "quarantine/" not in token
                and "quarantine\\" not in token
            ):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token.strip()[:140],
                    message="production/runtime code must not reference legacy/quarantine paths",
                    rule_id="INV-NO-LEGACY-REFERENCE",
                )
            )


def _append_topology_map_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = "warn" if str(profile).strip().upper() == "FAST" else _invariant_severity(profile)
    topology_rel = "docs/audit/TOPOLOGY_MAP.json"
    topology_abs = os.path.join(repo_root, topology_rel.replace("/", os.sep))
    try:
        topology_payload = json.load(open(topology_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        topology_payload = {}

    if not isinstance(topology_payload, dict):
        topology_payload = {}
    topology_nodes = list(topology_payload.get("nodes") or []) if isinstance(topology_payload, dict) else []
    if not topology_payload or not isinstance(topology_nodes, list):
        findings.append(
            _finding(
                severity=severity,
                file_path=topology_rel,
                line_number=1,
                snippet="",
                message="topology map artifact must exist and be valid JSON",
                rule_id="INV-TOPOLOGY-MAP-PRESENT",
            )
        )
        return

    declared_schema_paths: Set[str] = set()
    declared_registry_paths: Set[str] = set()
    for row in topology_nodes:
        if not isinstance(row, dict):
            continue
        node_kind = str(row.get("node_kind", "")).strip()
        node_path = _norm(str(row.get("path", "")).strip())
        if not node_path:
            continue
        if node_kind == "schema":
            declared_schema_paths.add(node_path)
        elif node_kind == "registry":
            declared_registry_paths.add(node_path)

    def _iter_schema_paths() -> List[str]:
        out: List[str] = []
        schema_root = os.path.join(repo_root, "schema")
        if os.path.isdir(schema_root):
            for walk_root, dirs, files in os.walk(schema_root):
                dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
                for name in sorted(files):
                    if not name.endswith(".schema"):
                        continue
                    rel = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                    out.append(rel)
        schemas_root = os.path.join(repo_root, "schemas")
        if os.path.isdir(schemas_root):
            for walk_root, dirs, files in os.walk(schemas_root):
                dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
                for name in sorted(files):
                    if not name.endswith(".schema.json"):
                        continue
                    rel = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                    out.append(rel)
        return sorted(set(out))

    def _iter_registry_paths() -> List[str]:
        out: List[str] = []
        registry_roots = (
            os.path.join(repo_root, "data", "registries"),
            os.path.join(repo_root, "data", "governance"),
        )
        for registry_root in registry_roots:
            if not os.path.isdir(registry_root):
                continue
            for walk_root, dirs, files in os.walk(registry_root):
                dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
                for name in sorted(files):
                    if not name.endswith(".json"):
                        continue
                    rel = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                    out.append(rel)
        return sorted(set(out))

    for rel_path in _iter_schema_paths():
        if rel_path in declared_schema_paths:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet=rel_path,
                message="schema must be declared in docs/audit/TOPOLOGY_MAP.json",
                rule_id="INV-NO-UNDECLARED-SCHEMA",
            )
        )

    for rel_path in _iter_registry_paths():
        if rel_path in declared_registry_paths:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet=rel_path,
                message="registry must be declared in docs/audit/TOPOLOGY_MAP.json",
                rule_id="INV-NO-UNDECLARED-REGISTRY",
            )
        )


def _append_time_constitution_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    time_engine_rel = "src/time/time_engine.py"
    time_engine_abs = os.path.join(repo_root, time_engine_rel.replace("/", os.sep))
    if not os.path.isfile(time_engine_abs):
        findings.append(
            _finding(
                severity=severity,
                file_path=time_engine_rel,
                line_number=1,
                snippet="",
                message="time engine is missing",
                rule_id="INV-NO-WALLCLOCK-IN-TIME-ENGINE",
            )
        )
    else:
        try:
            time_engine_text = open(time_engine_abs, "r", encoding="utf-8").read()
        except OSError:
            time_engine_text = ""
        if not time_engine_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=time_engine_rel,
                    line_number=1,
                    snippet="",
                    message="time engine is unreadable",
                    rule_id="INV-NO-WALLCLOCK-IN-TIME-ENGINE",
                )
            )
        else:
            for token in (
                "advance_time(",
                "_tick_dt_permille(",
                "policy_context",
                "time_tick_log",
            ):
                if token in time_engine_text:
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=time_engine_rel,
                        line_number=1,
                        snippet=token,
                        message="time engine missing deterministic time-governance token",
                        rule_id="INV-NO-WALLCLOCK-IN-TIME-ENGINE",
                    )
                )
            for line_no, line in _iter_lines(repo_root, time_engine_rel):
                lowered = str(line).lower()
                if (
                    "time.time(" not in lowered
                    and "datetime.now(" not in lowered
                    and "datetime.utcnow(" not in lowered
                    and "time.perf_counter(" not in lowered
                    and "time.monotonic(" not in lowered
                    and "time.sleep(" not in lowered
                ):
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=time_engine_rel,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="time engine must not use wall-clock/non-authoritative time APIs",
                        rule_id="INV-NO-WALLCLOCK-IN-TIME-ENGINE",
                    )
                )

    lineage_required_files = {
        "tools/xstack/sessionx/time_lineage.py": (
            "branch_from_checkpoint(",
            "shutil.copytree(",
            "parent_checkpoint_id",
            "new_save_id",
            "divergence_tick",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "process.time_branch_from_checkpoint",
            "refusal.time.branch_forbidden_by_policy",
        ),
        "tools/time/tool_time_branch_from_checkpoint.py": (
            "branch_from_checkpoint(",
        ),
        "schema/time/branch.schema": (
            "parent_save_id",
            "parent_checkpoint_id",
            "divergence_tick",
            "new_save_id",
        ),
    }
    for rel_path, tokens in lineage_required_files.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required time-branch lineage file is missing",
                    rule_id="INV-TIME_BRANCH_IS_LINEAGE",
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required time-branch lineage file is unreadable",
                    rule_id="INV-TIME_BRANCH_IS_LINEAGE",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="time branch lineage token is missing",
                    rule_id="INV-TIME_BRANCH_IS_LINEAGE",
                )
            )

    runtime_lineage_files = (
        "tools/xstack/sessionx/time_lineage.py",
        "tools/xstack/sessionx/process_runtime.py",
        "src/time/time_engine.py",
    )
    for rel_path in runtime_lineage_files:
        for line_no, line in _iter_lines(repo_root, rel_path):
            lowered = str(line).lower()
            if "process.time_rewind" in lowered or "process.time_set_tick" in lowered:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="retroactive in-place time mutation APIs are forbidden; branch lineage only",
                        rule_id="INV-TIME_BRANCH_IS_LINEAGE",
                    )
                )
            if "allow_retroactive_mutation" in lowered and "true" in lowered:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=str(line).strip()[:140],
                        message="runtime must not enable retroactive mutation; branch lineage only",
                        rule_id="INV-TIME_BRANCH_IS_LINEAGE",
                    )
                )


def _append_tier_transition_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    transition_controller_rel = "src/reality/transitions/transition_controller.py"
    transition_controller_abs = os.path.join(repo_root, transition_controller_rel.replace("/", os.sep))
    try:
        transition_controller_text = open(transition_controller_abs, "r", encoding="utf-8").read()
    except OSError:
        transition_controller_text = ""
    if not transition_controller_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=transition_controller_rel,
                line_number=1,
                snippet="",
                message="transition controller is missing or unreadable",
                rule_id="INV-TRANSITIONS-POLICY-DRIVEN",
            )
        )
        return

    required_policy_tokens = (
        "compute_transition_plan(",
        "transition_policy",
        "hysteresis_rules",
        "min_transition_interval_ticks",
        "arbitration_rule_id",
        "_candidate_sort_key(",
        "_quantize_distance(",
    )
    for token in required_policy_tokens:
        if token in transition_controller_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=transition_controller_rel,
                line_number=1,
                snippet=token,
                message="transition selection must be policy-driven and deterministic",
                rule_id="INV-TRANSITIONS-POLICY-DRIVEN",
            )
        )

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""
    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime missing; cannot verify transition pipeline invariants",
                rule_id="INV-TRANSITIONS-POLICY-DRIVEN",
            )
        )
        return

    required_runtime_tokens = (
        "_region_management_tick(",
        "_policy_payload(policy_context, \"transition_policy\")",
        "compute_transition_plan(",
        "transition_policy_id",
        "process.region_management_tick",
    )
    for token in required_runtime_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet=token,
                message="transition runtime path must resolve transition policy through policy context",
                rule_id="INV-TRANSITIONS-POLICY-DRIVEN",
            )
        )

    required_transition_event_tokens = (
        "_transition_event_row(",
        "_merge_transition_events(",
        "transition_events",
        "transition_event_ids",
        "deterministic_fingerprint",
        "invariant_checks",
    )
    for token in required_transition_event_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet=token,
                message="transition events must be recorded for each expand/collapse/degrade path",
                rule_id="INV-TRANSITION-EVENT-RECORDED",
            )
        )

    transition_event_schema_rel = "schema/reality/transition_event.schema"
    transition_event_schema_abs = os.path.join(repo_root, transition_event_schema_rel.replace("/", os.sep))
    try:
        transition_event_schema_text = open(transition_event_schema_abs, "r", encoding="utf-8").read()
    except OSError:
        transition_event_schema_text = ""
    if not transition_event_schema_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=transition_event_schema_rel,
                line_number=1,
                snippet="",
                message="transition_event schema is missing or unreadable",
                rule_id="INV-TRANSITION-EVENT-RECORDED",
            )
        )
    else:
        for token in ("event_id", "tick", "from_tier", "to_tier", "invariant_checks", "deterministic_fingerprint"):
            if token in transition_event_schema_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=transition_event_schema_rel,
                    line_number=1,
                    snippet=token,
                    message="transition_event schema must include canonical deterministic transition fields",
                    rule_id="INV-TRANSITION-EVENT-RECORDED",
                )
            )

    universe_state_schema_rel = "schemas/universe_state.schema.json"
    universe_state_schema_abs = os.path.join(repo_root, universe_state_schema_rel.replace("/", os.sep))
    try:
        universe_state_schema_text = open(universe_state_schema_abs, "r", encoding="utf-8").read()
    except OSError:
        universe_state_schema_text = ""
    if not universe_state_schema_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=universe_state_schema_rel,
                line_number=1,
                snippet="",
                message="universe_state schema missing; cannot verify transition event projection",
                rule_id="INV-TRANSITION-EVENT-RECORDED",
            )
        )
    elif "transition_events" not in universe_state_schema_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=universe_state_schema_rel,
                line_number=1,
                snippet="transition_events",
                message="universe_state schema must surface performance_state.transition_events",
                rule_id="INV-TRANSITION-EVENT-RECORDED",
            )
        )

    for rel_path in (transition_controller_rel, process_runtime_rel):
        for line_no, line in _iter_lines(repo_root, rel_path):
            lowered = str(line).lower()
            if (
                "time.time(" not in lowered
                and "datetime.now(" not in lowered
                and "datetime.utcnow(" not in lowered
                and "time.perf_counter(" not in lowered
                and "time.monotonic(" not in lowered
                and "time.sleep(" not in lowered
                and "os.times(" not in lowered
            ):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="transition selection and transition pipeline must not use wall-clock APIs",
                    rule_id="INV-NO-WALLCLOCK-IN-TRANSITION",
                )
            )


def _append_performance_constitution_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    cost_engine_rel = "src/performance/cost_engine.py"
    inspection_cache_rel = "src/performance/inspection_cache.py"
    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    transition_controller_rel = "src/reality/transitions/transition_controller.py"

    for rel_path, required_tokens in (
        (
            cost_engine_rel,
            (
                "compute_cost_snapshot(",
                "evaluate_envelope(",
                "reserve_inspection_budget(",
            ),
        ),
        (
            inspection_cache_rel,
            (
                "build_cache_key(",
                "build_inspection_snapshot(",
                "cache_lookup_or_store(",
            ),
        ),
    ):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="performance constitution file is missing or unreadable",
                    rule_id="INV-NO-WALLCLOCK-IN-PERFORMANCE",
                )
            )
            continue
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="performance accounting implementation is missing required deterministic token",
                    rule_id="INV-NO-WALLCLOCK-IN-PERFORMANCE",
                )
            )

    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""
    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime missing; cannot verify inspection-derived invariant",
                rule_id="INV-INSPECTION-IS-DERIVED",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime missing; cannot verify inspection-derived invariant",
                rule_id="INV-INSPECTION-DERIVED-ONLY",
            )
        )
    else:
        derived_tokens = (
            "process.inspect_generate_snapshot",
            "inspection_cache_lookup_or_store(",
            "skip_state_log = True",
            "refusal.inspect.budget_exceeded",
        )
        for token in derived_tokens:
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="inspection path must be derived, budget-gated, and non-mutating",
                    rule_id="INV-INSPECTION-IS-DERIVED",
                )
            )
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="inspection path must be derived, budget-gated, and non-mutating",
                    rule_id="INV-INSPECTION-DERIVED-ONLY",
                )
            )
        budget_token_groups = (
            ("negotiate_request(", "arbitrate_fidelity_requests("),
            ("inspection_budget_share_per_peer",),
            ("max_inspection_cost_units_per_tick",),
        )
        for token_group in budget_token_groups:
            if any(token in process_runtime_text for token in token_group):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=str(token_group[0]),
                    message="inspection path must enforce deterministic per-tick budget controls",
                    rule_id="INV-INSPECTION-BUDGETED",
                )
            )
        for token in (
            "_augment_inspection_target_payload_for_materialization(",
            "_augment_inspection_target_payload_for_maintenance(",
            "_augment_inspection_target_payload_for_commitment_reenactment(",
            "build_inspection_snapshot_artifact(",
        ):
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="inspection pipeline missing epistemic-safe snapshot derivation token",
                    rule_id="INV-NO-TRUTH-LEAK-VIA-INSPECTION",
                )
            )
        start = process_runtime_text.find('elif process_id == "process.inspect_generate_snapshot":')
        end = process_runtime_text.find('elif process_id in ("process.time_control_set_rate", "process.time_set_rate"):')
        if start >= 0 and end > start:
            branch_text = process_runtime_text[start:end]
            if "_advance_time(state" in branch_text:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet="_advance_time(state",
                        message="inspection process must not advance simulation time or mutate TruthModel",
                        rule_id="INV-INSPECTION-IS-DERIVED",
                    )
                )
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=process_runtime_rel,
                        line_number=1,
                        snippet="_advance_time(state",
                        message="inspection process must not advance simulation time or mutate TruthModel",
                        rule_id="INV-INSPECTION-DERIVED-ONLY",
                    )
                )

    inspection_engine_rel = "src/inspection/inspection_engine.py"
    inspection_engine_abs = os.path.join(repo_root, inspection_engine_rel.replace("/", os.sep))
    try:
        inspection_engine_text = open(inspection_engine_abs, "r", encoding="utf-8").read()
    except OSError:
        inspection_engine_text = ""
    if not inspection_engine_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=inspection_engine_rel,
                line_number=1,
                snippet="",
                message="inspection engine is missing or unreadable",
                rule_id="INV-NO-TRUTH-LEAK-VIA-INSPECTION",
            )
        )
    else:
        for token in (
            "visibility_level",
            "micro_allowed",
            "include_part_ids",
            "epistemic_redaction_level",
            "\"derived_only\": True",
        ):
            if token in inspection_engine_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=inspection_engine_rel,
                    line_number=1,
                    snippet=token,
                    message="inspection engine missing epistemic redaction/derived-only token",
                    rule_id="INV-NO-TRUTH-LEAK-VIA-INSPECTION",
                )
            )

    for rel_path in (cost_engine_rel, inspection_cache_rel, process_runtime_rel, transition_controller_rel):
        for line_no, line in _iter_lines(repo_root, rel_path):
            lowered = str(line).lower()
            if (
                "time.time(" not in lowered
                and "datetime.now(" not in lowered
                and "datetime.utcnow(" not in lowered
                and "time.perf_counter(" not in lowered
                and "time.monotonic(" not in lowered
                and "time.sleep(" not in lowered
                and "os.times(" not in lowered
            ):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=str(line).strip()[:140],
                    message="performance accounting/arbitration paths must not use wall-clock APIs",
                    rule_id="INV-NO-WALLCLOCK-IN-PERFORMANCE",
                )
            )


def _append_interaction_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    dispatch_rel = INTERACTION_DISPATCH_ALLOWED_DIRECT_PROCESS_FILE
    dispatch_abs = os.path.join(repo_root, dispatch_rel.replace("/", os.sep))
    try:
        dispatch_text = open(dispatch_abs, "r", encoding="utf-8").read()
    except OSError:
        dispatch_text = ""

    if not dispatch_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=dispatch_rel,
                line_number=1,
                snippet="",
                message="interaction dispatch file missing; cannot verify intent-only execution path",
                rule_id="INV-INTERACTION-INTENTS-ONLY",
            )
        )
    else:
        for token in (
            "def run_interaction_command(",
            "build_affordance_list(",
            "build_interaction_control_intent(",
            "build_control_resolution(",
            "execute_intent(",
            "interact.list_affordances",
            "interact.execute",
        ):
            if token in dispatch_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=dispatch_rel,
                    line_number=1,
                    snippet=token,
                    message="interaction dispatch must route execution through deterministic intent envelope/process path",
                    rule_id="INV-INTERACTION-INTENTS-ONLY",
                )
            )

    affordance_rel = INTERACTION_AFFORDANCE_FILE
    affordance_abs = os.path.join(repo_root, affordance_rel.replace("/", os.sep))
    try:
        affordance_text = open(affordance_abs, "r", encoding="utf-8").read()
    except OSError:
        affordance_text = ""
    if not affordance_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=affordance_rel,
                line_number=1,
                snippet="",
                message="affordance generator file missing; law-derived affordance validation unavailable",
                rule_id="INV-AFFORDANCES-DERIVED-FROM-LAW",
            )
        )
    else:
        for token in (
            "_allowed_processes(law_profile)",
            "_process_entitlement_map(law_profile)",
            "process_allowed = process_id in allowed_processes",
            "if not process_allowed:",
            "_action_rows(interaction_action_registry)",
        ):
            if token in affordance_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=affordance_rel,
                    line_number=1,
                    snippet=token,
                    message="affordance generation must be derived from law profile process allow-list and entitlement requirements",
                    rule_id="INV-AFFORDANCES-DERIVED-FROM-LAW",
                )
            )

    for rel_path in ACTION_SURFACE_REGISTRY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required ActionSurface registry file is missing",
                rule_id="INV-ACTION-SURFACE-DATA-DRIVEN",
            )
        )

    action_surface_rel = ACTION_SURFACE_ENGINE_FILE
    action_surface_abs = os.path.join(repo_root, action_surface_rel.replace("/", os.sep))
    try:
        action_surface_text = open(action_surface_abs, "r", encoding="utf-8").read()
    except OSError:
        action_surface_text = ""
    if not action_surface_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=action_surface_rel,
                line_number=1,
                snippet="",
                message="ActionSurface engine file missing; registry-driven surface resolution unavailable",
                rule_id="INV-ACTION-SURFACE-DATA-DRIVEN",
            )
        )
    else:
        for token in (
            "_rows_from_registry(",
            "_surface_type_set(",
            "_tool_tag_set(",
            "_visibility_policy_rows(",
            "_surface_lists_from_entity(",
            "allowed_process_ids",
        ):
            if token in action_surface_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=action_surface_rel,
                    line_number=1,
                    snippet=token,
                    message="ActionSurface resolution must remain registry-driven and metadata-derived",
                    rule_id="INV-ACTION-SURFACE-DATA-DRIVEN",
                )
            )
        for token in (
            'surface_type_id == "surface.',
            "startswith(\"surface.",
            "startswith('surface.",
        ):
            if token not in action_surface_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=action_surface_rel,
                    line_number=1,
                    snippet=token,
                    message="ActionSurface engine must not hardcode literal surface-type branching",
                    rule_id="INV-NO-HARDCODED-SURFACE-LOGIC",
                )
            )

    for token in (
        "resolve_action_surfaces(",
        "_surface_affordance_row(",
        "allowed_process_ids",
    ):
        if token in affordance_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=affordance_rel,
                line_number=1,
                snippet=token,
                message="affordance generation must resolve ActionSurfaces and bind process ids from surface metadata",
                rule_id="INV-ACTION-SURFACE-DATA-DRIVEN",
            )
        )
    for token in (
        "execute_intent(",
        "build_interaction_control_intent(",
        "build_control_resolution(",
    ):
        if token in dispatch_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=dispatch_rel,
                line_number=1,
                snippet=token,
                message="ActionSurface interactions must route through intent + process runtime only",
                rule_id="INV-ACTION-PROCESS-ONLY",
            )
        )

    for rel_path in TOOL_REGISTRY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required ToolEffect registry file is missing",
                rule_id="INV-TOOLS-DATA-DRIVEN",
            )
        )

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""

    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime file missing; tool process enforcement unavailable",
                rule_id="INV-TOOL_USE_REQUIRES_BIND",
            )
        )
    else:
        for token in (
            "process.tool_bind",
            "process.tool_unbind",
            "process.tool_use_prepare",
            "process.tool_readout_tick",
            "_active_tool_binding(tool_bindings, subject_id)",
            "refusal.tool.bind_required",
        ):
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="tool runtime must enforce active bind before use/readout",
                    rule_id="INV-TOOL_USE_REQUIRES_BIND",
                )
            )
        for token in (
            "_tool_type_rows(policy_context)",
            "_tool_effect_model_rows(policy_context)",
            "tool_type_registry",
            "tool_effect_model_registry",
        ):
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="tool runtime must resolve tool types/effects from registries, not hardcoded literals",
                    rule_id="INV-TOOLS-DATA-DRIVEN",
                )
            )

    for rel_path, text, tokens in (
        (
            action_surface_rel,
            action_surface_text,
            (
                "_tool_type_rows_by_id(",
                "_tool_effect_rows_by_id(",
                "tool_process_allowed_ids",
                "active_tool_effect_parameters",
            ),
        ),
        (
            affordance_rel,
            affordance_text,
            (
                "tool_process_allowed_ids",
                "tool_process_compatible",
                "active_tool_effect_parameters",
                "refusal.tool.incompatible",
            ),
        ),
        (
            dispatch_rel,
            dispatch_text,
            (
                "_active_tool_context(",
                "tool_effect",
                "tool_effect_model_id",
                "refusal.tool.bind_required",
            ),
        ),
    ):
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="tool integration surface missing; cannot validate data-driven flow",
                    rule_id="INV-TOOLS-DATA-DRIVEN",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="tool interactions must remain registry-driven and parameterized",
                    rule_id="INV-TOOLS-DATA-DRIVEN",
                )
            )

    task_engine_rel = "src/interaction/task/task_engine.py"
    task_engine_abs = os.path.join(repo_root, task_engine_rel.replace("/", os.sep))
    try:
        task_engine_text = open(task_engine_abs, "r", encoding="utf-8").read()
    except OSError:
        task_engine_text = ""
    if not task_engine_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=task_engine_rel,
                line_number=1,
                snippet="",
                message="task engine file missing; deterministic task progression unavailable",
                rule_id="INV-TASKS-PROCESS-ONLY-MUTATION",
            )
        )
    else:
        for token in (
            "def create_task_row(",
            "def tick_tasks(",
            "completion_intents",
            "process_id_to_execute",
            "dt_ticks",
        ):
            if token in task_engine_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=task_engine_rel,
                    line_number=1,
                    snippet=token,
                    message="task engine must expose deterministic create/tick/completion handoff primitives",
                    rule_id="INV-TASKS-PROCESS-ONLY-MUTATION",
                )
            )
        for token in (
            "time.time(",
            "datetime.",
            "perf_counter(",
            "monotonic(",
        ):
            if token not in task_engine_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=task_engine_rel,
                    line_number=1,
                    snippet=token,
                    message="task progression must never use wall-clock timing APIs",
                    rule_id="INV-NO-WALLCLOCK-IN-TASKS",
                )
            )

    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime file missing; task process enforcement unavailable",
                rule_id="INV-TASKS-PROCESS-ONLY-MUTATION",
            )
        )
    else:
        for token in (
            "process.task_create",
            "process.task_tick",
            "process.task_pause",
            "process.task_resume",
            "process.task_cancel",
            "_persist_task_state(",
            "pending_task_completion_intents",
        ):
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="task runtime must route work through canonical task process family and pending completion intents",
                    rule_id="INV-TASKS-PROCESS-ONLY-MUTATION",
                )
            )
        for token in (
            "time.time(",
            "datetime.",
            "perf_counter(",
            "monotonic(",
        ):
            if token not in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="task runtime integration must not depend on wall-clock APIs",
                    rule_id="INV-NO-WALLCLOCK-IN-TASKS",
                )
            )

    if dispatch_text and "process.task_create" not in dispatch_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=dispatch_rel,
                line_number=1,
                snippet="process.task_create",
                message="interaction dispatch must map long-running surface actions into process.task_create when task mappings exist",
                rule_id="INV-TASKS-PROCESS-ONLY-MUTATION",
            )
        )

    hardcoded_tool_patterns = (
        re.compile(r"(==|!=)\s*['\"]tool\.[^'\"]+['\"]"),
        re.compile(r"startswith\(\s*['\"]tool\."),
        re.compile(r"endswith\(\s*['\"]tool\."),
    )
    for rel_path in (action_surface_rel, affordance_rel, dispatch_rel, process_runtime_rel):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if token.startswith("#"):
                continue
            if "data/registries/" in token:
                continue
            if any(pattern.search(token) for pattern in hardcoded_tool_patterns):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token[:140],
                        message="tool runtime/interaction must not hardcode specific tool ids in logic",
                        rule_id="INV-NO-HARDCODED-TOOL-LOGIC",
                    )
                )

    mutation_pattern = re.compile(
        r"\[\s*['\"](" + "|".join(INTERACTION_TRUTH_MUTATION_FORBIDDEN_KEYS) + r")['\"]\s*\]\s*="
    )
    truth_symbol_pattern = re.compile(r"\b(truth_model|truthmodel)\b", re.IGNORECASE)

    for rel_path in INTERACTION_UI_SURFACE_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="interaction UI surface file is missing",
                    rule_id="INV-UI-NEVER-MUTATES-TRUTH",
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line)
            if truth_symbol_pattern.search(token):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token.strip()[:140],
                        message="interaction UI surfaces must not reference authoritative TruthModel/universe state symbols",
                        rule_id="INV-UI-NEVER-MUTATES-TRUTH",
                    )
                )
            if mutation_pattern.search(token):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token.strip()[:140],
                        message="interaction UI surfaces must not mutate authoritative truth collections directly",
                        rule_id="INV-UI-NEVER-MUTATES-TRUTH",
                    )
                )
            if "execute_intent(" in token and rel_path != INTERACTION_DISPATCH_ALLOWED_DIRECT_PROCESS_FILE:
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token.strip()[:140],
                        message="interaction surfaces must dispatch via run_interaction_command/intent envelopes, not direct process runtime calls",
                        rule_id="INV-INTERACTION-INTENTS-ONLY",
                    )
                )

    integration_tokens = (
        ("tools/xstack/sessionx/interaction.py", ("run_interaction_command(",)),
        (
            "tools/interaction/interaction_cli.py",
            (
                "run_interaction_command(",
                "interact.list_affordances",
                "interact.execute",
            ),
        ),
    )
    for rel_path, tokens in integration_tokens:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="interaction integration surface missing; cannot verify intent-only flow",
                    rule_id="INV-INTERACTION-INTENTS-ONLY",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                message="interaction integration surfaces must delegate through canonical interaction dispatch APIs",
                rule_id="INV-INTERACTION-INTENTS-ONLY",
            )
        )

    for rel_path in MACHINE_REGISTRY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required machine/port registry file is missing",
                rule_id="INV-MACHINE_OPERATIONS-DATA-DRIVEN",
            )
        )

    machine_runtime_tokens = (
        "process.port_insert_batch",
        "process.port_extract_batch",
        "process.port_connect",
        "process.port_disconnect",
        "process.machine_operate",
        "process.machine_pull_from_node",
        "process.machine_push_to_node",
        "_persist_machine_state(",
        "_machine_event_row(",
    )
    for token in machine_runtime_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet=token,
                message="machine/port process runtime token is missing",
                rule_id="INV-PORTS-PROCESS-ONLY",
            )
        )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(
            (
                "tools/xstack/sessionx/process_runtime.py",
                "tools/xstack/testx/tests/",
                "tools/xstack/repox/check.py",
            )
        ):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if any(
                marker in token
                for marker in (
                    'state["machine_ports"]',
                    "state['machine_ports']",
                    'state["machine_port_connections"]',
                    "state['machine_port_connections']",
                    'state["machine_assemblies"]',
                    "state['machine_assemblies']",
                    'state["machine_provenance_events"]',
                    "state['machine_provenance_events']",
                )
            ):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token[:140],
                        message="machine/port state mutation must occur only through process runtime commit paths",
                        rule_id="INV-PORTS-PROCESS-ONLY",
                    )
                )

    machine_data_tokens = {
        "src/machines/port_engine.py": (
            "port_type_rows_by_id(",
            "machine_type_rows_by_id(",
            "machine_operation_rows_by_id(",
            "validate_port_accepts_material(",
            "insert_into_port(",
            "extract_from_port(",
        ),
        process_runtime_rel: (
            "_machine_type_rows(policy_context)",
            "_machine_operation_rows(policy_context)",
            "_port_type_rows(policy_context)",
        ),
    }
    for rel_path, tokens in machine_data_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required machine/port data-driven implementation file is missing",
                    rule_id="INV-MACHINE_OPERATIONS-DATA-DRIVEN",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required machine/port data-driven token is missing",
                    rule_id="INV-MACHINE_OPERATIONS-DATA-DRIVEN",
                )
            )

    no_silent_batch_tokens = {
        process_runtime_rel: (
            "event.batch_created",
            "_machine_output_batch_id(",
        ),
        "src/machines/port_engine.py": (
            "extract_from_port(",
        ),
    }
    for rel_path, tokens in no_silent_batch_tokens.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required batch provenance implementation file is missing",
                    rule_id="INV-NO-SILENT-BATCH-CREATION",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="required batch provenance token is missing",
                    rule_id="INV-NO-SILENT-BATCH-CREATION",
                )
            )


def _append_domain_control_registered_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    control_rel = "data/registries/control_action_registry.json"
    interaction_rel = "data/registries/interaction_action_registry.json"
    control_payload, control_err = _load_json_object(repo_root, control_rel)
    interaction_payload, interaction_err = _load_json_object(repo_root, interaction_rel)
    if control_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=control_rel,
                line_number=1,
                snippet="",
                message="control action registry is missing or invalid; cannot verify user-facing control registration",
                rule_id="INV-DOMAIN-CONTROL-REGISTERED",
            )
        )
        return
    if interaction_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=interaction_rel,
                line_number=1,
                snippet="",
                message="interaction action registry is missing or invalid; cannot verify user-facing process families",
                rule_id="INV-DOMAIN-CONTROL-REGISTERED",
            )
        )
        return

    control_actions = list((dict(control_payload.get("record") or {})).get("actions") or [])
    interaction_actions = list((dict(interaction_payload.get("record") or {})).get("actions") or [])
    produced_process_ids: Set[str] = set()
    produced_families: Set[str] = set()
    adapter_allows_dynamic_process = False
    for row in control_actions:
        if not isinstance(row, dict):
            continue
        action_id = str(row.get("action_id", "")).strip()
        produces = dict(row.get("produces") or {})
        process_id = str(produces.get("process_id", "")).strip()
        if process_id.startswith("process."):
            produced_process_ids.add(process_id)
            parts = process_id.split(".")
            if len(parts) >= 2 and str(parts[1]).strip():
                produced_families.add(str(parts[1]).strip())
        ext = dict(row.get("extensions") or {})
        if (
            action_id == "action.interaction.execute_process"
            and str(ext.get("adapter", "")).strip() == "legacy.process_id"
        ):
            adapter_allows_dynamic_process = True

    missing_families: Dict[str, Set[str]] = {}
    for row in interaction_actions:
        if not isinstance(row, dict):
            continue
        process_id = str(row.get("process_id", "")).strip()
        if not process_id.startswith("process."):
            continue
        parts = process_id.split(".")
        family = str(parts[1]).strip() if len(parts) >= 2 else ""
        if not family:
            continue
        if process_id in produced_process_ids:
            continue
        if family in produced_families:
            continue
        if adapter_allows_dynamic_process:
            continue
        missing_families.setdefault(family, set()).add(process_id)

    for family in sorted(missing_families.keys()):
        process_ids = sorted(missing_families[family])
        findings.append(
            _finding(
                severity=severity,
                file_path=control_rel,
                line_number=1,
                snippet=family,
                message=(
                    "user-facing process family '{}' is not represented in control_action_registry and no adapter action is declared "
                    "(examples: {})"
                ).format(family, ",".join(process_ids[:4])),
                rule_id="INV-DOMAIN-CONTROL-REGISTERED",
            )
        )


def _append_action_grammar_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    control_rel = "data/registries/control_action_registry.json"
    interaction_rel = "data/registries/interaction_action_registry.json"
    task_rel = "data/registries/task_type_registry.json"
    process_rel = "data/registries/process_registry.json"
    family_rel = "data/registries/action_family_registry.json"
    template_rel = "data/registries/action_template_registry.json"

    control_payload, control_err = _load_json_object(repo_root, control_rel)
    interaction_payload, interaction_err = _load_json_object(repo_root, interaction_rel)
    task_payload, task_err = _load_json_object(repo_root, task_rel)
    process_payload, process_err = _load_json_object(repo_root, process_rel)
    template_payload, template_err = _load_json_object(repo_root, template_rel)
    family_payload, _family_err = _load_json_object(repo_root, family_rel)

    if template_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=template_rel,
                line_number=1,
                snippet="",
                message="action_template_registry is missing or invalid; cannot verify action-family coverage",
                rule_id="INV-ACTION-MUST-HAVE-FAMILY",
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=template_rel,
                line_number=1,
                snippet="",
                message="action_template_registry is missing or invalid; cannot verify unregistered action templates",
                rule_id="INV-NO-UNREGISTERED-ACTION",
            )
        )
        return

    source_errors = [
        (control_rel, control_err),
        (interaction_rel, interaction_err),
        (task_rel, task_err),
        (process_rel, process_err),
    ]
    for file_path, err in source_errors:
        if not err:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=file_path,
                line_number=1,
                snippet="",
                message="required source registry is missing or invalid; cannot fully verify action-template coverage",
                rule_id="INV-ACTION-MUST-HAVE-FAMILY",
            )
        )
        return

    family_rows = list((dict(family_payload.get("record") or {})).get("families") or [])
    family_ids = set()
    for row in family_rows:
        if not isinstance(row, dict):
            continue
        family_id = str(row.get("action_family_id", "")).strip()
        if family_id:
            family_ids.add(family_id)

    control_action_ids: Set[str] = set()
    for row in list((dict(control_payload.get("record") or {})).get("actions") or []):
        if not isinstance(row, dict):
            continue
        action_id = str(row.get("action_id", "")).strip()
        if action_id:
            control_action_ids.add(action_id)
    interaction_action_ids: Set[str] = set()
    for row in list((dict(interaction_payload.get("record") or {})).get("actions") or []):
        if not isinstance(row, dict):
            continue
        action_id = str(row.get("action_id", "")).strip()
        if action_id:
            interaction_action_ids.add(action_id)
    task_type_ids: Set[str] = set()
    for row in list((dict(task_payload.get("record") or {})).get("task_types") or []):
        if not isinstance(row, dict):
            continue
        task_type_id = str(row.get("task_type_id", "")).strip()
        if task_type_id:
            task_type_ids.add(task_type_id)
    process_ids: Set[str] = set()
    for row in list((dict(process_payload.get("record") or {})).get("processes") or []):
        if not isinstance(row, dict):
            continue
        process_id = str(row.get("process_id", "")).strip()
        if process_id:
            process_ids.add(process_id)

    source_action_ids: Set[str] = set(control_action_ids) | set(interaction_action_ids) | set(task_type_ids) | set(process_ids)

    template_rows = list((dict(template_payload.get("record") or {})).get("templates") or [])
    template_by_id: Dict[str, dict] = {}
    for row in sorted((item for item in template_rows if isinstance(item, dict)), key=lambda item: str(item.get("action_template_id", ""))):
        template_id = str(row.get("action_template_id", "")).strip()
        if not template_id:
            continue
        template_by_id.setdefault(template_id, dict(row))

    for action_id in sorted(source_action_ids):
        template_row = dict(template_by_id.get(action_id) or {})
        if not template_row:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=template_rel,
                    line_number=1,
                    snippet=action_id,
                    message="source action/process/task is missing action_template mapping",
                    rule_id="INV-ACTION-MUST-HAVE-FAMILY",
                )
            )
            continue
        action_family_id = str(template_row.get("action_family_id", "")).strip()
        if not action_family_id:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=template_rel,
                    line_number=1,
                    snippet=action_id,
                    message="action_template mapping is missing action_family_id",
                    rule_id="INV-ACTION-MUST-HAVE-FAMILY",
                )
            )
            continue
        if family_ids and action_family_id not in family_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=template_rel,
                    line_number=1,
                    snippet=action_family_id,
                    message="action_template references unknown action_family_id",
                    rule_id="INV-ACTION-MUST-HAVE-FAMILY",
                )
            )

    for template_id in sorted(template_by_id.keys()):
        template_row = dict(template_by_id.get(template_id) or {})
        ext = dict(template_row.get("extensions") or {})
        template_kind = str(ext.get("template_kind", "")).strip()
        if template_kind == "control_action" and template_id not in control_action_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=template_rel,
                    line_number=1,
                    snippet=template_id,
                    message="control_action template is not registered in control_action_registry",
                    rule_id="INV-NO-UNREGISTERED-ACTION",
                )
            )
        elif template_kind == "interaction_action" and template_id not in interaction_action_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=template_rel,
                    line_number=1,
                    snippet=template_id,
                    message="interaction_action template is not registered in interaction_action_registry",
                    rule_id="INV-NO-UNREGISTERED-ACTION",
                )
            )
        elif template_kind == "task_type" and template_id not in task_type_ids:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=template_rel,
                    line_number=1,
                    snippet=template_id,
                    message="task_type template is not registered in task_type_registry",
                    rule_id="INV-NO-UNREGISTERED-ACTION",
                )
            )


def _append_info_grammar_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    template_rel = "data/registries/action_template_registry.json"
    mapping_rel = "data/registries/info_artifact_family_registry.json"

    template_payload, template_err = _load_json_object(repo_root, template_rel)
    mapping_payload, mapping_err = _load_json_object(repo_root, mapping_rel)
    if mapping_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=mapping_rel,
                line_number=1,
                snippet="",
                message="info artifact-family mapping registry is missing or invalid",
                rule_id="INV-INFO-ARTIFACT-MUST-HAVE-FAMILY",
            )
        )
        return
    if template_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=template_rel,
                line_number=1,
                snippet="",
                message="action_template registry missing/invalid; cannot verify artifact family mappings",
                rule_id="INV-INFO-ARTIFACT-MUST-HAVE-FAMILY",
            )
        )
        return

    mapping_record = dict(mapping_payload.get("record") or {})
    family_rows = list(mapping_record.get("families") or [])
    known_families: Set[str] = set()
    for row in family_rows:
        if not isinstance(row, dict):
            continue
        family_id = str(row.get("info_family_id", "")).strip()
        if family_id:
            known_families.add(family_id)

    mapping_rows = list(mapping_record.get("artifact_type_mappings") or [])
    artifact_to_family: Dict[str, str] = {}
    for row in mapping_rows:
        if not isinstance(row, dict):
            continue
        artifact_type_id = str(row.get("artifact_type_id", "")).strip()
        info_family_id = str(row.get("info_family_id", "")).strip()
        if not artifact_type_id:
            continue
        artifact_to_family[artifact_type_id] = info_family_id
        if (not info_family_id) or (known_families and info_family_id not in known_families):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=mapping_rel,
                    line_number=1,
                    snippet="{}->{}".format(artifact_type_id, info_family_id),
                    message="artifact type mapping must reference a valid info_family_id",
                    rule_id="INV-INFO-ARTIFACT-MUST-HAVE-FAMILY",
                )
            )

    template_rows = list((dict(template_payload.get("record") or {})).get("templates") or [])
    required_artifact_types: Set[str] = set()
    for row in template_rows:
        if not isinstance(row, dict):
            continue
        artifact_types = list(row.get("produced_artifact_types") or [])
        for token in artifact_types:
            artifact_type_id = str(token).strip()
            if artifact_type_id:
                required_artifact_types.add(artifact_type_id)

    for artifact_type_id in sorted(required_artifact_types):
        info_family_id = str(artifact_to_family.get(artifact_type_id, "")).strip()
        if not info_family_id:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=mapping_rel,
                    line_number=1,
                    snippet=artifact_type_id,
                    message="artifact type produced by action templates has no info family mapping",
                    rule_id="INV-INFO-ARTIFACT-MUST-HAVE-FAMILY",
                )
            )
            continue
        if known_families and info_family_id not in known_families:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=mapping_rel,
                    line_number=1,
                    snippet="{}->{}".format(artifact_type_id, info_family_id),
                    message="artifact type maps to unknown info family id",
                    rule_id="INV-INFO-ARTIFACT-MUST-HAVE-FAMILY",
                )
            )


def _append_meta_contract_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    tier_rule_id = "INV-TIER-CONTRACT-REQUIRED"
    coupling_rule_id = "INV-COUPLING-CONTRACT-REQUIRED"
    explain_rule_id = "INV-EXPLAIN-CONTRACT-REQUIRED"
    undeclared_rule_id = "INV-NO-UNDECLARED-COUPLING"

    tier_rel = "data/registries/tier_contract_registry.json"
    coupling_rel = "data/registries/coupling_contract_registry.json"
    explain_rel = "data/registries/explain_contract_registry.json"

    tier_payload, tier_err = _load_json_object(repo_root, tier_rel)
    coupling_payload, coupling_err = _load_json_object(repo_root, coupling_rel)
    explain_payload, explain_err = _load_json_object(repo_root, explain_rel)

    tier_rows = list(tier_payload.get("tier_contracts") or [])
    if not tier_rows:
        tier_rows = list((dict(tier_payload.get("record") or {})).get("tier_contracts") or [])
    if tier_err or (not tier_rows):
        findings.append(
            _finding(
                severity=severity,
                file_path=tier_rel,
                line_number=1,
                snippet="tier_contracts",
                message="tier contract registry is missing/invalid or empty",
                rule_id=tier_rule_id,
            )
        )
    else:
        required_subsystems = {"ELEC", "THERM", "MOB", "SIG", "PHYS"}
        declared_subsystems = set()
        for row in tier_rows:
            if not isinstance(row, dict):
                continue
            subsystem_id = str(row.get("subsystem_id", "")).strip().upper()
            if subsystem_id:
                declared_subsystems.add(subsystem_id)
            if not str(row.get("contract_id", "")).strip():
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=tier_rel,
                        line_number=1,
                        snippet="contract_id",
                        message="tier contract rows must declare contract_id",
                        rule_id=tier_rule_id,
                    )
                )
                break
        for subsystem_id in sorted(required_subsystems - declared_subsystems):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=tier_rel,
                    line_number=1,
                    snippet=subsystem_id,
                    message="required subsystem tier contract is missing",
                    rule_id=tier_rule_id,
                )
            )

    coupling_rows = list(coupling_payload.get("coupling_contracts") or [])
    if not coupling_rows:
        coupling_rows = list((dict(coupling_payload.get("record") or {})).get("coupling_contracts") or [])
    if coupling_err or (not coupling_rows):
        findings.append(
            _finding(
                severity=severity,
                file_path=coupling_rel,
                line_number=1,
                snippet="coupling_contracts",
                message="coupling contract registry is missing/invalid or empty",
                rule_id=coupling_rule_id,
            )
        )
        findings.append(
            _finding(
                severity=severity,
                file_path=coupling_rel,
                line_number=1,
                snippet="coupling_contracts",
                message="cannot verify undeclared coupling when coupling registry is unavailable",
                rule_id=undeclared_rule_id,
            )
        )
    else:
        declared_contracts = set()
        declared_mechanisms = set()
        for row in coupling_rows:
            if not isinstance(row, dict):
                continue
            contract_key = (
                str(row.get("coupling_class_id", "")).strip(),
                str(row.get("from_domain_id", "")).strip().upper(),
                str(row.get("to_domain_id", "")).strip().upper(),
                str(row.get("mechanism", "")).strip(),
            )
            if all(contract_key):
                declared_contracts.add(contract_key)
            mechanism_id = str(row.get("mechanism_id", "")).strip()
            if mechanism_id:
                declared_mechanisms.add(mechanism_id)

        required_contracts = (
            ("energy_coupling", "ELEC", "THERM", "energy_transform"),
            ("energy_coupling", "FIELD", "THERM", "constitutive_model"),
            ("force_coupling", "THERM", "MECH", "constitutive_model"),
            ("info_coupling", "SIG", "SIG", "signal_policy"),
        )
        for contract in required_contracts:
            if contract in declared_contracts:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=coupling_rel,
                    line_number=1,
                    snippet="{}:{}->{} ({})".format(contract[0], contract[1], contract[2], contract[3]),
                    message="required baseline coupling contract is missing",
                    rule_id=coupling_rule_id,
                )
            )

        for mechanism_id in (
            "transform.electrical_to_thermal",
            "model.phys_irradiance_heating_stub",
            "model.mech.fatigue.default",
            "belief.default",
        ):
            if mechanism_id in declared_mechanisms:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=coupling_rel,
                    line_number=1,
                    snippet=mechanism_id,
                    message="coupling mechanism is referenced by baseline domain coupling but not declared",
                    rule_id=undeclared_rule_id,
                )
            )

        direct_coupling_patterns_by_prefix = {
            "src/electric/": (
                re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
            ),
            "src/thermal/": (
                re.compile(r"\belec_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']elec_", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
            ),
            "src/signals/": (
                re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\belec_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']elec_", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
            ),
            "src/mobility/": (
                re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\belec_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']elec_", re.IGNORECASE),
                re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
            ),
        }
        scan_prefixes = tuple(direct_coupling_patterns_by_prefix.keys())
        skip_prefixes = (
            "docs/",
            "schema/",
            "schemas/",
            "tools/auditx/analyzers/",
            "tools/xstack/testx/tests/",
        )
        allowed_files = {
            "src/models/model_engine.py",
            "tools/xstack/sessionx/process_runtime.py",
            "tools/xstack/repox/check.py",
        }
        for rel_path in _scan_files(repo_root):
            rel_norm = _norm(rel_path)
            if not rel_norm.endswith(".py"):
                continue
            if not any(rel_norm.startswith(prefix) for prefix in scan_prefixes):
                continue
            if rel_norm.startswith(skip_prefixes):
                continue
            if rel_norm in allowed_files:
                continue
            active_patterns = ()
            for prefix, patterns in direct_coupling_patterns_by_prefix.items():
                if rel_norm.startswith(prefix):
                    active_patterns = patterns
                    break
            if not active_patterns:
                continue
            for line_no, line in _iter_lines(repo_root, rel_norm):
                snippet = str(line).strip()
                if (not snippet) or snippet.startswith("#"):
                    continue
                if not any(pattern.search(snippet) for pattern in active_patterns):
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="potential direct cross-domain coupling mutation detected outside declared contract/model pathways",
                        rule_id=undeclared_rule_id,
                    )
                )
                break

    explain_rows = list(explain_payload.get("explain_contracts") or [])
    if not explain_rows:
        explain_rows = list((dict(explain_payload.get("record") or {})).get("explain_contracts") or [])
    if explain_err or (not explain_rows):
        findings.append(
            _finding(
                severity=severity,
                file_path=explain_rel,
                line_number=1,
                snippet="explain_contracts",
                message="explain contract registry is missing/invalid or empty",
                rule_id=explain_rule_id,
            )
        )
    else:
        required_event_ids = {
            "elec.trip",
            "therm.overheat",
            "mob.derailment",
            "sig.delivery_loss",
            "mech.fracture",
        }
        declared_event_ids = set()
        for row in explain_rows:
            if not isinstance(row, dict):
                continue
            event_kind_id = str(row.get("event_kind_id", "")).strip()
            if event_kind_id:
                declared_event_ids.add(event_kind_id)
            if not str(row.get("explain_artifact_type_id", "")).strip():
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=explain_rel,
                        line_number=1,
                        snippet=event_kind_id or "explain_artifact_type_id",
                        message="explain contract rows must declare explain_artifact_type_id",
                        rule_id=explain_rule_id,
                    )
                )
                break
            if not list(row.get("required_inputs") or []):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=explain_rel,
                        line_number=1,
                        snippet=event_kind_id or "required_inputs",
                        message="explain contract rows should declare required_inputs for deterministic explain generation",
                        rule_id=explain_rule_id,
                    )
                )
                break
        for event_kind_id in sorted(required_event_ids - declared_event_ids):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=explain_rel,
                    line_number=1,
                    snippet=event_kind_id,
                    message="required baseline explain contract is missing",
                    rule_id=explain_rule_id,
                )
            )


def _append_affordance_matrix_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)
    matrix_rel = "data/meta/real_world_affordance_matrix.json"
    matrix_payload, matrix_err = _load_json_object(repo_root, matrix_rel)

    if matrix_err:
        findings.append(
            _finding(
                severity=severity,
                file_path=matrix_rel,
                line_number=1,
                snippet="",
                message="RWAM metadata is missing or invalid; new series/substrates cannot declare affordance coverage",
                rule_id="INV-AFFORDANCE-DECLARED",
            )
        )
        return

    affordance_rows = list(matrix_payload.get("affordances") or [])
    if not affordance_rows:
        findings.append(
            _finding(
                severity=severity,
                file_path=matrix_rel,
                line_number=1,
                snippet="affordances",
                message="RWAM must declare canonical affordance rows",
                rule_id="INV-AFFORDANCE-DECLARED",
            )
        )
        return

    required_affordance_ids = {
        "matter_transformation",
        "motion_force_transmission",
        "containment_interfaces",
        "measurement_verification",
        "communication_coordination",
        "institutions_contracts",
        "environment_living_systems",
        "time_synchronization",
        "safety_protection",
    }
    affordance_ids: Set[str] = set()
    allowed_tiers = {"macro", "meso", "micro"}
    for row in affordance_rows:
        if not isinstance(row, dict):
            continue
        affordance_id = str(row.get("id", "")).strip()
        if not affordance_id:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=matrix_rel,
                    line_number=1,
                    snippet="id",
                    message="RWAM affordance rows must declare id",
                    rule_id="INV-AFFORDANCE-DECLARED",
                )
            )
            continue
        affordance_ids.add(affordance_id)

        substrates = list(row.get("substrates") or [])
        if not substrates:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=matrix_rel,
                    line_number=1,
                    snippet=affordance_id,
                    message="RWAM affordance '{}' must declare substrates".format(affordance_id),
                    rule_id="INV-AFFORDANCE-DECLARED",
                )
            )
        tiers = [str(item).strip() for item in (row.get("tiers") or []) if str(item).strip()]
        if not tiers:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=matrix_rel,
                    line_number=1,
                    snippet=affordance_id,
                    message="RWAM affordance '{}' must declare tiers".format(affordance_id),
                    rule_id="INV-AFFORDANCE-DECLARED",
                )
            )
        elif any(token not in allowed_tiers for token in tiers):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=matrix_rel,
                    line_number=1,
                    snippet=affordance_id,
                    message="RWAM affordance '{}' uses unknown tier labels".format(affordance_id),
                    rule_id="INV-AFFORDANCE-DECLARED",
                )
            )
        implemented = [str(item).strip() for item in (row.get("series_implemented") or []) if str(item).strip()]
        planned = [str(item).strip() for item in (row.get("series_planned") or []) if str(item).strip()]
        if (not implemented) and (not planned):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=matrix_rel,
                    line_number=1,
                    snippet=affordance_id,
                    message="RWAM affordance '{}' must declare implemented or planned series coverage".format(affordance_id),
                    rule_id="INV-AFFORDANCE-DECLARED",
                )
            )

    missing_affordances = sorted(required_affordance_ids - affordance_ids)
    for affordance_id in missing_affordances:
        findings.append(
            _finding(
                severity=severity,
                file_path=matrix_rel,
                line_number=1,
                snippet=affordance_id,
                message="canonical affordance '{}' is missing from RWAM".format(affordance_id),
                rule_id="INV-AFFORDANCE-DECLARED",
            )
        )

    covered_series: Set[str] = set()
    for row in affordance_rows:
        if not isinstance(row, dict):
            continue
        for token in list(row.get("series_implemented") or []):
            series_id = str(token).strip()
            if series_id:
                covered_series.add(series_id)
        for token in list(row.get("series_planned") or []):
            series_id = str(token).strip()
            if series_id:
                covered_series.add(series_id)

    series_rows = list(matrix_payload.get("series_affordance_coverage") or [])
    for row in series_rows:
        if not isinstance(row, dict):
            continue
        series_id = str(row.get("series_id", "")).strip()
        if series_id:
            covered_series.add(series_id)
        row_affordances = [str(item).strip() for item in (row.get("affordance_ids") or []) if str(item).strip()]
        if not row_affordances:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=matrix_rel,
                    line_number=1,
                    snippet=series_id or "series_affordance_coverage",
                    message="RWAM series_affordance_coverage rows must declare affordance_ids",
                    rule_id="INV-AFFORDANCE-DECLARED",
                )
            )
            continue
        for affordance_id in row_affordances:
            if affordance_id in required_affordance_ids:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=matrix_rel,
                    line_number=1,
                    snippet=affordance_id,
                    message="RWAM series mapping references unknown affordance id",
                    rule_id="INV-AFFORDANCE-DECLARED",
                )
            )

    retro_audit_dir = os.path.join(repo_root, "docs", "audit")
    discovered_series: Set[str] = set()
    if os.path.isdir(retro_audit_dir):
        retro_re = re.compile(r"^([A-Z]+)\d+_RETRO_AUDIT\.md$")
        for name in os.listdir(retro_audit_dir):
            token = str(name).strip()
            match = retro_re.fullmatch(token)
            if match:
                discovered_series.add(str(match.group(1)).strip())

    for series_id in sorted(discovered_series):
        if series_id in covered_series:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=matrix_rel,
                line_number=1,
                snippet=series_id,
                message="series '{}' appears in retro audits but is not declared in RWAM".format(series_id),
                rule_id="INV-AFFORDANCE-DECLARED",
            )
        )


def _append_platform_renderer_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    for rel_path in PLATFORM_ABSTRACTION_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="platform abstraction module is missing",
                rule_id="INV-PLATFORM-ISOLATION",
            )
        )

    os_dependency_patterns = (
        re.compile(r"^\s*#\s*include\s*[<\"]windows\.h[\">]", re.IGNORECASE),
        re.compile(r"^\s*#\s*include\s*[<\"]X11/", re.IGNORECASE),
        re.compile(r"^\s*#\s*include\s*[<\"]Cocoa/", re.IGNORECASE),
        re.compile(r"\bctypes\.windll\b", re.IGNORECASE),
        re.compile(r"\bimport\s+win32api\b", re.IGNORECASE),
    )
    scan_root = os.path.join(repo_root, "src")
    if os.path.isdir(scan_root):
        for walk_root, dirs, files in os.walk(scan_root):
            dirs[:] = sorted(dirs)
            files = sorted(files)
            rel_root = _norm(os.path.relpath(walk_root, repo_root))
            if rel_root.startswith("src/platform"):
                continue
            for name in files:
                _, ext = os.path.splitext(name.lower())
                if ext not in (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                for line_no, line in _iter_lines(repo_root, rel_path):
                    snippet = str(line).strip()
                    if not snippet:
                        continue
                    for pattern in os_dependency_patterns:
                        if not pattern.search(snippet):
                            continue
                        findings.append(
                            _finding(
                                severity=severity,
                                file_path=rel_path,
                                line_number=line_no,
                                snippet=snippet[:140],
                                message="platform-specific OS dependency token must remain isolated to src/platform",
                                rule_id="INV-PLATFORM-ISOLATION",
                            )
                        )
                        break

    renderer_truth_pattern = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
    renderer_mutation_pattern = re.compile(r"\b(process_runtime|apply_intent|authority_context|process_id)\b", re.IGNORECASE)
    for rel_path in HW_RENDERER_RENDERMODEL_ONLY_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="hardware renderer contract file is missing",
                    rule_id="INV-HW-RENDERER-RENDERMODEL-ONLY",
                )
            )
            continue

        has_render_model_token = False
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line)
            lowered = token.lower()
            if "render_model" in lowered or "rendermodel" in lowered:
                has_render_model_token = True
            if renderer_truth_pattern.search(token):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token.strip()[:140],
                        message="hardware renderer path references forbidden truth symbol",
                        rule_id="INV-HW-RENDERER-RENDERMODEL-ONLY",
                    )
                )
            if renderer_mutation_pattern.search(token):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=token.strip()[:140],
                        message="hardware renderer path must not couple to process mutation surfaces",
                        rule_id="INV-HW-RENDERER-RENDERMODEL-ONLY",
                    )
                )
        if not has_render_model_token:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="render_model",
                    message="hardware renderer path must consume RenderModel payloads",
                    rule_id="INV-HW-RENDERER-RENDERMODEL-ONLY",
                )
            )

    hw_renderer_rel = "src/client/render/renderers/hw_renderer_gl.py"
    hw_renderer_abs = os.path.join(repo_root, hw_renderer_rel.replace("/", os.sep))
    try:
        hw_text = open(hw_renderer_abs, "r", encoding="utf-8").read()
    except OSError:
        hw_text = ""
    for token in (
        "def render_hardware_gl_snapshot(",
        "create_graphics_context(",
        "render_software_snapshot(",
    ):
        if hw_text and token in hw_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=hw_renderer_rel,
                line_number=1,
                snippet=token,
                message="hardware renderer backend missing deterministic RenderModel-only integration token",
                rule_id="INV-HW-RENDERER-RENDERMODEL-ONLY",
            )
        )


def _append_control_ir_enforcement_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_ir_files = (
        "src/control/ir/control_ir_verifier.py",
        "src/control/ir/control_ir_compiler.py",
        "src/control/ir/control_ir_programs.py",
    )
    for rel_path in required_ir_files:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="",
                message="required control IR module is missing",
                rule_id="INV-NO-MACRO-BEHAVIOR-WITHOUT-IR",
            )
        )

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_abs = os.path.join(repo_root, process_runtime_rel.replace("/", os.sep))
    try:
        process_runtime_text = open(process_runtime_abs, "r", encoding="utf-8").read()
    except OSError:
        process_runtime_text = ""
    if not process_runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime file missing; cannot enforce Control IR macro integration",
                rule_id="INV-NO-MACRO-BEHAVIOR-WITHOUT-IR",
            )
        )
    else:
        for token in (
            "build_blueprint_execution_ir(",
            "build_autopilot_stub_ir(",
            "build_ai_controller_stub_ir(",
            "compile_ir_program(",
        ):
            if token in process_runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=process_runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="multi-step automation surfaces must route through Control IR builders/compile path",
                    rule_id="INV-NO-MACRO-BEHAVIOR-WITHOUT-IR",
                )
            )

    forbidden_tokens = ("eval(", "exec(", "__import__(", "ast.literal_eval(")
    scan_roots = (
        "src/control",
        "tools/xstack/sessionx",
        "src/materials/construction",
    )
    for root in scan_roots:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                for line_no, line in _iter_lines(repo_root, rel_path):
                    snippet = str(line).strip()
                    if not snippet:
                        continue
                    for token in forbidden_tokens:
                        if token not in snippet:
                            continue
                        findings.append(
                            _finding(
                                severity=severity,
                                file_path=rel_path,
                                line_number=line_no,
                                snippet=snippet[:140],
                                message="dynamic evaluation is forbidden in runtime and control paths",
                                rule_id="INV-NO-DYNAMIC-EVAL",
                            )
                        )
                        break


def _append_negotiation_kernel_enforcement_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_tokens_by_file = {
        "src/control/negotiation/negotiation_kernel.py": (
            "def negotiate_request(",
            "NEGOTIATION_AXIS_ORDER",
        ),
        "src/control/control_plane_engine.py": (
            "negotiate_request(",
            "_decision_log_row(",
        ),
    }
    for rel_path, required_tokens in sorted(required_tokens_by_file.items(), key=lambda item: item[0]):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="required negotiation kernel integration file is missing",
                    rule_id="INV-NO-DOMAIN-DOWNGRADE-LOGIC",
                )
            )
            continue
        text = _file_text(repo_root, rel_path)
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="downgrade/refusal decisions must flow through negotiation kernel integration points",
                    rule_id="INV-NO-DOMAIN-DOWNGRADE-LOGIC",
                )
            )

    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(
            (
                "tools/xstack/testx/tests/",
                "tools/auditx/analyzers/",
                "tools/xstack/repox/",
                "docs/",
            )
        ):
            continue
        if rel_path == "src/control/negotiation/negotiation_kernel.py":
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line)
            if "build_downgrade_entry(" not in token:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=token.strip()[:140],
                    message="downgrade entries must be constructed only in the negotiation kernel",
                    rule_id="INV-NO-DOMAIN-DOWNGRADE-LOGIC",
                )
            ) 


def _append_fidelity_engine_enforcement_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    fidelity_core_rel = "src/control/fidelity/fidelity_engine.py"
    fidelity_core_text = _file_text(repo_root, fidelity_core_rel)
    if not fidelity_core_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=fidelity_core_rel,
                line_number=1,
                snippet="",
                message="fidelity arbitration core is missing",
                rule_id="INV-FIDELITY-USES-ENGINE",
            )
        )
        return
    for token in ("def arbitrate_fidelity_requests(", "RANK_FAIR_POLICY_ID", "REFUSAL_CTRL_FIDELITY_DENIED"):
        if token in fidelity_core_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=fidelity_core_rel,
                line_number=1,
                snippet=token,
                message="fidelity arbitration engine is missing required deterministic policy/refusal token",
                rule_id="INV-FIDELITY-USES-ENGINE",
            )
        )

    domain_required_tokens = {
        "src/materials/materialization/materialization_engine.py": (
            "build_fidelity_request(",
            "arbitrate_fidelity_requests(",
        ),
        "src/inspection/inspection_engine.py": (
            "build_fidelity_request(",
            "arbitrate_fidelity_requests(",
        ),
        "src/materials/commitments/commitment_engine.py": (
            "build_fidelity_request(",
            "arbitrate_fidelity_requests(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            "arbitrate_fidelity_requests(",
            "REFUSAL_CTRL_FIDELITY_DENIED",
        ),
    }
    for rel_path, required_tokens in sorted(domain_required_tokens.items(), key=lambda item: item[0]):
        text = _file_text(repo_root, rel_path)
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="domain fidelity integration file is missing",
                    rule_id="INV-FIDELITY-USES-ENGINE",
                )
            )
            continue
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="domain fidelity path must use CTRL-5 fidelity engine APIs",
                    rule_id="INV-FIDELITY-USES-ENGINE",
                )
            )

    # Domain files must not contain inline micro->meso->macro downgrade chains.
    downgrade_smell_tokens = (
        "if desired_fidelity == \"micro\" and micro_cost >",
        "if fidelity_achieved == \"meso\" and meso_cost >",
        "if desired_fidelity == \"micro\" and not micro_allowed",
    )
    for rel_path in (
        "src/materials/commitments/commitment_engine.py",
        "src/materials/materialization/materialization_engine.py",
        "src/inspection/inspection_engine.py",
    ):
        text = _file_text(repo_root, rel_path)
        if not text:
            continue
        for token in downgrade_smell_tokens:
            if token not in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="inline domain fidelity downgrade logic detected; use CTRL-5 fidelity engine decisions",
                    rule_id="INV-NO-DOMAIN-FIDELITY-DOWNGRADE",
                )
            )


def _append_plan_execution_enforcement_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _file_text(repo_root, runtime_rel)
    if not runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet="",
                message="process runtime missing for plan execution enforcement checks",
                rule_id="INV-NO-DIRECT-STRUCTURE-INSTALL",
            )
        )
        return

    plan_execute_token = 'elif process_id == "process.plan_execute":'
    plan_create_token = 'elif process_id == "process.plan_create":'
    plan_update_token = 'elif process_id == "process.plan_update_incremental":'
    for token in (plan_create_token, plan_update_token, plan_execute_token):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="planning/execution pipeline must expose process.plan_* entrypoints",
                rule_id="INV-NO-DIRECT-STRUCTURE-INSTALL",
            )
        )

    branch_start = runtime_text.find(plan_execute_token)
    branch_end = runtime_text.find('elif process_id == "process.construction_project_create":', max(0, branch_start))
    if branch_start >= 0:
        branch_text = runtime_text[branch_start : (branch_end if branch_end > branch_start else len(runtime_text))]
        if "build_plan_execution_ir(" not in branch_text or "construction_commitments" not in branch_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=runtime_rel,
                    line_number=1,
                    snippet="build_plan_execution_ir/construction_commitments",
                    message="plan execution must compile plan artifacts to IR and emit commitments",
                    rule_id="INV-NO-DIRECT-STRUCTURE-INSTALL",
                )
            )
        if "installed_structure_instances =" in branch_text or "create_construction_project(" in branch_text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=runtime_rel,
                    line_number=1,
                    snippet="installed_structure_instances =",
                    message="plan_execute must not directly install structures",
                    rule_id="INV-NO-DIRECT-STRUCTURE-INSTALL",
                )
            )

    overlays_rel = "src/client/interaction/inspection_overlays.py"
    overlays_text = _file_text(repo_root, overlays_rel)
    if not overlays_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=overlays_rel,
                line_number=1,
                snippet="",
                message="inspection overlay file missing for ghost derivation invariant",
                rule_id="INV-GHOST-IS-DERIVED",
            )
        )
    else:
        for token in ("_plan_overlay_payload(", "overlay_kind\": \"plan_ghost", "\"derived_only\": True"):
            if token in overlays_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=overlays_rel,
                    line_number=1,
                    snippet=token,
                    message="ghost overlays must be derived from plan artifacts and explicitly marked derived-only",
                    rule_id="INV-GHOST-IS-DERIVED",
                )
            )


def _append_capability_enforcement_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    capability_registry_rel = "data/registries/capability_registry.json"
    capability_engine_rel = "src/control/capability/capability_engine.py"
    control_plane_rel = "src/control/control_plane_engine.py"
    plan_engine_rel = "src/control/planning/plan_engine.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"

    capability_registry_text = _file_text(repo_root, capability_registry_rel)
    capability_engine_text = _file_text(repo_root, capability_engine_rel)
    if not capability_registry_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=capability_registry_rel,
                line_number=1,
                snippet="",
                message="capability registry is required for capability-driven feature declarations",
                rule_id="INV-CAPABILITY-REGISTRY-REQUIRED",
            )
        )
    if not capability_engine_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=capability_engine_rel,
                line_number=1,
                snippet="",
                message="capability engine module is required",
                rule_id="INV-CAPABILITY-REGISTRY-REQUIRED",
            )
        )
    else:
        for token in ("def has_capability(", "def get_capability_params(", "normalize_capability_binding_rows("):
            if token in capability_engine_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=capability_engine_rel,
                    line_number=1,
                    snippet=token,
                    message="capability engine missing required deterministic query API",
                    rule_id="INV-CAPABILITY-REGISTRY-REQUIRED",
                )
            )

    control_plane_text = _file_text(repo_root, control_plane_rel)
    for token in ("required_capabilities", "resolve_missing_capabilities("):
        if token in control_plane_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=control_plane_rel,
                line_number=1,
                snippet=token,
                message="control resolution must validate required capabilities through capability bindings",
                rule_id="INV-CAPABILITY-REGISTRY-REQUIRED",
            )
        )

    plan_engine_text = _file_text(repo_root, plan_engine_rel)
    for token in ("capability.can_be_planned", "has_capability("):
        if token in plan_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=plan_engine_rel,
                line_number=1,
                snippet=token,
                message="planning path must use capability.can_be_planned checks",
                rule_id="INV-NO-TYPE-BRANCHING",
            )
        )

    runtime_text = _file_text(repo_root, runtime_rel)
    for token in ("capability.has_pose_slots", "capability.has_ports"):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="runtime pose/port paths must gate via capability bindings",
                rule_id="INV-CAPABILITY-REGISTRY-REQUIRED",
            )
        )

    capability_ids = set()
    if capability_registry_text:
        try:
            capability_payload = json.loads(capability_registry_text)
        except ValueError:
            capability_payload = {}
        record = dict(capability_payload.get("record") or {})
        rows = list(record.get("capabilities") or [])
        for row in rows:
            if isinstance(row, dict):
                token = str(row.get("capability_id", "")).strip()
                if token:
                    capability_ids.add(token)
    control_action_registry_text = _file_text(repo_root, "data/registries/control_action_registry.json")
    if control_action_registry_text:
        try:
            action_payload = json.loads(control_action_registry_text)
        except ValueError:
            action_payload = {}
        actions = list(dict(action_payload.get("record") or {}).get("actions") or [])
        for row in actions:
            if not isinstance(row, dict):
                continue
            action_id = str(row.get("action_id", "")).strip() or "<unknown>"
            required_caps = sorted(
                set(str(item).strip() for item in list(row.get("required_capabilities") or []) if str(item).strip())
            )
            for capability_id in required_caps:
                if capability_id in capability_ids:
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path="data/registries/control_action_registry.json",
                        line_number=1,
                        snippet=capability_id,
                        message="control action '{}' references capability '{}' missing from capability registry".format(
                            action_id,
                            capability_id,
                        ),
                        rule_id="INV-CAPABILITY-REGISTRY-REQUIRED",
                    )
                )

    # Static scan for gameplay type-branching heuristics in production code.
    type_branch_patterns = (
        re.compile(r"\b(entity_type|assembly_type|entity_class|assembly_class)\b\s*=="),
        re.compile(r"\b\w*type\w*\s*==\s*[\"'](?:vehicle|building|machine)[\"']"),
    )
    for rel_path in _scan_files(repo_root):
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith(("tools/xstack/testx/tests/", "tools/auditx/analyzers/", "docs/")):
            continue
        if not rel_path.startswith(("src/control/", "src/interaction/", "tools/xstack/sessionx/")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            for pattern in type_branch_patterns:
                if not pattern.search(snippet):
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_path,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="core gameplay branching should use capabilities, not type/class checks",
                        rule_id="INV-NO-TYPE-BRANCHING",
                    )
                )
                break

    for token in (
        "apply_elec_budget_degradation(",
        "state[\"elec_degradation_events\"]",
        "degradation_event_hash_chain",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="electrical network tick must apply deterministic budget degradation and emit degradation events",
                rule_id="INV-ELEC-BUDGETED",
            )
        )

    for token in (
        "cascade_max_iterations",
        "cascade_iteration_limit_reached",
        "elec_cascade_iteration_rows",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="electrical cascade processing must be bounded with deterministic iteration caps and state",
                rule_id="INV-ELEC-CASCADE-BOUNDED",
            )
        )

    for token in (
        "state[\"elec_trip_events\"]",
        "state[\"trip_event_hash_chain\"]",
        "evaluate_protection_trip_plan(",
        "build_safety_event(",
    ):
        if token in runtime_text or token in power_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="electrical trip mutations must be logged and hash-chained through runtime safety/protection paths",
                rule_id="INV-ELEC-ALL-TRIPS-LOGGED",
            )
        )


def _append_effect_system_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    required_tokens_by_file = {
        "src/control/effects/effect_engine.py": (
            "def build_effect(",
            "def prune_expired_effect_rows(",
            "def get_effective_modifier(",
        ),
        "tools/xstack/sessionx/process_runtime.py": (
            'elif process_id == "process.effect_apply":',
            'elif process_id == "process.effect_remove":',
            "normalize_effect_rows(",
            "prune_expired_effect_rows(",
        ),
        "src/control/control_plane_engine.py": (
            "def _effect_influence(",
            "REFUSAL_EFFECT_FORBIDDEN",
            "get_effective_modifier_map(",
        ),
    }
    for rel_path, tokens in sorted(required_tokens_by_file.items(), key=lambda item: item[0]):
        text = _file_text(repo_root, rel_path)
        if not text:
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet="",
                    message="effect system enforcement requires canonical effect integration file",
                    rule_id="INV-EFFECT-USES-ENGINE",
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                    snippet=token,
                    message="effect system integration is missing required deterministic token",
                    rule_id="INV-EFFECT-USES-ENGINE",
                )
            )

    temp_modifier_patterns = (
        re.compile(r"state\[[\"'](?:interior_movement_constraints|temporary_[^\"']+|temp_[^\"']+)[\"']\]\s*="),
        re.compile(r"\b(speed|traction|visibility)\b\s*\*=\s*(?:0?\.\d+|\d+\s*/\s*\d+)"),
        re.compile(r"\bif\b[^\n]*(damag|smoke|flood)[^\n]*\b(speed|traction|visibility)\b"),
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(
            (
                "tools/xstack/testx/tests/",
                "tools/auditx/analyzers/",
                "docs/",
            )
        ):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in temp_modifier_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="temporary modifiers must use CTRL-8 effect rows instead of ad-hoc inline flags/multipliers",
                    rule_id="INV-NO-ADHOC-TEMP-MODIFIERS",
                )
            )
            break


def _append_specsheet_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    spec_engine_rel = "src/specs/spec_engine.py"
    runtime_text = _file_text(repo_root, runtime_rel)
    spec_engine_text = _file_text(repo_root, spec_engine_rel)
    if not runtime_text or not spec_engine_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel if not runtime_text else spec_engine_rel,
                line_number=1,
                snippet="",
                message="specsheet enforcement requires runtime and spec engine integration files",
                rule_id="INV-SPECSHEET-OPTIONAL",
            )
        )
        return

    for token in (
        "def _spec_pack_payload_rows(",
        "if os.path.isfile(default_pack_abs):",
        "load_spec_sheet_rows(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="specsheet runtime integration is missing deterministic optional-pack token",
                rule_id="INV-SPECSHEET-OPTIONAL",
            )
        )

    for rel_path in (
        "tools/xstack/session_boot.py",
        "tools/xstack/session_create.py",
        "tools/xstack/sessionx/creator.py",
    ):
        text = _file_text(repo_root, rel_path)
        if (not text) or ("specs.default.realistic.m1" not in text):
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=rel_path,
                line_number=1,
                snippet="specs.default.realistic.m1",
                message="runtime/session boot must not require default SpecSheet pack",
                rule_id="INV-SPECSHEET-OPTIONAL",
            )
        )

    hardcoded_spec_patterns = (
        re.compile(r"\b(?:gauge_mm|track_gauge_mm|road_width_mm|width_mm|max_speed_kph|min_clearance_mm|min_curvature_radius_mm)\b\s*[:=]\s*\d{2,6}\b"),
        re.compile(r"[\"'](?:gauge_mm|track_gauge_mm|road_width_mm|width_mm|max_speed_kph|min_clearance_mm|min_curvature_radius_mm)[\"']\s*:\s*\d{2,6}\b"),
    )
    skip_prefixes = (
        "src/specs/",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in hardcoded_spec_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="infrastructure spec constants must be declared in SpecSheets/registries, not hardcoded inline",
                    rule_id="INV-NO-HARDCODED-GAUGE-WIDTH-SPECS",
                )
            )
            break


def _append_formalization_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    inference_rel = "src/infrastructure/formalization/inference_engine.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    control_action_registry_rel = "data/registries/control_action_registry.json"
    control_policy_registry_rel = "data/registries/control_policy_registry.json"

    inference_text = _file_text(repo_root, inference_rel)
    runtime_text = _file_text(repo_root, runtime_rel)
    if not inference_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=inference_rel,
                line_number=1,
                snippet="",
                message="formalization inference engine is missing",
                rule_id="INV-INFERENCE-DERIVED-ONLY",
            )
        )
    else:
        required_inference_tokens = (
            "def infer_candidates(",
            "degrade.formalization.inference_budget",
            "normalize_inference_candidate_rows(",
        )
        for token in required_inference_tokens:
            if token in inference_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=inference_rel,
                    line_number=1,
                    snippet=token,
                    message="formalization inference engine missing required deterministic token",
                    rule_id="INV-INFERENCE-DERIVED-ONLY",
                )
            )

        forbidden_inference_patterns = (
            re.compile(r"\bstate\s*\["),
            re.compile(r"\bnetwork_graphs\b"),
            re.compile(r"\bformalization_states\b"),
            re.compile(r"\bcreate_commitment_row\s*\("),
            re.compile(r"\bexecute_intent\s*\("),
        )
        for line_no, line in _iter_lines(repo_root, inference_rel):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in forbidden_inference_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=inference_rel,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="inference engine must remain derived-only and must not mutate truth/network/process state",
                    rule_id="INV-INFERENCE-DERIVED-ONLY",
                )
            )
            break

    if not runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet="",
                message="formalization process runtime integration is missing",
                rule_id="INV-FORMALIZATION-THROUGH-CONTROL",
            )
        )
    else:
        for token in (
            'elif process_id == "process.formalization_infer":',
            'elif process_id == "process.formalization_accept_candidate":',
            'elif process_id == "process.formalization_promote_networked":',
            'elif process_id == "process.formalization_revert":',
        ):
            if token in runtime_text:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=runtime_rel,
                    line_number=1,
                    snippet=token,
                    message="formalization runtime process handler is missing",
                    rule_id="INV-FORMALIZATION-THROUGH-CONTROL",
                )
            )

    control_action_abs = os.path.join(repo_root, control_action_registry_rel.replace("/", os.sep))
    control_action_payload = _read_json_object(control_action_abs)
    action_rows = []
    if isinstance(control_action_payload.get("record"), dict):
        action_rows = list((dict(control_action_payload.get("record") or {})).get("actions") or [])
    if (not action_rows) and isinstance(control_action_payload.get("actions"), list):
        action_rows = list(control_action_payload.get("actions") or [])
    action_process_map = {}
    for row in sorted((item for item in action_rows if isinstance(item, dict)), key=lambda item: str(item.get("action_id", ""))):
        action_id = str(row.get("action_id", "")).strip()
        produces = dict(row.get("produces") or {})
        process_id = str(produces.get("process_id", "")).strip()
        if action_id and process_id:
            action_process_map[action_id] = process_id
    required_action_map = {
        "action.formalize.infer": "process.formalization_infer",
        "action.formalize.accept": "process.formalization_accept_candidate",
        "action.formalize.promote_network": "process.formalization_promote_networked",
        "action.formalize.revert": "process.formalization_revert",
    }
    for action_id, process_id in sorted(required_action_map.items(), key=lambda item: item[0]):
        actual = str(action_process_map.get(action_id, "")).strip()
        if actual == process_id:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=control_action_registry_rel,
                line_number=1,
                snippet="{} -> {}".format(action_id, process_id),
                message="formalization user-facing action must be registered through control action registry",
                rule_id="INV-FORMALIZATION-THROUGH-CONTROL",
            )
        )

    control_policy_abs = os.path.join(repo_root, control_policy_registry_rel.replace("/", os.sep))
    control_policy_payload = _read_json_object(control_policy_abs)
    policy_rows = []
    if isinstance(control_policy_payload.get("record"), dict):
        policy_rows = list((dict(control_policy_payload.get("record") or {})).get("policies") or [])
    if (not policy_rows) and isinstance(control_policy_payload.get("policies"), list):
        policy_rows = list(control_policy_payload.get("policies") or [])
    has_formalize_pattern = False
    for row in policy_rows:
        if not isinstance(row, dict):
            continue
        allowed_actions = sorted(
            set(str(item).strip() for item in list(row.get("allowed_actions") or []) if str(item).strip())
        )
        if "action.formalize.*" in set(allowed_actions):
            has_formalize_pattern = True
            break
    if not has_formalize_pattern:
        findings.append(
            _finding(
                severity=severity,
                file_path=control_policy_registry_rel,
                line_number=1,
                snippet="action.formalize.*",
                message="control policy registry should include action.formalize.* where formalization is allowed",
                rule_id="INV-FORMALIZATION-THROUGH-CONTROL",
            )
        )

    formalization_process_literal = re.compile(r"[\"']process\.formalization_[A-Za-z0-9_.-]+[\"']")
    direct_dispatch_call = re.compile(r"\b(?:run_process|execute_process|runtime_execute_intent|execute_intent)\s*\(")
    allowed_literal_prefixes = (
        "tools/xstack/sessionx/process_runtime.py",
        "data/registries/control_action_registry.json",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith((".py", ".json")):
            continue
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        if rel_norm.startswith(allowed_literal_prefixes):
            continue
        if rel_norm.startswith(("build/", "dist/", ".xstack_cache/")):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not formalization_process_literal.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="formalization process ids must be surfaced through control action registry only",
                    rule_id="INV-FORMALIZATION-THROUGH-CONTROL",
                )
            )
            break

    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.startswith(("src/client/", "src/interaction/")):
            continue
        if not rel_norm.endswith(".py"):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not direct_dispatch_call.search(snippet):
                continue
            if not formalization_process_literal.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="formalization accept/promote/revert must route through control plane intents, not direct process calls",
                    rule_id="INV-FORMALIZATION-THROUGH-CONTROL",
                )
            )
            break


def _append_mechanics_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    mechanics_engine_rel = "src/mechanics/structural_graph_engine.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    engine_text = _file_text(repo_root, mechanics_engine_rel)
    runtime_text = _file_text(repo_root, runtime_rel)
    if (not engine_text) or (not runtime_text):
        missing = mechanics_engine_rel if not engine_text else runtime_rel
        findings.append(
            _finding(
                severity=severity,
                file_path=missing,
                line_number=1,
                snippet="",
                message="mechanics enforcement requires canonical engine and runtime integration files",
                rule_id="INV-STRUCTURAL-FAILURE-THROUGH-MECH",
            )
        )
        return

    for token in (
        "def evaluate_structural_graphs(",
        "degrade.mechanics.budget",
        "stress_ratio_permille",
    ):
        if token in engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=mechanics_engine_rel,
                line_number=1,
                snippet=token,
                message="mechanics engine is missing required deterministic load/stress token",
                rule_id="INV-NO-ADHOC-LOAD-CHECK",
            )
        )

    for token in (
        'elif process_id == "process.mechanics_tick":',
        'elif process_id == "process.mechanics_fracture":',
        'elif process_id == "process.weld_joint":',
        'elif process_id == "process.cut_joint":',
        'elif process_id == "process.drill_hole":',
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="structural load/failure behavior must route through mechanics processes",
                rule_id="INV-STRUCTURAL-FAILURE-THROUGH-MECH",
            )
        )

    ad_hoc_load_patterns = (
        re.compile(r"\bif\b[^\n]*(?:load|stress_ratio)[^\n]*[><=]{1,2}[^\n]*(?:break|fracture|fail)", re.IGNORECASE),
        re.compile(r"\b(?:max_load|load_rating|stress_ratio)\b\s*[*+/=-]+\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)", re.IGNORECASE),
    )
    structural_failure_pattern = re.compile(r"failure_state[^\\n=]*=\s*[\"']failed[\"']", re.IGNORECASE)
    skip_prefixes = (
        "src/mechanics/",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/")):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if any(pattern.search(snippet) for pattern in ad_hoc_load_patterns):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="load/stress checks must use structural_graph_engine outputs, not ad-hoc inline conditions",
                        rule_id="INV-NO-ADHOC-LOAD-CHECK",
                    )
                )
                break
            if structural_failure_pattern.search(snippet) and "structural" in snippet.lower():
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="structural failure state transitions must route through process.mechanics_fracture",
                        rule_id="INV-STRUCTURAL-FAILURE-THROUGH-MECH",
                    )
                )
                break


def _append_field_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _invariant_severity(profile)

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    field_engine_rel = "src/fields/field_engine.py"
    runtime_text = _file_text(repo_root, runtime_rel)
    field_text = _file_text(repo_root, field_engine_rel)
    if (not runtime_text) or (not field_text):
        missing = runtime_rel if not runtime_text else field_engine_rel
        findings.append(
            _finding(
                severity=severity,
                file_path=missing,
                line_number=1,
                snippet="",
                message="FIELD integration requires canonical runtime and field engine modules",
                rule_id="INV-FIELD-QUERIES-ONLY",
            )
        )
        return

    required_runtime_tokens = (
        'elif process_id == "process.field_tick":',
        "field_modifier_snapshot(",
        "get_field_value(",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="field behavior must be sourced via deterministic FieldLayer query/runtime hooks",
                rule_id="INV-FIELD-QUERIES-ONLY",
            )
        )

    required_engine_tokens = (
        "def get_field_value(",
        "def update_field_layers(",
        "field_id",
    )
    for token in required_engine_tokens:
        if token in field_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=field_engine_rel,
                line_number=1,
                snippet=token,
                message="field engine must expose deterministic query/update entrypoints",
                rule_id="INV-FIELD-QUERIES-ONLY",
            )
        )

    weather_flag_pattern = re.compile(
        r"\b(?:is_|has_)?(?:rain|raining|weather|fog|snow|ice|storm)_(?:mode|flag|state)\b",
        re.IGNORECASE,
    )
    inline_weather_logic_pattern = re.compile(
        r"\bif\b[^\n]*(?:rain|raining|weather|fog|snow|ice|storm)[^\n]*(?:traction|friction|visibility|wind|speed)\b",
        re.IGNORECASE,
    )
    inline_multiplier_pattern = re.compile(
        r"\b(?:traction|friction|visibility|wind)\b\s*[*+\-\/]=\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)",
        re.IGNORECASE,
    )
    allowed_prefixes = (
        "src/fields/",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/repox/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
        "docs/",
        "data/",
        "schema/",
        "schemas/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if rel_norm.startswith(allowed_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if weather_flag_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="ad-hoc weather mode/flag tokens are forbidden; use FieldLayer query/effect paths",
                        rule_id="INV-NO-ADHOC-WEATHER-FLAGS",
                    )
                )
                break
            if inline_weather_logic_pattern.search(snippet) or inline_multiplier_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="weather/traction/visibility logic must route through FieldLayer queries only",
                        rule_id="INV-FIELD-QUERIES-ONLY",
                    )
                )
                break


def _append_field_generalization_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    field_registry_rel = "data/registries/field_type_registry.json"
    field_registry_payload, field_registry_error = _load_json_object(repo_root, field_registry_rel)
    field_rows = list((dict(field_registry_payload.get("record") or {})).get("field_types") or []) if not field_registry_error else []
    registered_field_ids = set()
    for row in list(field_rows or []):
        if not isinstance(row, dict):
            continue
        for token in (
            str(row.get("field_type_id", "")).strip(),
            str(row.get("field_id", "")).strip(),
        ):
            if token:
                registered_field_ids.add(token)

    if field_registry_error or not registered_field_ids:
        findings.append(
            _finding(
                severity=severity,
                file_path=field_registry_rel,
                line_number=1,
                snippet="field_types",
                message="field type registry is missing or empty; cannot enforce field registration invariants",
                rule_id="INV-FIELD-TYPE-REGISTERED",
            )
        )
    else:
        token_pattern = re.compile(r"\bfield\.[A-Za-z0-9_.-]+\b")
        scan_paths = (
            "src/fields/",
            "src/models/model_engine.py",
            "tools/xstack/sessionx/process_runtime.py",
            "data/registries/field_type_registry.json",
            "data/registries/constitutive_model_registry.json",
        )
        skip_files = {
            "tools/xstack/repox/check.py",
        }
        allowed_non_field_tokens = {
            "field.static",
            "field.static_default",
            "field.scheduled",
            "field.scheduled_linear",
            "field.profile_defined",
            "field.flow_linked",
            "field.hazard_linked",
            "field.update_policy_guard",
            "field.free_motion.influence",
        }
        field_id_context_markers = (
            "field_id",
            "field_type_id",
            "input_id",
            "get_field_value(",
            "field_type_rows",
        )
        for rel_path in _scan_files(repo_root):
            rel_norm = _norm(rel_path)
            if not any(rel_norm == token or rel_norm.startswith(token) for token in scan_paths):
                continue
            if rel_norm in skip_files:
                continue
            if not rel_norm.endswith((".py", ".json", ".schema", ".schema.json", ".md", ".txt")):
                continue
            for line_no, line in _iter_lines(repo_root, rel_norm):
                snippet = str(line).strip()
                if (not snippet) or snippet.startswith("#"):
                    continue
                if "refusal.field." in snippet.lower():
                    continue
                if not any(marker in snippet.lower() for marker in field_id_context_markers):
                    continue
                unknown_tokens: List[str] = []
                for token in token_pattern.findall(snippet):
                    candidate = str(token).strip().rstrip(".,:;")
                    lowered = candidate.lower()
                    if lowered.endswith(".json") or lowered.endswith(".schema") or lowered.endswith(".schema.json"):
                        continue
                    if candidate in allowed_non_field_tokens:
                        continue
                    if candidate in registered_field_ids:
                        continue
                    unknown_tokens.append(candidate)
                if not unknown_tokens:
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="field identifier is not registered in data/registries/field_type_registry.json: {}".format(
                            ",".join(sorted(set(unknown_tokens)))
                        ),
                        rule_id="INV-FIELD-TYPE-REGISTERED",
                    )
                )
                break

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _file_text(repo_root, runtime_rel)
    required_runtime_tokens = (
        'elif process_id == "process.field_update":',
        "_apply_field_updates(",
        "_persist_field_state(",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="field mutation must route through process.field_update and deterministic field persistence hooks",
                rule_id="INV-FIELD-MUTATION-THROUGH-PROCESS",
            )
        )

    direct_field_write_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']field_layers[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']field_cells[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']field_sample_rows[\"']\s*\]\s*=", re.IGNORECASE),
    )
    mutation_scan_prefixes = (
        "src/",
        "tools/xstack/sessionx/",
    )
    mutation_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    mutation_allowed_files = {
        "tools/xstack/sessionx/process_runtime.py",
        "src/fields/field_engine.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(mutation_scan_prefixes):
            continue
        if rel_norm.startswith(mutation_skip_prefixes):
            continue
        if rel_norm in mutation_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in direct_field_write_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="direct field-state mutation is forbidden outside process.field_update/field engine pathways",
                    rule_id="INV-FIELD-MUTATION-THROUGH-PROCESS",
                )
            )
            break


def _append_mobility_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = "warn"

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    control_plane_rel = "src/control/control_plane_engine.py"
    constitution_rel = "docs/mobility/MOBILITY_CONSTITUTION.md"
    travel_engine_rel = "src/mobility/travel/travel_engine.py"

    runtime_text = _file_text(repo_root, process_runtime_rel)
    control_text = _file_text(repo_root, control_plane_rel)
    constitution_text = _file_text(repo_root, constitution_rel)
    travel_engine_text = _file_text(repo_root, travel_engine_rel)
    constitution_lower = constitution_text.lower()

    if "process.body_move_attempt" not in runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.body_move_attempt",
                message="mobility movement application must remain process-mediated through control dispatch",
                rule_id="INV-MOB-THROUGH-CONTROL",
            )
        )
    if "ControlIntent" not in control_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=control_plane_rel,
                line_number=1,
                snippet="ControlIntent",
                message="mobility driving and scheduling intents must route through ControlIntent/IR",
                rule_id="INV-MOB-THROUGH-CONTROL",
            )
        )

    if ("guide geometry" not in constitution_lower) and ("guide_geometry" not in constitution_lower):
        findings.append(
            _finding(
                severity=severity,
                file_path=constitution_rel,
                line_number=1,
                snippet="guide geometry",
                message="mobility constitution must declare guide geometry usage for deterministic movement constraints",
                rule_id="INV-MOB-USES-GUIDEGEOMETRY",
            )
        )
    if ("network graph" not in constitution_lower) and ("networkgraph" not in constitution_lower):
        findings.append(
            _finding(
                severity=severity,
                file_path=constitution_rel,
                line_number=1,
                snippet="network graph",
                message="mobility constitution must declare NetworkGraph dependency for route/network constraints",
                rule_id="INV-MOB-USES-NETWORKGRAPH",
            )
        )

    train_special_case_pattern = re.compile(
        r"\b(?:spec\.track|movement_surface\b[^\n]*(?:track|rail|road)|if\b[^\n]*(?:train|rail|track|road)[^\n]*(?:speed|traction|signal|derail|curve|curvature))\b",
        re.IGNORECASE,
    )
    vehicle_special_case_pattern = re.compile(
        r"\bif\b[^\n]*(?:vehicle_class_id|vehicle_type_id|vehicle_type)\b[^\n]*(?:==|!=)\s*[\"'](?:veh\.|vehicle\.)",
        re.IGNORECASE,
    )
    global_micro_motion_pattern = re.compile(
        r"\bfor\b[^\n]*(?:body_assemblies|vehicle|agent|entity)[^\n]*(?:in|range)\b",
        re.IGNORECASE,
    )
    global_micro_effect_pattern = re.compile(
        r"\b(?:transform_mm|position_mm|velocity|speed_cap|collision|drift)\b",
        re.IGNORECASE,
    )
    network_graph_tokens = ("network_graph", "NetworkGraph", "route_query", "route_result")
    guide_geometry_tokens = ("guide_geometry", "guide spline", "follow_spline", "constraint.follow_spline")

    train_skip_prefixes = (
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
        "docs/",
        "schema/",
        "schemas/",
    )
    mobility_scan_prefixes = ("src/", "tools/xstack/sessionx/")
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(mobility_scan_prefixes):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if train_special_case_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="train/road/rail movement special-casing must migrate into unified MOB constraints",
                        rule_id="INV-NO-TRAIN-SPECIALCASE",
                    )
                )
                break
            if vehicle_special_case_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="vehicle type/class hardcoded branching is forbidden; vehicle behavior must be spec/capability driven",
                        rule_id="INV-NO-VEHICLE-SPECIALCASE",
                    )
                )
                break
            if global_micro_motion_pattern.search(snippet) and global_micro_effect_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="global micro-motion loops are forbidden; micro movement must remain ROI-scoped",
                        rule_id="INV-NO-GLOBAL-MICRO-MOTION",
                    )
                )
                break

    if not any(token in runtime_text for token in network_graph_tokens):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="network_graph",
                message="mobility runtime should route graph traversal through NetworkGraph interfaces",
                rule_id="INV-MOB-USES-NETWORKGRAPH",
            )
        )
    if (
        'elif process_id == "process.mobility_network_create_from_formalization":' not in runtime_text
        or "build_mobility_network_graph(" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.mobility_network_create_from_formalization",
                message="mobility network promotion must create graph topology through NetworkGraph payload mapping",
                rule_id="INV-MOB-NETWORK-USES-NETWORKGRAPH",
            )
        )
    if (
        'elif process_id == "process.vehicle_register_from_structure":' not in runtime_text
        or "build_vehicle(" not in runtime_text
        or "build_motion_state(" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.vehicle_register_from_structure",
                message="vehicle truth rows must be authored as assembly-backed records through process.vehicle_register_from_structure",
                rule_id="INV-VEHICLES-AS-ASSEMBLIES",
            )
        )
    if (
        'elif process_id == "process.vehicle_check_compatibility":' not in runtime_text
        or "evaluate_vehicle_edge_compatibility(" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.vehicle_check_compatibility",
                message="vehicle movement eligibility must run deterministic spec compatibility checks before routing/itinerary use",
                rule_id="INV-SPEC-COMPATIBILITY-REQUIRED",
            )
        )
    if (
        'elif process_id == "process.switch_set_state":' not in runtime_text
        or "apply_transition(" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.switch_set_state",
                message="switching must route through state-machine transitions only",
                rule_id="INV-SWITCH-STATE-MACHINE-ONLY",
            )
        )
    if (
        'elif process_id == "process.signal_set_aspect":' not in runtime_text
        or 'elif process_id == "process.signal_tick":' not in runtime_text
        or "select_signal_transition_id(" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.signal_set_aspect/process.signal_tick",
                message="signal transitions must be process/state-machine mediated through signaling processes",
                rule_id="INV-SIGNALS-STATE-MACHINE-ONLY",
            )
        )
    if (
        "evaluate_signal_aspects(" not in runtime_text
        or "signal_rule_policy_registry" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="evaluate_signal_aspects",
                message="interlocking decisions must route through policy-driven signal evaluation",
                rule_id="INV-INTERLOCKING-POLICY-DRIVEN",
            )
        )
    if "query_route_result(" not in runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="query_route_result(",
                message="mobility routing must route through ABS deterministic routing engine",
                rule_id="INV-NO-ADHOC-ROUTING",
            )
        )
    adhoc_stop_patterns = (
        re.compile(r"\bif\b[^\n]*(?:signal|aspect)[^\n]*(?:stop)[^\n]*(?:velocity|speed|brake)", re.IGNORECASE),
    )
    adhoc_stop_allowed = {
        process_runtime_rel,
        "src/mobility/signals/signal_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in adhoc_stop_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in adhoc_stop_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="ad-hoc stop logic is forbidden; stop/go must be policy-driven via signaling layer",
                    rule_id="INV-NO-ADHOC-STOP-LOGIC",
                )
            )
            break
    if (
        'elif process_id == "process.itinerary_create":' not in runtime_text
        or 'elif process_id == "process.travel_start":' not in runtime_text
        or 'elif process_id == "process.travel_tick":' not in runtime_text
        or "build_travel_commitment(" not in runtime_text
        or "build_travel_event(" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.travel_start/process.travel_tick",
                message="macro travel must route through itinerary + travel commitments/events process paths",
                rule_id="INV-TRAVEL-THROUGH-COMMITMENTS",
            )
        )
    if (
        'elif process_id == "process.mobility_micro_tick":' not in runtime_text
        or "roi_vehicle_ids" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.mobility_micro_tick",
                message="micro constrained motion must run through process.mobility_micro_tick with explicit ROI gating",
                rule_id="INV-MICRO-MOTION-ROI-ONLY",
            )
        )
    if (
        'elif process_id == "process.mobility_free_tick":' not in runtime_text
        or "roi_subject_ids" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.mobility_free_tick",
                message="micro free motion must run through process.mobility_free_tick with explicit ROI subject gating",
                rule_id="INV-FREE-MOTION-ROI-ONLY",
            )
        )
    if 'elif process_id == "process.mob_derail":' not in runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.mob_derail",
                message="derailment transitions must route through process.mob_derail",
                rule_id="INV-DERAILMENT-PROCESS-ONLY",
            )
        )
    for token in (
        'elif process_id == "process.mobility_wear_tick":',
        'elif process_id == "process.inspect_track":',
        'elif process_id == "process.service_track":',
        'elif process_id == "process.inspect_vehicle":',
        'elif process_id == "process.service_vehicle":',
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet=token,
                message="mobility wear/inspection/service flows must be process-mediated through MOB-9 handlers",
                rule_id="INV-WEAR-THROUGH-HAZARD-ONLY",
            )
        )
    if (
        'elif process_id == "process.mob_failure":' not in runtime_text
        or 'elif process_id == "process.mob_track_failure":' not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.mob_failure/process.mob_track_failure",
                message="wear threshold breaches must route through explicit mobility failure processes",
                rule_id="INV-WEAR-THROUGH-HAZARD-ONLY",
            )
        )
    if not any(token in runtime_text for token in guide_geometry_tokens):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="guide_geometry",
                message="mobility runtime should consume guide geometry constraints rather than hardcoded movement branches",
                rule_id="INV-MOB-USES-GUIDEGEOMETRY",
            )
        )
    silent_position_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']vehicle_motion_states[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']itineraries[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']travel_commitments[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']travel_events[\"']\s*\]\s*=", re.IGNORECASE),
    )
    silent_position_allowed = {
        process_runtime_rel,
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in silent_position_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in silent_position_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="silent vehicle position/progress mutation outside process runtime is forbidden",
                    rule_id="INV-NO-SILENT-POSITION-UPDATES",
                )
            )
            break

    micro_mutation_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']micro_motion_states[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']coupling_constraints[\"']\s*\]\s*=", re.IGNORECASE),
    )
    micro_mutation_allowed = {
        process_runtime_rel,
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in micro_mutation_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in micro_mutation_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="micro motion truth writes must happen through mobility micro process paths only",
                    rule_id="INV-MICRO-MOTION-ROI-ONLY",
                )
            )
            break

    free_motion_mutation_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']free_motion_states[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']body_assemblies[\"']\s*\]\s*=", re.IGNORECASE),
    )
    free_motion_allowed = {
        process_runtime_rel,
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in free_motion_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in free_motion_mutation_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="free-motion position/body truth writes must happen through mobility free process runtime only",
                    rule_id="INV-POSITION-UPDATES-PROCESS-ONLY",
                )
            )
            break

    derail_bypass_pattern = re.compile(r"\b(?:incident\.derailment|vehicle_derailed)\b", re.IGNORECASE)
    derail_allowed_files = {
        process_runtime_rel,
        "src/mobility/micro/constrained_motion_solver.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in derail_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not derail_bypass_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="derailment signaling outside process.mob_derail runtime path is forbidden",
                    rule_id="INV-DERAILMENT-PROCESS-ONLY",
                )
            )
            break

    wallclock_motion_pattern = re.compile(r"\b(?:time\.time|datetime\.now|perf_counter|monotonic)\s*\(", re.IGNORECASE)
    wallclock_scan_prefixes = (
        "src/mobility/",
        "tools/xstack/sessionx/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(wallclock_scan_prefixes):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not wallclock_motion_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="wall-clock APIs are forbidden in mobility motion paths; use tick inputs only",
                    rule_id="INV-NO-WALLCLOCK-IN-MOTION",
                )
            )
            break

    adhoc_friction_wind_patterns = (
        re.compile(r"\b(?:friction|traction)\b\s*[*+\-\/]=\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)", re.IGNORECASE),
        re.compile(r"\b(?:wind|drift)\b\s*[*+\-\/]=\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)", re.IGNORECASE),
        re.compile(r"\bif\b[^\n]*(?:rain|snow|ice|fog|weather|wind)[^\n]*(?:speed|traction|friction|drift)\b", re.IGNORECASE),
    )
    adhoc_friction_wind_allowed = {
        process_runtime_rel,
        "src/fields/field_engine.py",
        "src/mobility/micro/free_motion_solver.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in adhoc_friction_wind_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in adhoc_friction_wind_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="friction/wind modifiers must route through FieldLayer + mobility free-motion/effect paths",
                    rule_id="INV-NO-ADHOC-FRICTION-WIND",
                )
            )
            break
    adhoc_wear_flag_patterns = (
        re.compile(r"\b(?:wear|degradation)_(?:flag|state|critical|broken)\b", re.IGNORECASE),
        re.compile(
            r"\b(?:track_wear|wheel_wear|brake_wear|engine_wear|signal_wear|switch_wear)\b\s*(?:[*+\-\/]=|=\s*(?:True|False|0|1)\b)",
            re.IGNORECASE,
        ),
        re.compile(r"\bif\b[^\n]*(?:track_wear|wheel_wear|brake_wear|engine_wear|signal_wear|switch_wear)\b", re.IGNORECASE),
    )
    adhoc_wear_allowed = {
        process_runtime_rel,
        "src/mobility/maintenance/wear_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in adhoc_wear_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in adhoc_wear_flag_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="ad-hoc wear/degradation flags are forbidden; use mobility wear state + hazard/schedule processes",
                    rule_id="INV-NO-ADHOC-WEAR-FLAGS",
                )
            )
            break
    wear_state_mutation_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']mobility_wear_states[\"']\s*\]\s*=", re.IGNORECASE),
    )
    wear_state_mutation_allowed = {
        process_runtime_rel,
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in wear_state_mutation_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in wear_state_mutation_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="mobility wear truth writes outside process runtime are forbidden",
                    rule_id="INV-WEAR-THROUGH-HAZARD-ONLY",
                )
            )
            break
    if (
        'elif process_id == "process.compartment_flow_tick":' not in runtime_text
        or "_sync_vehicle_interior_spatial_frame(" not in runtime_text
        or "_vehicle_row_for_interior_graph(" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="process.compartment_flow_tick/_sync_vehicle_interior_spatial_frame",
                message="vehicle interiors must stay integrated with INT substrate flow + spatial frame process hooks",
                rule_id="INV-INTERIORS-USE-INT-SUBSTRATE",
            )
        )
    adhoc_vehicle_cabin_patterns = (
        re.compile(r"\bvehicle_cabin_(?:pressure|oxygen|smoke|flood|leak)\b", re.IGNORECASE),
        re.compile(r"\bcabin_(?:pressure|oxygen|smoke|flood|leak)\b", re.IGNORECASE),
        re.compile(r"\bif\b[^\n]*(?:vehicle|cabin)[^\n]*(?:pressure|oxygen|smoke|flood|leak)\b", re.IGNORECASE),
    )
    adhoc_vehicle_cabin_allowed = {
        process_runtime_rel,
        "src/interior/compartment_flow_engine.py",
        "src/interior/compartment_flow_builder.py",
        "src/inspection/inspection_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in adhoc_vehicle_cabin_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in adhoc_vehicle_cabin_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="ad-hoc vehicle cabin logic is forbidden; route through INT compartment flow/instrument process layers",
                    rule_id="INV-NO-ADHOC-VEHICLE-CABIN-LOGIC",
                )
            )
            break
    if "edge_occupancies" not in runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet="edge_occupancies",
                message="travel tick must persist deterministic edge occupancy state alongside edge transition events",
                rule_id="INV-NO-SILENT-EDGE-ENTRY",
            )
        )
    if ("event.delay.congestion" not in runtime_text) and ("event.delay.congestion" not in travel_engine_text):
        findings.append(
            _finding(
                severity=severity,
                file_path=travel_engine_rel,
                line_number=1,
                snippet="event.delay.congestion",
                message="congestion-induced travel delays must emit explicit delay events with deterministic reason metadata",
                rule_id="INV-NO-ADHOC-CONGESTION",
            )
        )
    silent_edge_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']edge_occupancies[\"']\s*\]\s*=", re.IGNORECASE),
    )
    silent_edge_allowed = {
        process_runtime_rel,
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in silent_edge_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in silent_edge_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="edge occupancy mutation outside authoritative travel process/runtime path is forbidden",
                    rule_id="INV-NO-SILENT-EDGE-ENTRY",
                )
            )
            break
    adhoc_congestion_patterns = (
        re.compile(
            r"\bif\b[^\n]*(?:congestion|occupancy|capacity|traffic)[^\n]*(?:speed|eta|delay|arrival|progress)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:edge_eta_ticks|estimated_arrival_tick|delay_ticks|allowed_speed_mm_per_tick)\b\s*[*+\-\/]=\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:congestion_ratio_permille|current_occupancy|capacity_units)\b\s*[<>]=?\s*\d+",
            re.IGNORECASE,
        ),
    )
    adhoc_congestion_allowed = {
        process_runtime_rel,
        "src/mobility/travel/travel_engine.py",
        "src/mobility/traffic/traffic_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in adhoc_congestion_allowed:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in adhoc_congestion_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="congestion speed/eta/delay logic must route through mobility traffic + travel engines only",
                    rule_id="INV-NO-ADHOC-CONGESTION",
                )
            )
            break
    adhoc_routing_patterns = (
        re.compile(r"\b(?:dijkstra|a[_-]?star|bellman[_-]?ford|floyd[_-]?warshall)\b", re.IGNORECASE),
        re.compile(r"\broute\b[^\n]*(?:for\s+\w+\s+in\s+\w+)", re.IGNORECASE),
        re.compile(r"\b(?:neighbors|adjacency)\b[^\n]*(?:route|path)", re.IGNORECASE),
    )
    adhoc_routing_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    adhoc_routing_allow = {
        "src/core/graph/routing_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(adhoc_routing_skip_prefixes):
            continue
        if rel_norm in adhoc_routing_allow:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in adhoc_routing_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="ad-hoc mobility routing logic detected; route queries must use NetworkGraph/ABS routing",
                    rule_id="INV-NO-ADHOC-ROUTING",
                )
            )
            break
    for token in (
        'elif process_id == "process.geometry_create":',
        'elif process_id == "process.geometry_edit":',
        'elif process_id == "process.geometry_finalize":',
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=process_runtime_rel,
                line_number=1,
                snippet=token,
                message="guide geometry authoritative writes must route through geometry process handlers",
                rule_id="INV-GEOMETRY-CREATION-PROCESS-ONLY",
            )
        )

    geometry_mutation_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']guide_geometries[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']mobility_junctions[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']geometry_derived_metrics[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']geometry_candidates[\"']\s*\]\s*=", re.IGNORECASE),
    )
    geometry_allowed_files = {
        process_runtime_rel,
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(mobility_scan_prefixes):
            continue
        if rel_norm.startswith(train_skip_prefixes):
            continue
        if rel_norm in geometry_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in geometry_mutation_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="guide geometry truth writes must happen through process.geometry_* handlers only",
                    rule_id="INV-GEOMETRY-CREATION-PROCESS-ONLY",
                )
            )
            break

    hardcoded_gauge_pattern = re.compile(
        r"\b(?:gauge_mm|track_gauge_mm)\b\s*[:=]\s*\d{2,6}\b|[\"'](?:gauge_mm|track_gauge_mm)[\"']\s*:\s*\d{2,6}\b",
        re.IGNORECASE,
    )
    gauge_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
        "src/specs/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(mobility_scan_prefixes):
            continue
        if rel_norm.startswith(gauge_skip_prefixes):
            continue
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not hardcoded_gauge_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="hardcoded gauge constants are forbidden in mobility runtime; use SpecSheets/registries",
                    rule_id="INV-NO-HARDCODED-GAUGE",
                )
            )
            break


def _append_safety_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    safety_engine_rel = "src/safety/safety_engine.py"
    safety_registry_rel = "data/registries/safety_pattern_registry.json"
    runtime_text = _file_text(repo_root, runtime_rel)
    safety_engine_text = _file_text(repo_root, safety_engine_rel)
    safety_registry_text = _file_text(repo_root, safety_registry_rel)

    required_runtime_tokens = (
        'elif process_id == "process.safety_tick":',
        "_load_safety_pattern_registry(",
        "evaluate_safety_instances(",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="safety protections must run through process.safety_tick and Safety Pattern evaluation helpers",
                rule_id="INV-NO-ADHOC-SAFETY-LOGIC",
            )
        )

    required_engine_tokens = (
        "def safety_pattern_rows_by_id(",
        "def normalize_safety_instance_rows(",
        "def evaluate_safety_instances(",
    )
    for token in required_engine_tokens:
        if token in safety_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=safety_engine_rel,
                line_number=1,
                snippet=token,
                message="safety engine must expose deterministic pattern/instance evaluation primitives",
                rule_id="INV-NO-ADHOC-SAFETY-LOGIC",
            )
        )

    required_pattern_ids = (
        "safety.interlock_block",
        "safety.fail_safe_stop",
        "safety.relief_pressure",
        "safety.breaker_trip",
        "safety.redundant_pair",
        "safety.deadman_basic",
        "safety.loto_basic",
        "safety.graceful_degrade_basic",
        "safety.overtemp_trip",
        "safety.thermal_runaway",
    )
    for token in required_pattern_ids:
        if token in safety_registry_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=safety_registry_rel,
                line_number=1,
                snippet=token,
                message="safety registry must include baseline SAFETY-0 pattern template ids",
                rule_id="INV-NO-ADHOC-SAFETY-LOGIC",
            )
        )

    inline_safety_patterns = (
        re.compile(r"\b(?:interlock|failsafe|fail_safe|deadman|watchdog|lockout|tagout|breaker|relief)\b[^\n]*(?:=|apply|state|speed_cap)", re.IGNORECASE),
        re.compile(r"\bif\b[^\n]*(?:overload|fault|trip|interlock|watchdog|lockout)[^\n]*(?:then|return|apply|set)", re.IGNORECASE),
    )
    scan_prefixes = ("src/", "tools/xstack/sessionx/")
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        runtime_rel,
        safety_engine_rel,
        "src/mobility/signals/signal_engine.py",
        "tools/xstack/sessionx/observation.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in inline_safety_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="protective safety behavior must use registered safety patterns, not inline domain logic",
                    rule_id="INV-NO-ADHOC-SAFETY-LOGIC",
                )
            )
            break


def _append_electric_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = "warn"

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    power_engine_rel = "src/electric/power_network_engine.py"
    runtime_text = _file_text(repo_root, runtime_rel)
    power_engine_text = _file_text(repo_root, power_engine_rel)

    for token in (
        'elif process_id == "process.elec.connect_wire":',
        'elif process_id == "process.elec.network_tick":',
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="electrical process handlers must exist in process runtime for deterministic power flow orchestration",
                rule_id="INV-POWER-FLOW-THROUGH-BUNDLE",
            )
        )

    for token in (
        "def build_power_flow_channel(",
        '"bundle.power_phasor"',
        "def solve_power_network_e1(",
        "def solve_power_network_e0(",
    ):
        if token in power_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=power_engine_rel,
                line_number=1,
                snippet=token,
                message="power network logic must route through bundle.power_phasor helpers (E1/E0) rather than ad-hoc channels",
                rule_id="INV-POWER-FLOW-THROUGH-BUNDLE",
            )
        )

    for token in (
        "safety.breaker_trip",
        "evaluate_safety_instances(",
        "_apply_safety_actions(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="breaker overload handling must flow through SAFETY pattern evaluation/apply paths",
                rule_id="INV-BREAKER-THROUGH-SAFETY",
            )
        )

    for token in (
        "evaluate_protection_trip_plan(",
        "detect_faults(",
        "safety.breaker_trip",
        "_apply_safety_actions(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="electrical protection/fault orchestration must route through deterministic SAFETY and fault engines",
                rule_id="INV-ELEC-PROTECTION-THROUGH-SAFETY",
            )
        )

    for token in (
        'elif process_id in {"process.elec.lockout_tagout", "process.elec_apply_loto", "process.elec_remove_loto"}:',
        "state[\"safety_lockouts\"]",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="LOTO state transitions must be handled through deterministic process/state-machine paths",
                rule_id="INV-LOTO-STATE_MACHINE-ONLY",
            )
        )

    observation_rel = "tools/xstack/sessionx/observation.py"
    inspection_rel = "src/inspection/inspection_engine.py"
    overlay_rel = "src/client/interaction/inspection_overlays.py"
    control_registry_rel = "data/registries/control_action_registry.json"
    action_template_rel = "data/registries/action_template_registry.json"
    observation_text = _file_text(repo_root, observation_rel)
    inspection_text = _file_text(repo_root, inspection_rel)
    overlay_text = _file_text(repo_root, overlay_rel)
    control_registry_text = _file_text(repo_root, control_registry_rel)
    action_template_text = _file_text(repo_root, action_template_rel)

    for token in (
        "ch.diegetic.elec.energized",
        "ch.diegetic.elec.voltage",
        "ch.diegetic.elec.current_proxy",
        "ch.diegetic.elec.pf",
        "ch.diegetic.elec.trip_warning",
    ):
        if token in observation_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=observation_rel,
                line_number=1,
                snippet=token,
                message="electrical UX channels must be surfaced through observation/perceived-model pathways",
                rule_id="INV-NO-TRUTH-IN-UI",
            )
        )

    for token in (
        "action.elec.panel.open",
        "action.elec.panel.close",
        "action.elec.breaker.toggle",
        "action.elec.breaker.reset",
        "action.elec.isolator.open",
        "action.elec.isolator.close",
        "action.elec.loto.apply",
        "action.elec.loto.remove",
        "action.elec.connector.plug",
        "action.elec.connector.unplug",
        "action.elec.explain_trip",
    ):
        if token in control_registry_text and token in action_template_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=control_registry_rel,
                line_number=1,
                snippet=token,
                message="electrical interactive actions must be declared in control/action-template registries",
                rule_id="INV-ALL-ELEC-ACTIONS-THROUGH-CONTROL",
            )
        )

    for token in (
        'elif process_id == "process.elec.explain_trip":',
        "state[\"elec_trip_explanations\"]",
        "section.elec.device_states",
        "section.elec.fault_summary",
    ):
        if token in runtime_text or token in inspection_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel if "process_id" in token or "state[" in token else inspection_rel,
                line_number=1,
                snippet=token,
                message="trip explanations must remain derived artifacts from fault/safety/decision records",
                rule_id="INV-EPILOG-EXPLANATIONS-DERIVED-ONLY",
            )
        )

    truth_ui_patterns = (
        re.compile(r"ch\.truth\.overlay\.[^\n]*elec", re.IGNORECASE),
        re.compile(r"truth_overlay[^\n]*elec", re.IGNORECASE),
    )
    for rel_norm, text in (
        (observation_rel, observation_text),
        (overlay_rel, overlay_text),
        (inspection_rel, inspection_text),
    ):
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in truth_ui_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="electrical UX must not consume truth-overlay channels directly",
                    rule_id="INV-NO-TRUTH-IN-UI",
                )
            )
            break

    inline_power_loss_pattern = re.compile(
        r"\b(?:loss_p|heat_loss|line_loss|resistance_proxy|pf_permille)\b\s*=\s*[^#\n]*(?:\*|/|\+|-|//)",
        re.IGNORECASE,
    )
    inline_breaker_pattern = re.compile(
        r"\bbreaker_state\b\s*=\s*[\"'](?:tripped|open|closed|reset)[\"']",
        re.IGNORECASE,
    )
    inline_fault_trip_pattern = re.compile(
        r"\b(?:fault(?:_kind)?|overcurrent|short_circuit|ground_fault|open_circuit)\b[^\n]*(?:trip|tripped|open|disconnect|capacity_per_tick\s*=\s*0|safety_disconnected)",
        re.IGNORECASE,
    )
    inline_loto_pattern = re.compile(
        r"\b(?:loto_active|loto_lock_tag|safety_lockouts)\b\s*=",
        re.IGNORECASE,
    )
    scan_prefixes = ("src/", "tools/xstack/sessionx/")
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_power_loss_files = {
        runtime_rel,
        power_engine_rel,
        "src/core/flow/flow_engine.py",
        "src/models/model_engine.py",
        "tools/xstack/repox/check.py",
    }
    allowed_breaker_files = {
        runtime_rel,
        "src/safety/safety_engine.py",
        "tools/xstack/repox/check.py",
    }
    allowed_fault_trip_files = {
        runtime_rel,
        "src/electric/fault/fault_engine.py",
        "src/electric/protection/protection_engine.py",
        "src/safety/safety_engine.py",
        "tools/xstack/repox/check.py",
    }
    allowed_loto_files = {
        runtime_rel,
        "src/safety/safety_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if rel_norm not in allowed_power_loss_files and inline_power_loss_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="inline electrical loss/PF logic detected outside canonical power engine/model paths",
                        rule_id="INV-POWER-FLOW-THROUGH-BUNDLE",
                    )
                )
                break
            if rel_norm not in allowed_breaker_files and inline_breaker_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="breaker state mutation detected outside SAFETY/runtime protection handlers",
                        rule_id="INV-BREAKER-THROUGH-SAFETY",
                    )
                )
                break
            if rel_norm not in allowed_fault_trip_files and inline_fault_trip_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="fault/trip behavior detected outside canonical electrical fault/protection/safety paths",
                        rule_id="INV-NO-ADHOC-FAULT-TRIP",
                    )
                )
                break
            if rel_norm not in allowed_loto_files and inline_loto_pattern.search(snippet):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="LOTO lock state mutation detected outside deterministic process/state-machine handlers",
                        rule_id="INV-LOTO-STATE_MACHINE-ONLY",
                    )
                )
                break

    strict_severity = _strict_only_severity(profile)
    if 'elif process_id == "process.apply_force":' not in runtime_text:
        findings.append(
            _finding(
                severity=strict_severity,
                file_path=runtime_rel,
                line_number=1,
                snippet='elif process_id == "process.apply_force":',
                message="force application must route through deterministic process.apply_force handler",
                rule_id="INV-FORCE-THROUGH-PROCESS",
            )
        )
    if 'elif process_id == "process.apply_impulse":' not in runtime_text:
        findings.append(
            _finding(
                severity=strict_severity,
                file_path=runtime_rel,
                line_number=1,
                snippet='elif process_id == "process.apply_impulse":',
                message="impulse application must route through deterministic process.apply_impulse handler",
                rule_id="INV-FORCE-THROUGH-PROCESS",
            )
        )
    if (
        "_ensure_momentum_state_rows(state)" not in runtime_text
        or "state[\"momentum_states\"]" not in runtime_text
    ):
        findings.append(
            _finding(
                severity=strict_severity,
                file_path=runtime_rel,
                line_number=1,
                snippet="momentum_states",
                message="runtime must declare and normalize momentum_state truth rows before motion integration",
                rule_id="INV-MOMENTUM-STATE-DECLARED",
            )
        )
    momentum_schema_paths = (
        "schema/physics/momentum_state.schema",
        "schemas/momentum_state.schema.json",
    )
    for rel_path in momentum_schema_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            _finding(
                severity=strict_severity,
                file_path=rel_path,
                line_number=1,
                snippet="momentum_state",
                message="momentum_state schema must be present and registered for PHYS-1 process payload contracts",
                rule_id="INV-MOMENTUM-STATE-DECLARED",
            )
        )

    direct_velocity_patterns = (
        re.compile(r"\bvelocity_mm_per_tick\b\s*=", re.IGNORECASE),
        re.compile(r"\bvelocity\b\s*=\s*[^#\n]*(?:accel|acceleration|force|impulse)", re.IGNORECASE),
    )
    inline_accel_patterns = (
        re.compile(
            r"\bvelocity(?:_mm_per_tick)?\b\s*=\s*[^#\n]*(?:\+|-)\s*[^#\n]*(?:accel|acceleration)(?:_[a-z]+)?",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bvelocity(?:_mm_per_tick)?\b\s*=\s*[^#\n]*(?:accel|acceleration)[^#\n]*(?:\*|//|/)\s*",
            re.IGNORECASE,
        ),
    )
    velocity_scan_prefixes = ("src/", "tools/xstack/sessionx/")
    velocity_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    velocity_allowed_files = {
        runtime_rel,
        "src/mobility/micro/free_motion_solver.py",
        "src/mobility/micro/constrained_motion_solver.py",
        "src/physics/momentum_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(velocity_scan_prefixes):
            continue
        if rel_norm.startswith(velocity_skip_prefixes):
            continue
        if rel_norm in velocity_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if any(pattern.search(snippet) for pattern in direct_velocity_patterns):
                findings.append(
                    _finding(
                        severity=strict_severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="velocity writes must be derived from momentum in process/solver pathways, not ad-hoc assignments",
                        rule_id="INV-NO-DIRECT-VELOCITY-MUTATION",
                    )
                )
                break
            if any(pattern.search(snippet) for pattern in inline_accel_patterns):
                findings.append(
                    _finding(
                        severity=strict_severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="inline acceleration-to-velocity updates are forbidden outside momentum substrate integration paths",
                        rule_id="INV-NO-DIRECT-VELOCITY-MUTATION",
                    )
                )
                break


def _append_thermal_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = "warn"
    strict_severity = _strict_only_severity(profile)

    convention_rel = "docs/thermal/LOSS_TO_HEAT_CONVENTION.md"
    convention_abs = os.path.join(repo_root, convention_rel.replace("/", os.sep))
    if not os.path.isfile(convention_abs):
        findings.append(
            _finding(
                severity=strict_severity,
                file_path=convention_rel,
                line_number=1,
                snippet="",
                message="loss-to-heat convention must exist so dissipated energy remains auditable and replay-safe",
                rule_id="INV-LOSS-MAPPED-TO-HEAT",
            )
        )

    thermal_policy_rel = "data/registries/thermal_policy_registry.json"
    thermal_policy_text = _file_text(repo_root, thermal_policy_rel)
    for token in (
        "therm.policy.default",
        "therm.policy.rank_strict",
        "therm.policy.none",
    ):
        if token in thermal_policy_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=thermal_policy_rel,
                line_number=1,
                snippet=token,
                message="thermal policy registry must include explicit optional/null policy coverage for deterministic null-boot safety",
                rule_id="INV-THERM-POLICIES-OPTIONAL",
            )
        )

    runtime_files = (
        "tools/xstack/sessionx/creator.py",
        "tools/xstack/sessionx/runner.py",
        "tools/xstack/sessionx/process_runtime.py",
    )
    for rel_path in runtime_files:
        text = _file_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if "therm.policy.default" not in snippet:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="runtime must not force mandatory thermal policy at boot; thermal policy remains optional",
                    rule_id="INV-THERM-POLICIES-OPTIONAL",
                )
            )
            break

    power_engine_rel = "src/electric/power_network_engine.py"
    power_engine_text = _file_text(repo_root, power_engine_rel)
    for token in ("quantity.thermal.heat_loss_stub", "effect.temperature_increase_local"):
        if token in power_engine_text:
            continue
        findings.append(
            _finding(
                severity=strict_severity,
                file_path=power_engine_rel,
                line_number=1,
                snippet=token,
                message="electrical dissipation pathways should map loss outputs to thermal quantity/effect conventions",
                rule_id="INV-LOSS-MAPPED-TO-HEAT",
            )
        )

    thermal_engine_rel = "src/thermal/network/thermal_network_engine.py"
    thermal_engine_text = _file_text(repo_root, thermal_engine_rel)
    for token in ("evaluate_model_bindings(", "solve_thermal_network_t1(", "solve_thermal_network_t0("):
        if token in thermal_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=thermal_engine_rel,
                line_number=1,
                snippet=token,
                message="thermal network solve must remain model-driven with deterministic T1/T0 downgrade path",
                rule_id="INV-THERM-MODEL-ONLY",
            )
        )

    model_engine_rel = "src/models/model_engine.py"
    model_engine_text = _file_text(repo_root, model_engine_rel)
    for token in ("model_type.therm_ambient_exchange", "model_type.therm_radiator_exchange"):
        if token in model_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=model_engine_rel,
                line_number=1,
                snippet=token,
                message="ambient/radiator exchange must be declared and dispatched via constitutive model types",
                rule_id="INV-THERM-AMBIENT-THROUGH-MODEL",
            )
        )
    for token in ("model_type.therm_phase_transition", "model_type.therm_cure_progress"):
        if token in model_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=model_engine_rel,
                line_number=1,
                snippet=token,
                message="THERM phase/cure behavior must be declared in constitutive models and dispatched through model engine",
                rule_id="INV-PHASE-CHANGE-MODEL-ONLY",
            )
        )
    for token in ("model_type.therm_ignite_stub", "model_type.therm_combust_stub"):
        if token in model_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=model_engine_rel,
                line_number=1,
                snippet=token,
                message="THERM fire ignition/combustion logic must be declared and dispatched through constitutive model types",
                rule_id="INV-FIRE-MODEL-ONLY",
            )
        )
    for token in ("max_fire_spread_per_tick", "fire_iteration_limit", "spread_cap_reached"):
        if token in thermal_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=thermal_engine_rel,
                line_number=1,
                snippet=token,
                message="fire spread evaluation must be deterministically bounded in thermal network solve",
                rule_id="INV-FIRE-MODEL-ONLY",
            )
        )
    thermal_stress_tool_rel = "tools/thermal/tool_run_therm_stress.py"
    thermal_stress_tool_text = _file_text(repo_root, thermal_stress_tool_rel)
    for token in (
        "max_cost_units_per_tick",
        "remaining_budget",
        "solve_thermal_network_t1(",
        "solve_thermal_network_t0(",
    ):
        if token in thermal_stress_tool_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=thermal_stress_tool_rel,
                line_number=1,
                snippet=token,
                message="thermal stress execution must enforce deterministic budget envelopes and explicit T1/T0 downgrade paths",
                rule_id="INV-THERM-BUDGETED",
            )
        )
    for token in (
        "control_decision_log",
        "thermal_degradation_event_rows",
        "degrade.therm",
    ):
        if token in thermal_stress_tool_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=thermal_stress_tool_rel,
                line_number=1,
                snippet=token,
                message="thermal degradation decisions must be explicit and logged in deterministic decision/event streams",
                rule_id="INV-THERM-DEGRADE-LOGGED",
            )
        )
    proof_bundle_rel = "src/control/proof/control_proof_bundle.py"
    proof_bundle_text = _file_text(repo_root, proof_bundle_rel)
    for token in (
        "heat_input_hash_chain",
        "thermal_heat_input_log_rows",
    ):
        if token in thermal_stress_tool_text or token in proof_bundle_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=thermal_stress_tool_rel,
                line_number=1,
                snippet=token,
                message="thermal heat inputs must be logged and hash-chained for replay/proof auditability",
                rule_id="INV-HEAT_INPUTS-LOGGED",
            )
        )
    for token in (
        "_cooling_binding_rows(",
        "_apply_boundary_exchange_outputs(",
        "model.therm_ambient_exchange",
        "model.therm_radiator_exchange",
    ):
        if token in thermal_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=thermal_engine_rel,
                line_number=1,
                snippet=token,
                message="thermal ambient and radiator exchange must flow through model bindings and deterministic output application",
                rule_id="INV-THERM-AMBIENT-THROUGH-MODEL",
            )
        )

    cooling_pattern = re.compile(
        r"\b(?:ambient_coupling_coefficient|forced_cooling_multiplier|radiator_profile_id|heat_exchange)\b[^\n]*(?:=|\.append\(|\.extend\()",
        re.IGNORECASE,
    )
    cooling_scan_prefixes = ("src/", "tools/xstack/sessionx/")
    cooling_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    cooling_allowed_files = {
        thermal_engine_rel,
        model_engine_rel,
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(cooling_scan_prefixes):
            continue
        if rel_norm.startswith(cooling_skip_prefixes):
            continue
        if rel_norm in cooling_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not cooling_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="cooling/ambient coupling logic appears outside canonical thermal model pathways",
                    rule_id="INV-NO-ADHOC-COOLING",
                )
            )
            break

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _file_text(repo_root, runtime_rel)
    for token in (
        "elif process_id == \"process.start_fire\":",
        "elif process_id == \"process.fire_tick\":",
        "elif process_id == \"process.end_fire\":",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="fire state transitions must execute through explicit deterministic process handlers",
                rule_id="INV-FIRE-MODEL-ONLY",
            )
        )
    for token in (
        "elif process_id == \"process.material_transform_phase\":",
        "elif process_id == \"process.cure_state_tick\":",
        "_load_material_phase_registry(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="phase transition and cure progression must execute through explicit deterministic process handlers",
                rule_id="INV-NO-ADHOC-CURE-LOGIC",
            )
        )

    phase_cure_pattern = re.compile(
        r"\b(?:phase_tag|cure_progress|cure_temp_min|cure_temp_max)\b[^\n]*(?:=|\.append\(|\.extend\()",
        re.IGNORECASE,
    )
    phase_cure_allowed_files = {
        "src/models/model_engine.py",
        "src/thermal/network/thermal_network_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/repox/check.py",
    }
    phase_cure_scan_prefixes = ("src/", "tools/xstack/sessionx/")
    phase_cure_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(phase_cure_scan_prefixes):
            continue
        if rel_norm.startswith(phase_cure_skip_prefixes):
            continue
        if rel_norm in phase_cure_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not phase_cure_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="phase/cure state mutation appears outside canonical model/process handlers",
                rule_id="INV-NO-ADHOC-CURE-LOGIC",
            )
        )
            break

    burn_pattern = re.compile(
        r"\b(?:fire|ignition|combust|fuel_remaining|spread_threshold|heat_release_rate)\b[^\n]*(?:=|\.append\(|\.extend\()",
        re.IGNORECASE,
    )
    burn_allowed_files = {
        "src/models/model_engine.py",
        "src/thermal/network/thermal_network_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
        "src/inspection/inspection_engine.py",
        "tools/xstack/repox/check.py",
    }
    burn_scan_prefixes = ("src/", "tools/xstack/sessionx/")
    burn_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(burn_scan_prefixes):
            continue
        if rel_norm.startswith(burn_skip_prefixes):
            continue
        if rel_norm in burn_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not burn_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="fire/combustion state mutation appears outside canonical thermal model/process handlers",
                    rule_id="INV-NO-ADHOC-BURN-LOGIC",
                )
            )
            break

    mutation_pattern = re.compile(
        r"\bstate\s*\[\s*[\"'](?:temperature|field\.temperature|thermal_)[^\"']*[\"']\s*\]\s*=",
        re.IGNORECASE,
    )
    scan_prefixes = (
        "src/",
        "tools/xstack/sessionx/",
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        thermal_engine_rel,
        "src/fields/field_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not mutation_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="temperature writes must go through thermal model/process paths only",
                    rule_id="INV-NO-DIRECT-TEMP-MUTATION",
                )
            )
            break


def _append_cross_domain_mutation_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    scan_specs = (
        {
            "root": "src/electric/",
            "pattern": re.compile(
                r"\bstate\s*\[\s*[\"'](?:temperature|field\.temperature|thermal_|heat_)[^\"']*[\"']\s*\]\s*=",
                re.IGNORECASE,
            ),
            "allowed": {
                "src/electric/power_network_engine.py",
                "src/models/model_engine.py",
                "tools/xstack/repox/check.py",
            },
            "message": "ELEC must not directly mutate THERM state; use constitutive model outputs + effect/hazard/process pathways",
        },
        {
            "root": "src/thermal/",
            "pattern": re.compile(
                r"\bstate\s*\[\s*[\"'](?:stress|strain|joint|fracture|failure|mech\.)[^\"']*[\"']\s*\]\s*=",
                re.IGNORECASE,
            ),
            "allowed": {
                "src/thermal/network/thermal_network_engine.py",
                "src/models/model_engine.py",
                "tools/xstack/repox/check.py",
            },
            "message": "THERM must not directly mutate MECH state; couple through constitutive model outputs and process/effect/hazard channels",
        },
        {
            "root": "src/fluid/",
            "pattern": re.compile(
                r"\bstate\s*\[\s*[\"'](?:temperature|thermal_|stress|strain|breaker|fault|signal_)[^\"']*[\"']\s*\]\s*=",
                re.IGNORECASE,
            ),
            "allowed": {
                "src/models/model_engine.py",
                "tools/xstack/repox/check.py",
            },
            "message": "FLUID cross-domain writes must be model-mediated; direct mutation of foreign-domain truth is forbidden",
        },
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    for spec in scan_specs:
        root = str(spec.get("root", ""))
        if not root:
            continue
        pattern = spec.get("pattern")
        if not isinstance(pattern, re.Pattern):
            continue
        allowed_files = set(spec.get("allowed") or set())
        message = str(spec.get("message", "")).strip() or "cross-domain mutation must remain model-mediated"
        for rel_path in _scan_files(repo_root):
            rel_norm = _norm(rel_path)
            if not rel_norm.endswith(".py"):
                continue
            if not rel_norm.startswith(root):
                continue
            if rel_norm.startswith(skip_prefixes):
                continue
            if rel_norm in allowed_files:
                continue
            for line_no, line in _iter_lines(repo_root, rel_norm):
                snippet = str(line).strip()
                if (not snippet) or snippet.startswith("#"):
                    continue
                if not pattern.search(snippet):
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message=message,
                        rule_id="INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL",
                    )
                )
                break


def _append_loss_target_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    power_engine_rel = "src/electric/power_network_engine.py"
    power_engine_text = _file_text(repo_root, power_engine_rel)
    for token in ("quantity.thermal.heat_loss_stub", "effect.temperature_increase_local"):
        if token in power_engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=power_engine_rel,
                line_number=1,
                snippet=token,
                message="loss pathways must declare explicit heat quantity/effect target",
                rule_id="INV-LOSS-MAPPED-TO-HEAT",
            )
        )

    loss_assignment_pattern = re.compile(
        r"\b(?:loss_p|line_loss|heat_loss|dissipated_loss|resistance_proxy|loss_permille)\b\s*=",
        re.IGNORECASE,
    )
    scan_prefixes = ("src/electric/", "src/thermal/")
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        power_engine_rel,
        "src/thermal/network/thermal_network_engine.py",
        "src/models/model_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not loss_assignment_pattern.search(snippet):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="loss source must declare explicit target quantity/effect (heat_loss or temperature effect)",
                    rule_id="INV-LOSS-MAPPED-TO-HEAT",
                )
            )
            break


def _append_energy_ledger_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    transform_rule_id = "INV-ENERGY-TRANSFORM-REGISTERED"
    mutation_rule_id = "INV-NO-DIRECT-ENERGY-MUTATION"
    registry_rel = "data/registries/energy_transformation_registry.json"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    engine_rel = "src/physics/energy/energy_ledger_engine.py"

    payload, payload_error = _load_json_object(repo_root, registry_rel)
    rows = list(payload.get("energy_transformations") or [])
    if not rows:
        rows = list((dict(payload.get("record") or {})).get("energy_transformations") or [])
    registered_transforms = set(
        str(row.get("transformation_id", "")).strip()
        for row in list(rows or [])
        if isinstance(row, dict) and str(row.get("transformation_id", "")).strip()
    )
    if payload_error or not registered_transforms:
        findings.append(
            _finding(
                severity=severity,
                file_path=registry_rel,
                line_number=1,
                snippet="energy_transformations",
                message="energy transformation registry is missing or empty; PHYS-3 transform routing cannot be enforced",
                rule_id=transform_rule_id,
            )
        )
    else:
        required_transform_ids = (
            "transform.kinetic_to_thermal",
            "transform.electrical_to_thermal",
            "transform.chemical_to_thermal",
            "transform.potential_to_kinetic",
            "transform.external_irradiance",
        )
        for transform_id in required_transform_ids:
            if transform_id in registered_transforms:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=registry_rel,
                    line_number=1,
                    snippet=transform_id,
                    message="required PHYS-3 energy transformation id is missing",
                    rule_id=transform_rule_id,
                )
            )

    runtime_text = _file_text(repo_root, runtime_rel)
    required_runtime_tokens = (
        "_record_energy_transformation_in_state(",
        "_record_boundary_flux_event_in_state(",
        "energy_ledger_hash_chain",
        "boundary_flux_hash_chain",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="energy ledger runtime integration token is missing",
                rule_id=transform_rule_id,
            )
        )

    engine_text = _file_text(repo_root, engine_rel)
    engine_required_tokens = (
        "record_energy_transformation(",
        "evaluate_energy_balance(",
        "build_energy_ledger_entry(",
        "build_boundary_flux_event(",
    )
    for token in engine_required_tokens:
        if token in engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=engine_rel,
                line_number=1,
                snippet=token,
                message="energy ledger engine helper token is missing",
                rule_id=transform_rule_id,
            )
        )

    transform_literal_pattern = re.compile(
        r"transformation_id\s*=\s*[\"'](transform\.[A-Za-z0-9_.-]+)[\"']",
        re.IGNORECASE,
    )
    scan_prefixes = ("src/", "tools/xstack/sessionx/")
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            match = transform_literal_pattern.search(snippet)
            if not match:
                continue
            transform_id = str(match.group(1) or "").strip()
            if (not transform_id) or transform_id in registered_transforms:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="energy transformation id is not registered: {}".format(transform_id),
                    rule_id=transform_rule_id,
                )
            )
            break

    direct_energy_write_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']energy_quantity_totals[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\[\s*[\"']quantity\.energy_[A-Za-z0-9_]+[\"']\s*\]\s*[+\-*/]?=", re.IGNORECASE),
    )
    mutation_scan_prefixes = ("src/", "tools/xstack/sessionx/")
    mutation_skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    mutation_allowed_files = {
        runtime_rel,
        engine_rel,
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(mutation_scan_prefixes):
            continue
        if rel_norm.startswith(mutation_skip_prefixes):
            continue
        if rel_norm in mutation_allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in direct_energy_write_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="direct energy mutation detected outside PHYS-3 energy ledger runtime pathways",
                    rule_id=mutation_rule_id,
                )
            )
            break


def _append_entropy_policy_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    update_rule_id = "INV-ENTROPY-UPDATE-THROUGH-ENGINE"
    efficiency_rule_id = "INV-NO-SILENT-EFFICIENCY-DROP"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    engine_rel = "src/physics/entropy/entropy_engine.py"
    contribution_registry_rel = "data/registries/entropy_contribution_registry.json"
    effect_registry_rel = "data/registries/entropy_effect_policy_registry.json"

    contribution_payload, contribution_error = _load_json_object(repo_root, contribution_registry_rel)
    contribution_rows = list(contribution_payload.get("entropy_contributions") or [])
    if not contribution_rows:
        contribution_rows = list((dict(contribution_payload.get("record") or {})).get("entropy_contributions") or [])
    contribution_ids = set(
        str(row.get("contribution_id", "")).strip()
        for row in list(contribution_rows or [])
        if isinstance(row, dict) and str(row.get("contribution_id", "")).strip()
    )
    if contribution_error or not contribution_ids:
        findings.append(
            _finding(
                severity=severity,
                file_path=contribution_registry_rel,
                line_number=1,
                snippet="entropy_contributions",
                message="entropy contribution registry is missing or empty",
                rule_id=update_rule_id,
            )
        )
    else:
        required_contribution_ids = {
            "entropy.from_friction",
            "entropy.from_combustion",
            "entropy.from_plastic_deformation",
            "entropy.from_phase_change_stub",
        }
        for contribution_id in sorted(required_contribution_ids):
            if contribution_id in contribution_ids:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=contribution_registry_rel,
                    line_number=1,
                    snippet=contribution_id,
                    message="required PHYS-4 entropy contribution id is missing",
                    rule_id=update_rule_id,
                )
            )

    effect_payload, effect_error = _load_json_object(repo_root, effect_registry_rel)
    effect_rows = list(effect_payload.get("entropy_effect_policies") or [])
    if not effect_rows:
        effect_rows = list((dict(effect_payload.get("record") or {})).get("entropy_effect_policies") or [])
    effect_ids = set(
        str(row.get("policy_id", "")).strip()
        for row in list(effect_rows or [])
        if isinstance(row, dict) and str(row.get("policy_id", "")).strip()
    )
    if effect_error or not effect_ids:
        findings.append(
            _finding(
                severity=severity,
                file_path=effect_registry_rel,
                line_number=1,
                snippet="entropy_effect_policies",
                message="entropy effect policy registry is missing or empty",
                rule_id=update_rule_id,
            )
        )
    else:
        required_effect_ids = {
            "entropy_effect.basic_linear",
            "entropy_effect.none",
            "entropy_effect.strict",
        }
        for policy_id in sorted(required_effect_ids):
            if policy_id in effect_ids:
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=effect_registry_rel,
                    line_number=1,
                    snippet=policy_id,
                    message="required PHYS-4 entropy effect policy id is missing",
                    rule_id=update_rule_id,
                )
            )

    runtime_text = _file_text(repo_root, runtime_rel)
    runtime_required_tokens = (
        "_record_entropy_contribution_in_state(",
        "_apply_entropy_reset_in_state(",
        "entropy_hash_chain",
        "entropy_reset_events_hash_chain",
        "evaluate_entropy_effects(",
        "process.decay_tick",
    )
    for token in runtime_required_tokens:
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="entropy runtime integration token is missing",
                rule_id=update_rule_id,
            )
        )

    engine_text = _file_text(repo_root, engine_rel)
    engine_required_tokens = (
        "record_entropy_contribution(",
        "apply_entropy_reset(",
        "evaluate_entropy_effects(",
    )
    for token in engine_required_tokens:
        if token in engine_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=engine_rel,
                line_number=1,
                snippet=token,
                message="entropy engine helper token is missing",
                rule_id=update_rule_id,
            )
        )

    direct_entropy_write_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']entropy_state_rows[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']entropy_event_rows[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']entropy_reset_events[\"']\s*\]\s*=", re.IGNORECASE),
    )
    scan_prefixes = ("src/", "tools/xstack/sessionx/")
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        runtime_rel,
        "src/physics/entropy/entropy_engine.py",
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in direct_entropy_write_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="entropy mutation detected outside PHYS-4 entropy runtime pathways",
                    rule_id=update_rule_id,
                )
            )
            break

    silent_drop_tokens = ("backlog_penalty", "wear_penalty")
    for token in silent_drop_tokens:
        if token not in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="inline maintenance degradation token indicates entropy policy bypass",
                rule_id=efficiency_rule_id,
            )
        )
    if "maintenance_degradation" in runtime_text and "evaluate_entropy_effects(" not in runtime_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet="evaluate_entropy_effects(",
                message="maintenance degradation effects must be entropy-policy evaluated",
                rule_id=efficiency_rule_id,
            )
        )


def _append_constitutive_model_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    severity = _strict_only_severity(profile)
    deprecated_sites = _deprecated_inline_response_curve_sites(repo_root)

    constitution_rel = "docs/meta/CONSTITUTIVE_MODEL_CONSTITUTION.md"
    catalog_rel = "docs/meta/CONSTITUTIVE_MODEL_CATALOG.md"
    for rel_path in (constitution_rel, catalog_rel):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=1,
                snippet="",
                message="constitutive model governance docs missing; realism response curves cannot be centrally registered",
                rule_id="INV-REALISM-DETAIL-MUST-BE-MODEL",
            )
        )

    inline_response_patterns = (
        re.compile(
            r"\b(?:threshold|multiplier|attenuation|friction|wear|drift|derail|curve|coefficient|ratio)\w*\b\s*=\s*[^#\n]*(?:\*|/|\+|-|min\(|max\(|clamp)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bif\b[^\n]*(?:friction|wear|attenuation|curvature|threshold|ratio|temperature|moisture|wind|radiation)\b[^\n]*(?:>=|<=|>|<)",
            re.IGNORECASE,
        ),
    )
    scan_prefixes = (
        "src/fields/",
        "src/mobility/",
        "src/signals/",
        "src/mechanics/",
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in inline_response_patterns):
                continue
            if (rel_norm, line_no) in deprecated_sites:
                break
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="realism detail response logic must be registered as a constitutive model or mapped in deprecation registry",
                    rule_id="INV-REALISM-DETAIL-MUST-BE-MODEL",
                )
            )
            break


def _append_model_output_process_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    del profile
    severity = "warn"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _file_text(repo_root, runtime_rel)
    required_tokens = (
        "elif process_id == \"process.model_evaluate_tick\":",
        "elif process_id == \"process.hazard_increment\":",
        "elif process_id == \"process.flow_adjust\":",
        "_persist_model_state(",
        "evaluate_model_bindings(",
    )
    for token in required_tokens:
        if token in runtime_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet=token,
                message="constitutive model outputs must flow through process handlers with deterministic persistence",
                rule_id="INV-MODEL-OUTPUTS-PROCESS-ONLY",
            )
        )

    bypass_patterns = (
        re.compile(
            r"\bmodel_(?:bindings|evaluation_results|cache_rows|hazard_rows|flow_adjustment_rows)\b[^\n]*(?:=|\.append\(|\.extend\(|\.pop\()",
            re.IGNORECASE,
        ),
    )
    scan_prefixes = ("src/", "tools/xstack/sessionx/")
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "src/models/model_engine.py",
        runtime_rel,
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(scan_prefixes):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in bypass_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="constitutive model state/output mutations must be handled by model output process handlers",
                    rule_id="INV-MODEL-OUTPUTS-PROCESS-ONLY",
                )
            )
            break


def _append_signal_transport_invariant_findings(
    findings: List[Dict[str, object]],
    repo_root: str,
    profile: str,
) -> None:
    del profile
    severity = "warn"

    transport_rel = "src/signals/transport/transport_engine.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    transport_text = _file_text(repo_root, transport_rel)
    runtime_text = _file_text(repo_root, runtime_rel)

    required_tokens = (
        "def process_signal_send(",
        "def process_signal_transport_tick(",
        "def process_knowledge_acquire(",
        "enqueue_signal_envelope(",
        "tick_signal_transport(",
        "build_knowledge_receipt(",
        "resolve_address_recipients(",
        "normalize_info_artifact_rows(",
    )
    for token in required_tokens:
        if token in transport_text:
            continue
        findings.append(
            _finding(
                severity=severity,
                file_path=transport_rel,
                line_number=1,
                snippet=token,
                message="signal communication must route through deterministic transport and receipt process helpers",
                rule_id="INV-SIGNAL-TRANSPORT-ONLY",
            )
        )

    if "query_route_result(" not in transport_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=transport_rel,
                line_number=1,
                snippet="query_route_result(",
                message="signal routing must use ABS routing engine query_route_result(...)",
                rule_id="INV-SIGNALS-USE-ABS-ROUTING",
            )
        )
    if "execute_channel_transport_tick(" not in transport_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=transport_rel,
                line_number=1,
                snippet="execute_channel_transport_tick(",
                message="signal channel capacity/delay logic must be centralized through channel executor",
                rule_id="INV-NO-ADHOC-CAPACITY-LOGIC",
            )
        )
    if "loss_policy_rows_by_id(" not in transport_text or "attenuation_policy_rows_by_id(" not in transport_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=transport_rel,
                line_number=1,
                snippet="loss_policy_rows_by_id/attenuation_policy_rows_by_id",
                message="signal quality must resolve loss and attenuation from registered policy registries",
                rule_id="INV-LOSS-POLICY-REGISTERED",
            )
        )
    channel_executor_rel = "src/signals/transport/channel_executor.py"
    channel_executor_text = _file_text(repo_root, channel_executor_rel)
    if "loss_rows_by_id.get(loss_policy_id" not in channel_executor_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=channel_executor_rel,
                line_number=1,
                snippet="loss_rows_by_id.get(loss_policy_id",
                message="channel executor must evaluate delivery outcomes from registered loss policies only",
                rule_id="INV-LOSS-POLICY-REGISTERED",
            )
        )
    if "process_knowledge_acquire(" not in transport_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=transport_rel,
                line_number=1,
                snippet="process_knowledge_acquire(",
                message="knowledge acquisition requires receipt process mediation",
                rule_id="INV-RECEIPT-REQUIRED-FOR-KNOWLEDGE",
            )
        )
    if "_has_direct_route(" in transport_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=transport_rel,
                line_number=1,
                snippet="_has_direct_route(",
                message="direct edge routing helpers are forbidden; use ABS route queries",
                rule_id="INV-SIGNALS-USE-ABS-ROUTING",
            )
        )

    runtime_tokens = (
        'process_id == "process.signal_send"',
        'process_id == "process.signal_transport_tick"',
        'process_id == "process.knowledge_acquire"',
    )
    if runtime_text and (not all(token in runtime_text for token in runtime_tokens)):
        findings.append(
            _finding(
                severity=severity,
                file_path=runtime_rel,
                line_number=1,
                snippet="process.signal_send/process.signal_transport_tick/process.knowledge_acquire",
                message="authoritative runtime should expose SIG transport process hooks to prevent direct message bypasses",
                rule_id="INV-SIGNAL-TRANSPORT-ONLY",
            )
        )

    direct_knowledge_patterns = (
        re.compile(r"\bstate\s*\[\s*[\"']knowledge_receipts[\"']\s*\]\s*=", re.IGNORECASE),
        re.compile(r"\bknowledge_receipts\s*\.append\s*\(", re.IGNORECASE),
        re.compile(r"\bsubject_knowledge\b\s*=", re.IGNORECASE),
    )
    direct_message_patterns = (
        re.compile(r"\b(?:inbox|mailbox|message_queue)\b\s*\.append\s*\(", re.IGNORECASE),
        re.compile(r"\b(?:inbox|mailbox|message_queue)\b\s*\[", re.IGNORECASE),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        transport_rel,
        runtime_rel,
        "tools/xstack/repox/check.py",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm.startswith(skip_prefixes):
            continue
        if rel_norm in allowed_files:
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if any(pattern.search(snippet) for pattern in direct_knowledge_patterns):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="knowledge receipt mutation must be process-mediated through SIG transport flow",
                        rule_id="INV-NO-DIRECT-KNOWLEDGE-TRANSFER",
                    )
                )
                break
            if any(pattern.search(snippet) for pattern in direct_message_patterns):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="artifact/message delivery bypasses deterministic SIG queue execution",
                        rule_id="INV-NO-DIRECT-ARTIFACT-DELIVERY",
                    )
                )
                break

    adhoc_capacity_patterns = (
        re.compile(r"\bcapacity_per_tick\b", re.IGNORECASE),
        re.compile(r"\bremaining_delay_ticks\b", re.IGNORECASE),
        re.compile(r"\bpath_edge_ids\b", re.IGNORECASE),
    )
    adhoc_capacity_allow = {
        "src/signals/transport/transport_engine.py",
        "src/signals/transport/channel_executor.py",
        "tools/xstack/repox/check.py",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith("src/signals/"):
            continue
        if any(rel_norm == allow or rel_norm.startswith(allow) for allow in adhoc_capacity_allow):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in adhoc_capacity_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="signal capacity/delay queue logic must execute only in SIG channel executor",
                    rule_id="INV-NO-ADHOC-CAPACITY-LOGIC",
                )
            )
            break

    receipt_required_allow = {
        transport_rel,
        runtime_rel,
        "tools/xstack/repox/check.py",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
    }
    receipt_bypass_patterns = (
        re.compile(r"\bknowledge_receipt_rows\s*=", re.IGNORECASE),
        re.compile(r"\bbuild_knowledge_receipt\s*\(", re.IGNORECASE),
        re.compile(r"\bprocess_knowledge_acquire\s*\(", re.IGNORECASE),
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if any(rel_norm == allow or rel_norm.startswith(allow) for allow in receipt_required_allow):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in receipt_bypass_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="knowledge changes must be coupled to SIG receipt process path",
                    rule_id="INV-RECEIPT-REQUIRED-FOR-KNOWLEDGE",
                )
            )
            break

    direct_drop_patterns = (
        re.compile(r"\bdelivery_state\s*=\s*[\"']lost[\"']", re.IGNORECASE),
        re.compile(r"\breturn\s+[\"']lost[\"']", re.IGNORECASE),
        re.compile(r"\bstatus\s*=\s*[\"']lost[\"']", re.IGNORECASE),
    )
    direct_drop_allow = {
        transport_rel,
        channel_executor_rel,
        "tools/xstack/repox/check.py",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
    }
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith("src/"):
            continue
        if any(rel_norm == allow or rel_norm.startswith(allow) for allow in direct_drop_allow):
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in direct_drop_patterns):
                continue
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_norm,
                    line_number=line_no,
                    snippet=snippet[:140],
                    message="message drop/lost transitions must be centralized in SIG transport quality policies",
                    rule_id="INV-NO-DIRECT-MESSAGE-DROP",
                )
            )
            break

    trust_engine_rel = "src/signals/trust/trust_engine.py"
    trust_engine_text = _file_text(repo_root, trust_engine_rel)
    if "def process_trust_update(" not in trust_engine_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=trust_engine_rel,
                line_number=1,
                snippet="def process_trust_update(",
                message="trust updates must be process-mediated through process.trust_update",
                rule_id="INV-VERIFICATION-PROCESS-ONLY",
            )
        )
    if "def process_message_verify_claim(" not in trust_engine_text:
        findings.append(
            _finding(
                severity=severity,
                file_path=trust_engine_rel,
                line_number=1,
                snippet="def process_message_verify_claim(",
                message="verification must run through process.message_verify_claim before trust mutation",
                rule_id="INV-VERIFICATION-PROCESS-ONLY",
            )
        )

    if ("truth_verification_state" in trust_engine_text) and ("allow_truth_observer" not in trust_engine_text):
        findings.append(
            _finding(
                severity=severity,
                file_path=trust_engine_rel,
                line_number=1,
                snippet="truth_verification_state",
                message="truth-linked verification inputs require explicit entitlement gate",
                rule_id="INV-NO-OMNISCIENT-TRUST-UPDATES",
            )
        )

    omniscient_truth_patterns = (
        re.compile(r"\btruth_model\b", re.IGNORECASE),
        re.compile(r"\buniverse_state\b", re.IGNORECASE),
        re.compile(r"\bground_truth\b", re.IGNORECASE),
    )
    verification_process_patterns = (
        re.compile(r"\bprocess_message_verify_claim\s*\(", re.IGNORECASE),
        re.compile(r"\bprocess_trust_update\s*\(", re.IGNORECASE),
        re.compile(r"\bbuild_verification_result\s*\(", re.IGNORECASE),
    )
    verification_allow_prefixes = (
        "src/signals/trust/",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
    )
    for rel_path in _scan_files(repo_root):
        rel_norm = _norm(rel_path)
        if not rel_norm.endswith(".py"):
            continue
        if not rel_norm.startswith(("src/", "tools/xstack/sessionx/")):
            continue
        if rel_norm == "tools/xstack/repox/check.py":
            continue
        for line_no, line in _iter_lines(repo_root, rel_norm):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if any(pattern.search(snippet) for pattern in omniscient_truth_patterns):
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="trust/belief updates must not depend on omniscient truth symbols",
                        rule_id="INV-NO-OMNISCIENT-TRUST-UPDATES",
                    )
                )
                break
            if any(pattern.search(snippet) for pattern in verification_process_patterns):
                if any(rel_norm.startswith(prefix) for prefix in verification_allow_prefixes):
                    continue
                findings.append(
                    _finding(
                        severity=severity,
                        file_path=rel_norm,
                        line_number=line_no,
                        snippet=snippet[:140],
                        message="verification/trust transitions must be centralized in SIG trust process helpers",
                        rule_id="INV-VERIFICATION-PROCESS-ONLY",
                    )
                )
                break


def run_repox_check(repo_root: str, profile: str) -> Dict[str, object]:
    token = str(profile or "").strip().upper() or "FAST"
    files = _scan_files(repo_root)
    findings: List[Dict[str, object]] = []

    for rel_path in files:
        for line_no, line in _iter_lines(repo_root, rel_path):
            _append_forbidden_identifier_findings(findings, rel_path, line_no, line, token)
            _append_mode_flag_findings(findings, rel_path, line_no, line, token)
            _append_reserved_misuse_findings(findings, rel_path, line_no, line, token)
            _append_domain_token_hardcode_findings(findings, rel_path, line_no, line, token)
            _append_contract_token_hardcode_findings(findings, rel_path, line_no, line, token)
            _append_constraint_hardcode_findings(findings, rel_path, line_no, line, token)
            _append_strict_placeholder_findings(findings, rel_path, line_no, line, token)
            _append_renderer_truth_boundary_findings(findings, rel_path, line_no, line, token)
    _append_session_pipeline_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_multiplayer_contract_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_ranked_governance_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_hidden_ban_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_reality_profile_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_phys_profile_declared_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_conservation_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_dimension_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_taxonomy_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_structure_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_logistics_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_construction_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_maintenance_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_materialization_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_commitment_reenactment_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_material_scale_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_core_abstraction_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_retro_consistency_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_deprecation_framework_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_topology_map_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_time_constitution_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_tier_transition_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_performance_constitution_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_interaction_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_domain_control_registered_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_action_grammar_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_info_grammar_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_meta_contract_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_affordance_matrix_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_platform_renderer_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_control_ir_enforcement_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_negotiation_kernel_enforcement_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_fidelity_engine_enforcement_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_plan_execution_enforcement_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_capability_enforcement_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_effect_system_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_specsheet_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_formalization_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_mechanics_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_field_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_field_generalization_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_mobility_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_thermal_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_cross_domain_mutation_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_loss_target_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_energy_ledger_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_entropy_policy_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_unregistered_quantity_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_electric_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_safety_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_constitutive_model_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_model_output_process_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_signal_transport_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_boundary_blocker_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_domain_foundation_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_worldgen_constraint_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_derived_provenance_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_auditx_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_ci_lane_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_regression_lock_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_cross_system_matrix_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_status_now_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_representation_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )
    _append_negative_invariant_findings(
        findings=findings,
        repo_root=repo_root,
        profile=token,
    )

    ordered = sorted(
        findings,
        key=lambda row: (
            _severity_rank(str(row.get("severity", ""))),
            str(row.get("file_path", "")),
            int(row.get("line_number", 0) or 0),
            str(row.get("rule_id", "")),
            str(row.get("message", "")),
        ),
    )
    status = _status_from_findings(ordered)
    message = "repox scan {} (files={}, findings={})".format(
        "passed" if status == "pass" else "completed_with_findings",
        len(files),
        len(ordered),
    )
    return {
        "status": status,
        "message": message,
        "findings": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic RepoX minimal policy checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_repox_check(repo_root=repo_root, profile=str(args.profile))
    print(json.dumps(result, indent=2, sort_keys=True))
    status = str(result.get("status", "error"))
    if status == "pass":
        return 0
    if status == "refusal":
        return 2
    if status == "fail":
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

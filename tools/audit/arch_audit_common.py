"""Deterministic ARCH-AUDIT-0 report helpers."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.stability import validate_all_registries, validate_pack_compat  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


ARCH_AUDIT_ID = "arch.audit.v1"
ARCH_AUDIT2_ID = "arch.audit.cross_layer.v1"
DEFAULT_REPORT_MD_REL = os.path.join("docs", "audit", "ARCH_AUDIT_REPORT.md")
DEFAULT_REPORT_JSON_REL = os.path.join("data", "audit", "arch_audit_report.json")
DEFAULT_BASELINE_DOC_REL = os.path.join("docs", "audit", "ARCH_AUDIT_BASELINE.md")
DEFAULT_AUDIT2_REPORT_MD_REL = os.path.join("docs", "audit", "ARCH_AUDIT2_REPORT.md")
DEFAULT_AUDIT2_REPORT_JSON_REL = os.path.join("data", "audit", "arch_audit2_report.json")
DEFAULT_AUDIT2_FINAL_DOC_REL = os.path.join("docs", "audit", "ARCH_AUDIT2_FINAL.md")
DEFAULT_NUMERIC_SCAN_REPORT_MD_REL = os.path.join("docs", "audit", "NUMERIC_SCAN_REPORT.md")
DEFAULT_CONCURRENCY_SCAN_REPORT_MD_REL = os.path.join("docs", "audit", "CONCURRENCY_SCAN_REPORT.md")
WORLDGEN_LOCK_DOC_REL = os.path.join("docs", "worldgen", "WORLDGEN_LOCK_v0_0_0.md")
WORLDGEN_LOCK_RETRO_AUDIT_REL = os.path.join("docs", "audit", "WORLDGEN_LOCK0_RETRO_AUDIT.md")
WORLDGEN_LOCK_REGISTRY_REL = os.path.join("data", "registries", "worldgen_lock_registry.json")
WORLDGEN_LOCK_BASELINE_SEED_REL = os.path.join("data", "baselines", "worldgen", "baseline_seed.txt")
WORLDGEN_LOCK_BASELINE_SNAPSHOT_REL = os.path.join("data", "baselines", "worldgen", "baseline_worldgen_snapshot.json")
WORLDGEN_LOCK_GENERATE_TOOL_REL = os.path.join("tools", "worldgen", "tool_generate_worldgen_baseline")
WORLDGEN_LOCK_GENERATE_TOOL_PY_REL = os.path.join("tools", "worldgen", "tool_generate_worldgen_baseline.py")
WORLDGEN_LOCK_VERIFY_TOOL_REL = os.path.join("tools", "worldgen", "tool_verify_worldgen_lock")
WORLDGEN_LOCK_VERIFY_TOOL_PY_REL = os.path.join("tools", "worldgen", "tool_verify_worldgen_lock.py")
WORLDGEN_LOCK_VERIFY_JSON_REL = os.path.join("data", "audit", "worldgen_lock_verify.json")
WORLDGEN_LOCK_VERIFY_DOC_REL = os.path.join("docs", "audit", "WORLDGEN_LOCK_VERIFY.md")
BASELINE_UNIVERSE_RETRO_AUDIT_REL = os.path.join("docs", "audit", "BASELINE_UNIVERSE0_RETRO_AUDIT.md")
BASELINE_UNIVERSE_DOC_REL = os.path.join("docs", "mvp", "BASELINE_UNIVERSE_v0_0_0.md")
BASELINE_UNIVERSE_INSTANCE_MANIFEST_REL = os.path.join("data", "baselines", "universe", "baseline_instance.manifest.json")
BASELINE_UNIVERSE_PACK_LOCK_REL = os.path.join("data", "baselines", "universe", "baseline_pack_lock.json")
BASELINE_UNIVERSE_PROFILE_BUNDLE_REL = os.path.join("data", "baselines", "universe", "baseline_profile_bundle.json")
BASELINE_UNIVERSE_SAVE_REL = os.path.join("data", "baselines", "universe", "baseline_save_0.save")
BASELINE_UNIVERSE_SNAPSHOT_REL = os.path.join("data", "baselines", "universe", "baseline_universe_snapshot.json")
BASELINE_UNIVERSE_GENERATE_TOOL_REL = os.path.join("tools", "mvp", "tool_generate_baseline_universe")
BASELINE_UNIVERSE_GENERATE_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_generate_baseline_universe.py")
BASELINE_UNIVERSE_VERIFY_TOOL_REL = os.path.join("tools", "mvp", "tool_verify_baseline_universe")
BASELINE_UNIVERSE_VERIFY_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_verify_baseline_universe.py")
BASELINE_UNIVERSE_VERIFY_JSON_REL = os.path.join("data", "audit", "baseline_universe_verify.json")
BASELINE_UNIVERSE_VERIFY_DOC_REL = os.path.join("docs", "audit", "BASELINE_UNIVERSE_VERIFY.md")
BASELINE_UNIVERSE_BASELINE_DOC_REL = os.path.join("docs", "audit", "BASELINE_UNIVERSE_BASELINE.md")
MVP_GAMEPLAY_RETRO_AUDIT_REL = os.path.join("docs", "audit", "MVP_GAMEPLAY0_RETRO_AUDIT.md")
MVP_GAMEPLAY_DOC_REL = os.path.join("docs", "mvp", "MVP_GAMEPLAY_LOOP_v0_0_0.md")
MVP_GAMEPLAY_SNAPSHOT_REL = os.path.join("data", "baselines", "gameplay", "gameplay_loop_snapshot.json")
MVP_GAMEPLAY_RUN_TOOL_REL = os.path.join("tools", "mvp", "tool_run_gameplay_loop")
MVP_GAMEPLAY_RUN_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_run_gameplay_loop.py")
MVP_GAMEPLAY_VERIFY_TOOL_REL = os.path.join("tools", "mvp", "tool_verify_gameplay_loop")
MVP_GAMEPLAY_VERIFY_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_verify_gameplay_loop.py")
MVP_GAMEPLAY_VERIFY_JSON_REL = os.path.join("data", "audit", "gameplay_verify.json")
MVP_GAMEPLAY_VERIFY_DOC_REL = os.path.join("docs", "audit", "MVP_GAMEPLAY_VERIFY.md")
MVP_GAMEPLAY_RUN_DOC_REL = os.path.join("docs", "audit", "MVP_GAMEPLAY_LOOP_RUN.md")
MVP_GAMEPLAY_BASELINE_DOC_REL = os.path.join("docs", "audit", "MVP_GAMEPLAY_BASELINE.md")
DISASTER_RETRO_AUDIT_REL = os.path.join("docs", "audit", "DISASTER_TEST0_RETRO_AUDIT.md")
DISASTER_MODEL_DOC_REL = os.path.join("docs", "mvp", "DISASTER_SUITE_MODEL_v0_0_0.md")
DISASTER_CASES_REL = os.path.join("data", "baselines", "disaster", "disaster_suite_cases.json")
DISASTER_GENERATE_TOOL_REL = os.path.join("tools", "mvp", "tool_generate_disaster_suite")
DISASTER_GENERATE_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_generate_disaster_suite.py")
DISASTER_RUN_TOOL_REL = os.path.join("tools", "mvp", "tool_run_disaster_suite")
DISASTER_RUN_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_run_disaster_suite.py")
DISASTER_RUN_JSON_REL = os.path.join("data", "audit", "disaster_suite_run.json")
DISASTER_RUN_DOC_REL = os.path.join("docs", "audit", "DISASTER_SUITE_RUN.md")
DISASTER_BASELINE_REL = os.path.join("data", "regression", "disaster_suite_baseline.json")
DISASTER_BASELINE_DOC_REL = os.path.join("docs", "audit", "DISASTER_SUITE_BASELINE.md")
ECOSYSTEM_VERIFY_RETRO_AUDIT_REL = os.path.join("docs", "audit", "ECOSYSTEM_VERIFY0_RETRO_AUDIT.md")
ECOSYSTEM_VERIFY_MODEL_DOC_REL = os.path.join("docs", "mvp", "ECOSYSTEM_VERIFY_MODEL_v0_0_0.md")
ECOSYSTEM_VERIFY_RUN_TOOL_REL = os.path.join("tools", "mvp", "tool_verify_ecosystem")
ECOSYSTEM_VERIFY_RUN_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_verify_ecosystem.py")
ECOSYSTEM_VERIFY_RUN_JSON_REL = os.path.join("data", "audit", "ecosystem_verify_run.json")
ECOSYSTEM_VERIFY_RUN_DOC_REL = os.path.join("docs", "audit", "ECOSYSTEM_VERIFY_RUN.md")
ECOSYSTEM_VERIFY_BASELINE_REL = os.path.join("data", "regression", "ecosystem_verify_baseline.json")
ECOSYSTEM_VERIFY_BASELINE_DOC_REL = os.path.join("docs", "audit", "ECOSYSTEM_VERIFY_BASELINE.md")
UPDATE_SIM_RETRO_AUDIT_REL = os.path.join("docs", "audit", "UPDATE_SIM0_RETRO_AUDIT.md")
UPDATE_SIM_MODEL_DOC_REL = os.path.join("docs", "release", "UPDATE_SIM_MODEL_v0_0_0.md")
UPDATE_SIM_BASELINE_INDEX_REL = os.path.join("data", "baselines", "update_sim", "release_index_baseline.json")
UPDATE_SIM_UPGRADE_INDEX_REL = os.path.join("data", "baselines", "update_sim", "release_index_upgrade.json")
UPDATE_SIM_YANKED_INDEX_REL = os.path.join("data", "baselines", "update_sim", "release_index_yanked.json")
UPDATE_SIM_STRICT_INDEX_REL = os.path.join("data", "baselines", "update_sim", "release_index_strict.json")
UPDATE_SIM_RUN_TOOL_REL = os.path.join("tools", "mvp", "tool_run_update_sim")
UPDATE_SIM_RUN_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_run_update_sim.py")
UPDATE_SIM_RUN_JSON_REL = os.path.join("data", "audit", "update_sim_run.json")
UPDATE_SIM_RUN_DOC_REL = os.path.join("docs", "audit", "UPDATE_SIM_RUN.md")
UPDATE_SIM_BASELINE_REL = os.path.join("data", "regression", "update_sim_baseline.json")
TRUST_STRICT_RETRO_AUDIT_REL = os.path.join("docs", "audit", "TRUST_STRICT0_RETRO_AUDIT.md")
TRUST_STRICT_MODEL_DOC_REL = os.path.join("docs", "security", "TRUST_STRICT_MODEL_v0_0_0.md")
TRUST_STRICT_RUN_TOOL_REL = os.path.join("tools", "security", "tool_run_trust_strict_suite")
TRUST_STRICT_RUN_TOOL_PY_REL = os.path.join("tools", "security", "tool_run_trust_strict_suite.py")
TRUST_STRICT_RUN_JSON_REL = os.path.join("data", "audit", "trust_strict_run.json")
TRUST_STRICT_RUN_DOC_REL = os.path.join("docs", "audit", "TRUST_STRICT_SUITE_RUN.md")
TRUST_STRICT_BASELINE_REL = os.path.join("data", "regression", "trust_strict_baseline.json")
TRUST_STRICT_BASELINE_DOC_REL = os.path.join("docs", "audit", "TRUST_STRICT_BASELINE.md")
TRUST_STRICT_UNSIGNED_RELEASE_INDEX_REL = os.path.join("data", "baselines", "trust", "unsigned_release_index.json")
TRUST_STRICT_SIGNED_RELEASE_INDEX_REL = os.path.join("data", "baselines", "trust", "signed_release_index.json")
TRUST_STRICT_UNSIGNED_PACK_REL = os.path.join("data", "baselines", "trust", "unsigned_official_pack.compat.json")
TRUST_STRICT_SIGNED_LICENSE_REL = os.path.join("data", "baselines", "trust", "signed_license_capability.json")
LICENSE_CAPABILITY_SCHEMA_REL = os.path.join("schema", "security", "license_capability_artifact.schema")
LICENSE_CAPABILITY_SCHEMA_JSON_REL = os.path.join("schemas", "license_capability_artifact.schema.json")

TRUTH_PURITY_TARGETS = (
    os.path.join("schema", "universe", "universe_state.schema"),
    os.path.join("schema", "universe", "universe_identity.schema"),
    os.path.join("schemas", "universe_state.schema.json"),
    os.path.join("schemas", "universe_identity.schema.json"),
    os.path.join("src", "server", "server_boot.py"),
    os.path.join("src", "server", "server_console.py"),
    os.path.join("src", "universe", "universe_identity_builder.py"),
    os.path.join("src", "universe", "universe_contract_enforcer.py"),
)
TRUTH_PURITY_FORBIDDEN = {
    "sky_gradient": "Truth state must not store derived sky gradients.",
    "starfield": "Truth state must not store starfield presentation payloads.",
    "star_rows": "Truth state must not store derived star rows.",
    "moon_phase": "Truth state must not store moon phase presentation values.",
    "moon_illumination": "Truth state must not store moon illumination presentation values.",
    "illumination_view_artifact": "Truth state must not store derived illumination artifacts.",
    "illumination_surfaces": "Truth state must not store renderer-facing illumination surfaces.",
    "shadow_buffer": "Truth state must not store shadow buffers.",
    "shadow_map": "Truth state must not store shadow maps.",
    "water_visual": "Truth state must not store water visual state.",
    "water_render": "Truth state must not store water render state.",
    "render_state": "Truth state must not store renderer state.",
    "render_buffer": "Truth state must not store render buffers.",
}
RENDERER_SCAN_PREFIXES = (
    os.path.join("src", "client", "render"),
    os.path.join("tools", "render"),
    os.path.join("tools", "xstack", "sessionx", "render_model.py"),
)
RENDERER_FORBIDDEN_RE = re.compile(r"\b(truth_model|truthmodel|universe_state|process_runtime)\b", re.IGNORECASE)
SEMANTIC_SYMBOL_SPECS = (
    (
        "compat_negotiation",
        "negotiate_endpoint_descriptors",
        os.path.join("src", "compat", "capability_negotiation.py"),
        "Compatibility negotiation must have a single authoritative semantic engine.",
    ),
    (
        "compat_negotiation",
        "verify_negotiation_record",
        os.path.join("src", "compat", "capability_negotiation.py"),
        "Negotiation replay verification must resolve through the same authoritative semantic engine.",
    ),
    (
        "overlay_merge",
        "merge_overlay_view",
        os.path.join("src", "geo", "overlay", "overlay_merge_engine.py"),
        "Overlay merge must have a single authoritative semantic engine.",
    ),
    (
        "overlay_merge",
        "overlay_proof_surface",
        os.path.join("src", "geo", "overlay", "overlay_merge_engine.py"),
        "Overlay merge proof synthesis must remain in the authoritative overlay engine.",
    ),
    (
        "illumination",
        "build_illumination_view_artifact",
        os.path.join("src", "astro", "illumination", "illumination_geometry_engine.py"),
        "Illumination artifact synthesis must have one authoritative model implementation.",
    ),
    (
        "illumination",
        "build_lighting_view_surface",
        os.path.join("src", "worldgen", "earth", "lighting", "lighting_view_engine.py"),
        "Lighting view synthesis must stay in the authoritative illumination pipeline.",
    ),
    (
        "illumination",
        "evaluate_horizon_shadow",
        os.path.join("src", "worldgen", "earth", "lighting", "horizon_shadow_engine.py"),
        "Horizon-shadow evaluation must stay in the authoritative illumination pipeline.",
    ),
    (
        "id_generation",
        "geo_object_id",
        os.path.join("src", "geo", "index", "object_id_engine.py"),
        "Geo object identity generation must have one authoritative engine.",
    ),
)
SEMANTIC_SCAN_PREFIXES = ("src", "tools")
DETERMINISM_SCAN_PREFIXES = (
    os.path.join("src", "server"),
    os.path.join("src", "universe"),
    os.path.join("src", "process"),
    os.path.join("src", "logic"),
    os.path.join("src", "field"),
    os.path.join("src", "fields"),
    os.path.join("src", "geo"),
    os.path.join("src", "worldgen"),
    os.path.join("src", "time"),
    os.path.join("src", "compat"),
)
WALLCLOCK_TOKENS = (
    "time.time(",
    "datetime.now(",
    "datetime.utcnow(",
    "time.monotonic(",
    "time.perf_counter(",
)
UNNAMED_RNG_TOKENS = (
    "random.",
    "uuid.uuid4(",
    "secrets.",
    "os.urandom(",
)
UNORDERED_LOOP_RE = re.compile(r"for\s+.+\s+in\s+.+\.(?:items|keys|values)\s*\(\)\s*:")
APPROVED_FLOAT_PATHS = {
    os.path.join("src", "geo", "kernel", "geo_kernel.py"),
    os.path.join("src", "geo", "metric", "metric_engine.py"),
    os.path.join("src", "process", "qc", "qc_engine.py"),
}
NUMERIC_SCAN_CHECK_ORDER = [
    "float_in_truth_scan",
    "noncanonical_serialization_scan",
    "compiler_flag_scan",
]
CONCURRENCY_SCAN_CHECK_ORDER = [
    "parallel_truth_scan",
    "parallel_output_scan",
    "truth_atomic_scan",
]
NUMERIC_TRUTH_TARGETS = (
    os.path.join("src", "astro", "ephemeris", "kepler_proxy_engine.py"),
    os.path.join("src", "astro", "illumination", "illumination_geometry_engine.py"),
    os.path.join("src", "fields", "field_engine.py"),
    os.path.join("src", "logic", "compile", "logic_proof_engine.py"),
    os.path.join("src", "logic", "eval", "common.py"),
    os.path.join("src", "logic", "fault", "fault_engine.py"),
    os.path.join("src", "meta", "numeric.py"),
    os.path.join("src", "mobility", "micro", "free_motion_solver.py"),
    os.path.join("src", "physics", "energy", "energy_ledger_engine.py"),
    os.path.join("src", "physics", "momentum_engine.py"),
    os.path.join("src", "time", "time_mapping_engine.py"),
)
WORLDGEN_NUMERIC_TRUTH_TARGETS = (
    os.path.join("src", "geo", "worldgen", "worldgen_engine.py"),
    os.path.join("src", "worldgen", "galaxy", "galaxy_object_stub_generator.py"),
    os.path.join("src", "worldgen", "mw", "mw_cell_generator.py"),
    os.path.join("src", "worldgen", "mw", "mw_system_refiner_l2.py"),
    os.path.join("src", "worldgen", "mw", "mw_surface_refiner_l3.py"),
    os.path.join("src", "worldgen", "mw", "insolation_proxy.py"),
    os.path.join("src", "worldgen", "mw", "sol_anchor.py"),
    os.path.join("src", "worldgen", "earth", "earth_surface_generator.py"),
    os.path.join("src", "worldgen", "earth", "climate_field_engine.py"),
    os.path.join("src", "worldgen", "earth", "hydrology_engine.py"),
    os.path.join("src", "worldgen", "earth", "tide_field_engine.py"),
    os.path.join("src", "worldgen", "earth", "season_phase_engine.py"),
    os.path.join("src", "worldgen", "earth", "tide_phase_engine.py"),
    os.path.join("src", "worldgen", "earth", "material", "material_proxy_engine.py"),
)
REVIEWED_NUMERIC_BRIDGE_PATHS = {
    os.path.join("src", "geo", "kernel", "geo_kernel.py"): "projection/query bridge with deterministic quantization",
    os.path.join("src", "geo", "metric", "metric_engine.py"): "geodesic approximation bridge with bounded deterministic rounding",
    os.path.join("src", "meta", "instrumentation", "instrumentation_engine.py"): "measurement quantization bridge that snaps back onto deterministic integer quanta",
    os.path.join("src", "mobility", "geometry", "geometry_engine.py"): "geometry snap bridge that quantizes endpoints back to integer grid coordinates",
    os.path.join("src", "mobility", "micro", "constrained_motion_solver.py"): "heading derivation bridge that emits integer milli-degree results only",
    os.path.join("src", "process", "qc", "qc_engine.py"): "qc rate derivation bridge that quantizes report values back to integers",
}
NUMERIC_SERIALIZATION_TARGETS = (
    os.path.join("src", "compat", "capability_negotiation.py"),
    os.path.join("src", "meta", "identity", "identity_validator.py"),
    os.path.join("src", "release", "build_id_engine.py"),
    os.path.join("src", "release", "release_manifest_engine.py"),
    os.path.join("src", "release", "update_resolver.py"),
    os.path.join("src", "security", "trust", "trust_verifier.py"),
)
PARALLEL_TRUTH_TARGETS = (
    os.path.join("src", "process"),
    os.path.join("src", "field"),
    os.path.join("src", "fields"),
    os.path.join("src", "logic"),
    os.path.join("src", "time"),
    os.path.join("src", "universe"),
    os.path.join("tools", "xstack", "sessionx", "process_runtime.py"),
    os.path.join("tools", "xstack", "sessionx", "scheduler.py"),
)
PARALLEL_OUTPUT_TARGETS = (
    os.path.join("src", "appshell", "supervisor", "supervisor_engine.py"),
    os.path.join("tools", "xstack", "core", "scheduler.py"),
)
TRUTH_ATOMIC_TARGETS = PARALLEL_TRUTH_TARGETS
CONCURRENCY_PRIMITIVE_TOKENS = (
    "ThreadPoolExecutor",
    "ProcessPoolExecutor",
    "threading.Thread(",
    "threading.Lock(",
    "threading.RLock(",
    "threading.Semaphore(",
    "threading.Barrier(",
    "concurrent.futures",
    "multiprocessing",
)
TRUTH_ATOMIC_TOKENS = (
    "atomic",
    "compare_exchange",
    "fetch_add",
    "fetch_sub",
    "test_and_set",
    "interlocked",
)
PARALLEL_OUTPUT_REQUIRED_TOKENS = {
    os.path.join("src", "appshell", "supervisor", "supervisor_engine.py"): (
        "canonicalize_parallel_mapping_rows(",
        "build_field_sort_key(",
    ),
    os.path.join("tools", "xstack", "core", "scheduler.py"): (
        "ThreadPoolExecutor",
        "ready.sort(",
        "ordered = sorted(",
    ),
}
COMPILER_FLAG_SCAN_FILES = (
    "CMakeLists.txt",
    "CMakePresets.json",
    os.path.join("tools", "CMakeLists.txt"),
)
UNSAFE_FLOAT_FLAG_TOKENS = (
    "-ffast-math",
    "-funsafe-math-optimizations",
    "-Ofast",
    "-ffp-model=fast",
    "-fp-model fast",
    "/fp:fast",
    "fp:fast",
    "march=native",
)
NUMERIC_FLOAT_TOKEN_RE = re.compile(r"\bfloat\s*\(", re.IGNORECASE)
NUMERIC_FLOAT_LITERAL_RE = re.compile(r"(?<![\"'A-Za-z0-9_])(?:\d+\.\d+|\.\d+)(?![\"'A-Za-z0-9_])")
NUMERIC_MATH_FLOAT_RE = re.compile(r"\bmath\.(?:asin|acos|atan|atan2|sin|cos|tan|sqrt|radians|degrees)\s*\(")
NONCANONICAL_NUMERIC_SERIALIZATION_PATTERNS = (
    re.compile(r"\{[^{}\n]*:[^{}\n]*\.[0-9]+[eEfFgG][^{}\n]*\}"),
    re.compile(r"format\s*\([^,\n]+,\s*[\"'][^\"']*\.[0-9]+[eEfFgG][^\"']*[\"']"),
    re.compile(r"\bjson\.dumps\s*\("),
)
CONTRACT_PIN_TARGETS = {
    os.path.join("schema", "universe", "universe_identity.schema"): (
        "universe_contract_bundle_ref",
        "universe_contract_bundle_hash",
    ),
    os.path.join("schemas", "universe_identity.schema.json"): (
        "universe_contract_bundle_ref",
        "universe_contract_bundle_hash",
    ),
    os.path.join("schemas", "session_spec.schema.json"): (
        "contract_bundle_hash",
    ),
    os.path.join("src", "universe", "universe_contract_enforcer.py"): (
        "enforce_session_contract_bundle",
        "universe_contract_bundle_hash",
        "contract_bundle_hash",
    ),
}
DIST_COMPOSITION_TARGETS = (
    os.path.join("tools", "dist", "dist_tree_common.py"),
    os.path.join("tools", "dist", "tool_assemble_dist_tree.py"),
    os.path.join("tools", "setup", "setup_cli.py"),
    os.path.join("tools", "launcher", "launch.py"),
)
UPDATE_MODEL_TARGETS = (
    os.path.join("src", "release", "update_resolver.py"),
    os.path.join("tools", "setup", "setup_cli.py"),
    os.path.join("tools", "release", "update_model_common.py"),
)
TRUST_TARGETS = (
    os.path.join("src", "security", "trust", "trust_verifier.py"),
    os.path.join("src", "release", "update_resolver.py"),
    os.path.join("src", "appshell", "pack_verifier_adapter.py"),
    os.path.join("tools", "dist", "dist_verify_common.py"),
    os.path.join("tools", "release", "tool_verify_release_manifest.py"),
)
TARGET_MATRIX_TARGETS = (
    os.path.join("tools", "release", "update_model_common.py"),
    os.path.join("tools", "release", "arch_matrix_common.py"),
    os.path.join("src", "compat", "capability_negotiation.py"),
    os.path.join("data", "registries", "target_matrix_registry.json"),
)
ARCHIVE_DETERMINISM_TARGETS = (
    os.path.join("src", "release"),
    os.path.join("tools", "dist"),
    os.path.join("tools", "release"),
)
ARCHIVE_DETERMINISM_FORBIDDEN = (
    "zipfile",
    "tarfile",
    "ZipInfo(",
    "TarInfo(",
    "make_archive(",
    "shutil.make_archive(",
)
ARCHIVE_TIMESTAMP_FORBIDDEN = (
    "timestamp",
    "mtime",
    "date_time",
    "datetime.utcnow(",
    "datetime.now(",
    "time.time(",
    "time.time_ns(",
    "os.path.getmtime(",
)
DIST_COMPONENT_LITERAL_RE = re.compile(
    r"(?i)(bundle|component|selected|include)[a-z0-9_]*\s*=\s*[\[\(][^\]\)]*[\"'](?:binary|pack|profile|lock|docs|manifest)\.[^\"']+[\"']"
)
TRUST_BYPASS_FORBIDDEN = (
    "bypass_trust_verify",
    "skip_hash_verify",
    "accept_without_hash",
    "accept_unsigned_strict",
    "local_dev_bypass",
)
ARCH_AUDIT2_CHECK_ORDER = [
    "dist_bundle_composition_scan",
    "update_model_scan",
    "trust_bypass_scan",
    "target_matrix_scan",
    "archive_determinism_scan",
]


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = str(rel_path or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token.replace("/", os.sep))))


def _ensure_dir(path: str) -> None:
    token = str(path or "").strip()
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def load_json_if_present(repo_root: str, rel_path: str) -> dict:
    abs_path = _repo_abs(repo_root, rel_path)
    if not abs_path or not os.path.isfile(abs_path):
        return {}
    return _read_json(abs_path)


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))
    return _norm(path)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return _norm(path)


def _report_fingerprint(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def _finding_row(
    *,
    category: str,
    path: str,
    line: int,
    message: str,
    snippet: str = "",
    severity: str = "RISK",
    classification: str = "blocking",
    rule_id: str = "",
) -> dict:
    payload = {
        "category": str(category).strip(),
        "classification": str(classification).strip() or "blocking",
        "severity": str(severity).strip() or "RISK",
        "path": _norm(path),
        "line": int(line or 0),
        "message": str(message).strip(),
        "snippet": str(snippet or "").strip()[:200],
    }
    if _token(rule_id):
        payload["rule_id"] = _token(rule_id)
    return payload


def _sorted_findings(rows: Iterable[Mapping[str, object]]) -> list[dict]:
    normalized = [dict(row or {}) for row in list(rows or []) if isinstance(row, Mapping)]
    normalized.sort(
        key=lambda row: (
            _token(row.get("classification")),
            _token(row.get("path")),
            int(row.get("line", 0) or 0),
            _token(row.get("category")),
            _token(row.get("message")),
        )
    )
    return normalized


def _check_result_payload(
    *,
    check_id: str,
    description: str,
    scanned_paths: Iterable[str],
    blocking_findings: Iterable[Mapping[str, object]] = (),
    known_exceptions: Iterable[Mapping[str, object]] = (),
    inventory: Mapping[str, object] | None = None,
) -> dict:
    blocking_rows = _sorted_findings(blocking_findings)
    known_rows = _sorted_findings(known_exceptions)
    result = "fail" if blocking_rows else ("known_exception" if known_rows else "pass")
    payload = {
        "check_id": str(check_id).strip(),
        "description": str(description).strip(),
        "result": result,
        "scanned_paths": sorted(_norm(path) for path in list(scanned_paths or []) if _token(path)),
        "blocking_finding_count": len(blocking_rows),
        "known_exception_count": len(known_rows),
        "blocking_findings": blocking_rows,
        "known_exceptions": known_rows,
        "inventory": dict(inventory or {}),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _report_fingerprint(payload)
    return payload


def _iter_python_files(repo_root: str, prefixes: Iterable[str]) -> list[str]:
    out: list[str] = []
    for prefix in list(prefixes or []):
        abs_prefix = _repo_abs(repo_root, str(prefix))
        if not abs_prefix:
            continue
        if os.path.isfile(abs_prefix):
            if abs_prefix.endswith(".py"):
                out.append(_norm(os.path.relpath(abs_prefix, repo_root)))
            continue
        if not os.path.isdir(abs_prefix):
            continue
        for root, dirs, files in os.walk(abs_prefix):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                out.append(_norm(os.path.relpath(os.path.join(root, name), repo_root)))
    return sorted(set(out))


def _existing_paths(repo_root: str, paths: Iterable[str]) -> list[str]:
    rows: list[str] = []
    for rel_path in list(paths or []):
        token = _norm(rel_path)
        if not token:
            continue
        abs_path = _repo_abs(repo_root, token)
        if abs_path and os.path.exists(abs_path):
            rows.append(token)
    return sorted(set(rows))


def _iter_override_paths(repo_root: str, override_paths: Sequence[str] | None, defaults: Iterable[str]) -> list[str]:
    if not override_paths:
        return _existing_paths(repo_root, defaults)
    rows: list[str] = []
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    for raw_path in list(override_paths or []):
        token = _token(raw_path)
        if not token:
            continue
        abs_path = _repo_abs(repo_root_abs, token)
        if not abs_path or not os.path.isfile(abs_path):
            continue
        rows.append(_norm(os.path.relpath(abs_path, repo_root_abs)))
    return sorted(set(rows))


def _iter_repo_files_by_suffix(repo_root: str, suffixes: Sequence[str]) -> list[str]:
    root = os.path.normpath(os.path.abspath(repo_root))
    wanted = tuple(str(item or "").lower() for item in list(suffixes or []) if str(item or "").strip())
    out: list[str] = []
    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted(
            name
            for name in dirs
            if name not in {".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache"}
        )
        for name in sorted(files):
            rel_path = _norm(os.path.relpath(os.path.join(current_root, name), root))
            lower = rel_path.lower()
            if wanted and not lower.endswith(wanted):
                continue
            out.append(rel_path)
    return sorted(set(out))


def _violation_finding_rows(
    rows: Iterable[Mapping[str, object]],
    *,
    default_category: str,
    default_message: str,
    fallback_rule_id: str = "",
) -> list[dict]:
    findings: list[dict] = []
    for row in list(rows or []):
        item = dict(row or {})
        findings.append(
            _finding_row(
                category=_token(item.get("category")) or default_category,
                path=_token(item.get("file_path")) or _token(item.get("path")),
                line=int(item.get("line_number", item.get("line", 1)) or 1),
                message=_token(item.get("message")) or default_message,
                snippet=_token(item.get("code")) or _token(item.get("snippet")),
                rule_id=_token(item.get("rule_id")) or fallback_rule_id,
            )
        )
    return findings


def _truth_key_match(rel_path: str, line: str, token: str) -> bool:
    lower = str(line).lower()
    if token not in lower:
        return False
    if rel_path.endswith(".py") or rel_path.endswith(".json"):
        return bool(re.search(r"[\"'][^\"']*{}[^\"']*[\"']\s*:".format(re.escape(token)), line, re.IGNORECASE))
    return bool(re.search(r"^\s*(?:-\s*)?{}[a-z0-9_]*\s*:".format(re.escape(token)), lower))


def scan_truth_purity(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    findings: list[dict] = []
    scanned_paths: list[str] = []
    for rel_path in TRUTH_PURITY_TARGETS:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if not abs_path or not os.path.isfile(abs_path):
            continue
        scanned_paths.append(_norm(rel_path))
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            for token, message in sorted(TRUTH_PURITY_FORBIDDEN.items(), key=lambda item: item[0]):
                if not _truth_key_match(_norm(rel_path), line, token):
                    continue
                findings.append(
                    _finding_row(
                        category="truth_purity",
                        path=_norm(rel_path),
                        line=line_no,
                        message=message,
                        snippet=line,
                    )
                )
    return _check_result_payload(
        check_id="truth_purity_scan",
        description="Search governed truth schemas and canonical materializers for forbidden presentation fields.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"target_count": len(TRUTH_PURITY_TARGETS)},
    )


def scan_renderer_truth_access(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    findings: list[dict] = []
    scanned_paths = _iter_python_files(repo_root_abs, RENDERER_SCAN_PREFIXES)
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not RENDERER_FORBIDDEN_RE.search(snippet):
                continue
            findings.append(
                _finding_row(
                    category="renderer_truth_access",
                    path=rel_path,
                    line=line_no,
                    message="Renderer-facing code must not reference TruthModel, UniverseState, or process runtime directly.",
                    snippet=snippet,
                )
            )
    return _check_result_payload(
        check_id="renderer_truth_access_scan",
        description="Search renderer modules for direct truth/runtime access.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"renderer_file_count": len(scanned_paths)},
    )


def scan_duplicate_semantics(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_python_files(repo_root_abs, SEMANTIC_SCAN_PREFIXES)
    watched_symbols = {symbol for _topic, symbol, _path, _message in SEMANTIC_SYMBOL_SPECS}
    definitions: dict[str, list[dict]] = {}
    pattern = re.compile(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            match = pattern.match(line)
            if not match:
                continue
            symbol = str(match.group(1))
            if symbol not in watched_symbols:
                continue
            definitions.setdefault(symbol, []).append({"path": rel_path, "line": line_no})
    findings: list[dict] = []
    inventory = {"symbols": {}}
    for topic, symbol, expected_path, message in SEMANTIC_SYMBOL_SPECS:
        occurrences = list(definitions.get(symbol) or [])
        inventory["symbols"][symbol] = {
            "topic": topic,
            "expected_path": _norm(expected_path),
            "occurrences": [dict(row) for row in sorted(occurrences, key=lambda row: (_token(row.get("path")), int(row.get("line", 0) or 0)))],
        }
        if len(occurrences) != 1:
            findings.append(
                _finding_row(
                    category="duplicate_semantics",
                    path=_norm(expected_path),
                    line=1,
                    message="{} Expected exactly one definition of '{}'.".format(message, symbol),
                    snippet=json.dumps(inventory["symbols"][symbol]["occurrences"], sort_keys=True),
                )
            )
            continue
        occurrence = dict(occurrences[0] or {})
        if _norm(occurrence.get("path", "")) == _norm(expected_path):
            continue
        findings.append(
            _finding_row(
                category="duplicate_semantics",
                path=_norm(occurrence.get("path", "")),
                line=int(occurrence.get("line", 0) or 0),
                message="{} '{}' moved away from its authoritative engine.".format(message, symbol),
                snippet=str(occurrence.get("path", "")),
            )
        )
    return _check_result_payload(
        check_id="duplicate_semantics_scan",
        description="Verify that governed semantic entry points resolve through one authoritative implementation.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory=inventory,
    )


def _is_approved_float_line(rel_path: str, line: str) -> bool:
    rel_norm = _norm(rel_path)
    lower = str(line).lower()
    if rel_norm in {_norm(path) for path in APPROVED_FLOAT_PATHS}:
        return True
    if "isinstance(" in lower and "float" in lower:
        return True
    if "round(float(" in lower:
        return True
    if lower.startswith("def _as_float(") or "return float(" in lower:
        return True
    return False


def _is_reviewed_numeric_bridge_line(rel_path: str, line: str) -> bool:
    rel_norm = _norm(rel_path)
    lower = str(line).strip().lower()
    if rel_norm in {_norm(path) for path in REVIEWED_NUMERIC_BRIDGE_PATHS}:
        return True
    if "isinstance(" in lower and "float" in lower:
        return True
    if "round(float(" in lower or "int(round(float(" in lower:
        return True
    if "return float(" in lower or lower.startswith("def _as_float("):
        return True
    return False


def scan_determinism(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_python_files(repo_root_abs, DETERMINISM_SCAN_PREFIXES)
    blocking: list[dict] = []
    known: list[dict] = []
    approved_float_paths: dict[str, int] = {}
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            for token in WALLCLOCK_TOKENS:
                if token in snippet:
                    blocking.append(
                        _finding_row(
                            category="determinism.wallclock",
                            path=rel_path,
                            line=line_no,
                            message="Truth paths must not depend on wall-clock time.",
                            snippet=snippet,
                        )
                    )
                    break
            for token in UNNAMED_RNG_TOKENS:
                if token in snippet:
                    blocking.append(
                        _finding_row(
                            category="determinism.unnamed_rng",
                            path=rel_path,
                            line=line_no,
                            message="Truth paths must not use unnamed RNG or host entropy sources.",
                            snippet=snippet,
                        )
                    )
                    break
            if UNORDERED_LOOP_RE.search(snippet) and "sorted(" not in snippet:
                known.append(
                    _finding_row(
                        category="determinism.unordered_iteration",
                        path=rel_path,
                        line=line_no,
                        message="Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.",
                        snippet=snippet,
                        classification="known_exception",
                    )
                )
            if ("float(" in snippet or re.search(r"\bfloat\b", snippet)) and not _is_approved_float_line(rel_path, snippet):
                known.append(
                    _finding_row(
                        category="determinism.float_usage",
                        path=rel_path,
                        line=line_no,
                        message="Unreviewed floating-point usage in a truth-side path; review under ARCH-AUDIT-1.",
                        snippet=snippet,
                        classification="known_exception",
                    )
                )
            elif ("float(" in snippet or re.search(r"\bfloat\b", snippet)) and _norm(rel_path) in {_norm(path) for path in APPROVED_FLOAT_PATHS}:
                approved_float_paths[_norm(rel_path)] = int(approved_float_paths.get(_norm(rel_path), 0)) + 1
    return _check_result_payload(
        check_id="determinism_scan",
        description="Scan truth-side paths for wall-clock usage, unnamed RNG, unordered iteration, and unreviewed float usage.",
        scanned_paths=scanned_paths,
        blocking_findings=blocking,
        known_exceptions=known,
        inventory={
            "approved_float_paths": dict(sorted(approved_float_paths.items(), key=lambda item: item[0])),
            "wallclock_token_count": sum(1 for row in blocking if _token(row.get("category")) == "determinism.wallclock"),
            "unnamed_rng_token_count": sum(1 for row in blocking if _token(row.get("category")) == "determinism.unnamed_rng"),
        },
    )


def scan_float_in_truth(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_override_paths(
        repo_root_abs,
        override_paths,
        list(NUMERIC_TRUTH_TARGETS) + sorted(REVIEWED_NUMERIC_BRIDGE_PATHS.keys()),
    )
    findings: list[dict] = []
    reviewed_hits: dict[str, int] = {}
    reviewed_reasons = dict((key, str(value)) for key, value in REVIEWED_NUMERIC_BRIDGE_PATHS.items())
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            has_float_token = bool(
                NUMERIC_FLOAT_TOKEN_RE.search(snippet)
                or NUMERIC_FLOAT_LITERAL_RE.search(snippet)
                or NUMERIC_MATH_FLOAT_RE.search(snippet)
            )
            if not has_float_token:
                continue
            if _is_reviewed_numeric_bridge_line(rel_path, snippet):
                reviewed_hits[_norm(rel_path)] = int(reviewed_hits.get(_norm(rel_path), 0)) + 1
                continue
            findings.append(
                _finding_row(
                    category="numeric.float_in_truth",
                    path=rel_path,
                    line=line_no,
                    message="truth-side numeric code must remain fixed-point/integer; floating-point usage is not allowed outside reviewed bridges.",
                    snippet=snippet,
                    rule_id="INV-FLOAT-ONLY-IN-RENDER",
                )
            )
    known = [
        _finding_row(
            category="numeric.reviewed_float_bridge",
            path=path,
            line=1,
            message="reviewed numeric bridge: {}".format(reviewed_reasons.get(path, "deterministic quantization bridge")),
            snippet="reviewed_float_bridge_hits={}".format(int(reviewed_hits.get(path, 0))),
            classification="known_exception",
            rule_id="INV-FLOAT-ONLY-IN-RENDER",
        )
        for path in sorted(reviewed_hits.keys())
    ]
    return _check_result_payload(
        check_id="float_in_truth_scan",
        description="Detect floating-point usage in governed numeric truth namespaces and inventory reviewed deterministic float bridges.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        known_exceptions=known,
        inventory={
            "reviewed_bridge_paths": dict((path, reviewed_reasons.get(path, "")) for path in sorted(reviewed_hits.keys())),
            "reviewed_bridge_hit_count": sum(int(value) for value in reviewed_hits.values()),
        },
    )


def scan_worldgen_lock(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    required_paths = [
        WORLDGEN_LOCK_DOC_REL,
        WORLDGEN_LOCK_RETRO_AUDIT_REL,
        WORLDGEN_LOCK_REGISTRY_REL,
        WORLDGEN_LOCK_BASELINE_SEED_REL,
        WORLDGEN_LOCK_BASELINE_SNAPSHOT_REL,
        WORLDGEN_LOCK_GENERATE_TOOL_REL,
        WORLDGEN_LOCK_GENERATE_TOOL_PY_REL,
        WORLDGEN_LOCK_VERIFY_TOOL_REL,
        WORLDGEN_LOCK_VERIFY_TOOL_PY_REL,
        WORLDGEN_LOCK_VERIFY_JSON_REL,
        WORLDGEN_LOCK_VERIFY_DOC_REL,
    ]
    scanned_paths = sorted(set(required_paths + list(WORLDGEN_NUMERIC_TRUTH_TARGETS)))
    findings: list[dict] = []

    for rel_path in required_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if abs_path and os.path.exists(abs_path):
            continue
        findings.append(
            _finding_row(
                category="worldgen_lock.required_surface",
                path=rel_path,
                line=1,
                message="required WORLDGEN-LOCK surface is missing.",
                rule_id="INV-WORLDGEN-LOCK-REQUIRED",
            )
        )

    registry_payload = load_json_if_present(repo_root_abs, WORLDGEN_LOCK_REGISTRY_REL)
    registry_record = _as_map(registry_payload.get("record"))
    registry_fp = _token(registry_record.get("deterministic_fingerprint"))
    if registry_payload and (not registry_fp):
        findings.append(
            _finding_row(
                category="worldgen_lock.registry_fingerprint",
                path=WORLDGEN_LOCK_REGISTRY_REL,
                line=1,
                message="worldgen lock registry is missing deterministic_fingerprint.",
                rule_id="INV-WORLDGEN-LOCK-REQUIRED",
            )
        )

    snapshot_payload = load_json_if_present(repo_root_abs, WORLDGEN_LOCK_BASELINE_SNAPSHOT_REL)
    snapshot_record = _as_map(snapshot_payload.get("record"))
    snapshot_fp = _token(snapshot_record.get("deterministic_fingerprint"))
    if snapshot_payload and (not snapshot_fp):
        findings.append(
            _finding_row(
                category="worldgen_lock.snapshot_fingerprint",
                path=WORLDGEN_LOCK_BASELINE_SNAPSHOT_REL,
                line=1,
                message="worldgen lock baseline snapshot is missing deterministic_fingerprint.",
                rule_id="INV-WORLDGEN-LOCK-REQUIRED",
            )
        )

    determinism_scan = scan_determinism(repo_root_abs)
    unnamed_rng_rows = [
        dict(row)
        for row in list(determinism_scan.get("blocking_findings") or [])
        if _token(row.get("category")) == "determinism.unnamed_rng"
        and (
            _token(row.get("path")).startswith("src/worldgen/")
            or _token(row.get("path")).startswith("src/geo/worldgen/")
        )
    ]
    for row in unnamed_rng_rows:
        findings.append(
            _finding_row(
                category="worldgen_lock.unnamed_rng",
                path=_token(row.get("path")),
                line=int(row.get("line", 1) or 1),
                message=_token(row.get("message")) or "unnamed RNG detected in worldgen truth path.",
                snippet=_token(row.get("snippet")),
                rule_id="INV-NO-UNNAMED-RNG",
            )
        )

    float_scan = scan_float_in_truth(repo_root_abs, override_paths=WORLDGEN_NUMERIC_TRUTH_TARGETS)
    float_rows = [dict(row) for row in list(float_scan.get("blocking_findings") or []) if isinstance(row, Mapping)]
    for row in float_rows:
        findings.append(
            _finding_row(
                category="worldgen_lock.float_in_truth",
                path=_token(row.get("path")),
                line=int(row.get("line", 1) or 1),
                message=_token(row.get("message")) or "floating-point usage detected in worldgen truth path.",
                snippet=_token(row.get("snippet")),
                rule_id="INV-WORLDGEN-LOCK-REQUIRED",
            )
        )

    if registry_payload and registry_record and snapshot_payload and snapshot_record:
        try:
            from tools.worldgen.worldgen_lock_common import registry_record_hash, snapshot_record_hash, verify_worldgen_lock
        except Exception:
            findings.append(
                _finding_row(
                    category="worldgen_lock.tooling_missing",
                    path=WORLDGEN_LOCK_VERIFY_TOOL_PY_REL,
                    line=1,
                    message="worldgen lock verification helpers could not be imported.",
                    rule_id="INV-WORLDGEN-LOCK-REQUIRED",
                )
            )
        else:
            expected_registry_fp = registry_record_hash(registry_record)
            if registry_fp != expected_registry_fp:
                findings.append(
                    _finding_row(
                        category="worldgen_lock.registry_fingerprint",
                        path=WORLDGEN_LOCK_REGISTRY_REL,
                        line=1,
                        message="worldgen lock registry deterministic_fingerprint does not match canonical record hash.",
                        rule_id="INV-WORLDGEN-LOCK-REQUIRED",
                    )
                )
            expected_snapshot_fp = snapshot_record_hash(snapshot_record)
            if snapshot_fp != expected_snapshot_fp:
                findings.append(
                    _finding_row(
                        category="worldgen_lock.snapshot_fingerprint",
                        path=WORLDGEN_LOCK_BASELINE_SNAPSHOT_REL,
                        line=1,
                        message="worldgen lock baseline snapshot deterministic_fingerprint does not match canonical record hash.",
                        rule_id="INV-WORLDGEN-LOCK-REQUIRED",
                    )
                )
            verify_report = verify_worldgen_lock(repo_root_abs)
            if not bool(verify_report.get("matches_snapshot")):
                findings.append(
                    _finding_row(
                        category="worldgen_lock.snapshot_drift",
                        path=WORLDGEN_LOCK_BASELINE_SNAPSHOT_REL,
                        line=1,
                        message="committed baseline snapshot does not match regeneration from baseline seed.",
                        snippet="; ".join(str(item).strip() for item in list(verify_report.get("mismatched_fields") or [])[:4] if str(item).strip()),
                        rule_id="INV-WORLDGEN-LOCK-REQUIRED",
                    )
                )

    return _check_result_payload(
        check_id="worldgen_lock_scan",
        description="Verify required WORLDGEN-LOCK artifacts, committed baseline replay, worldgen RNG discipline, and worldgen float discipline.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "unnamed_rng_worldgen_findings": len(unnamed_rng_rows),
            "float_in_worldgen_findings": len(float_rows),
            "registry_fingerprint": registry_fp,
            "snapshot_fingerprint": snapshot_fp,
        },
    )


def scan_baseline_universe(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    required_paths = [
        BASELINE_UNIVERSE_RETRO_AUDIT_REL,
        BASELINE_UNIVERSE_DOC_REL,
        BASELINE_UNIVERSE_INSTANCE_MANIFEST_REL,
        BASELINE_UNIVERSE_PACK_LOCK_REL,
        BASELINE_UNIVERSE_PROFILE_BUNDLE_REL,
        BASELINE_UNIVERSE_SAVE_REL,
        BASELINE_UNIVERSE_SNAPSHOT_REL,
        BASELINE_UNIVERSE_GENERATE_TOOL_REL,
        BASELINE_UNIVERSE_GENERATE_TOOL_PY_REL,
        BASELINE_UNIVERSE_VERIFY_TOOL_REL,
        BASELINE_UNIVERSE_VERIFY_TOOL_PY_REL,
        BASELINE_UNIVERSE_VERIFY_JSON_REL,
        BASELINE_UNIVERSE_VERIFY_DOC_REL,
        BASELINE_UNIVERSE_BASELINE_DOC_REL,
    ]
    scanned_paths = sorted(set(required_paths))
    findings: list[dict] = []

    for rel_path in required_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if abs_path and os.path.exists(abs_path):
            continue
        findings.append(
            _finding_row(
                category="baseline_universe.required_surface",
                path=rel_path,
                line=1,
                message="required BASELINE-UNIVERSE surface is missing.",
                rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
            )
        )

    snapshot_payload = load_json_if_present(repo_root_abs, BASELINE_UNIVERSE_SNAPSHOT_REL)
    snapshot_record = _as_map(snapshot_payload.get("record"))
    snapshot_fp = _token(snapshot_record.get("deterministic_fingerprint"))
    if snapshot_payload and (not snapshot_fp):
        findings.append(
            _finding_row(
                category="baseline_universe.snapshot_fingerprint",
                path=BASELINE_UNIVERSE_SNAPSHOT_REL,
                line=1,
                message="baseline universe snapshot is missing deterministic_fingerprint.",
                rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
            )
        )

    for rel_path in (
        BASELINE_UNIVERSE_INSTANCE_MANIFEST_REL,
        BASELINE_UNIVERSE_PACK_LOCK_REL,
        BASELINE_UNIVERSE_PROFILE_BUNDLE_REL,
    ):
        payload = load_json_if_present(repo_root_abs, rel_path)
        if not payload:
            continue
        if _as_map(payload.get("universal_identity_block")):
            continue
        findings.append(
            _finding_row(
                category="baseline_universe.identity_block_missing",
                path=rel_path,
                line=1,
                message="baseline universe artifact is missing universal_identity_block.",
                rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
            )
        )

    pack_lock_payload = load_json_if_present(repo_root_abs, BASELINE_UNIVERSE_PACK_LOCK_REL)
    if pack_lock_payload and snapshot_record:
        pack_lock_hash = _token(pack_lock_payload.get("pack_lock_hash"))
        if pack_lock_hash and pack_lock_hash != _token(snapshot_record.get("pack_lock_hash")):
            findings.append(
                _finding_row(
                    category="baseline_universe.pack_lock_drift",
                    path=BASELINE_UNIVERSE_PACK_LOCK_REL,
                    line=1,
                    message="baseline universe pack lock hash does not match frozen snapshot.",
                    snippet="expected={} actual={}".format(_token(snapshot_record.get("pack_lock_hash")), pack_lock_hash),
                    rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
                )
            )

    verify_report = {}
    if snapshot_payload and snapshot_record:
        try:
            from tools.mvp.baseline_universe_common import baseline_snapshot_record_hash, verify_baseline_universe
        except Exception:
            findings.append(
                _finding_row(
                    category="baseline_universe.tooling_missing",
                    path=BASELINE_UNIVERSE_VERIFY_TOOL_PY_REL,
                    line=1,
                    message="baseline universe verification helpers could not be imported.",
                    rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
                )
            )
        else:
            expected_snapshot_fp = baseline_snapshot_record_hash(snapshot_record)
            if snapshot_fp != expected_snapshot_fp:
                findings.append(
                    _finding_row(
                        category="baseline_universe.snapshot_fingerprint",
                        path=BASELINE_UNIVERSE_SNAPSHOT_REL,
                        line=1,
                        message="baseline universe snapshot deterministic_fingerprint does not match canonical record hash.",
                        rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
                    )
                )
            verify_report = dict(verify_baseline_universe(repo_root_abs) or {})
            if not bool(verify_report.get("matches_snapshot")):
                findings.append(
                    _finding_row(
                        category="baseline_universe.anchor_mismatch",
                        path=BASELINE_UNIVERSE_SNAPSHOT_REL,
                        line=1,
                        message="baseline universe snapshot does not match regeneration from frozen baseline seed and bundle lock.",
                        snippet="; ".join(str(item).strip() for item in list(verify_report.get("mismatched_fields") or [])[:6] if str(item).strip()),
                        rule_id="INV-BASELINE-ANCHORS-MATCH",
                    )
                )
            if not bool(verify_report.get("save_reload_matches")):
                findings.append(
                    _finding_row(
                        category="baseline_universe.anchor_mismatch",
                        path=BASELINE_UNIVERSE_SAVE_REL,
                        line=1,
                        message="baseline universe save-reload checkpoint does not reproduce the frozen T2 anchor.",
                        snippet=_token(verify_report.get("loaded_save_hash")),
                        rule_id="INV-BASELINE-ANCHORS-MATCH",
                    )
                )
            if not bool(verify_report.get("seed_matches_worldgen_lock")):
                findings.append(
                    _finding_row(
                        category="baseline_universe.seed_mismatch",
                        path=BASELINE_UNIVERSE_SNAPSHOT_REL,
                        line=1,
                        message="baseline universe seed does not match WORLDGEN-LOCK frozen seed.",
                        rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
                    )
                )
            if not bool(verify_report.get("pack_lock_matches_worldgen_lock")):
                findings.append(
                    _finding_row(
                        category="baseline_universe.pack_lock_drift",
                        path=BASELINE_UNIVERSE_PACK_LOCK_REL,
                        line=1,
                        message="baseline universe pack lock drifted from WORLDGEN-LOCK freeze.",
                        rule_id="INV-BASELINE-UNIVERSE-REQUIRED",
                    )
                )

    return _check_result_payload(
        check_id="baseline_universe_scan",
        description="Verify required BASELINE-UNIVERSE artifacts, committed baseline replay, save-reload anchor continuity, and WORLDGEN-LOCK alignment.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "snapshot_fingerprint": snapshot_fp,
            "verify_fingerprint": _token(_as_map(verify_report).get("deterministic_fingerprint")),
            "seed_matches_worldgen_lock": bool(_as_map(verify_report).get("seed_matches_worldgen_lock")),
            "pack_lock_matches_worldgen_lock": bool(_as_map(verify_report).get("pack_lock_matches_worldgen_lock")),
            "save_reload_matches": bool(_as_map(verify_report).get("save_reload_matches")),
        },
    )


def scan_gameplay_loop(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    required_paths = [
        MVP_GAMEPLAY_RETRO_AUDIT_REL,
        MVP_GAMEPLAY_DOC_REL,
        MVP_GAMEPLAY_SNAPSHOT_REL,
        MVP_GAMEPLAY_RUN_TOOL_REL,
        MVP_GAMEPLAY_RUN_TOOL_PY_REL,
        MVP_GAMEPLAY_VERIFY_TOOL_REL,
        MVP_GAMEPLAY_VERIFY_TOOL_PY_REL,
        MVP_GAMEPLAY_VERIFY_JSON_REL,
        MVP_GAMEPLAY_VERIFY_DOC_REL,
        MVP_GAMEPLAY_RUN_DOC_REL,
        MVP_GAMEPLAY_BASELINE_DOC_REL,
    ]
    scanned_paths = sorted(set(required_paths))
    findings: list[dict] = []

    for rel_path in required_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if abs_path and os.path.exists(abs_path):
            continue
        findings.append(
            _finding_row(
                category="gameplay_loop.required_surface",
                path=rel_path,
                line=1,
                message="required MVP gameplay loop surface is missing.",
                rule_id="INV-MVP-GAMEPLAY-HARNESS-REQUIRED",
            )
        )

    snapshot_payload = load_json_if_present(repo_root_abs, MVP_GAMEPLAY_SNAPSHOT_REL)
    snapshot_record = _as_map(snapshot_payload.get("record"))
    snapshot_fp = _token(snapshot_record.get("deterministic_fingerprint"))
    if snapshot_payload and (not snapshot_fp):
        findings.append(
            _finding_row(
                category="gameplay_loop.snapshot_fingerprint",
                path=MVP_GAMEPLAY_SNAPSHOT_REL,
                line=1,
                message="MVP gameplay loop snapshot is missing deterministic_fingerprint.",
                rule_id="INV-MVP-GAMEPLAY-HARNESS-REQUIRED",
            )
        )

    verify_report = {}
    if snapshot_payload and snapshot_record:
        try:
            from tools.mvp.gameplay_loop_common import gameplay_snapshot_record_hash, verify_gameplay_loop
        except Exception:
            findings.append(
                _finding_row(
                    category="gameplay_loop.tooling_missing",
                    path=MVP_GAMEPLAY_VERIFY_TOOL_PY_REL,
                    line=1,
                    message="MVP gameplay loop verification helpers could not be imported.",
                    rule_id="INV-MVP-GAMEPLAY-HARNESS-REQUIRED",
                )
            )
        else:
            expected_snapshot_fp = gameplay_snapshot_record_hash(snapshot_record)
            if snapshot_fp != expected_snapshot_fp:
                findings.append(
                    _finding_row(
                        category="gameplay_loop.snapshot_fingerprint",
                        path=MVP_GAMEPLAY_SNAPSHOT_REL,
                        line=1,
                        message="MVP gameplay loop snapshot deterministic_fingerprint does not match canonical record hash.",
                        rule_id="INV-MVP-GAMEPLAY-HARNESS-REQUIRED",
                    )
                )
            verify_report = dict(verify_gameplay_loop(repo_root_abs) or {})
            if not bool(verify_report.get("matches_snapshot")):
                findings.append(
                    _finding_row(
                        category="gameplay_loop.replay_mismatch",
                        path=MVP_GAMEPLAY_SNAPSHOT_REL,
                        line=1,
                        message="MVP gameplay loop snapshot does not match regeneration from the frozen baseline seed and baseline universe.",
                        snippet="; ".join(str(item).strip() for item in list(verify_report.get("mismatched_fields") or [])[:6] if str(item).strip()),
                        rule_id="INV-REPLAY-DETERMINISTIC",
                    )
                )
            if not bool(verify_report.get("save_reload_matches")):
                findings.append(
                    _finding_row(
                        category="gameplay_loop.replay_mismatch",
                        path=MVP_GAMEPLAY_SNAPSHOT_REL,
                        line=1,
                        message="MVP gameplay loop save-reload cycle does not reproduce the frozen post-edit anchor.",
                        snippet=_token(_as_map(verify_report.get("observed_record")).get("deterministic_fingerprint")),
                        rule_id="INV-REPLAY-DETERMINISTIC",
                    )
                )
            if not bool(verify_report.get("replay_matches_final_anchor")):
                findings.append(
                    _finding_row(
                        category="gameplay_loop.replay_mismatch",
                        path=MVP_GAMEPLAY_SNAPSHOT_REL,
                        line=1,
                        message="MVP gameplay loop replay does not reproduce the frozen final anchor after reload.",
                        rule_id="INV-REPLAY-DETERMINISTIC",
                    )
                )
            if not bool(verify_report.get("replay_matches_baseline")):
                findings.append(
                    _finding_row(
                        category="gameplay_loop.replay_mismatch",
                        path=MVP_GAMEPLAY_SNAPSHOT_REL,
                        line=1,
                        message="MVP gameplay loop replay does not reproduce the frozen baseline final anchor.",
                        rule_id="INV-REPLAY-DETERMINISTIC",
                    )
                )
            if not bool(verify_report.get("logic_deterministic")):
                findings.append(
                    _finding_row(
                        category="gameplay_loop.logic_mismatch",
                        path=MVP_GAMEPLAY_SNAPSHOT_REL,
                        line=1,
                        message="MVP gameplay loop logic interaction is no longer deterministic.",
                        rule_id="INV-REPLAY-DETERMINISTIC",
                    )
                )

    return _check_result_payload(
        check_id="gameplay_loop_scan",
        description="Verify required MVP gameplay loop surfaces, committed snapshot replay, save-reload continuity, and deterministic logic interaction.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "snapshot_fingerprint": snapshot_fp,
            "verify_fingerprint": _token(_as_map(verify_report).get("deterministic_fingerprint")),
            "matches_snapshot": bool(_as_map(verify_report).get("matches_snapshot")),
            "save_reload_matches": bool(_as_map(verify_report).get("save_reload_matches")),
            "replay_matches_final_anchor": bool(_as_map(verify_report).get("replay_matches_final_anchor")),
            "replay_matches_baseline": bool(_as_map(verify_report).get("replay_matches_baseline")),
            "logic_deterministic": bool(_as_map(verify_report).get("logic_deterministic")),
        },
    )


def scan_disaster_suite(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    required_paths = [
        DISASTER_RETRO_AUDIT_REL,
        DISASTER_MODEL_DOC_REL,
        DISASTER_CASES_REL,
        DISASTER_GENERATE_TOOL_REL,
        DISASTER_GENERATE_TOOL_PY_REL,
        DISASTER_RUN_TOOL_REL,
        DISASTER_RUN_TOOL_PY_REL,
        DISASTER_RUN_JSON_REL,
        DISASTER_RUN_DOC_REL,
        DISASTER_BASELINE_REL,
        DISASTER_BASELINE_DOC_REL,
    ]
    scanned_paths = sorted(set(required_paths))
    findings: list[dict] = []

    for rel_path in required_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if abs_path and os.path.exists(abs_path):
            continue
        findings.append(
            _finding_row(
                category="disaster_suite.required_surface",
                path=rel_path,
                line=1,
                message="required disaster suite surface is missing.",
                rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
            )
        )

    cases_payload = load_json_if_present(repo_root_abs, DISASTER_CASES_REL)
    cases_record = _as_map(cases_payload.get("record"))
    run_payload = load_json_if_present(repo_root_abs, DISASTER_RUN_JSON_REL)
    baseline_payload = load_json_if_present(repo_root_abs, DISASTER_BASELINE_REL)
    run_report = _as_map(run_payload)
    fresh_report = {}
    fresh_baseline = {}

    try:
        from tools.mvp.disaster_suite_common import (
            DISASTER_CASES_SCHEMA_ID,
            DISASTER_REGRESSION_REQUIRED_TAG,
            DISASTER_SUITE_BASELINE_SCHEMA_ID,
            DISASTER_SUITE_RUN_SCHEMA_ID,
            disaster_baseline_hash,
            disaster_cases_record_hash,
            disaster_run_report_hash,
            run_disaster_suite,
        )
    except Exception:
        findings.append(
            _finding_row(
                category="disaster_suite.tooling_missing",
                path=DISASTER_RUN_TOOL_PY_REL,
                line=1,
                message="disaster suite tooling could not be imported.",
                rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
            )
        )
    else:
        if cases_payload and str(cases_payload.get("schema_id", "")).strip() != DISASTER_CASES_SCHEMA_ID:
            findings.append(
                _finding_row(
                    category="disaster_suite.schema_invalid",
                    path=DISASTER_CASES_REL,
                    line=1,
                    message="disaster suite case registry schema_id mismatch.",
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        if run_payload and str(run_payload.get("schema_id", "")).strip() != DISASTER_SUITE_RUN_SCHEMA_ID:
            findings.append(
                _finding_row(
                    category="disaster_suite.schema_invalid",
                    path=DISASTER_RUN_JSON_REL,
                    line=1,
                    message="disaster suite run report schema_id mismatch.",
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        if baseline_payload and str(baseline_payload.get("schema_id", "")).strip() != DISASTER_SUITE_BASELINE_SCHEMA_ID:
            findings.append(
                _finding_row(
                    category="disaster_suite.schema_invalid",
                    path=DISASTER_BASELINE_REL,
                    line=1,
                    message="disaster suite regression baseline schema_id mismatch.",
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        cases_fp = _token(cases_record.get("deterministic_fingerprint"))
        if cases_record and cases_fp != disaster_cases_record_hash(cases_record):
            findings.append(
                _finding_row(
                    category="disaster_suite.cases_fingerprint",
                    path=DISASTER_CASES_REL,
                    line=1,
                    message="disaster suite case registry deterministic_fingerprint mismatch.",
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        run_fp = _token(run_report.get("deterministic_fingerprint"))
        if run_report and run_fp != disaster_run_report_hash(run_report):
            findings.append(
                _finding_row(
                    category="disaster_suite.run_fingerprint",
                    path=DISASTER_RUN_JSON_REL,
                    line=1,
                    message="disaster suite run report deterministic_fingerprint mismatch.",
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        baseline_fp = _token(baseline_payload.get("deterministic_fingerprint"))
        if baseline_payload and baseline_fp != disaster_baseline_hash(baseline_payload):
            findings.append(
                _finding_row(
                    category="disaster_suite.baseline_fingerprint",
                    path=DISASTER_BASELINE_REL,
                    line=1,
                    message="disaster suite regression baseline deterministic_fingerprint mismatch.",
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        required_tag = _token(_as_map(baseline_payload.get("update_policy")).get("required_commit_tag"))
        if baseline_payload and required_tag != DISASTER_REGRESSION_REQUIRED_TAG:
            findings.append(
                _finding_row(
                    category="disaster_suite.regression_tag",
                    path=DISASTER_BASELINE_REL,
                    line=1,
                    message="disaster suite regression baseline is missing the required update tag guard.",
                    snippet=required_tag,
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        if run_report and str(run_report.get("result", "")).strip() != "complete":
            findings.append(
                _finding_row(
                    category="disaster_suite.harness_mismatch",
                    path=DISASTER_RUN_JSON_REL,
                    line=1,
                    message="committed disaster suite run report is not passing.",
                    snippet="; ".join(str(item).strip() for item in list(run_report.get("mismatched_fields") or [])[:8] if str(item).strip()),
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        if list(run_report.get("silent_success_case_ids") or []):
            findings.append(
                _finding_row(
                    category="disaster_suite.silent_fallback",
                    path=DISASTER_RUN_JSON_REL,
                    line=1,
                    message="disaster suite recorded silent success on a failure scenario.",
                    snippet=", ".join(str(item).strip() for item in list(run_report.get("silent_success_case_ids") or [])[:8] if str(item).strip()),
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        if list(run_report.get("remediation_missing_case_ids") or []):
            findings.append(
                _finding_row(
                    category="disaster_suite.remediation_missing",
                    path=DISASTER_RUN_JSON_REL,
                    line=1,
                    message="disaster suite recorded refusal cases without remediation hints.",
                    snippet=", ".join(str(item).strip() for item in list(run_report.get("remediation_missing_case_ids") or [])[:8] if str(item).strip()),
                    rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        if cases_record:
            fresh_report = dict(
                run_disaster_suite(
                    repo_root_abs,
                    output_root_rel=os.path.join("build", "tmp", "omega4_disaster_arch_audit"),
                    write_outputs=False,
                )
                or {}
            )
            fresh_baseline = _as_map(fresh_report.get("baseline_payload"))
            if not bool(fresh_report.get("cases_match_expected")):
                findings.append(
                    _finding_row(
                        category="disaster_suite.harness_mismatch",
                        path=DISASTER_RUN_JSON_REL,
                        line=1,
                        message="fresh disaster suite rerun did not match the frozen case expectations.",
                        snippet="; ".join(str(item).strip() for item in list(fresh_report.get("mismatched_fields") or [])[:8] if str(item).strip()),
                        rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                    )
                )
            if list(fresh_report.get("silent_success_case_ids") or []):
                findings.append(
                    _finding_row(
                        category="disaster_suite.silent_fallback",
                        path=DISASTER_RUN_JSON_REL,
                        line=1,
                        message="fresh disaster suite rerun produced silent success on a failure scenario.",
                        snippet=", ".join(str(item).strip() for item in list(fresh_report.get("silent_success_case_ids") or [])[:8] if str(item).strip()),
                        rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                    )
                )
            if list(fresh_report.get("remediation_missing_case_ids") or []):
                findings.append(
                    _finding_row(
                        category="disaster_suite.remediation_missing",
                        path=DISASTER_RUN_JSON_REL,
                        line=1,
                        message="fresh disaster suite rerun produced refusal cases without remediation hints.",
                        snippet=", ".join(str(item).strip() for item in list(fresh_report.get("remediation_missing_case_ids") or [])[:8] if str(item).strip()),
                        rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                    )
                )
            if run_report and _token(run_report.get("deterministic_fingerprint")) != _token(fresh_report.get("deterministic_fingerprint")):
                findings.append(
                    _finding_row(
                        category="disaster_suite.harness_mismatch",
                        path=DISASTER_RUN_JSON_REL,
                        line=1,
                        message="committed disaster suite run report drifted from the fresh deterministic rerun.",
                        snippet=_token(fresh_report.get("deterministic_fingerprint")),
                        rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                    )
                )
            if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != _token(fresh_baseline.get("deterministic_fingerprint")):
                findings.append(
                    _finding_row(
                        category="disaster_suite.harness_mismatch",
                        path=DISASTER_BASELINE_REL,
                        line=1,
                        message="committed disaster regression baseline drifted from the fresh deterministic rerun.",
                        snippet=_token(fresh_baseline.get("deterministic_fingerprint")),
                        rule_id="INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST",
                    )
                )

    return _check_result_payload(
        check_id="disaster_suite_scan",
        description="Verify required disaster suite surfaces, committed regression baseline integrity, remediation completeness, silent-fallback refusal behavior, and deterministic rerun stability.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "case_count": int(cases_record.get("case_count", 0) or 0),
            "cases_fingerprint": _token(cases_record.get("deterministic_fingerprint")),
            "run_fingerprint": _token(run_report.get("deterministic_fingerprint")),
            "baseline_fingerprint": _token(baseline_payload.get("deterministic_fingerprint")),
            "rerun_fingerprint": _token(fresh_report.get("deterministic_fingerprint")),
            "rerun_baseline_fingerprint": _token(fresh_baseline.get("deterministic_fingerprint")),
            "cases_match_expected": bool(_as_map(fresh_report).get("cases_match_expected")),
            "silent_success_case_count": len(list(_as_map(fresh_report).get("silent_success_case_ids") or list(run_report.get("silent_success_case_ids") or []))),
            "remediation_missing_case_count": len(list(_as_map(fresh_report).get("remediation_missing_case_ids") or list(run_report.get("remediation_missing_case_ids") or []))),
            "required_commit_tag": _token(_as_map(baseline_payload.get("update_policy")).get("required_commit_tag")),
        },
    )


def scan_ecosystem_verify(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    required_paths = [
        ECOSYSTEM_VERIFY_RETRO_AUDIT_REL,
        ECOSYSTEM_VERIFY_MODEL_DOC_REL,
        ECOSYSTEM_VERIFY_RUN_TOOL_REL,
        ECOSYSTEM_VERIFY_RUN_TOOL_PY_REL,
        ECOSYSTEM_VERIFY_RUN_JSON_REL,
        ECOSYSTEM_VERIFY_RUN_DOC_REL,
        ECOSYSTEM_VERIFY_BASELINE_REL,
        ECOSYSTEM_VERIFY_BASELINE_DOC_REL,
    ]
    scanned_paths = sorted(set(required_paths))
    findings: list[dict] = []

    for rel_path in required_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if abs_path and os.path.exists(abs_path):
            continue
        findings.append(
            _finding_row(
                category="ecosystem_verify.required_surface",
                path=rel_path,
                line=1,
                message="required ecosystem verify surface is missing.",
                rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
            )
        )

    run_payload = load_json_if_present(repo_root_abs, ECOSYSTEM_VERIFY_RUN_JSON_REL)
    baseline_payload = load_json_if_present(repo_root_abs, ECOSYSTEM_VERIFY_BASELINE_REL)
    fresh_report = {}
    fresh_baseline = {}

    try:
        from tools.mvp.ecosystem_verify_common import (
            ECOSYSTEM_REGRESSION_REQUIRED_TAG,
            ECOSYSTEM_VERIFY_BASELINE_SCHEMA_ID,
            ECOSYSTEM_VERIFY_RUN_SCHEMA_ID,
            build_ecosystem_verify_baseline,
            ecosystem_verify_baseline_hash,
            ecosystem_verify_report_hash,
            verify_ecosystem,
        )
    except Exception:
        findings.append(
            _finding_row(
                category="ecosystem_verify.tooling_missing",
                path=ECOSYSTEM_VERIFY_RUN_TOOL_PY_REL,
                line=1,
                message="ecosystem verify tooling could not be imported.",
                rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
            )
        )
    else:
        if run_payload and str(run_payload.get("schema_id", "")).strip() != ECOSYSTEM_VERIFY_RUN_SCHEMA_ID:
            findings.append(
                _finding_row(
                    category="ecosystem_verify.schema_invalid",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="ecosystem verify run report schema_id mismatch.",
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if baseline_payload and str(baseline_payload.get("schema_id", "")).strip() != ECOSYSTEM_VERIFY_BASELINE_SCHEMA_ID:
            findings.append(
                _finding_row(
                    category="ecosystem_verify.schema_invalid",
                    path=ECOSYSTEM_VERIFY_BASELINE_REL,
                    line=1,
                    message="ecosystem verify regression baseline schema_id mismatch.",
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if run_payload and _token(run_payload.get("deterministic_fingerprint")) != ecosystem_verify_report_hash(run_payload):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.run_fingerprint",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="ecosystem verify run report deterministic_fingerprint mismatch.",
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != ecosystem_verify_baseline_hash(baseline_payload):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.baseline_fingerprint",
                    path=ECOSYSTEM_VERIFY_BASELINE_REL,
                    line=1,
                    message="ecosystem verify regression baseline deterministic_fingerprint mismatch.",
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        required_tag = _token(_as_map(baseline_payload.get("update_policy")).get("required_commit_tag"))
        if baseline_payload and required_tag != ECOSYSTEM_REGRESSION_REQUIRED_TAG:
            findings.append(
                _finding_row(
                    category="ecosystem_verify.baseline_guard",
                    path=ECOSYSTEM_VERIFY_BASELINE_REL,
                    line=1,
                    message="ecosystem verify regression baseline is missing the required update tag guard.",
                    snippet=required_tag,
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )

        identity_coverage = _as_map(run_payload.get("identity_coverage"))
        migration_coverage = _as_map(run_payload.get("migration_coverage"))
        update_coverage = _as_map(run_payload.get("update_coverage"))
        resolved_profiles = [_as_map(row) for row in list(run_payload.get("resolved_profiles") or []) if isinstance(row, Mapping)]
        if run_payload and _token(run_payload.get("result")) != "complete":
            findings.append(
                _finding_row(
                    category="ecosystem_verify.run_mismatch",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="committed ecosystem verify run report is not passing.",
                    snippet=_token(run_payload.get("deterministic_fingerprint")),
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if identity_coverage and (
            _token(identity_coverage.get("result")) != "complete"
            or list(identity_coverage.get("invalid_identity_paths") or [])
            or list(identity_coverage.get("missing_identity_kind_ids") or [])
            or _token(_as_map(identity_coverage.get("binary_identity")).get("result")) != "complete"
        ):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.identity_missing",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="ecosystem verify identity coverage is incomplete.",
                    snippet=", ".join(str(item).strip() for item in list(identity_coverage.get("invalid_identity_paths") or identity_coverage.get("missing_identity_kind_ids") or [])[:8] if str(item).strip()),
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if migration_coverage and (
            _token(migration_coverage.get("result")) != "complete"
            or list(migration_coverage.get("missing_policy_ids") or [])
            or not bool(migration_coverage.get("read_only_decision_defined"))
        ):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.migration_missing",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="ecosystem verify migration coverage is incomplete.",
                    snippet=", ".join(str(item).strip() for item in list(migration_coverage.get("missing_policy_ids") or [])[:8] if str(item).strip()),
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if update_coverage and (
            _token(update_coverage.get("result")) != "complete"
            or list(update_coverage.get("selected_yanked_component_ids") or [])
            or not bool(update_coverage.get("deterministic_replay_match"))
        ):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.yanked_selectable",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="ecosystem verify update coverage is allowing or hiding a yanked selection path.",
                    snippet=", ".join(str(item).strip() for item in list(update_coverage.get("selected_yanked_component_ids") or [])[:8] if str(item).strip()),
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if resolved_profiles and any(_token(row.get("result")) != "complete" or not bool(row.get("deterministic_replay_match")) for row in resolved_profiles):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.resolution_nondeterministic",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="ecosystem verify profile resolution is incomplete or nondeterministic.",
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )

        fresh_report = dict(verify_ecosystem(repo_root_abs, platform_tag="win64") or {})
        fresh_baseline = dict(build_ecosystem_verify_baseline(fresh_report) or {})
        if run_payload and _token(run_payload.get("deterministic_fingerprint")) != _token(fresh_report.get("deterministic_fingerprint")):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.run_mismatch",
                    path=ECOSYSTEM_VERIFY_RUN_JSON_REL,
                    line=1,
                    message="committed ecosystem verify run report drifted from the fresh deterministic rerun.",
                    snippet=_token(fresh_report.get("deterministic_fingerprint")),
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )
        if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != _token(fresh_baseline.get("deterministic_fingerprint")):
            findings.append(
                _finding_row(
                    category="ecosystem_verify.run_mismatch",
                    path=ECOSYSTEM_VERIFY_BASELINE_REL,
                    line=1,
                    message="committed ecosystem verify regression baseline drifted from the fresh deterministic rerun.",
                    snippet=_token(fresh_baseline.get("deterministic_fingerprint")),
                    rule_id="INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST",
                )
            )

    return _check_result_payload(
        check_id="ecosystem_verify_scan",
        description="Verify required ecosystem surfaces, deterministic install-profile resolution, identity coverage, migration-policy coverage, trust-policy integration, and yanked-safe update planning.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "run_fingerprint": _token(run_payload.get("deterministic_fingerprint")),
            "baseline_fingerprint": _token(baseline_payload.get("deterministic_fingerprint")),
            "rerun_fingerprint": _token(_as_map(fresh_report).get("deterministic_fingerprint")),
            "rerun_baseline_fingerprint": _token(_as_map(fresh_baseline).get("deterministic_fingerprint")),
            "resolved_profile_count": len(list(run_payload.get("resolved_profiles") or [])),
            "identity_invalid_count": len(list(_as_map(run_payload.get("identity_coverage")).get("invalid_identity_paths") or [])),
            "missing_policy_count": len(list(_as_map(run_payload.get("migration_coverage")).get("missing_policy_ids") or [])),
            "selected_yanked_count": len(list(_as_map(run_payload.get("update_coverage")).get("selected_yanked_component_ids") or [])),
            "required_commit_tag": _token(_as_map(baseline_payload.get("update_policy")).get("required_commit_tag")),
        },
    )


def scan_update_sim(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    required_paths = [
        UPDATE_SIM_RETRO_AUDIT_REL,
        UPDATE_SIM_MODEL_DOC_REL,
        UPDATE_SIM_BASELINE_INDEX_REL,
        UPDATE_SIM_UPGRADE_INDEX_REL,
        UPDATE_SIM_YANKED_INDEX_REL,
        UPDATE_SIM_STRICT_INDEX_REL,
        UPDATE_SIM_RUN_TOOL_REL,
        UPDATE_SIM_RUN_TOOL_PY_REL,
        UPDATE_SIM_RUN_JSON_REL,
        UPDATE_SIM_RUN_DOC_REL,
        UPDATE_SIM_BASELINE_REL,
    ]
    scanned_paths = sorted(set(required_paths))
    findings: list[dict] = []

    for rel_path in required_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if abs_path and os.path.exists(abs_path):
            continue
        findings.append(
            _finding_row(
                category="update_sim.required_surface",
                path=rel_path,
                line=1,
                message="required update simulation surface is missing.",
                rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
            )
        )

    run_payload = load_json_if_present(repo_root_abs, UPDATE_SIM_RUN_JSON_REL)
    baseline_payload = load_json_if_present(repo_root_abs, UPDATE_SIM_BASELINE_REL)
    fresh_report = {}
    fresh_baseline = {}
    fixture_payloads = {
        UPDATE_SIM_BASELINE_INDEX_REL: load_json_if_present(repo_root_abs, UPDATE_SIM_BASELINE_INDEX_REL),
        UPDATE_SIM_UPGRADE_INDEX_REL: load_json_if_present(repo_root_abs, UPDATE_SIM_UPGRADE_INDEX_REL),
        UPDATE_SIM_YANKED_INDEX_REL: load_json_if_present(repo_root_abs, UPDATE_SIM_YANKED_INDEX_REL),
        UPDATE_SIM_STRICT_INDEX_REL: load_json_if_present(repo_root_abs, UPDATE_SIM_STRICT_INDEX_REL),
    }

    try:
        from tools.mvp.update_sim_common import (
            UPDATE_SIM_BASELINE_SCHEMA_ID,
            UPDATE_SIM_REGRESSION_REQUIRED_TAG,
            UPDATE_SIM_RUN_SCHEMA_ID,
            build_update_sim_baseline,
            build_update_sim_fixture_payloads,
            run_update_sim,
            update_sim_baseline_hash,
            update_sim_report_hash,
        )
    except Exception:
        findings.append(
            _finding_row(
                category="update_sim.tooling_missing",
                path=UPDATE_SIM_RUN_TOOL_PY_REL,
                line=1,
                message="update simulation tooling could not be imported.",
                rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
            )
        )
    else:
        if run_payload and _token(run_payload.get("schema_id")) != UPDATE_SIM_RUN_SCHEMA_ID:
            findings.append(
                _finding_row(
                    category="update_sim.schema_invalid",
                    path=UPDATE_SIM_RUN_JSON_REL,
                    line=1,
                    message="update simulation run report schema_id mismatch.",
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )
        if baseline_payload and _token(baseline_payload.get("schema_id")) != UPDATE_SIM_BASELINE_SCHEMA_ID:
            findings.append(
                _finding_row(
                    category="update_sim.schema_invalid",
                    path=UPDATE_SIM_BASELINE_REL,
                    line=1,
                    message="update simulation regression baseline schema_id mismatch.",
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )
        if run_payload and _token(run_payload.get("deterministic_fingerprint")) != update_sim_report_hash(run_payload):
            findings.append(
                _finding_row(
                    category="update_sim.run_fingerprint",
                    path=UPDATE_SIM_RUN_JSON_REL,
                    line=1,
                    message="update simulation run report deterministic_fingerprint mismatch.",
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )
        if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != update_sim_baseline_hash(baseline_payload):
            findings.append(
                _finding_row(
                    category="update_sim.baseline_fingerprint",
                    path=UPDATE_SIM_BASELINE_REL,
                    line=1,
                    message="update simulation regression baseline deterministic_fingerprint mismatch.",
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )
        required_tag = _token(_as_map(baseline_payload.get("update_policy")).get("required_commit_tag"))
        if baseline_payload and required_tag != UPDATE_SIM_REGRESSION_REQUIRED_TAG:
            findings.append(
                _finding_row(
                    category="update_sim.baseline_guard",
                    path=UPDATE_SIM_BASELINE_REL,
                    line=1,
                    message="update simulation regression baseline is missing the required update tag guard.",
                    snippet=required_tag,
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )

        expected_fixtures = build_update_sim_fixture_payloads(repo_root_abs)
        for fixture_id, rel_path in (
            ("baseline", UPDATE_SIM_BASELINE_INDEX_REL),
            ("upgrade", UPDATE_SIM_UPGRADE_INDEX_REL),
            ("yanked", UPDATE_SIM_YANKED_INDEX_REL),
            ("strict", UPDATE_SIM_STRICT_INDEX_REL),
        ):
            current = _as_map(fixture_payloads.get(rel_path))
            expected = _as_map(expected_fixtures.get(fixture_id))
            if current and canonical_json_text(current) == canonical_json_text(expected):
                continue
            findings.append(
                _finding_row(
                    category="update_sim.fixture_drift",
                    path=rel_path,
                    line=1,
                    message="committed update simulation fixture drifted from the deterministic fixture generator.",
                    snippet=_token(expected.get("deterministic_fingerprint")),
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )

        if run_payload and _token(run_payload.get("result")) != "complete":
            findings.append(
                _finding_row(
                    category="update_sim.run_mismatch",
                    path=UPDATE_SIM_RUN_JSON_REL,
                    line=1,
                    message="committed update simulation run report is not passing.",
                    snippet=_token(run_payload.get("deterministic_fingerprint")),
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )

        upgrade = _as_map(run_payload.get("latest_compatible_upgrade"))
        yanked = _as_map(run_payload.get("yanked_candidate_exclusion"))
        rollback = _as_map(run_payload.get("rollback_restore"))
        if list(yanked.get("selected_yanked_component_ids") or []) or int(yanked.get("skipped_yanked_count", 0) or 0) < 1:
            findings.append(
                _finding_row(
                    category="update_sim.yanked_selectable",
                    path=UPDATE_SIM_RUN_JSON_REL,
                    line=1,
                    message="update simulation recorded yanked selection or failed to log the yanked skip deterministically.",
                    snippet=", ".join(list(yanked.get("selected_yanked_component_ids") or [])) or _token(yanked.get("skipped_yanked_count")),
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )
        if rollback and not bool(rollback.get("rollback_matches_baseline")):
            findings.append(
                _finding_row(
                    category="update_sim.rollback_not_restoring",
                    path=UPDATE_SIM_RUN_JSON_REL,
                    line=1,
                    message="update simulation rollback did not restore the baseline component-set hash.",
                    snippet=_token(rollback.get("restored_component_set_hash")),
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )
        if upgrade and (
            (not bool(upgrade.get("update_required")) and _token(upgrade.get("installed_component_set_hash")) != _token(upgrade.get("prior_component_set_hash")))
            or (not list(upgrade.get("upgraded_component_ids") or []) and _token(upgrade.get("installed_component_set_hash")) != _token(upgrade.get("prior_component_set_hash")))
        ):
            findings.append(
                _finding_row(
                    category="update_sim.silent_upgrade",
                    path=UPDATE_SIM_RUN_JSON_REL,
                    line=1,
                    message="update simulation changed the installed component set without an explicit upgrade delta.",
                    snippet=_token(upgrade.get("installed_component_set_hash")),
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )

        fresh_report = dict(
            run_update_sim(
                repo_root_abs,
                output_root_rel=os.path.join("build", "tmp", "omega6_update_arch_audit"),
                write_outputs=False,
            )
            or {}
        )
        fresh_baseline = dict(build_update_sim_baseline(fresh_report) or {})
        if run_payload and _token(run_payload.get("deterministic_fingerprint")) != _token(fresh_report.get("deterministic_fingerprint")):
            findings.append(
                _finding_row(
                    category="update_sim.run_mismatch",
                    path=UPDATE_SIM_RUN_JSON_REL,
                    line=1,
                    message="committed update simulation run report drifted from the fresh deterministic rerun.",
                    snippet=_token(fresh_report.get("deterministic_fingerprint")),
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )
        if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != _token(fresh_baseline.get("deterministic_fingerprint")):
            findings.append(
                _finding_row(
                    category="update_sim.run_mismatch",
                    path=UPDATE_SIM_BASELINE_REL,
                    line=1,
                    message="committed update simulation regression baseline drifted from the fresh deterministic rerun.",
                    snippet=_token(fresh_baseline.get("deterministic_fingerprint")),
                    rule_id="INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST",
                )
            )

    return _check_result_payload(
        check_id="update_sim_scan",
        description="Verify required offline update simulation surfaces, fixture stability, yanked exclusion, strict trust refusal, rollback restoration, and regression baseline agreement.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "run_fingerprint": _token(run_payload.get("deterministic_fingerprint")),
            "baseline_fingerprint": _token(baseline_payload.get("deterministic_fingerprint")),
            "rerun_fingerprint": _token(_as_map(fresh_report).get("deterministic_fingerprint")),
            "rerun_baseline_fingerprint": _token(_as_map(fresh_baseline).get("deterministic_fingerprint")),
            "selected_yanked_count": len(list(_as_map(run_payload.get("yanked_candidate_exclusion")).get("selected_yanked_component_ids") or [])),
            "rollback_matches_baseline": bool(_as_map(run_payload.get("rollback_restore")).get("rollback_matches_baseline")),
            "required_commit_tag": _token(_as_map(baseline_payload.get("update_policy")).get("required_commit_tag")),
        },
    )


def scan_trust_strict_suite(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    required_paths = [
        TRUST_STRICT_RETRO_AUDIT_REL,
        TRUST_STRICT_MODEL_DOC_REL,
        LICENSE_CAPABILITY_SCHEMA_REL,
        LICENSE_CAPABILITY_SCHEMA_JSON_REL,
        TRUST_STRICT_UNSIGNED_RELEASE_INDEX_REL,
        TRUST_STRICT_SIGNED_RELEASE_INDEX_REL,
        TRUST_STRICT_UNSIGNED_PACK_REL,
        TRUST_STRICT_SIGNED_LICENSE_REL,
        TRUST_STRICT_RUN_TOOL_REL,
        TRUST_STRICT_RUN_TOOL_PY_REL,
        TRUST_STRICT_RUN_JSON_REL,
        TRUST_STRICT_RUN_DOC_REL,
        TRUST_STRICT_BASELINE_REL,
        TRUST_STRICT_BASELINE_DOC_REL,
    ]
    scanned_paths = sorted(set(required_paths))
    findings: list[dict] = []

    for rel_path in required_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        if abs_path and os.path.exists(abs_path):
            continue
        findings.append(
            _finding_row(
                category="trust_strict.required_surface",
                path=rel_path,
                line=1,
                message="required trust strict surface is missing.",
                rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST",
            )
        )

    run_payload = load_json_if_present(repo_root_abs, TRUST_STRICT_RUN_JSON_REL)
    baseline_payload = load_json_if_present(repo_root_abs, TRUST_STRICT_BASELINE_REL)
    fresh_report = {}
    fresh_baseline = {}

    try:
        from tools.security.trust_strict_common import (
            TRUST_STRICT_BASELINE_SCHEMA_ID,
            TRUST_STRICT_REQUIRED_TAG,
            TRUST_STRICT_RUN_SCHEMA_ID,
            build_trust_fixture_payloads,
            build_trust_strict_baseline,
            run_trust_strict_suite,
            trust_strict_baseline_hash,
            trust_strict_run_hash,
        )
    except Exception:
        findings.append(
            _finding_row(
                category="trust_strict.required_surface",
                path=TRUST_STRICT_RUN_TOOL_PY_REL,
                line=1,
                message="trust strict tooling could not be imported.",
                rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST",
            )
        )
    else:
        if run_payload and _token(run_payload.get("schema_id")) != TRUST_STRICT_RUN_SCHEMA_ID:
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_RUN_JSON_REL, line=1, message="trust strict run schema_id mismatch.", rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))
        if baseline_payload and _token(baseline_payload.get("schema_id")) != TRUST_STRICT_BASELINE_SCHEMA_ID:
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_BASELINE_REL, line=1, message="trust strict baseline schema_id mismatch.", rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))
        if run_payload and _token(run_payload.get("deterministic_fingerprint")) != trust_strict_run_hash(run_payload):
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_RUN_JSON_REL, line=1, message="trust strict run deterministic_fingerprint mismatch.", rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))
        if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != trust_strict_baseline_hash(baseline_payload):
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_BASELINE_REL, line=1, message="trust strict baseline deterministic_fingerprint mismatch.", rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))
        if baseline_payload and _token(baseline_payload.get("required_update_tag")) != TRUST_STRICT_REQUIRED_TAG:
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_BASELINE_REL, line=1, message="trust strict baseline is missing the required regression update tag.", snippet=_token(baseline_payload.get("required_update_tag")), rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))

        expected_fixtures = build_trust_fixture_payloads(repo_root_abs)
        for fixture_id, rel_path in (
            ("unsigned_release_index", TRUST_STRICT_UNSIGNED_RELEASE_INDEX_REL),
            ("signed_release_index", TRUST_STRICT_SIGNED_RELEASE_INDEX_REL),
            ("unsigned_official_pack", TRUST_STRICT_UNSIGNED_PACK_REL),
            ("signed_license_capability", TRUST_STRICT_SIGNED_LICENSE_REL),
        ):
            current = load_json_if_present(repo_root_abs, rel_path)
            expected = _as_map(expected_fixtures.get(fixture_id))
            if current and canonical_json_text(current) == canonical_json_text(expected):
                continue
            findings.append(
                _finding_row(
                    category="trust_strict.required_surface",
                    path=rel_path,
                    line=1,
                    message="committed trust strict fixture drifted from the deterministic generator.",
                    snippet=_token(expected.get("deterministic_fingerprint")),
                    rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )

        if run_payload and _token(run_payload.get("result")) != "complete":
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_RUN_JSON_REL, line=1, message="committed trust strict run report is not passing.", snippet=_token(run_payload.get("deterministic_fingerprint")), rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))

        case_rows = { _token(_as_map(row).get("case_id")): _as_map(row) for row in list(run_payload.get("cases") or []) }
        strict_release = case_rows.get("strict_ranked_refuses_unsigned_release_index", {})
        strict_pack = case_rows.get("strict_ranked_refuses_unsigned_official_pack", {})
        license_case = case_rows.get("license_capability_requires_trusted_signature", {})
        display_case = case_rows.get("license_capability_availability_display", {})

        for case_id, row in (("strict_ranked_refuses_unsigned_release_index", strict_release), ("strict_ranked_refuses_unsigned_official_pack", strict_pack)):
            if _token(row.get("result")) == "complete":
                continue
            findings.append(
                _finding_row(
                    category="trust_strict.strict_allows_unsigned",
                    path=TRUST_STRICT_RUN_JSON_REL,
                    line=1,
                    message="strict trust case '{}' no longer refuses unsigned governed artifacts deterministically.".format(case_id),
                    snippet=_token(row.get("refusal_code")),
                    rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )

        license_details = _as_map(license_case.get("details"))
        if _token(license_case.get("result")) != "complete" or "signer.fixture.official" not in list(license_details.get("trusted_signer_ids") or []):
            findings.append(
                _finding_row(
                    category="trust_strict.license_capability_not_signed",
                    path=TRUST_STRICT_RUN_JSON_REL,
                    line=1,
                    message="license capability acceptance no longer proves a trusted signed artifact path.",
                    snippet=_token(license_case.get("refusal_code")),
                    rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )
        display_details = _as_map(display_case.get("details"))
        if _token(display_case.get("result")) != "complete" or not list(display_details.get("available_capability_ids") or []):
            findings.append(
                _finding_row(
                    category="trust_strict.required_surface",
                    path=TRUST_STRICT_RUN_JSON_REL,
                    line=1,
                    message="license capability availability display drifted from the frozen baseline behavior.",
                    snippet=_token(_as_map(display_case.get("details")).get("display_fingerprint")),
                    rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST",
                )
            )

        fresh_report = dict(run_trust_strict_suite(repo_root_abs, write_outputs=False) or {})
        fresh_baseline = dict(build_trust_strict_baseline(fresh_report) or {})
        if run_payload and _token(run_payload.get("deterministic_fingerprint")) != _token(fresh_report.get("deterministic_fingerprint")):
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_RUN_JSON_REL, line=1, message="committed trust strict run report drifted from the fresh deterministic rerun.", snippet=_token(fresh_report.get("deterministic_fingerprint")), rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))
        if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != _token(fresh_baseline.get("deterministic_fingerprint")):
            findings.append(_finding_row(category="trust_strict.required_surface", path=TRUST_STRICT_BASELINE_REL, line=1, message="committed trust strict baseline drifted from the fresh deterministic rerun.", snippet=_token(fresh_baseline.get("deterministic_fingerprint")), rule_id="INV-TRUST-STRICT-SUITE-MUST-PASS-BEFORE-DIST"))

    return _check_result_payload(
        check_id="trust_strict_scan",
        description="Verify frozen strict trust surfaces, offline fixtures, commercialization hook signing behavior, and regression baseline agreement.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "run_fingerprint": _token(run_payload.get("deterministic_fingerprint")),
            "baseline_fingerprint": _token(baseline_payload.get("deterministic_fingerprint")),
            "rerun_fingerprint": _token(_as_map(fresh_report).get("deterministic_fingerprint")),
            "rerun_baseline_fingerprint": _token(_as_map(fresh_baseline).get("deterministic_fingerprint")),
            "case_count": len(list(run_payload.get("cases") or [])),
            "required_commit_tag": _token(baseline_payload.get("required_update_tag")),
        },
    )


def scan_noncanonical_numeric_serialization(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, NUMERIC_SERIALIZATION_TARGETS)
    findings: list[dict] = []
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if "canonical_json_text(" in snippet or "canonical_sha256(" in snippet:
                continue
            if not any(pattern.search(snippet) for pattern in NONCANONICAL_NUMERIC_SERIALIZATION_PATTERNS):
                continue
            findings.append(
                _finding_row(
                    category="numeric.noncanonical_serialization",
                    path=rel_path,
                    line=line_no,
                    message="numeric serialization in governed manifests and descriptors must use canonical serializers and must not rely on ad hoc float formatting.",
                    snippet=snippet,
                    rule_id="INV-CANONICAL-NUMERIC-SERIALIZATION",
                )
            )
    return _check_result_payload(
        check_id="noncanonical_serialization_scan",
        description="Detect non-canonical numeric formatting and non-canonical JSON serialization in governed numeric/identity surfaces.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
    )


def scan_compiler_flags(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    defaults = list(COMPILER_FLAG_SCAN_FILES)
    defaults.extend(_iter_repo_files_by_suffix(repo_root_abs, (".cmake", ".vcxproj", ".props", ".targets", ".mk", ".sln")))
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, defaults)
    findings: list[dict] = []
    hit_count = 0
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        text = _read_text(abs_path)
        if not text:
            continue
        found_tokens = [token for token in UNSAFE_FLOAT_FLAG_TOKENS if token in text]
        if not found_tokens:
            continue
        hit_count += len(found_tokens)
        findings.append(
            _finding_row(
                category="numeric.compiler_flags",
                path=rel_path,
                line=1,
                message="build configuration must not enable compiler flags that relax floating-point determinism.",
                snippet=",".join(found_tokens[:6]),
                rule_id="INV-SAFE-FLOAT-COMPILER-FLAGS",
            )
        )
    return _check_result_payload(
        check_id="compiler_flag_scan",
        description="Scan build configuration surfaces for unsafe floating-point compiler flags and host-tuned numeric settings.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"unsafe_flag_hit_count": hit_count},
    )


def scan_parallel_truth(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, _iter_python_files(repo_root_abs, PARALLEL_TRUTH_TARGETS))
    findings: list[dict] = []
    primitive_hits = 0
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(token in snippet for token in CONCURRENCY_PRIMITIVE_TOKENS):
                continue
            primitive_hits += 1
            findings.append(
                _finding_row(
                    category="concurrency.parallel_truth",
                    path=rel_path,
                    line=line_no,
                    message="truth-side execution must not introduce ad hoc threaded or pooled execution without a deterministic shard merge contract.",
                    snippet=snippet,
                    rule_id="INV-NO-PARALLEL-TRUTH-WITHOUT-SHARD-MERGE",
                )
            )
            break
    return _check_result_payload(
        check_id="parallel_truth_scan",
        description="Detect threaded or pooled execution primitives in governed truth-side execution paths.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"parallel_primitive_hit_count": primitive_hits},
    )


def scan_parallel_output_canonicalization(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    defaults = list(PARALLEL_OUTPUT_TARGETS)
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, defaults)
    findings: list[dict] = []
    known: list[dict] = []
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        text = _read_text(abs_path)
        if not text:
            continue
        required_tokens = list(PARALLEL_OUTPUT_REQUIRED_TOKENS.get(rel_path) or [])
        if required_tokens:
            missing = [token for token in required_tokens if token not in text]
            if missing:
                findings.append(
                    _finding_row(
                        category="concurrency.parallel_output",
                        path=rel_path,
                        line=1,
                        message="parallel derived or validation output must be canonicalized before hashing or persistence.",
                        snippet="missing_tokens={}".format(",".join(missing[:4])),
                        rule_id="INV-PARALLEL-DERIVED-MUST-CANONICALIZE",
                    )
                )
            else:
                known.append(
                    _finding_row(
                        category="concurrency.parallel_output_safe_surface",
                        path=rel_path,
                        line=1,
                        message="parallel surface canonicalizes output ordering before hashing or persistence.",
                        snippet="canonical_parallel_surface",
                        classification="known_exception",
                        rule_id="INV-PARALLEL-DERIVED-MUST-CANONICALIZE",
                    )
                )
            continue
        if any(token in text for token in CONCURRENCY_PRIMITIVE_TOKENS) and "sorted(" not in text and "canonicalize_parallel_mapping_rows(" not in text:
            findings.append(
                _finding_row(
                    category="concurrency.parallel_output",
                    path=rel_path,
                    line=1,
                    message="parallel output surface uses concurrency primitives without an obvious canonicalization step.",
                    snippet="missing_sorted_or_canonical_merge",
                    rule_id="INV-PARALLEL-DERIVED-MUST-CANONICALIZE",
                )
            )
    return _check_result_payload(
        check_id="parallel_output_scan",
        description="Verify that known parallel derived and validation surfaces canonicalize merged output ordering.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        known_exceptions=known,
    )


def scan_truth_atomic_usage(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, _iter_python_files(repo_root_abs, TRUTH_ATOMIC_TARGETS))
    findings: list[dict] = []
    atomic_hit_count = 0
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        for line_no, line in enumerate(_read_text(abs_path).splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            lower = snippet.lower()
            if not any(token in lower for token in TRUTH_ATOMIC_TOKENS):
                continue
            atomic_hit_count += 1
            findings.append(
                _finding_row(
                    category="concurrency.truth_atomic",
                    path=rel_path,
                    line=line_no,
                    message="truth-side execution must not rely on atomic or interlocked timing semantics to decide outcomes.",
                    snippet=snippet,
                    rule_id="INV-NO-PARALLEL-TRUTH-WITHOUT-SHARD-MERGE",
                )
            )
            break
    return _check_result_payload(
        check_id="truth_atomic_scan",
        description="Detect atomic-style timing primitives in governed truth-side execution paths.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"truth_atomic_hit_count": atomic_hit_count},
    )


def scan_stability_markers(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    report = validate_all_registries(repo_root_abs)
    findings: list[dict] = []
    scanned_paths: list[str] = []
    for registry_report in list(report.get("reports") or []):
        row = dict(registry_report or {})
        rel_path = _norm(row.get("file_path", ""))
        if rel_path:
            scanned_paths.append(rel_path)
        for error in list(row.get("errors") or []):
            error_row = dict(error or {})
            findings.append(
                _finding_row(
                    category="stability_markers",
                    path=rel_path,
                    line=1,
                    message=_token(error_row.get("message")) or "stability validation failed",
                    snippet=_token(error_row.get("path")),
                )
            )
    return _check_result_payload(
        check_id="stability_marker_scan",
        description="Validate META-STABILITY markers for all governed registries.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"validator_fingerprint": _token(report.get("deterministic_fingerprint"))},
    )


def scan_contract_pins(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    findings: list[dict] = []
    scanned_paths: list[str] = []
    for rel_path, tokens in sorted(CONTRACT_PIN_TARGETS.items(), key=lambda item: item[0]):
        abs_path = _repo_abs(repo_root_abs, rel_path)
        scanned_paths.append(_norm(rel_path))
        text = _read_text(abs_path)
        if not text:
            findings.append(
                _finding_row(
                    category="contract_pin",
                    path=_norm(rel_path),
                    line=1,
                    message="Required contract-pin surface is missing or unreadable.",
                    snippet=_norm(rel_path),
                )
            )
            continue
        for token in list(tokens or []):
            if str(token) in text:
                continue
            findings.append(
                _finding_row(
                    category="contract_pin",
                    path=_norm(rel_path),
                    line=1,
                    message="Contract-pin surface is missing required token '{}'.".format(token),
                    snippet=str(token),
                )
            )
    return _check_result_payload(
        check_id="contract_pin_scan",
        description="Verify that UniverseIdentity and session boot surfaces pin the contract bundle.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"target_count": len(CONTRACT_PIN_TARGETS)},
    )


def scan_pack_compat(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    findings: list[dict] = []
    scanned_paths: list[str] = []
    validated_reports: list[dict] = []
    packs_root = _repo_abs(repo_root_abs, "packs")
    if os.path.isdir(packs_root):
        for root, dirs, files in os.walk(packs_root):
            dirs[:] = sorted(dirs)
            file_names = sorted(files)
            if "pack.json" not in file_names:
                continue
            rel_dir = _norm(os.path.relpath(root, repo_root_abs))
            compat_path = os.path.join(root, "pack.compat.json")
            if not os.path.isfile(compat_path):
                findings.append(
                    _finding_row(
                        category="pack_compat",
                        path=rel_dir,
                        line=1,
                        message="Strict pack governance requires pack.compat.json beside pack.json.",
                        snippet="pack.compat.json",
                    )
                )
                continue
            rel_compat = _norm(os.path.relpath(compat_path, repo_root_abs))
            scanned_paths.append(rel_compat)
            report = validate_pack_compat(compat_path)
            validated_reports.append(
                {
                    "file_path": rel_compat,
                    "result": _token(report.get("result")),
                    "stability_present": bool(report.get("stability_present", False)),
                    "deterministic_fingerprint": _token(report.get("deterministic_fingerprint")),
                }
            )
            for error in list(report.get("errors") or []):
                error_row = dict(error or {})
                findings.append(
                    _finding_row(
                        category="pack_compat",
                        path=rel_compat,
                        line=1,
                        message=_token(error_row.get("message")) or "pack compatibility validation failed",
                        snippet=_token(error_row.get("path")),
                    )
                )
    return _check_result_payload(
        check_id="pack_compat_scan",
        description="Verify strict pack compatibility manifest presence and stability metadata validity.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "validated_manifest_count": len(validated_reports),
            "validated_manifests": sorted(validated_reports, key=lambda row: _token(row.get("file_path"))),
        },
    )


def scan_dist_bundle_composition(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, DIST_COMPOSITION_TARGETS)
    findings: list[dict] = []
    governance_violations: list[dict] = []
    try:
        from tools.release.component_graph_common import component_graph_violations
        from tools.release.install_profile_common import install_profile_violations
    except Exception as exc:
        findings.append(
            _finding_row(
                category="dist_bundle_composition",
                path="tools/audit/arch_audit_common.py",
                line=1,
                message="unable to import component graph/install profile governance helpers ({})".format(str(exc)),
                snippet="component_graph_violations install_profile_violations",
                rule_id="INV-DIST-USES-COMPONENT-GRAPH",
            )
        )
    else:
        governance_violations.extend(component_graph_violations(repo_root_abs))
        governance_violations.extend(install_profile_violations(repo_root_abs))
    findings.extend(
        _violation_finding_rows(
            governance_violations,
            default_category="dist_bundle_composition",
            default_message="distribution composition governance drift detected",
            fallback_rule_id="INV-DIST-USES-COMPONENT-GRAPH",
        )
    )
    hardcoded_count = 0
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        text = _read_text(abs_path)
        if not text:
            continue
        if DIST_COMPONENT_LITERAL_RE.search(text) and "build_default_component_install_plan(" not in text and "resolve_component_graph(" not in text:
            hardcoded_count += 1
            findings.append(
                _finding_row(
                    category="dist_bundle_composition",
                    path=rel_path,
                    line=1,
                    message="distribution composition must derive from the component graph and install profiles, not hardcoded component lists.",
                    snippet="hardcoded_component_selector_list",
                    rule_id="INV-NO-HARDCODED-COMPONENT-SETS",
                )
            )
    return _check_result_payload(
        check_id="dist_bundle_composition_scan",
        description="Ensure distribution assembly derives bundle contents from the component graph and install profiles, not hardcoded component sets.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "governance_violation_count": len(governance_violations),
            "hardcoded_component_list_count": hardcoded_count,
        },
    )


def scan_update_model(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _existing_paths(repo_root_abs, UPDATE_MODEL_TARGETS)
    findings: list[dict] = []
    governance_violations: list[dict] = []
    try:
        from tools.release.update_model_common import update_model_violations
    except Exception as exc:
        findings.append(
            _finding_row(
                category="update_model",
                path="tools/release/update_model_common.py",
                line=1,
                message="unable to import update-model governance helpers ({})".format(str(exc)),
                snippet="update_model_violations",
                rule_id="INV-UPDATES-USE-RELEASE-INDEX",
            )
        )
    else:
        governance_violations.extend(update_model_violations(repo_root_abs))
    findings.extend(
        _violation_finding_rows(
            governance_violations,
            default_category="update_model",
            default_message="update-model governance drift detected",
            fallback_rule_id="INV-UPDATES-USE-RELEASE-INDEX",
        )
    )
    direct_download_hits = 0
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        text = _read_text(abs_path)
        if not text:
            continue
        for token in ("requests.", "urllib.request", "http.client", "download_file(", "curl "):
            if token not in text:
                continue
            direct_download_hits += 1
            findings.append(
                _finding_row(
                    category="update_model",
                    path=rel_path,
                    line=1,
                    message="update logic must resolve from release_index data and verification plans, not direct download calls in core logic.",
                    snippet=token,
                    rule_id="INV-UPDATES-USE-RELEASE-INDEX",
                )
            )
    return _check_result_payload(
        check_id="update_model_scan",
        description="Ensure update resolution is release-index-driven, component-graph-resolved, and free of direct download shortcuts.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "governance_violation_count": len(governance_violations),
            "direct_download_token_count": direct_download_hits,
        },
    )


def scan_trust_bypass(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, TRUST_TARGETS)
    findings: list[dict] = []
    governance_violations: list[dict] = []
    try:
        from tools.security.trust_model_common import trust_model_violations
    except Exception as exc:
        findings.append(
            _finding_row(
                category="trust_bypass",
                path="tools/security/trust_model_common.py",
                line=1,
                message="unable to import trust-model governance helpers ({})".format(str(exc)),
                snippet="trust_model_violations",
                rule_id="INV-TRUST-VERIFY-NONBYPASS",
            )
        )
    else:
        governance_violations.extend(trust_model_violations(repo_root_abs))
    findings.extend(
        _violation_finding_rows(
            governance_violations,
            default_category="trust_bypass",
            default_message="trust verification governance drift detected",
            fallback_rule_id="INV-TRUST-VERIFY-NONBYPASS",
        )
    )
    bypass_hits = 0
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        text = _read_text(abs_path)
        if not text:
            continue
        for token in TRUST_BYPASS_FORBIDDEN:
            if token not in text:
                continue
            bypass_hits += 1
            findings.append(
                _finding_row(
                    category="trust_bypass",
                    path=rel_path,
                    line=1,
                    message="trust and verification logic must not contain explicit bypass toggles or unsigned-acceptance shortcuts.",
                    snippet=token,
                    rule_id="INV-TRUST-VERIFY-NONBYPASS",
                )
            )
        if any(marker in text for marker in ("trust_policy_id", "signature", "content_hash")) and not any(
            marker in text for marker in ("verify_artifact_trust(", "verify_release_manifest(", "verify_pack_root(")
        ):
            bypass_hits += 1
            findings.append(
                _finding_row(
                    category="trust_bypass",
                    path=rel_path,
                    line=1,
                    message="artifact-acceptance code that reasons about trust inputs must route through trust verification helpers.",
                    snippet="missing_verify_artifact_trust",
                    rule_id="INV-TRUST-VERIFY-NONBYPASS",
                )
            )
    return _check_result_payload(
        check_id="trust_bypass_scan",
        description="Ensure hashes are mandatory, signatures are enforced per policy, and no trust-verification bypass exists.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "governance_violation_count": len(governance_violations),
            "trust_bypass_token_count": bypass_hits,
        },
    )


def scan_target_matrix(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _existing_paths(repo_root_abs, TARGET_MATRIX_TARGETS)
    findings: list[dict] = []
    governance_violations: list[dict] = []
    try:
        from tools.release.arch_matrix_common import arch_matrix_violations
    except Exception as exc:
        findings.append(
            _finding_row(
                category="target_matrix",
                path="tools/release/arch_matrix_common.py",
                line=1,
                message="unable to import target-matrix governance helpers ({})".format(str(exc)),
                snippet="arch_matrix_violations",
                rule_id="INV-TIER3-NOT-DOWNLOADABLE",
            )
        )
    else:
        governance_violations.extend(arch_matrix_violations(repo_root_abs))
    findings.extend(
        _violation_finding_rows(
            governance_violations,
            default_category="target_matrix",
            default_message="target-matrix governance drift detected",
            fallback_rule_id="INV-TIER3-NOT-DOWNLOADABLE",
        )
    )
    return _check_result_payload(
        check_id="target_matrix_scan",
        description="Ensure release indices honor target tiers and platform claims match the declared target matrix.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={"governance_violation_count": len(governance_violations)},
    )


def scan_archive_determinism(repo_root: str, override_paths: Sequence[str] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scanned_paths = _iter_override_paths(repo_root_abs, override_paths, _iter_python_files(repo_root_abs, ARCHIVE_DETERMINISM_TARGETS))
    findings: list[dict] = []
    archive_token_count = 0
    timestamp_token_count = 0
    for rel_path in scanned_paths:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        text = _read_text(abs_path)
        if not text:
            continue
        found_archive = sorted(token for token in ARCHIVE_DETERMINISM_FORBIDDEN if token in text)
        found_timestamps = sorted(token for token in ARCHIVE_TIMESTAMP_FORBIDDEN if token in text)
        archive_token_count += len(found_archive)
        timestamp_token_count += len(found_timestamps)
        if not found_archive or not found_timestamps:
            continue
        findings.append(
            _finding_row(
                category="archive_determinism",
                path=rel_path,
                line=1,
                message="archive tooling must not mix archive generation with timestamp or mtime-dependent metadata.",
                snippet="archives={} timestamps={}".format(",".join(found_archive[:4]), ",".join(found_timestamps[:4])),
                rule_id="INV-DIST-USES-COMPONENT-GRAPH",
            )
        )
    return _check_result_payload(
        check_id="archive_determinism_scan",
        description="Search governed distribution/update tooling for archive generation paths that would embed timestamps or non-deterministic ordering metadata.",
        scanned_paths=scanned_paths,
        blocking_findings=findings,
        inventory={
            "archive_token_count": archive_token_count,
            "timestamp_token_count": timestamp_token_count,
        },
    )


def scan_offline_archive(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    findings: list[dict] = []
    fresh_build = {}
    fresh_verify = {}
    fresh_baseline = {}
    verify_payload = {}
    baseline_payload = {}
    required_paths = []

    try:
        from tools.release.offline_archive_common import (
            OFFLINE_ARCHIVE_BASELINE_DOC_REL,
            OFFLINE_ARCHIVE_BASELINE_REL,
            OFFLINE_ARCHIVE_BASELINE_SCHEMA_ID,
            OFFLINE_ARCHIVE_BUILD_TOOL_PY_REL,
            OFFLINE_ARCHIVE_BUILD_TOOL_REL,
            OFFLINE_ARCHIVE_MODEL_DOC_REL,
            OFFLINE_ARCHIVE_REQUIRED_TAG,
            OFFLINE_ARCHIVE_RETRO_AUDIT_REL,
            OFFLINE_ARCHIVE_VERIFY_DOC_REL,
            OFFLINE_ARCHIVE_VERIFY_JSON_REL,
            OFFLINE_ARCHIVE_VERIFY_SCHEMA_ID,
            OFFLINE_ARCHIVE_VERIFY_TOOL_PY_REL,
            OFFLINE_ARCHIVE_VERIFY_TOOL_REL,
            build_archive_baseline,
            build_offline_archive,
            load_offline_archive_baseline,
            load_offline_archive_verify,
            offline_archive_baseline_hash,
            offline_archive_verify_hash,
            verify_offline_archive,
        )
    except Exception:
        return _check_result_payload(
            check_id="offline_archive_scan",
            description="Verify frozen offline archive build and verification surfaces.",
            scanned_paths=[],
            blocking_findings=[
                _finding_row(
                    category="offline_archive.required_surface",
                    path="tools/release/offline_archive_common.py",
                    line=1,
                    message="offline archive tooling could not be imported.",
                    rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE",
                )
            ],
            inventory={},
        )

    required_paths = [
        OFFLINE_ARCHIVE_RETRO_AUDIT_REL,
        OFFLINE_ARCHIVE_MODEL_DOC_REL,
        OFFLINE_ARCHIVE_BUILD_TOOL_REL,
        OFFLINE_ARCHIVE_BUILD_TOOL_PY_REL,
        OFFLINE_ARCHIVE_VERIFY_TOOL_REL,
        OFFLINE_ARCHIVE_VERIFY_TOOL_PY_REL,
        OFFLINE_ARCHIVE_VERIFY_JSON_REL,
        OFFLINE_ARCHIVE_VERIFY_DOC_REL,
        OFFLINE_ARCHIVE_BASELINE_REL,
        OFFLINE_ARCHIVE_BASELINE_DOC_REL,
    ]
    for rel_path in required_paths:
        if os.path.exists(_repo_abs(repo_root_abs, rel_path)):
            continue
        findings.append(
            _finding_row(
                category="offline_archive.required_surface",
                path=rel_path,
                line=1,
                message="required offline archive surface is missing.",
                rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE",
            )
        )

    verify_payload = load_offline_archive_verify(repo_root_abs)
    baseline_payload = load_offline_archive_baseline(repo_root_abs)
    if verify_payload and _token(verify_payload.get("schema_id")) != OFFLINE_ARCHIVE_VERIFY_SCHEMA_ID:
        findings.append(_finding_row(category="offline_archive.required_surface", path=OFFLINE_ARCHIVE_VERIFY_JSON_REL, line=1, message="offline archive verify schema_id mismatch.", rule_id="INV-OFFLINE-ARCHIVE-VERIFY-MUST-PASS"))
    if baseline_payload and _token(baseline_payload.get("schema_id")) != OFFLINE_ARCHIVE_BASELINE_SCHEMA_ID:
        findings.append(_finding_row(category="offline_archive.required_surface", path=OFFLINE_ARCHIVE_BASELINE_REL, line=1, message="offline archive baseline schema_id mismatch.", rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE"))
    if verify_payload and _token(verify_payload.get("deterministic_fingerprint")) != offline_archive_verify_hash(verify_payload):
        findings.append(_finding_row(category="offline_archive.nondeterministic_archive", path=OFFLINE_ARCHIVE_VERIFY_JSON_REL, line=1, message="offline archive verify deterministic_fingerprint mismatch.", rule_id="INV-OFFLINE-ARCHIVE-VERIFY-MUST-PASS"))
    if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != offline_archive_baseline_hash(baseline_payload):
        findings.append(_finding_row(category="offline_archive.nondeterministic_archive", path=OFFLINE_ARCHIVE_BASELINE_REL, line=1, message="offline archive baseline deterministic_fingerprint mismatch.", rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE"))
    if baseline_payload and _token(baseline_payload.get("required_update_tag")) != OFFLINE_ARCHIVE_REQUIRED_TAG:
        findings.append(_finding_row(category="offline_archive.required_surface", path=OFFLINE_ARCHIVE_BASELINE_REL, line=1, message="offline archive baseline is missing the required regression update tag.", snippet=_token(baseline_payload.get("required_update_tag")), rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE"))

    if verify_payload and _token(verify_payload.get("result")) != "complete":
        findings.append(
            _finding_row(
                category="offline_archive.verify_failed",
                path=OFFLINE_ARCHIVE_VERIFY_JSON_REL,
                line=1,
                message="committed offline archive verify report is not passing.",
                snippet=_token(verify_payload.get("deterministic_fingerprint")),
                rule_id="INV-OFFLINE-ARCHIVE-VERIFY-MUST-PASS",
            )
        )

    for row in list(_as_map(verify_payload).get("errors") or []):
        item = _as_map(row)
        code = _token(item.get("code"))
        if code in {"archive_artifact_missing", "archive_support_surface_missing"}:
            findings.append(
                _finding_row(
                    category="offline_archive.missing_archive_artifact",
                    path=_token(item.get("path")) or OFFLINE_ARCHIVE_VERIFY_JSON_REL,
                    line=1,
                    message=_token(item.get("message")) or "offline archive is missing a required archived artifact",
                    snippet=code,
                    rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE",
                )
            )

    try:
        fresh_build = build_offline_archive(
            repo_root_abs,
            output_root_rel=os.path.join("build", "tmp", "omega8_archive_arch_audit"),
        )
        fresh_verify = verify_offline_archive(repo_root_abs, archive_path=_token(fresh_build.get("archive_bundle_path")), baseline_path="")
        fresh_baseline = build_archive_baseline(fresh_build, fresh_verify)
    except Exception as exc:
        findings.append(
            _finding_row(
                category="offline_archive.verify_failed",
                path=OFFLINE_ARCHIVE_VERIFY_JSON_REL,
                line=1,
                message="fresh offline archive build/verify rerun failed ({}).".format(str(exc)),
                rule_id="INV-OFFLINE-ARCHIVE-VERIFY-MUST-PASS",
            )
        )
    else:
        if _token(fresh_verify.get("result")) != "complete":
            findings.append(
                _finding_row(
                    category="offline_archive.verify_failed",
                    path=OFFLINE_ARCHIVE_VERIFY_JSON_REL,
                    line=1,
                    message="fresh offline archive verify rerun is not passing.",
                    snippet=_token(fresh_verify.get("deterministic_fingerprint")),
                    rule_id="INV-OFFLINE-ARCHIVE-VERIFY-MUST-PASS",
                )
            )
        for row in list(_as_map(fresh_verify).get("errors") or []):
            item = _as_map(row)
            code = _token(item.get("code"))
            if code in {"archive_artifact_missing", "archive_support_surface_missing"}:
                findings.append(
                    _finding_row(
                        category="offline_archive.missing_archive_artifact",
                        path=_token(item.get("path")) or OFFLINE_ARCHIVE_VERIFY_JSON_REL,
                        line=1,
                        message=_token(item.get("message")) or "fresh offline archive rerun is missing a required archived artifact",
                        snippet=code,
                        rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE",
                    )
                )
        for field_name, rel_path in (
            ("archive_bundle_hash", OFFLINE_ARCHIVE_BASELINE_REL),
            ("archive_record_hash", OFFLINE_ARCHIVE_BASELINE_REL),
            ("archive_projection_hash", OFFLINE_ARCHIVE_BASELINE_REL),
            ("deterministic_fingerprint", OFFLINE_ARCHIVE_VERIFY_JSON_REL),
        ):
            committed = _token(_as_map(baseline_payload if "archive_" in field_name else verify_payload).get(field_name))
            fresh = _token(_as_map(fresh_baseline if "archive_" in field_name else fresh_verify).get(field_name))
            if committed and committed != fresh:
                findings.append(
                    _finding_row(
                        category="offline_archive.nondeterministic_archive",
                        path=rel_path,
                        line=1,
                        message="committed offline archive surface drifted from the fresh deterministic rerun.",
                        snippet="{} != {}".format(committed, fresh),
                        rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE" if "archive_" in field_name else "INV-OFFLINE-ARCHIVE-VERIFY-MUST-PASS",
                    )
                )
        if baseline_payload and _token(baseline_payload.get("deterministic_fingerprint")) != _token(fresh_baseline.get("deterministic_fingerprint")):
            findings.append(
                _finding_row(
                    category="offline_archive.nondeterministic_archive",
                    path=OFFLINE_ARCHIVE_BASELINE_REL,
                    line=1,
                    message="committed offline archive baseline drifted from the fresh deterministic rerun.",
                    snippet=_token(fresh_baseline.get("deterministic_fingerprint")),
                    rule_id="INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE",
                )
            )

    return _check_result_payload(
        check_id="offline_archive_scan",
        description="Verify the frozen offline archive build, retained reconstruction surfaces, archive hash stability, and offline rerun of the Ω baseline verification lane.",
        scanned_paths=sorted(set(required_paths)),
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "verify_fingerprint": _token(_as_map(verify_payload).get("deterministic_fingerprint")),
            "baseline_fingerprint": _token(_as_map(baseline_payload).get("deterministic_fingerprint")),
            "fresh_verify_fingerprint": _token(_as_map(fresh_verify).get("deterministic_fingerprint")),
            "fresh_baseline_fingerprint": _token(_as_map(fresh_baseline).get("deterministic_fingerprint")),
            "fresh_archive_bundle_hash": _token(_as_map(fresh_build).get("archive_bundle_hash")),
            "fresh_archive_record_hash": _token(_as_map(fresh_build).get("archive_record_hash")),
            "required_commit_tag": _token(_as_map(baseline_payload).get("required_update_tag")),
        },
    )


def scan_toolchain_matrix(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    findings: list[dict] = []
    required_paths: list[str] = []
    committed_run_dirs: list[str] = []
    matrix_registry = {}
    profile_registry = {}

    try:
        from tools.mvp.toolchain_matrix_common import (
            DEFAULT_ENV_ID,
            TOOLCHAIN_MATRIX_MODEL_DOC_REL,
            TOOLCHAIN_MATRIX_REGISTRY_REL,
            TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID,
            TOOLCHAIN_MATRIX_RETRO_AUDIT_REL,
            TOOLCHAIN_TEST_PROFILE_REGISTRY_REL,
            TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID,
            build_default_toolchain_matrix_registry,
            build_default_toolchain_test_profile_registry,
            list_committed_toolchain_run_dirs,
            load_toolchain_matrix_registry,
            load_toolchain_test_profile_registry,
        )
    except Exception:
        return _check_result_payload(
            check_id="toolchain_matrix_scan",
            description="Verify the Ω-9 toolchain matrix registry, docs, and committed deterministic run surface.",
            scanned_paths=[],
            blocking_findings=[
                _finding_row(
                    category="toolchain_matrix.required_surface",
                    path="tools/mvp/toolchain_matrix_common.py",
                    line=1,
                    message="toolchain matrix tooling could not be imported.",
                    rule_id="INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT",
                )
            ],
            inventory={},
        )

    required_paths = [
        TOOLCHAIN_MATRIX_RETRO_AUDIT_REL,
        TOOLCHAIN_MATRIX_MODEL_DOC_REL,
        TOOLCHAIN_MATRIX_REGISTRY_REL,
        TOOLCHAIN_TEST_PROFILE_REGISTRY_REL,
        os.path.join("tools", "mvp", "tool_run_toolchain_matrix"),
        os.path.join("tools", "mvp", "tool_run_toolchain_matrix.py"),
        os.path.join("tools", "mvp", "tool_compare_toolchain_runs"),
        os.path.join("tools", "mvp", "tool_compare_toolchain_runs.py"),
        os.path.join("docs", "audit", "TOOLCHAIN_MATRIX_BASELINE.md"),
    ]
    for rel_path in required_paths:
        if os.path.exists(_repo_abs(repo_root_abs, rel_path)):
            continue
        findings.append(
            _finding_row(
                category="toolchain_matrix.required_surface",
                path=rel_path,
                line=1,
                message="required toolchain matrix surface is missing.",
                rule_id="INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT",
            )
        )

    matrix_registry = load_toolchain_matrix_registry(repo_root_abs)
    profile_registry = load_toolchain_test_profile_registry(repo_root_abs)
    expected_matrix_registry = build_default_toolchain_matrix_registry()
    expected_profile_registry = build_default_toolchain_test_profile_registry()
    if _token(matrix_registry.get("schema_id")) != TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID:
        findings.append(_finding_row(category="toolchain_matrix.required_surface", path=TOOLCHAIN_MATRIX_REGISTRY_REL, line=1, message="toolchain matrix registry schema_id mismatch.", rule_id="INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT"))
    if _token(profile_registry.get("schema_id")) != TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID:
        findings.append(_finding_row(category="toolchain_matrix.required_surface", path=TOOLCHAIN_TEST_PROFILE_REGISTRY_REL, line=1, message="toolchain test profile registry schema_id mismatch.", rule_id="INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT"))
    if matrix_registry != expected_matrix_registry:
        findings.append(_finding_row(category="toolchain_matrix.required_surface", path=TOOLCHAIN_MATRIX_REGISTRY_REL, line=1, message="toolchain matrix registry drifted from the canonical Ω-9 surface.", rule_id="INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT"))
    if profile_registry != expected_profile_registry:
        findings.append(_finding_row(category="toolchain_matrix.required_surface", path=TOOLCHAIN_TEST_PROFILE_REGISTRY_REL, line=1, message="toolchain test profile registry drifted from the canonical Ω-9 surface.", rule_id="INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT"))

    committed_run_dirs = list_committed_toolchain_run_dirs(repo_root_abs)
    if not committed_run_dirs:
        findings.append(
            _finding_row(
                category="toolchain_matrix.report_missing",
                path=os.path.join("artifacts", "toolchain_runs", DEFAULT_ENV_ID),
                line=1,
                message="no committed Ω-9 toolchain run artifacts were found.",
                rule_id="INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT",
            )
        )

    return _check_result_payload(
        check_id="toolchain_matrix_scan",
        description="Verify the Ω-9 toolchain matrix docs, registries, comparison tooling, and presence of committed deterministic run outputs.",
        scanned_paths=sorted(set(required_paths)),
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "matrix_env_count": len(_as_map(matrix_registry.get("record")).get("environments") or []),
            "profile_count": len(_as_map(profile_registry.get("record")).get("profiles") or []),
            "committed_run_count": len(committed_run_dirs),
        },
    )


def scan_dist_final_plan(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    findings: list[dict] = []
    required_paths: list[str] = []
    dryrun_report: dict = {}

    try:
        from tools.release.dist_final_common import (
            DIST_FINAL_CHECKLIST_DOC_REL,
            DIST_FINAL_DRYRUN_DOC_REL,
            DIST_FINAL_DRYRUN_TOOL_PY_REL,
            DIST_FINAL_DRYRUN_TOOL_REL,
            DIST_FINAL_EXPECTED_ARTIFACTS_REL,
            DIST_FINAL_PLAN_DOC_REL,
            OMEGA10_RETRO_AUDIT_REL,
            build_dist_final_dryrun_report,
        )
    except Exception:
        return _check_result_payload(
            check_id="dist_final_plan_scan",
            description="Verify the Ω-10 final distribution plan, checklist, expected artifacts surface, and deterministic dry-run gate.",
            scanned_paths=[],
            blocking_findings=[
                _finding_row(
                    category="dist_final_plan.required_surface",
                    path=os.path.join("tools", "release", "dist_final_common.py"),
                    line=1,
                    message="final distribution plan tooling could not be imported.",
                    rule_id="INV-DIST-FINAL-PLAN-PRESENT",
                )
            ],
            inventory={},
        )

    required_paths = [
        OMEGA10_RETRO_AUDIT_REL,
        DIST_FINAL_PLAN_DOC_REL,
        DIST_FINAL_CHECKLIST_DOC_REL,
        DIST_FINAL_EXPECTED_ARTIFACTS_REL,
        DIST_FINAL_DRYRUN_TOOL_REL,
        DIST_FINAL_DRYRUN_TOOL_PY_REL,
        DIST_FINAL_DRYRUN_DOC_REL,
    ]
    for rel_path in required_paths:
        if os.path.exists(_repo_abs(repo_root_abs, rel_path)):
            continue
        findings.append(
            _finding_row(
                category="dist_final_plan.required_surface",
                path=rel_path,
                line=1,
                message="required Ω-10 final distribution plan surface is missing.",
                rule_id="INV-DIST-FINAL-PLAN-PRESENT",
            )
        )

    dryrun_report = build_dist_final_dryrun_report(repo_root_abs)
    if _token(dryrun_report.get("result")) != "complete":
        detail_parts: list[str] = []
        missing_paths = list(dryrun_report.get("missing_paths") or [])
        artifact_issues = list(dryrun_report.get("artifact_issues") or [])
        if missing_paths:
            detail_parts.append("missing={}".format(",".join(_token(path) for path in missing_paths[:6])))
        if artifact_issues:
            detail_parts.append(
                "issues={}".format(
                    ",".join(_token(_as_map(row).get("code")) for row in artifact_issues[:6])
                )
            )
        findings.append(
            _finding_row(
                category="dist_final_plan.dryrun_failed",
                path=DIST_FINAL_DRYRUN_DOC_REL,
                line=1,
                message="Ω-10 dry-run did not complete cleanly.",
                snippet="; ".join(part for part in detail_parts if part)[:200],
                rule_id="INV-DIST-FINAL-DRYRUN-PASS-BEFORE-DIST7",
            )
        )

    return _check_result_payload(
        check_id="dist_final_plan_scan",
        description="Verify the Ω-10 final distribution plan, execution checklist, machine-readable expected artifacts registry, and deterministic dry-run gate.",
        scanned_paths=sorted(set(required_paths)),
        blocking_findings=findings,
        inventory={
            "required_surface_count": len(required_paths),
            "dryrun_result": _token(dryrun_report.get("result")),
            "dryrun_missing_count": int(dryrun_report.get("missing_count", 0) or 0),
            "dryrun_artifact_issue_count": int(dryrun_report.get("artifact_issue_count", 0) or 0),
            "dryrun_expected_artifact_count": int(dryrun_report.get("expected_artifact_count", 0) or 0),
            "dryrun_fingerprint": _token(dryrun_report.get("deterministic_fingerprint")),
        },
    )


def run_arch_audit(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    check_order = [
        "truth_purity_scan",
        "renderer_truth_access_scan",
        "duplicate_semantics_scan",
        "determinism_scan",
        "float_in_truth_scan",
        "worldgen_lock_scan",
        "baseline_universe_scan",
        "gameplay_loop_scan",
        "disaster_suite_scan",
        "ecosystem_verify_scan",
        "update_sim_scan",
        "trust_strict_scan",
        "offline_archive_scan",
        "toolchain_matrix_scan",
        "dist_final_plan_scan",
        "noncanonical_serialization_scan",
        "compiler_flag_scan",
        "parallel_truth_scan",
        "parallel_output_scan",
        "truth_atomic_scan",
        "stability_marker_scan",
        "contract_pin_scan",
        "pack_compat_scan",
        "dist_bundle_composition_scan",
        "update_model_scan",
        "trust_bypass_scan",
        "target_matrix_scan",
        "archive_determinism_scan",
    ]
    checks = {
        "truth_purity_scan": scan_truth_purity(repo_root_abs),
        "renderer_truth_access_scan": scan_renderer_truth_access(repo_root_abs),
        "duplicate_semantics_scan": scan_duplicate_semantics(repo_root_abs),
        "determinism_scan": scan_determinism(repo_root_abs),
        "float_in_truth_scan": scan_float_in_truth(repo_root_abs),
        "worldgen_lock_scan": scan_worldgen_lock(repo_root_abs),
        "baseline_universe_scan": scan_baseline_universe(repo_root_abs),
        "gameplay_loop_scan": scan_gameplay_loop(repo_root_abs),
        "disaster_suite_scan": scan_disaster_suite(repo_root_abs),
        "ecosystem_verify_scan": scan_ecosystem_verify(repo_root_abs),
        "update_sim_scan": scan_update_sim(repo_root_abs),
        "trust_strict_scan": scan_trust_strict_suite(repo_root_abs),
        "offline_archive_scan": scan_offline_archive(repo_root_abs),
        "toolchain_matrix_scan": scan_toolchain_matrix(repo_root_abs),
        "dist_final_plan_scan": scan_dist_final_plan(repo_root_abs),
        "noncanonical_serialization_scan": scan_noncanonical_numeric_serialization(repo_root_abs),
        "compiler_flag_scan": scan_compiler_flags(repo_root_abs),
        "parallel_truth_scan": scan_parallel_truth(repo_root_abs),
        "parallel_output_scan": scan_parallel_output_canonicalization(repo_root_abs),
        "truth_atomic_scan": scan_truth_atomic_usage(repo_root_abs),
        "stability_marker_scan": scan_stability_markers(repo_root_abs),
        "contract_pin_scan": scan_contract_pins(repo_root_abs),
        "pack_compat_scan": scan_pack_compat(repo_root_abs),
        "dist_bundle_composition_scan": scan_dist_bundle_composition(repo_root_abs),
        "update_model_scan": scan_update_model(repo_root_abs),
        "trust_bypass_scan": scan_trust_bypass(repo_root_abs),
        "target_matrix_scan": scan_target_matrix(repo_root_abs),
        "archive_determinism_scan": scan_archive_determinism(repo_root_abs),
    }
    blocking_rows: list[dict] = []
    known_rows: list[dict] = []
    for check_id in check_order:
        payload = dict(checks.get(check_id) or {})
        blocking_rows.extend([dict(row) for row in list(payload.get("blocking_findings") or []) if isinstance(row, Mapping)])
        known_rows.extend([dict(row) for row in list(payload.get("known_exceptions") or []) if isinstance(row, Mapping)])
    report = {
        "report_id": ARCH_AUDIT_ID,
        "result": "complete" if not blocking_rows else "violation",
        "release_status": "pass" if not blocking_rows else "fail",
        "check_order": list(check_order),
        "checks": dict((key, dict(checks[key])) for key in check_order),
        "blocking_finding_count": len(blocking_rows),
        "known_exception_count": len(known_rows),
        "blocking_findings": _sorted_findings(blocking_rows),
        "known_exceptions": _sorted_findings(known_rows),
        "ready_for_arch_audit_1": not bool(blocking_rows),
        "ready_for_earth10_sol1_gal_stubs": not bool(blocking_rows),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = _report_fingerprint(report)
    return report


def build_arch_audit2_report(report: Mapping[str, object] | None) -> dict:
    source = _as_map(report)
    check_rows = _as_map(source.get("checks"))
    blocking_rows: list[dict] = []
    known_rows: list[dict] = []
    for check_id in ARCH_AUDIT2_CHECK_ORDER:
        payload = _as_map(check_rows.get(check_id))
        blocking_rows.extend([dict(row) for row in list(payload.get("blocking_findings") or []) if isinstance(row, Mapping)])
        known_rows.extend([dict(row) for row in list(payload.get("known_exceptions") or []) if isinstance(row, Mapping)])
    audit2 = {
        "report_id": ARCH_AUDIT2_ID,
        "source_report_id": _token(source.get("report_id")) or ARCH_AUDIT_ID,
        "result": "complete" if not blocking_rows else "violation",
        "release_status": "pass" if not blocking_rows else "fail",
        "check_order": list(ARCH_AUDIT2_CHECK_ORDER),
        "checks": dict((key, _as_map(check_rows.get(key))) for key in ARCH_AUDIT2_CHECK_ORDER),
        "blocking_finding_count": len(blocking_rows),
        "known_exception_count": len(known_rows),
        "blocking_findings": _sorted_findings(blocking_rows),
        "known_exceptions": _sorted_findings(known_rows),
        "ready_for_convergence_gate_0": not bool(blocking_rows),
        "ready_for_dist_final_gates": not bool(blocking_rows),
        "deterministic_fingerprint": "",
    }
    audit2["deterministic_fingerprint"] = _report_fingerprint(audit2)
    return audit2


def build_numeric_scan_report(report: Mapping[str, object] | None) -> dict:
    source = _as_map(report)
    check_rows = _as_map(source.get("checks"))
    blocking_rows: list[dict] = []
    known_rows: list[dict] = []
    for check_id in NUMERIC_SCAN_CHECK_ORDER:
        payload = _as_map(check_rows.get(check_id))
        blocking_rows.extend([dict(row) for row in list(payload.get("blocking_findings") or []) if isinstance(row, Mapping)])
        known_rows.extend([dict(row) for row in list(payload.get("known_exceptions") or []) if isinstance(row, Mapping)])
    numeric_report = {
        "report_id": "numeric.discipline.scan.v1",
        "source_report_id": _token(source.get("report_id")) or ARCH_AUDIT_ID,
        "result": "complete" if not blocking_rows else "violation",
        "release_status": "pass" if not blocking_rows else "fail",
        "check_order": list(NUMERIC_SCAN_CHECK_ORDER),
        "checks": dict((key, _as_map(check_rows.get(key))) for key in NUMERIC_SCAN_CHECK_ORDER),
        "blocking_finding_count": len(blocking_rows),
        "known_exception_count": len(known_rows),
        "blocking_findings": _sorted_findings(blocking_rows),
        "known_exceptions": _sorted_findings(known_rows),
        "deterministic_fingerprint": "",
    }
    numeric_report["deterministic_fingerprint"] = _report_fingerprint(numeric_report)
    return numeric_report


def build_concurrency_scan_report(report: Mapping[str, object] | None) -> dict:
    source = _as_map(report)
    check_rows = _as_map(source.get("checks"))
    blocking_rows: list[dict] = []
    known_rows: list[dict] = []
    for check_id in CONCURRENCY_SCAN_CHECK_ORDER:
        payload = _as_map(check_rows.get(check_id))
        blocking_rows.extend([dict(row) for row in list(payload.get("blocking_findings") or []) if isinstance(row, Mapping)])
        known_rows.extend([dict(row) for row in list(payload.get("known_exceptions") or []) if isinstance(row, Mapping)])
    concurrency_report = {
        "report_id": "concurrency.contract.scan.v1",
        "source_report_id": _token(source.get("report_id")) or ARCH_AUDIT_ID,
        "result": "complete" if not blocking_rows else "violation",
        "release_status": "pass" if not blocking_rows else "fail",
        "check_order": list(CONCURRENCY_SCAN_CHECK_ORDER),
        "checks": dict((key, _as_map(check_rows.get(key))) for key in CONCURRENCY_SCAN_CHECK_ORDER),
        "blocking_finding_count": len(blocking_rows),
        "known_exception_count": len(known_rows),
        "blocking_findings": _sorted_findings(blocking_rows),
        "known_exceptions": _sorted_findings(known_rows),
        "deterministic_fingerprint": "",
    }
    concurrency_report["deterministic_fingerprint"] = _report_fingerprint(concurrency_report)
    return concurrency_report


def render_arch_audit_report(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Canon-aligned documentation set tracked by ARCH-AUDIT and REPO-REVIEW-3.",
        "",
        "# ARCH Audit Report",
        "",
        "- report_id: `{}`".format(_token(payload.get("report_id"))),
        "- result: `{}`".format(_token(payload.get("result"))),
        "- release_status: `{}`".format(_token(payload.get("release_status"))),
        "- blocking_finding_count: `{}`".format(int(payload.get("blocking_finding_count", 0) or 0)),
        "- known_exception_count: `{}`".format(int(payload.get("known_exception_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Checks",
        "",
    ]
    for check_id in list(payload.get("check_order") or []):
        check = _as_map(_as_map(payload.get("checks")).get(check_id))
        lines.extend(
            [
                "### {}".format(check_id),
                "- result: `{}`".format(_token(check.get("result"))),
                "- blocking_finding_count: `{}`".format(int(check.get("blocking_finding_count", 0) or 0)),
                "- known_exception_count: `{}`".format(int(check.get("known_exception_count", 0) or 0)),
                "- deterministic_fingerprint: `{}`".format(_token(check.get("deterministic_fingerprint"))),
            ]
        )
        if list(check.get("blocking_findings") or []):
            lines.append("- blocking findings:")
            for row in list(check.get("blocking_findings") or []):
                finding = dict(row or {})
                lines.append("  - `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
        if list(check.get("known_exceptions") or []):
            lines.append("- known exceptions:")
            for row in list(check.get("known_exceptions") or []):
                finding = dict(row or {})
                lines.append("  - `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_numeric_scan_report(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Numeric discipline baseline and release-pinned numeric policy docs.",
        "",
        "# Numeric Scan Report",
        "",
        "- report_id: `{}`".format(_token(payload.get("report_id"))),
        "- source_report_id: `{}`".format(_token(payload.get("source_report_id"))),
        "- result: `{}`".format(_token(payload.get("result"))),
        "- release_status: `{}`".format(_token(payload.get("release_status"))),
        "- blocking_finding_count: `{}`".format(int(payload.get("blocking_finding_count", 0) or 0)),
        "- known_exception_count: `{}`".format(int(payload.get("known_exception_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Numeric Checks",
        "",
    ]
    for check_id in list(payload.get("check_order") or []):
        check = _as_map(_as_map(payload.get("checks")).get(check_id))
        lines.extend(
            [
                "### {}".format(check_id),
                "- result: `{}`".format(_token(check.get("result"))),
                "- blocking_finding_count: `{}`".format(int(check.get("blocking_finding_count", 0) or 0)),
                "- known_exception_count: `{}`".format(int(check.get("known_exception_count", 0) or 0)),
                "- deterministic_fingerprint: `{}`".format(_token(check.get("deterministic_fingerprint"))),
            ]
        )
        if list(check.get("blocking_findings") or []):
            lines.append("- blocking findings:")
            for row in list(check.get("blocking_findings") or []):
                finding = dict(row or {})
                lines.append("  - `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
        if list(check.get("known_exceptions") or []):
            lines.append("- known exceptions:")
            for row in list(check.get("known_exceptions") or []):
                finding = dict(row or {})
                lines.append("  - `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_concurrency_scan_report(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Release-pinned concurrency policy baseline and shard-merge execution contracts.",
        "",
        "# Concurrency Scan Report",
        "",
        "- report_id: `{}`".format(_token(payload.get("report_id"))),
        "- source_report_id: `{}`".format(_token(payload.get("source_report_id"))),
        "- result: `{}`".format(_token(payload.get("result"))),
        "- release_status: `{}`".format(_token(payload.get("release_status"))),
        "- blocking_finding_count: `{}`".format(int(payload.get("blocking_finding_count", 0) or 0)),
        "- known_exception_count: `{}`".format(int(payload.get("known_exception_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Concurrency Checks",
        "",
    ]
    for check_id in list(payload.get("check_order") or []):
        check = _as_map(_as_map(payload.get("checks")).get(check_id))
        lines.extend(
            [
                "### {}".format(check_id),
                "- result: `{}`".format(_token(check.get("result"))),
                "- blocking_finding_count: `{}`".format(int(check.get("blocking_finding_count", 0) or 0)),
                "- known_exception_count: `{}`".format(int(check.get("known_exception_count", 0) or 0)),
                "- deterministic_fingerprint: `{}`".format(_token(check.get("deterministic_fingerprint"))),
            ]
        )
        if list(check.get("blocking_findings") or []):
            lines.append("- blocking findings:")
            for row in list(check.get("blocking_findings") or []):
                finding = dict(row or {})
                lines.append("  - `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
        if list(check.get("known_exceptions") or []):
            lines.append("- known exceptions:")
            for row in list(check.get("known_exceptions") or []):
                finding = dict(row or {})
                lines.append("  - `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_arch_audit_baseline(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Canon-aligned documentation set tracked by ARCH-AUDIT and REPO-REVIEW-3.",
        "",
        "# ARCH Audit Baseline",
        "",
        "## Checks",
        "",
    ]
    for check_id in list(payload.get("check_order") or []):
        check = _as_map(_as_map(payload.get("checks")).get(check_id))
        lines.append("- `{}` -> `{}` (blocking=`{}`, known_exceptions=`{}`)".format(check_id, _token(check.get("result")), int(check.get("blocking_finding_count", 0) or 0), int(check.get("known_exception_count", 0) or 0)))
    lines.extend(["", "## Known Provisional Exceptions", ""])
    known = list(payload.get("known_exceptions") or [])
    if not known:
        lines.append("- none")
    else:
        for row in known:
            finding = dict(row or {})
            lines.append("- `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "- ARCH-AUDIT-1: `{}`".format("ready" if bool(payload.get("ready_for_arch_audit_1", False)) else "blocked"),
            "- EARTH-10 / SOL-1 / GAL stubs: `{}`".format("ready" if bool(payload.get("ready_for_earth10_sol1_gal_stubs", False)) else "blocked"),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_arch_audit2_report(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Final release/distribution audit baseline governed by ARCH-AUDIT-2.",
        "",
        "# ARCH Audit 2 Report",
        "",
        "- report_id: `{}`".format(_token(payload.get("report_id"))),
        "- source_report_id: `{}`".format(_token(payload.get("source_report_id"))),
        "- result: `{}`".format(_token(payload.get("result"))),
        "- release_status: `{}`".format(_token(payload.get("release_status"))),
        "- blocking_finding_count: `{}`".format(int(payload.get("blocking_finding_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Cross-Layer Checks",
        "",
    ]
    for check_id in list(payload.get("check_order") or []):
        check = _as_map(_as_map(payload.get("checks")).get(check_id))
        lines.extend(
            [
                "### {}".format(check_id),
                "- result: `{}`".format(_token(check.get("result"))),
                "- blocking_finding_count: `{}`".format(int(check.get("blocking_finding_count", 0) or 0)),
                "- deterministic_fingerprint: `{}`".format(_token(check.get("deterministic_fingerprint"))),
            ]
        )
        if list(check.get("blocking_findings") or []):
            lines.append("- blocking findings:")
            for row in list(check.get("blocking_findings") or []):
                finding = dict(row or {})
                lines.append("  - `{}`:{} {}".format(_token(finding.get("path")), int(finding.get("line", 0) or 0), _token(finding.get("message"))))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_arch_audit2_final(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Final release/distribution audit baseline governed by ARCH-AUDIT-2.",
        "",
        "# ARCH Audit 2 Final",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- blocking_finding_count: `{}`".format(int(payload.get("blocking_finding_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Check Summary",
        "",
    ]
    for check_id in list(payload.get("check_order") or []):
        check = _as_map(_as_map(payload.get("checks")).get(check_id))
        lines.append(
            "- `{}` -> `{}` (blocking=`{}`)".format(
                check_id,
                _token(check.get("result")),
                int(check.get("blocking_finding_count", 0) or 0),
            )
        )
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "- CONVERGENCE-GATE-0: `{}`".format("ready" if bool(payload.get("ready_for_convergence_gate_0", False)) else "blocked"),
            "- DIST final gates: `{}`".format("ready" if bool(payload.get("ready_for_dist_final_gates", False)) else "blocked"),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_arch_audit_outputs(
    repo_root: str,
    *,
    report: Mapping[str, object],
    report_path: str = DEFAULT_REPORT_MD_REL,
    json_path: str = DEFAULT_REPORT_JSON_REL,
    baseline_path: str = "",
    numeric_scan_path: str = DEFAULT_NUMERIC_SCAN_REPORT_MD_REL,
    concurrency_scan_path: str = DEFAULT_CONCURRENCY_SCAN_REPORT_MD_REL,
    audit2_report_path: str = DEFAULT_AUDIT2_REPORT_MD_REL,
    audit2_json_path: str = DEFAULT_AUDIT2_REPORT_JSON_REL,
    audit2_final_path: str = DEFAULT_AUDIT2_FINAL_DOC_REL,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    audit2_report = build_arch_audit2_report(report)
    numeric_report = build_numeric_scan_report(report)
    concurrency_report = build_concurrency_scan_report(report)
    written = {
        "report_path": _write_text(_repo_abs(repo_root_abs, report_path), render_arch_audit_report(report)),
        "json_path": _write_canonical_json(_repo_abs(repo_root_abs, json_path), report),
        "numeric_scan_path": _write_text(_repo_abs(repo_root_abs, numeric_scan_path), render_numeric_scan_report(numeric_report)),
        "concurrency_scan_path": _write_text(_repo_abs(repo_root_abs, concurrency_scan_path), render_concurrency_scan_report(concurrency_report)),
        "audit2_report_path": _write_text(_repo_abs(repo_root_abs, audit2_report_path), render_arch_audit2_report(audit2_report)),
        "audit2_json_path": _write_canonical_json(_repo_abs(repo_root_abs, audit2_json_path), audit2_report),
        "audit2_final_path": _write_text(_repo_abs(repo_root_abs, audit2_final_path), render_arch_audit2_final(audit2_report)),
    }
    if _token(baseline_path):
        written["baseline_path"] = _write_text(_repo_abs(repo_root_abs, baseline_path), render_arch_audit_baseline(report))
    return written


def load_or_run_arch_audit_report(repo_root: str, json_path: str = DEFAULT_REPORT_JSON_REL) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    payload = load_json_if_present(repo_root_abs, json_path)
    if _token(payload.get("report_id")) == ARCH_AUDIT_ID and _token(payload.get("result")):
        return payload
    return run_arch_audit(repo_root_abs)


__all__ = [
    "ARCH_AUDIT_ID",
    "ARCH_AUDIT2_ID",
    "CONCURRENCY_SCAN_CHECK_ORDER",
    "DEFAULT_CONCURRENCY_SCAN_REPORT_MD_REL",
    "DEFAULT_NUMERIC_SCAN_REPORT_MD_REL",
    "DEFAULT_AUDIT2_FINAL_DOC_REL",
    "DEFAULT_AUDIT2_REPORT_JSON_REL",
    "DEFAULT_AUDIT2_REPORT_MD_REL",
    "ARCH_AUDIT2_CHECK_ORDER",
    "NUMERIC_SCAN_CHECK_ORDER",
    "DEFAULT_BASELINE_DOC_REL",
    "DEFAULT_REPORT_JSON_REL",
    "DEFAULT_REPORT_MD_REL",
    "build_arch_audit2_report",
    "build_concurrency_scan_report",
    "build_numeric_scan_report",
    "load_json_if_present",
    "load_or_run_arch_audit_report",
    "render_arch_audit_baseline",
    "render_arch_audit2_final",
    "render_arch_audit2_report",
    "render_arch_audit_report",
    "render_concurrency_scan_report",
    "render_numeric_scan_report",
    "run_arch_audit",
    "scan_baseline_universe",
    "scan_archive_determinism",
    "scan_offline_archive",
    "scan_toolchain_matrix",
    "scan_dist_final_plan",
    "scan_contract_pins",
    "scan_compiler_flags",
    "scan_disaster_suite",
    "scan_dist_bundle_composition",
    "scan_determinism",
    "scan_ecosystem_verify",
    "scan_duplicate_semantics",
    "scan_float_in_truth",
    "scan_gameplay_loop",
    "scan_noncanonical_numeric_serialization",
    "scan_pack_compat",
    "scan_parallel_output_canonicalization",
    "scan_parallel_truth",
    "scan_renderer_truth_access",
    "scan_stability_markers",
    "scan_target_matrix",
    "scan_trust_strict_suite",
    "scan_trust_bypass",
    "scan_truth_atomic_usage",
    "scan_truth_purity",
    "scan_update_sim",
    "scan_update_model",
    "write_arch_audit_outputs",
]

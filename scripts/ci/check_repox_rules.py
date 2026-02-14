#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime

DEV_SCRIPT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dev"))
if DEV_SCRIPT_DIR not in sys.path:
    sys.path.insert(0, DEV_SCRIPT_DIR)

from env_tools_lib import (
    WORKSPACE_ID_ENV_KEY,
    canonicalize_env_for_workspace,
    canonical_tools_dir_details,
    detect_repo_root,
    resolve_tool,
)
import identity_fingerprint_lib
from hygiene_utils import DEFAULT_EXCLUDES, iter_files, read_text, strip_c_comments_and_strings, normalize_path


AUTHORITATIVE_DIRS = (
    os.path.join("engine", "modules", "core"),
    os.path.join("engine", "modules", "sim"),
    os.path.join("engine", "modules", "world"),
    os.path.join("game", "core"),
    os.path.join("game", "rules"),
)

SOURCE_EXTS = [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"]

FORBIDDEN_RNG_CALL_RE = re.compile(
    r"\b(rand|srand|rand_r|random|arc4random|drand48|lrand48|mrand48|getrandom|"
    r"BCryptGenRandom|RtlGenRandom|CryptGenRandom)\s*\("
)
FORBIDDEN_TIME_CALL_RE = re.compile(
    r"\b(time|clock|gettimeofday|clock_gettime|QueryPerformanceCounter|GetSystemTime|"
    r"GetTickCount|GetTickCount64|mach_absolute_time)\s*\("
)
FORBIDDEN_TIME_TOKEN_RE = re.compile(r"\bCLOCK_REALTIME\b")
FORBIDDEN_CHRONO_RE = re.compile(r"\bstd::chrono::|\bchrono::")
FORBIDDEN_FLOAT_RE = re.compile(r"\b(long\s+double|double|float)\b")

REVERSE_DNS_RE = re.compile(
    r'["\']((?:org|com|net|io|edu|gov|co|ai|dev)\.[a-z0-9]+(?:\.[a-z0-9]+)+)["\']',
    re.IGNORECASE,
)
ALLOWED_REVERSE_DNS_PREFIXES = (
    "noise.stream.",
    "rng.state.noise.stream.",
)

ENUM_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_]*(CUSTOM|OTHER|UNKNOWN|MISC|UNSPECIFIED)[A-Za-z0-9_]*\b")
INCLUDE_DIRECTIVE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')

ABS_WIN_RE = re.compile(r"[A-Za-z]:[\\/]")
ABS_UNIX_RE = re.compile(r"/(Users|home|var|etc|opt|usr|private)/")
ABS_UNC_RE = re.compile(r"\\\\\\\\[^\\\\/]+[\\\\/]")

AMBIGUOUS_DIR_NAMES = {"misc", "tmp", "temp", "old", "junk"}

OVERRIDES_PATH = os.path.join("docs", "architecture", "LOCKLIST_OVERRIDES.json")

FROZEN_SECTION = "## Frozen constitutional surfaces"
NEXT_SECTION_PREFIX = "## "
PATH_RE = re.compile(r"`([^`]+)`")
DOC_REF_RE = re.compile(r"docs/[A-Za-z0-9_./-]+\.(?:md|txt)", re.IGNORECASE)
CANON_LEVEL_RE = re.compile(r"\bcanon[-_ ]?clean[-_ ]?(\d+)\b", re.IGNORECASE)
CANON_LEVEL_FIELD_RE = re.compile(r"\bcanon_level\s*[:=]\s*([A-Za-z0-9_.-]+)\b", re.IGNORECASE)

ALLOWED_ARCHIVE_ROOTS = (
    "docs/archive",
    "legacy",
    "labs",
    "tmp",
)

CANON_INDEX_PATH = "docs/architecture/CANON_INDEX.md"
DOCS_ROOT = "docs"
DOC_EXTS = [".md", ".txt"]
DOC_STATUS_VALUES = {"CANONICAL", "DERIVED", "HISTORICAL"}
CANON_STATE_PATH = os.path.join("repo", "canon_state.json")
PROCESS_REGISTRY_REL = os.path.join("data", "registries", "process_registry.json")
PROCESS_SCHEMA_ID = "dominium.schema.process"
PROCESS_REGISTRY_SCHEMA_ID = "dominium.schema.process_registry"
SCHEMA_MIGRATION_REGISTRY_REL = os.path.join("schema", "SCHEMA_MIGRATION_REGISTRY.json")
SCHEMA_MIGRATION_REGISTRY_SCHEMA_ID = "dominium.schema.migration_registry"
SOLVER_REGISTRY_REL = os.path.join("data", "registries", "solver_registry.json")
SOLVER_REGISTRY_SCHEMA_ID = "dominium.registry.solver_registry"
PROCESS_FIXTURE_PATHS = (
    os.path.join("tests", "contract", "terrain_fixtures.json"),
)
PROCESS_ID_LITERAL_RE = re.compile(r'"(process\.[A-Za-z0-9_.]+)"')
PROCESS_ID_LITERAL_ALLOW = {"process.mine.unknown"}
SCHEMA_VERSION_RE = re.compile(r"^\s*schema_version\s*:\s*(\d+\.\d+\.\d+)\s*$", re.MULTILINE)
SCHEMA_ID_RE = re.compile(r"^\s*schema_id\s*:\s*([A-Za-z0-9_.-]+)\s*$", re.MULTILINE)
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
SCHEMA_ID_LITERAL_RE = re.compile(r'"(dominium\.schema\.[A-Za-z0-9_.-]+)"')
CAPABILITY_SET_IDS = (
    "CAPSET_WORLD_NONBIO",
    "CAPSET_WORLD_LIFE_NONINTELLIGENT",
    "CAPSET_WORLD_LIFE_INTELLIGENT",
    "CAPSET_WORLD_PRETOOL",
    "CAPSET_SOCIETY_INSTITUTIONS",
    "CAPSET_INFRASTRUCTURE_INDUSTRY",
    "CAPSET_FUTURE_AFFORDANCES",
)
# Keep capability id validation aligned with shared reverse-dns helpers.
PACK_CAPABILITY_RE = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9][a-z0-9_-]*)+$")
PREALPHA_MATURITY_TAG = "pack.maturity.prealpha"
PREALPHA_STABILITY_TAG = "pack.stability.disposable"
FORBIDDEN_LEGACY_GATING_TOKEN_PARTS = (
    "S" + "TAGE_",
    "requires" + "_stage",
    "provides" + "_stage",
    "stage" + "_features",
    "required" + "_stage",
    "PROGRE" + "SSION_",
    "COMPLE" + "TION_",
)
FORBIDDEN_LEGACY_GATING_TOKEN_RE = re.compile(
    r"\b(" + "|".join(re.escape(token) for token in FORBIDDEN_LEGACY_GATING_TOKEN_PARTS) + r")\b"
)
SOLVER_COST_CLASS_SET = ("low", "medium", "high", "critical")
SOLVER_RESOLUTION_SET = ("macro", "micro", "hybrid")
COMMAND_REGISTRY_REL = os.path.join("libs", "appcore", "command", "command_registry.c")
UI_BIND_TABLE_REL = os.path.join("libs", "appcore", "ui_bind", "ui_command_binding_table.c")
CAPABILITY_MATRIX_REL = os.path.join("tests", "testx", "CAPABILITY_MATRIX.yaml")
CAPABILITY_FIXTURE_ROOT = os.path.join("tests", "fixtures", "worlds")
CAPABILITY_TESTX_ROOT = os.path.join("tests", "testx", "capability_sets")
CAPABILITY_REGRESSION_ROOT = os.path.join("tests", "testx", "capability_regression")
CAPABILITY_MATRIX_SUITE_NAMES = (
    "test_load_and_validate",
    "test_command_surface",
    "test_pack_gating",
    "test_epistemics",
    "test_determinism_smoke",
    "test_replay_hash",
)
CAPABILITY_SET_TO_DIR = {
    "CAPSET_WORLD_NONBIO": "capset_world_nonbio",
    "CAPSET_WORLD_LIFE_NONINTELLIGENT": "capset_world_life_nonintelligent",
    "CAPSET_WORLD_LIFE_INTELLIGENT": "capset_world_life_intelligent",
    "CAPSET_WORLD_PRETOOL": "capset_world_pretool",
    "CAPSET_SOCIETY_INSTITUTIONS": "capset_society_institutions",
    "CAPSET_INFRASTRUCTURE_INDUSTRY": "capset_infrastructure_industry",
    "CAPSET_FUTURE_AFFORDANCES": "capset_future_affordances",
}

CAMERA_BLUEPRINT_COMMAND_EXPECTATIONS = {
    "camera.set_mode": {
        "required_capabilities": ("ui.camera.mode.embodied",),
        "epistemic_scope": "DOM_EPISTEMIC_SCOPE_PARTIAL",
        "failure_ref": "k_failure_camera",
    },
    "camera.set_pose": {
        "required_capabilities": ("ui.camera.mode.embodied",),
        "epistemic_scope": "DOM_EPISTEMIC_SCOPE_OBS_ONLY",
        "failure_ref": "k_failure_camera",
    },
    "blueprint.preview": {
        "required_capabilities": ("ui.blueprint.preview",),
        "epistemic_scope": "DOM_EPISTEMIC_SCOPE_MEMORY_ONLY",
        "failure_ref": "k_failure_blueprint",
    },
    "blueprint.place": {
        "required_capabilities": ("ui.blueprint.place",),
        "epistemic_scope": "DOM_EPISTEMIC_SCOPE_OBS_ONLY",
        "failure_ref": "k_failure_blueprint",
    },
}

CAMERA_MODE_RUNTIME_CAPABILITIES = (
    "ui.camera.mode.embodied",
    "ui.camera.mode.memory",
    "ui.camera.mode.observer",
)
OBSERVER_TOOL_ENTITLEMENTS = (
    "tool.truth.view",
    "tool.observation.stream",
    "tool.memory.read",
)

FORBIDDEN_RENDER_TRUTH_TOKENS = (
    "authoritative_world_state",
    "truth_snapshot_stream",
    "hidden_truth_cache",
)

RULESET_ROOT = os.path.join("repo", "repox", "rulesets")
REPOX_EXEMPTIONS_PATH = os.path.join("repo", "repox", "repox_exemptions.json")
PROOF_MANIFEST_DEFAULT = os.path.join("docs", "audit", "proof_manifest.json")
REPOX_PROFILE_REL = os.path.join("docs", "audit", "repox", "REPOX_PROFILE.json")
STRUCTURE_SCOPE_EXCLUDED_PREFIXES = (
    "docs/audit",
    "dist",
    "build",
    "tmp",
    ".xstack_cache",
)
EXEMPTION_INLINE_RE = re.compile(r"@repox:allow\((?P<rule_id>[A-Za-z0-9_.-]+)\)(?P<tail>[^\r\n]*)")
EXEMPTION_REASON_RE = re.compile(r'reason="([^"]+)"')
EXEMPTION_EXPIRES_RE = re.compile(r'expires="(\d{4}-\d{2}-\d{2})"')
MECHANISM_ONLY_MARKER = "@repox:mechanism_only"
INFRA_ONLY_MARKER = "@repox:infrastructure_only"
PROTOTYPE_MARKER = "@repox:prototype"
DUPLICATION_MARKER = "@repox:deliberate_duplication"
RATCHET_KEY = "ratchet_after"

DIST_PKG_ROOT_REL = os.path.join("dist", "pkg")
DIST_META_ROOT_REL = os.path.join("dist", "meta")
DIST_SYS_ROOT_REL = os.path.join("dist", "sys")
PLATFORM_REGISTRY_REL = os.path.join("data", "registries", "platform_registry.json")
PRODUCT_GRAPH_REL = os.path.join("data", "registries", "product_graph.json")
MODE_BACKEND_REL = os.path.join("data", "registries", "mode_backend.json")
PLATFORM_REGISTRY_SCHEMA_ID = "dominium.schema.distribution.platform_registry"
PRODUCT_GRAPH_SCHEMA_ID = "dominium.schema.distribution.product_graph"
MODE_BACKEND_SCHEMA_ID = "dominium.schema.ui.mode_backend"
PKG_MANIFEST_REQUIRED_FIELDS = (
    "pkg_id",
    "pkg_version",
    "platform",
    "arch",
    "abi",
    "requires_capabilities",
    "provides_capabilities",
    "entitlements",
    "compression",
    "chunk_size_bytes",
    "file_exports",
    "content_hash",
)
CANONICAL_PLATFORM_IDS = (
    "winnt",
    "win9x",
    "win16",
    "dos",
    "macosx",
    "macclassic",
    "linux",
    "android",
    "ios",
    "web",
)
FORBIDDEN_PLATFORM_ALIASES = (
    "win",
    "windows",
    "mac",
    "osx",
)
DIST_PLATFORM_CANON_ROOTS = (
    os.path.join("dist", "pkg"),
    os.path.join("dist", "sys"),
    os.path.join("dist", "sym"),
    os.path.join("dist", "meta"),
    os.path.join("dist", "wrap"),
    os.path.join("dist", "redist"),
)
IDENTITY_FINGERPRINT_REL = os.path.join("docs", "audit", "identity_fingerprint.json")
IDENTITY_EXPLANATION_REL = os.path.join("docs", "audit", "identity_fingerprint_explanation.md")
GLOSSARY_SCHEMA_REL = os.path.join("schema", "governance", "glossary.schema")
GLOSSARY_REGISTRY_REL = os.path.join("data", "registries", "glossary.json")
PRESENTATION_MATRIX_SCHEMA_REL = os.path.join("schema", "governance", "presentation_matrix.schema")
PRESENTATION_MATRIX_REGISTRY_REL = os.path.join("data", "registries", "presentation_matrix.json")
PRESENTATION_MATRIX_SCHEMA_ID = "dominium.schema.governance.presentation_matrix"  # schema_version: 1.0.0
AUDITX_PROMOTION_POLICY_REL = os.path.join("docs", "governance", "AUDITX_PROMOTION_POLICY.md")
REPO_HEALTH_SNAPSHOT_JSON_REL = os.path.join("docs", "audit", "system", "REPO_HEALTH_SNAPSHOT.json")
REPO_HEALTH_SNAPSHOT_MD_REL = os.path.join("docs", "audit", "system", "REPO_HEALTH_SNAPSHOT.md")
GOVERNANCE_FINAL_REPORT_REL = os.path.join("docs", "audit", "system", "GOVERNANCE_FINAL_REPORT.md")
DERIVED_ARTIFACT_CONTRACT_SCHEMA_REL = os.path.join("schema", "governance", "derived_artifact_contract.schema")
DERIVED_ARTIFACT_REGISTRY_REL = os.path.join("data", "registries", "derived_artifacts.json")
DERIVED_ARTIFACT_SCHEMA_ID = "dominium.schema.governance.derived_artifact_contract"  # schema_version: 1.0.0
DERIVED_ARTIFACT_CLASSES = ("CANONICAL", "DERIVED_VIEW", "RUN_META")
DERIVED_ARTIFACT_REQUIRED_IDS = (
    "artifact.auditx.findings",
    "artifact.auditx.invariant_map",
    "artifact.auditx.promotion_candidates",
    "artifact.auditx.trends",
    "artifact.auditx.run_meta",
    "artifact.identity.fingerprint",
    "artifact.ui.bind.table",
)
DERIVED_ARTIFACT_CANONICAL_FORBIDDEN_KEYS = (
    "created_utc",
    "generated_utc",
    "last_reviewed",
    "timestamp",
    "timestamp_utc",
    "run_id",
    "duration_ms",
)
REMEDIATION_PLAYBOOK_SCHEMA_REL = os.path.join("schema", "governance", "remediation_playbook.schema")
REMEDIATION_PLAYBOOK_REGISTRY_REL = os.path.join("data", "registries", "remediation_playbooks.json")
REMEDIATION_PLAYBOOK_SCHEMA_ID = ".".join(("dominium", "schema", "governance", "remediation_playbook"))  # schema_version is validated from payload
REMEDIATION_PLAYBOOK_REQUIRED_BLOCKERS = (
    "TOOL_DISCOVERY",
    "DERIVED_ARTIFACT_STALE",
    "DIST_OUTPUT_MISSING",
    "PKG_INDEX_MISSING",
    "SCHEMA_MISMATCH",
    "UI_BIND_DRIFT",
    "BUILD_OUTPUT_MISSING",
    "PATH_CWD_DEPENDENCY",
    "DOC_CANON_DRIFT",
    "WORKSPACE_COLLISION",
    "VERSIONING_POLICY_MISMATCH",
)
FAILURE_CLASS_SCHEMA_REL = os.path.join("schema", "governance", "failure_classes.schema")
FAILURE_CLASS_REGISTRY_REL = os.path.join("data", "registries", "failure_classes.json")
FAILURE_CLASS_SCHEMA_ID = "dominium.schema.governance.failure_classes"  # schema_version: 1.0.0

COMPAT_MATRIX_SCHEMA_REL = os.path.join("schema", "governance", "compat_matrix.schema")
COMPAT_MATRIX_REGISTRY_REL = os.path.join("data", "registries", "compat_matrix.json")
COMPAT_MATRIX_SCHEMA_ID = "dominium.schema.governance.compat_matrix"  # schema_version: 1.0.0
COMPAT_MIGRATION_SCHEMA_REL = os.path.join("schema", "governance", "migration_spec.schema")
COMPAT_MIGRATION_REGISTRY_REL = os.path.join("data", "registries", "migrations.json")
COMPAT_MIGRATION_SCHEMA_ID = "dominium.schema.governance.migration_spec"  # schema_version: 1.0.0
COMPAT_SCHEMA_POLICY_SCHEMA_REL = os.path.join("schema", "governance", "schema_version_policy.schema")
COMPAT_SCHEMA_POLICY_REGISTRY_REL = os.path.join("data", "registries", "schema_version_policy.json")
COMPAT_SCHEMA_POLICY_SCHEMA_ID = "dominium.schema.governance.schema_version_policy"  # schema_version: 1.0.0
SECUREX_TRUST_POLICY_SCHEMA_REL = os.path.join("schema", "governance", "trust_policy.schema")
SECUREX_TRUST_POLICY_REGISTRY_REL = os.path.join("data", "registries", "trust_policy.json")
SECUREX_TRUST_POLICY_SCHEMA_ID = "dominium.schema.governance.trust_policy"  # schema_version: 1.0.0
SECUREX_PRIVILEGE_MODEL_SCHEMA_REL = os.path.join("schema", "governance", "privilege_model.schema")
SECUREX_PRIVILEGE_MODEL_REGISTRY_REL = os.path.join("data", "registries", "security_roles.json")
SECUREX_PRIVILEGE_MODEL_SCHEMA_ID = "dominium.schema.governance.privilege_model"  # schema_version: 1.0.0
SECUREX_INTEGRITY_MANIFEST_REL = os.path.join("docs", "audit", "security", "INTEGRITY_MANIFEST.json")
SECUREX_INTEGRITY_MANIFEST_SCHEMA_ID = "dominium.schema.governance.integrity_manifest"  # schema_version: 1.0.0

BUILD_PRESET_CONTRACT_CONFIGURE = (
    "msvc-dev-debug",
    "msvc-dev-release",
    "msvc-verify",
    "msvc-verify-full",
    "release-winnt-x86_64",
    "linux-gcc-dev",
    "linux-clang-dev",
    "linux-verify",
    "linux-verify-full",
    "release-linux-x86_64",
    "macos-dev",
    "macos-verify",
    "macos-verify-full",
    "release-macos-arm64",
    "win9x-x86_32-legacy",
    "win16-x86_16",
    "dos-x86_16",
)

BUILD_PRESET_CONTRACT_TARGETS = {
    "msvc-dev-debug": "all_runtime",
    "msvc-dev-release": "all_runtime",
    "msvc-verify": "verify_fast",
    "msvc-verify-full": "verify_full",
    "release-winnt-x86_64": "dist_all",
    "linux-gcc-dev": "all_runtime",
    "linux-clang-dev": "all_runtime",
    "linux-verify": "verify_fast",
    "linux-verify-full": "verify_full",
    "release-linux-x86_64": "dist_all",
    "macos-dev": "all_runtime",
    "macos-verify": "verify_fast",
    "macos-verify-full": "verify_full",
    "release-macos-arm64": "dist_all",
    "win9x-x86_32-legacy": "all_runtime",
    "win16-x86_16": "all_runtime",
    "dos-x86_16": "all_runtime",
}

CANONICAL_TOOL_IDS = (
    "tool_ui_bind",
    "tool_ui_validate",
    "tool_ui_doc_annotate",
)

AUDITX_CANONICAL_ARTIFACTS = (
    "docs/audit/auditx/FINDINGS.json",
    "docs/audit/auditx/INVARIANT_MAP.json",
    "docs/audit/auditx/PROMOTION_CANDIDATES.json",
    "docs/audit/auditx/TRENDS.json",
)
AUDITX_RUN_META_ARTIFACT = "docs/audit/auditx/RUN_META.json"
AUDITX_CANONICAL_FORBIDDEN_KEYS = (
    "created_utc",
    "last_reviewed",
    "generated_utc",
    "duration_ms",
    "scan_id",
    "run_id",
)

TOOL_SCAN_EXTS = (
    ".py",
    ".cmake",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".cmd",
    ".bat",
    ".ps1",
    ".sh",
)
TOOL_SCAN_SKIP_PREFIXES = (
    "tools/auditx/cache/",
    "tools/compatx/cache/",
    "tools/performx/cache/",
    "tools/securex/cache/",
    ".xstack_cache/",
    "docs/audit/remediation/",
)
DIRECT_GATE_SCAN_ROOTS = (
    os.path.join("scripts", "dev"),
    os.path.join("scripts", "ci"),
    os.path.join(".github", "workflows"),
)
DIRECT_GATE_SCAN_EXTS = (".py", ".sh", ".cmd", ".bat", ".ps1", ".yml", ".yaml")
DIRECT_GATE_ALLOWLIST = {
    normalize_path(os.path.join("scripts", "dev", "gate.py")),
    normalize_path(os.path.join("scripts", "dev", "gate_shim.py")),
    normalize_path(os.path.join("scripts", "dev", "run_repox.py")),
    normalize_path(os.path.join("scripts", "dev", "run_testx.py")),
    normalize_path(os.path.join("scripts", "dev", "testx_proof_engine.py")),
    normalize_path(os.path.join("scripts", "ci", "check_repox_rules.py")),
}


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def load_allowed_top_level(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "REPO_INTENT.md")
    allowed = set()
    if not os.path.isfile(path):
        return allowed
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if "|" not in line:
                continue
            backticks = re.findall(r"`([^`]+)`", line)
            for item in backticks:
                name = item.strip().strip("/")
                if name:
                    allowed.add(name)
    return allowed


def check_top_level(repo_root, allowed):
    violations = []
    for entry in os.listdir(repo_root):
        if entry.startswith(".") and entry not in allowed:
            if entry in (".git",):
                continue
        full = os.path.join(repo_root, entry)
        if not os.path.isdir(full):
            continue
        if entry not in allowed and not entry.startswith("."):
            violations.append("INV-REPOX-STRUCTURE: top-level directory not in REPO_INTENT: {}".format(entry))
    return violations


def check_archived_paths(repo_root):
    manifest_path = os.path.join(repo_root, "tests", "contract", "archive_manifest.json")
    if not os.path.isfile(manifest_path):
        return ["INV-REPOX-STRUCTURE: missing archive manifest: tests/contract/archive_manifest.json"]
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    violations = []
    for entry in manifest.get("archives", []):
        rel_path = entry.get("path", "")
        if not rel_path:
            continue
        norm = normalize_path(rel_path)
        if not any(norm == root or norm.startswith(root + "/") for root in ALLOWED_ARCHIVE_ROOTS):
            violations.append("INV-REPOX-STRUCTURE: archived path not under archive/quarantine: {}".format(rel_path))
    return violations


def _load_overrides(repo_root):
    path = os.path.join(repo_root, OVERRIDES_PATH)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return []
    overrides = payload.get("overrides", [])
    if not isinstance(overrides, list):
        return []
    return overrides


def _parse_date(value):
    if not value or not isinstance(value, str):
        return None
    parts = value.split("-")
    if len(parts) != 3:
        return None
    try:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def is_override_active(repo_root, invariant_id, today=None):
    if today is None:
        today = date.today()
    for entry in _load_overrides(repo_root):
        inv = entry.get("invariant")
        if inv != invariant_id:
            continue
        expiry = _parse_date(entry.get("expires"))
        if expiry is None:
            continue
        if expiry >= today:
            return True
    return False


def run_git(args, repo_root):
    git_cmd = shutil.which("git")
    if not git_cmd:
        fallback = []
        if os.name == "nt":
            roots = [
                os.environ.get("ProgramFiles", ""),
                os.environ.get("ProgramW6432", ""),
                os.environ.get("ProgramFiles(x86)", ""),
                os.environ.get("LocalAppData", ""),
            ]
            suffixes = (
                os.path.join("Git", "cmd", "git.exe"),
                os.path.join("Git", "bin", "git.exe"),
                os.path.join("Programs", "Git", "cmd", "git.exe"),
            )
            for root in roots:
                if not root:
                    continue
                for suffix in suffixes:
                    candidate = os.path.join(root, suffix)
                    if os.path.isfile(candidate):
                        fallback.append(candidate)
        else:
            for candidate in ("/usr/bin/git", "/bin/git", "/usr/local/bin/git"):
                if os.path.isfile(candidate):
                    fallback.append(candidate)
        git_cmd = fallback[0] if fallback else "git"
    try:
        result = subprocess.run(
            [git_cmd] + args,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _resolve_canonical_tools_dir(repo_root):
    try:
        tool_dir, _, _, _ = canonical_tools_dir_details(
            repo_root,
            ws_id=os.environ.get(WORKSPACE_ID_ENV_KEY, ""),
            env=os.environ,
        )
    except RuntimeError as exc:
        return "", str(exc)
    return os.path.normpath(tool_dir), ""


def _canonicalize_tools_path(repo_root):
    try:
        env, _ = canonicalize_env_for_workspace(
            dict(os.environ),
            repo_root,
            ws_id=os.environ.get(WORKSPACE_ID_ENV_KEY, ""),
        )
    except RuntimeError as exc:
        return "", str(exc)
    os.environ.update(env)
    tool_dir = env.get("DOM_CANONICAL_TOOLS_DIR", "")
    if not tool_dir:
        tool_dir, detail = _resolve_canonical_tools_dir(repo_root)
        if not tool_dir:
            return "", detail
    return tool_dir, ""


def _path_contains_dir(path_value, target_dir):
    target_norm = os.path.normcase(os.path.normpath(target_dir))
    for entry in path_value.split(os.pathsep):
        if not entry:
            continue
        entry_norm = os.path.normcase(os.path.normpath(entry))
        if entry_norm == target_norm:
            return True
    return False


def parse_changed_files(output):
    if not output:
        return []
    return [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]


def get_changed_files(repo_root, diff_filter="ACMR"):
    env_files = os.environ.get("DOM_CHANGED_FILES", "").strip()
    if env_files:
        return [item.strip().replace("\\", "/") for item in env_files.split(";") if item.strip()]

    baseline = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    diff_output = run_git(["diff", "--name-only", "--diff-filter={}".format(diff_filter), "{}...HEAD".format(baseline)],
                          repo_root)
    if diff_output is not None:
        files = parse_changed_files(diff_output)
        if files:
            return files

    status_output = run_git(["status", "--porcelain"], repo_root)
    if status_output is None:
        return None
    files = []
    for line in status_output.splitlines():
        if not line:
            continue
        # Parse porcelain output defensively instead of assuming fixed offsets.
        parts = line.split(None, 1)
        path = parts[1].strip() if len(parts) == 2 else ""
        if path:
            files.append(path.replace("\\", "/"))
    return files


def get_diff_added_lines(repo_root):
    baseline = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    diff_output = run_git(["diff", "--unified=0", "{}...HEAD".format(baseline)], repo_root)
    if diff_output is None:
        return None
    current = None
    added = {}
    for line in diff_output.splitlines():
        if line.startswith("+++ "):
            if line.startswith("+++ b/"):
                current = line[6:].strip()
            else:
                current = None
            continue
        if not current:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added.setdefault(current, []).append(line[1:])
    return added


def _normalize_rel_path(path):
    return normalize_path(path or "").strip("/")


def _violation_to_record(raw):
    text = str(raw).strip()
    if not text:
        return {"raw": "", "rule_id": "INV-UNKNOWN", "detail": "", "path": ""}
    if ":" in text:
        rule_id, detail = text.split(":", 1)
        rule_id = rule_id.strip()
        detail = detail.strip()
    else:
        rule_id = "INV-UNKNOWN"
        detail = text

    path = ""
    if detail:
        first = detail.split()[0].strip()
        first = first.rstrip(",.;")
        if "/" in first and not first.startswith("("):
            if ":" in first:
                path = first.split(":", 1)[0]
            else:
                path = first
    return {"raw": text, "rule_id": rule_id, "detail": detail, "path": _normalize_rel_path(path)}


def _load_ruleset_catalog(repo_root):
    root = os.path.join(repo_root, RULESET_ROOT)
    errors = []
    catalog = {}
    if not os.path.isdir(root):
        errors.append("INV-REPOX-RULESET-MISSING: missing ruleset directory {}".format(RULESET_ROOT))
        return catalog, errors

    for entry in sorted(os.listdir(root)):
        if not entry.endswith(".json"):
            continue
        rel_file = _normalize_rel_path(os.path.join(RULESET_ROOT, entry))
        abs_file = os.path.join(root, entry)
        try:
            with open(abs_file, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError):
            errors.append("INV-REPOX-RULESET-MISSING: invalid ruleset json {}".format(rel_file))
            continue

        rules = payload.get("rules")
        if not isinstance(rules, list) or not rules:
            errors.append("INV-REPOX-RULESET-MISSING: ruleset has no rules {}".format(rel_file))
            continue

        for idx, rule in enumerate(rules, start=1):
            if not isinstance(rule, dict):
                errors.append("INV-REPOX-RULESET-MISSING: invalid rule record {}#{}".format(rel_file, idx))
                continue
            rule_id = str(rule.get("rule_id", "")).strip()
            severity = str(rule.get("severity", "")).strip().upper()
            scope_paths = rule.get("scope_paths")
            doc_link = str(rule.get("documentation", "")).strip()
            exemption_policy = str(rule.get("exemption_policy", "")).strip()
            if not rule_id:
                errors.append("INV-REPOX-RULESET-MISSING: missing rule_id {}#{}".format(rel_file, idx))
                continue
            if severity not in ("WARN", "FAIL"):
                errors.append("INV-REPOX-RULESET-MISSING: invalid severity {} for {}".format(severity, rule_id))
                continue
            if not isinstance(scope_paths, list):
                errors.append("INV-REPOX-RULESET-MISSING: scope_paths missing for {}".format(rule_id))
                continue
            if not doc_link:
                errors.append("INV-REPOX-RULESET-MISSING: documentation missing for {}".format(rule_id))
                continue
            if not exemption_policy:
                errors.append("INV-REPOX-RULESET-MISSING: exemption_policy missing for {}".format(rule_id))
                continue
            if rule_id in catalog:
                errors.append("INV-REPOX-RULESET-MISSING: duplicate rule_id {}".format(rule_id))
                continue
            catalog[rule_id] = {
                "rule_id": rule_id,
                "ruleset_id": str(payload.get("ruleset_id", "")).strip() or "repox/unknown",
                "severity": severity,
                "scope_paths": [normalize_path(str(p)) for p in scope_paths if str(p).strip()],
                "documentation": doc_link,
                "exemption_policy": exemption_policy,
                "ratchet_after": str(rule.get(RATCHET_KEY, "")).strip(),
            }
    if not catalog:
        errors.append("INV-REPOX-RULESET-MISSING: no rules loaded from {}".format(RULESET_ROOT))
    return catalog, errors


def _load_sidecar_exemptions(repo_root):
    errors = []
    exemptions = []
    path = os.path.join(repo_root, REPOX_EXEMPTIONS_PATH)
    if not os.path.isfile(path):
        return exemptions, errors

    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        errors.append("INV-REPOX-EXEMPTION-POLICY: invalid json {}".format(REPOX_EXEMPTIONS_PATH))
        return exemptions, errors

    entries = payload.get("exemptions")
    if not isinstance(entries, list):
        errors.append("INV-REPOX-EXEMPTION-POLICY: exemptions must be a list in {}".format(REPOX_EXEMPTIONS_PATH))
        return exemptions, errors

    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append("INV-REPOX-EXEMPTION-POLICY: invalid exemption entry {}#{}".format(REPOX_EXEMPTIONS_PATH, idx))
            continue
        rule_id = str(entry.get("rule_id", "")).strip()
        reason = str(entry.get("reason", "")).strip()
        expires = str(entry.get("expires", "")).strip()
        if not rule_id:
            errors.append("INV-REPOX-EXEMPTION-POLICY: missing rule_id in {}#{}".format(REPOX_EXEMPTIONS_PATH, idx))
            continue
        exemptions.append({
            "source": REPOX_EXEMPTIONS_PATH,
            "line": idx,
            "rule_id": rule_id,
            "reason": reason,
            "expires": expires,
            "path": _normalize_rel_path(entry.get("path", "")),
        })
    return exemptions, errors


def _load_inline_exemptions(repo_root):
    exemptions = []
    roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "libs"),
        os.path.join(repo_root, "tools"),
        os.path.join(repo_root, "scripts"),
        os.path.join(repo_root, "schema"),
        os.path.join(repo_root, "data"),
        os.path.join(repo_root, "tests"),
        os.path.join(repo_root, "docs"),
    ]
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS + DOC_EXTS + [".json", ".schema", ".yaml", ".yml", ".toml"]):
        text = read_text(path)
        if not text or "@repox:allow(" not in text:
            continue
        rel = repo_rel(repo_root, path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            match = EXEMPTION_INLINE_RE.search(line)
            if not match:
                continue
            tail = match.group("tail") or ""
            reason_match = EXEMPTION_REASON_RE.search(tail)
            expires_match = EXEMPTION_EXPIRES_RE.search(tail)
            exemptions.append({
                "source": rel,
                "line": line_no,
                "rule_id": match.group("rule_id").strip(),
                "reason": reason_match.group(1).strip() if reason_match else "",
                "expires": expires_match.group(1).strip() if expires_match else "",
                "path": rel,
            })
    return exemptions


def _rule_is_exempted(record, exemptions):
    rule_id = record.get("rule_id")
    path = _normalize_rel_path(record.get("path"))
    for exemption in exemptions:
        if exemption.get("rule_id") != rule_id:
            continue
        ex_path = _normalize_rel_path(exemption.get("path", ""))
        if not ex_path:
            return True
        if path and (path == ex_path or path.startswith(ex_path + "/") or ex_path.startswith(path + "/")):
            return True
        if path and ex_path and (path in ex_path or ex_path in path):
            return True
    return False


def _resolve_rule_severity(meta, today):
    severity = meta.get("severity", "FAIL")
    ratchet = meta.get("ratchet_after", "")
    if severity != "WARN":
        return severity
    ratchet_date = _parse_date(ratchet)
    if ratchet_date and today >= ratchet_date:
        return "FAIL"
    return "WARN"


def _apply_ruleset_policy(repo_root, violations, today=None):
    if today is None:
        today = date.today()
    records = [_violation_to_record(item) for item in violations]
    catalog, catalog_errors = _load_ruleset_catalog(repo_root)
    sidecar, sidecar_errors = _load_sidecar_exemptions(repo_root)
    inline = _load_inline_exemptions(repo_root)
    exemptions = sidecar + inline

    policy_failures = []
    policy_failures.extend(catalog_errors)
    policy_failures.extend(sidecar_errors)

    for exemption in exemptions:
        rule_id = exemption.get("rule_id", "")
        reason = exemption.get("reason", "")
        expires = exemption.get("expires", "")
        meta = catalog.get(rule_id)
        if meta is None:
            policy_failures.append(
                "INV-REPOX-EXEMPTION-POLICY: unknown rule_id {} in {}:{}".format(
                    rule_id, exemption.get("source"), exemption.get("line")
                )
            )
            continue
        policy = meta.get("exemption_policy", "")
        if policy == "deny":
            policy_failures.append(
                "INV-REPOX-EXEMPTION-POLICY: exemptions denied for {} at {}:{}".format(
                    rule_id, exemption.get("source"), exemption.get("line")
                )
            )
            continue
        if not reason:
            policy_failures.append(
                "INV-REPOX-EXEMPTION-POLICY: missing reason for {} at {}:{}".format(
                    rule_id, exemption.get("source"), exemption.get("line")
                )
            )
        if policy in ("allow_with_expiry", "allow"):
            expiry_date = _parse_date(expires)
            if expiry_date is None:
                policy_failures.append(
                    "INV-REPOX-EXEMPTION-POLICY: missing/invalid expiry for {} at {}:{}".format(
                        rule_id, exemption.get("source"), exemption.get("line")
                    )
                )
            elif expiry_date < today:
                policy_failures.append(
                    "INV-REPOX-EXEMPTION-POLICY: expired exemption for {} at {}:{} (expired {})".format(
                        rule_id, exemption.get("source"), exemption.get("line"), expires
                    )
                )

    fail_items = []
    warn_items = []
    for record in records:
        rule_id = record.get("rule_id")
        meta = catalog.get(rule_id)
        if meta is None:
            fail_items.append(
                "INV-REPOX-RULESET-MISSING: rule_id not mapped to ruleset {}".format(rule_id)
            )
            continue
        if _rule_is_exempted(record, exemptions):
            continue
        severity = _resolve_rule_severity(meta, today)
        if severity == "WARN":
            warn_items.append(record.get("raw"))
        else:
            fail_items.append(record.get("raw"))

    fail_items.extend(policy_failures)
    return sorted(set(fail_items)), sorted(set(warn_items))


def _collect_manifest_test_names(repo_root):
    names = set()
    roots = [os.path.join(repo_root, "tests"), os.path.join(repo_root, "cmake")]
    pattern = re.compile(r"dom_add_testx\s*\(\s*NAME\s+([A-Za-z0-9_]+)", re.MULTILINE)
    for path in iter_files(roots, DEFAULT_EXCLUDES, [".cmake", ".txt"]):
        text = read_text(path) or ""
        for match in pattern.finditer(text):
            names.add(match.group(1))
    return sorted(names)


def _build_proof_manifest(repo_root, warnings, failures):
    changed_files = get_changed_files(repo_root) or []
    changed = sorted(normalize_path(path) for path in changed_files)
    required_tests = set()
    required_invariants = set()
    required_test_tags = {"invariant"}
    impacted_subsystems = set()
    required_refusal_codes = {
        "CAMERA_REFUSE_ENTITLEMENT",
        "BLUEPRINT_REFUSE_CAPABILITY",
        "REFUSE_CAPABILITY_MISSING",
    }
    required_capability_checks = set(CAMERA_MODE_RUNTIME_CAPABILITIES + OBSERVER_TOOL_ENTITLEMENTS)

    for path in changed:
        top = path.split("/", 1)[0] if "/" in path else path
        if top in ("engine", "game", "client", "server", "launcher", "setup", "tools", "schema", "data", "docs", "tests", "libs"):
            impacted_subsystems.add(top)
        if path.startswith("client/") or path.startswith("libs/appcore/command/") or path.startswith("libs/appcore/ui_bind/"):
            required_tests.update({
                "capability_runtime_enforcement",
                "freecam_epistemics",
                "blueprint_refusal",
                "ui_client_menu_parity",
            })
            required_test_tags.update({"ui", "parity", "capability"})
            required_invariants.update({
                "INV-COMMAND-CAPABILITY-METADATA",
                "INV-RUNTIME-CAPABILITY-GUARDS",
                "INV-UI-CANONICAL-COMMAND",
            })
        if path.startswith("engine/") or path.startswith("game/"):
            required_tests.update({
                "inv_process_only_mutation",
                "invariant_process_only_mutation",
                "determinism_replay_hash_invariance",
            })
            required_test_tags.update({"runtime", "determinism", "regression"})
            required_invariants.update({
                "INV-PROCESS-REGISTRY",
                "INV-PROCESS-RUNTIME-ID",
            })
        if path.startswith("schema/") or path.startswith("data/"):
            required_tests.update({
                "schema_version_immutability_contracts",
                "schema_migration_contracts",
            })
            required_test_tags.update({"schema", "registry", "invariant"})
            required_invariants.update({
                "INV-SCHEMA-VERSION-BUMP",
                "INV-SCHEMA-MIGRATION-ROUTES",
            })
        if path.startswith("tools/"):
            required_test_tags.update({"tools", "integration"})
        if path.startswith("tests/"):
            required_test_tags.update({"regression"})
        if path.startswith("docs/"):
            required_test_tags.update({"docs"})

    manifest = {
        "schema_id": "dominium.repox.proof_manifest",
        "schema_version": "1.0.0",
        "generated_by": "scripts/ci/check_repox_rules.py",
        "changed_paths": changed,
        "changed_files": changed,
        "impacted_subsystems": sorted(impacted_subsystems),
        "impacted_invariants": sorted(required_invariants),
        "required_test_tags": sorted(required_test_tags),
        "required_capability_checks": sorted(required_capability_checks),
        "required_refusal_codes": sorted(required_refusal_codes),
        "required_invariants": sorted(required_invariants),
        "required_tests": sorted(required_tests),
        "focused_test_subset": sorted(required_tests),
        "warnings": sorted(set(warnings)),
        "failures": sorted(set(failures)),
        "available_testx_tests": _collect_manifest_test_names(repo_root),
    }
    return manifest


def write_proof_manifest(repo_root, out_path, warnings, failures):
    payload = _build_proof_manifest(repo_root, warnings, failures)
    target = os.path.join(repo_root, out_path)
    target_dir = os.path.dirname(target)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def parse_frozen_paths(text):
    lines = text.splitlines()
    paths = []
    in_section = False
    for line in lines:
        if line.strip() == FROZEN_SECTION:
            in_section = True
            continue
        if in_section and line.startswith(NEXT_SECTION_PREFIX):
            break
        if not in_section:
            continue
        if "|" not in line:
            continue
        match = PATH_RE.search(line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def load_frozen_paths(repo_root):
    index_path = os.path.join(repo_root, "docs", "architecture", "CONTRACTS_INDEX.md")
    if not os.path.isfile(index_path):
        return []
    text = read_text(index_path) or ""
    return parse_frozen_paths(text)


def load_canon_index(repo_root):
    path = os.path.join(repo_root, CANON_INDEX_PATH)
    if not os.path.isfile(path):
        return None
    text = read_text(path) or ""
    canon = {"CANONICAL": set(), "DERIVED": set(), "HISTORICAL": set()}
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## CANONICAL":
            current = "CANONICAL"
            continue
        if stripped == "## DERIVED":
            current = "DERIVED"
            continue
        if stripped == "## HISTORICAL":
            current = "HISTORICAL"
            continue
        if stripped.startswith("## "):
            current = None
            continue
        if current and stripped.startswith("-"):
            match = PATH_RE.search(stripped)
            if match:
                canon[current].add(normalize_path(match.group(1)))
    return canon


def parse_doc_header(text):
    if text is None:
        return None
    lines = text.splitlines()
    if len(lines) < 4:
        return None
    if not (lines[0].startswith("Status:") and lines[1].startswith("Last Reviewed:")
            and lines[2].startswith("Supersedes:") and lines[3].startswith("Superseded By:")):
        return None
    return {
        "status": lines[0].split(":", 1)[1].strip(),
        "reviewed": lines[1].split(":", 1)[1].strip(),
        "supersedes": lines[2].split(":", 1)[1].strip(),
        "superseded_by": lines[3].split(":", 1)[1].strip(),
    }


def extract_doc_refs(text):
    refs = set()
    if not text:
        return refs
    for match in DOC_REF_RE.finditer(text):
        token = match.group(0).rstrip(").,;:'\"")
        refs.add(normalize_path(token))
    return refs


def check_doc_headers(repo_root, canon_index):
    invariant_id = "INV-DOC-STATUS-HEADER"
    skip_header = is_override_active(repo_root, invariant_id)
    skip_index = is_override_active(repo_root, "INV-CANON-INDEX")
    skip_superseded = is_override_active(repo_root, "INV-CANON-NO-SUPERSEDED")
    violations = []
    docs_root = os.path.join(repo_root, DOCS_ROOT)
    if not os.path.isdir(docs_root):
        return [] if skip_header else ["{}: missing docs/ directory".format(invariant_id)]

    canon = canon_index or {"CANONICAL": set(), "DERIVED": set(), "HISTORICAL": set()}
    for path in iter_files([docs_root], DEFAULT_EXCLUDES, DOC_EXTS):
        rel = repo_rel(repo_root, path)
        text = read_text(path)
        header = parse_doc_header(text)
        if header is None:
            if not skip_header:
                violations.append("{}: missing status header: {}".format(invariant_id, rel))
            continue
        status = header.get("status", "")
        reviewed = header.get("reviewed", "")
        superseded_by = header.get("superseded_by", "")
        if status not in DOC_STATUS_VALUES:
            if not skip_header:
                violations.append("{}: invalid status '{}' in {}".format(invariant_id, status, rel))
        if _parse_date(reviewed) is None:
            if not skip_header:
                violations.append("{}: invalid Last Reviewed date '{}' in {}".format(invariant_id, reviewed, rel))
        if status == "CANONICAL" and superseded_by and superseded_by.lower() != "none":
            if not skip_superseded:
                violations.append("INV-CANON-NO-SUPERSEDED: canonical doc marked superseded: {}".format(rel))
        if status == "HISTORICAL" and not rel.startswith("docs/archive/"):
            if not skip_index:
                violations.append("INV-CANON-INDEX: historical doc outside docs/archive: {}".format(rel))
        if rel in canon.get("CANONICAL", set()) and status != "CANONICAL":
            if not skip_index:
                violations.append("INV-CANON-INDEX: canon index mismatch (expected CANONICAL): {}".format(rel))
        if rel in canon.get("DERIVED", set()) and status != "DERIVED":
            if not skip_index:
                violations.append("INV-CANON-INDEX: canon index mismatch (expected DERIVED): {}".format(rel))
        if rel in canon.get("HISTORICAL", set()) and status != "HISTORICAL":
            if not skip_index:
                violations.append("INV-CANON-INDEX: canon index mismatch (expected HISTORICAL): {}".format(rel))
        if rel.startswith("docs/architecture/") and rel not in canon.get("CANONICAL", set()) and rel not in canon.get("DERIVED", set()):
            if not skip_index:
                violations.append("INV-CANON-INDEX: architecture doc missing from CANON_INDEX: {}".format(rel))
        if rel.startswith("docs/archive/") and rel not in canon.get("HISTORICAL", set()):
            if not skip_index:
                violations.append("INV-CANON-INDEX: archive doc missing from CANON_INDEX: {}".format(rel))
        if status == "CANONICAL" and rel not in canon.get("CANONICAL", set()):
            if not skip_index:
                violations.append("INV-CANON-INDEX: canonical doc not listed in CANON_INDEX: {}".format(rel))
    return violations


def check_canon_index_entries(repo_root, canon_index):
    invariant_id = "INV-CANON-INDEX"
    if is_override_active(repo_root, invariant_id):
        return []
    if canon_index is None:
        return ["{}: missing {}".format(invariant_id, CANON_INDEX_PATH)]
    violations = []
    for entries in canon_index.values():
        for rel in entries:
            if not os.path.isfile(os.path.join(repo_root, rel)):
                violations.append("{}: listed doc missing: {}".format(invariant_id, rel))
    return violations


def _normalize_canon_level(value):
    if not value:
        return ""
    cleaned = str(value).strip().lower()
    cleaned = cleaned.replace("_", "-").replace(" ", "")
    if cleaned.startswith("canon-"):
        cleaned = cleaned[len("canon-"):]
    return cleaned


def check_canon_state(repo_root):
    invariant_id = "INV-CANON-STATE"
    if is_override_active(repo_root, invariant_id):
        return []
    path = os.path.join(repo_root, CANON_STATE_PATH)
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, CANON_STATE_PATH)]
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return ["{}: invalid json {}".format(invariant_id, CANON_STATE_PATH)]

    canon_level = _normalize_canon_level(payload.get("canon_level"))
    if not canon_level:
        return ["{}: canon_level missing or empty in {}".format(invariant_id, CANON_STATE_PATH)]

    validated = payload.get("validated_by", {})
    for key in ("repox", "testx", "determinism", "schema"):
        if validated.get(key) is not True:
            return ["{}: validated_by.{} must be true in {}".format(invariant_id, key, CANON_STATE_PATH)]

    evidence = payload.get("evidence", {})
    for key in ("process_registry", "schema_alignment", "testx_contract"):
        rel = evidence.get(key, "")
        if not rel:
            return ["{}: evidence.{} missing in {}".format(invariant_id, key, CANON_STATE_PATH)]
        if not os.path.isfile(os.path.join(repo_root, rel)):
            return ["{}: evidence path missing for {}: {}".format(invariant_id, key, rel)]

    for path in iter_files([os.path.join(repo_root, DOCS_ROOT)], DEFAULT_EXCLUDES, DOC_EXTS):
        rel = repo_rel(repo_root, path)
        text = read_text(path) or ""
        for match in CANON_LEVEL_RE.finditer(text):
            doc_level = _normalize_canon_level("clean-{}".format(match.group(1)))
            if doc_level and doc_level != canon_level:
                return ["{}: doc canon level mismatch: {} -> {} (expected {})".format(
                    invariant_id, rel, doc_level, canon_level
                )]
        for match in CANON_LEVEL_FIELD_RE.finditer(text):
            doc_level = _normalize_canon_level(match.group(1))
            if doc_level and doc_level != canon_level:
                return ["{}: doc canon level mismatch: {} -> {} (expected {})".format(
                    invariant_id, rel, doc_level, canon_level
                )]
    return []


def check_doc_references(repo_root, canon_index):
    if is_override_active(repo_root, "INV-CANON-NO-HIST-REF"):
        return []
    violations = []
    canon = canon_index or {"CANONICAL": set(), "DERIVED": set(), "HISTORICAL": set()}
    historical = canon.get("HISTORICAL", set())

    for path in iter_files([os.path.join(repo_root, DOCS_ROOT)], DEFAULT_EXCLUDES, DOC_EXTS):
        rel = repo_rel(repo_root, path)
        text = read_text(path) or ""
        refs = extract_doc_refs(text)
        for ref in refs:
            if ref.startswith("docs/archive/") and not rel.startswith("docs/archive/"):
                if rel != CANON_INDEX_PATH:
                    violations.append("INV-CANON-NO-HIST-REF: archived doc referenced by {}".format(rel))
            if rel != CANON_INDEX_PATH and rel in canon.get("CANONICAL", set()) and ref in historical:
                violations.append("INV-CANON-NO-HIST-REF: canonical doc references historical: {} -> {}".format(rel, ref))
    return violations


def check_code_doc_references(repo_root, canon_index):
    if is_override_active(repo_root, "INV-CANON-CODE-REF"):
        return []
    violations = []
    canon = canon_index or {"CANONICAL": set(), "DERIVED": set(), "HISTORICAL": set()}
    canonical = canon.get("CANONICAL", set())
    code_roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "tools"),
    ]
    for path in iter_files(code_roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path)
        text = read_text(path) or ""
        refs = extract_doc_refs(text)
        for ref in refs:
            if ref not in canonical:
                violations.append("INV-CANON-CODE-REF: non-canonical doc referenced by code: {} -> {}".format(rel, ref))
    return violations


def check_schema_version_bumps(repo_root):
    invariant_id = "INV-SCHEMA-VERSION-BUMP"
    if is_override_active(repo_root, invariant_id):
        return []
    violations = []
    changed_files = get_changed_files(repo_root)
    if changed_files is None:
        return ["{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    schema_files = [path for path in changed_files if path.startswith("schema/") and path.endswith(".schema")]
    if not schema_files:
        return []
    baseline = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    for rel in schema_files:
        baseline_blob = run_git(["show", "{}:{}".format(baseline, rel)], repo_root)
        if baseline_blob is None:
            continue
        current_path = os.path.join(repo_root, rel)
        if not os.path.isfile(current_path):
            # Deleted schemas are handled by migration-route validation.
            continue
        current_text = read_text(current_path) or ""
        baseline_match = SCHEMA_VERSION_RE.search(baseline_blob)
        current_match = SCHEMA_VERSION_RE.search(current_text)
        if not baseline_match or not current_match:
            violations.append("{}: schema_version missing in {}".format(invariant_id, rel))
            continue
        diff = run_git(["diff", "--unified=0", baseline, "--", rel], repo_root)
        if diff is None:
            violations.append("{}: unable to diff {}".format(invariant_id, rel))
            continue
        removed = re.search(r"^-schema_version:\s*(.+)$", diff, re.MULTILINE)
        added = re.search(r"^\+schema_version:\s*(.+)$", diff, re.MULTILINE)
        if not (removed and added) or removed.group(1).strip() == added.group(1).strip():
            violations.append("{}: schema_version not bumped for {}".format(invariant_id, rel))
    return violations


def _load_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _sha256_file(path):
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(1 << 16)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError:
        return ""
    return digest.hexdigest()


def _parse_semver(value):
    if not isinstance(value, str):
        return None
    match = SEMVER_RE.match(value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _load_schema_migration_registry(repo_root):
    path = os.path.join(repo_root, SCHEMA_MIGRATION_REGISTRY_REL)
    payload = _load_json_file(path)
    return path, payload


def _migration_route_exists(routes, schema_id, source_version, target_version):
    for route in routes:
        if not isinstance(route, dict):
            continue
        if route.get("schema_id") != schema_id:
            continue
        if route.get("source_version") != source_version:
            continue
        if route.get("target_version") != target_version:
            continue
        return True
    return False


def check_schema_migration_routes(repo_root):
    invariant_id = "INV-SCHEMA-MIGRATION-ROUTES"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    path, migration_registry = _load_schema_migration_registry(repo_root)
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, SCHEMA_MIGRATION_REGISTRY_REL)]
    if not isinstance(migration_registry, dict):
        return ["{}: invalid json {}".format(invariant_id, SCHEMA_MIGRATION_REGISTRY_REL)]

    if migration_registry.get("schema_id") != SCHEMA_MIGRATION_REGISTRY_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, SCHEMA_MIGRATION_REGISTRY_REL))
    if _parse_semver(migration_registry.get("schema_version")) is None:
        violations.append("{}: invalid schema_version in {}".format(invariant_id, SCHEMA_MIGRATION_REGISTRY_REL))

    routes = migration_registry.get("migrations")
    if not isinstance(routes, list):
        return ["{}: migrations missing in {}".format(invariant_id, SCHEMA_MIGRATION_REGISTRY_REL)]

    process_registry = _load_json_file(os.path.join(repo_root, PROCESS_REGISTRY_REL))
    process_ids = set()
    if isinstance(process_registry, dict) and isinstance(process_registry.get("records"), list):
        for entry in process_registry.get("records"):
            if isinstance(entry, dict):
                process_id = entry.get("process_id")
                if isinstance(process_id, str):
                    process_ids.add(process_id)

    route_keys = set()
    for idx, route in enumerate(routes):
        if not isinstance(route, dict):
            violations.append("{}: invalid migration route at index {}".format(invariant_id, idx))
            continue
        schema_id = route.get("schema_id")
        source_version = route.get("source_version")
        target_version = route.get("target_version")
        process_id = route.get("migration_process_id")
        function_ref = route.get("migration_function")
        invocation = route.get("invocation")
        data_loss = route.get("data_loss")

        if not schema_id:
            violations.append("{}: route missing schema_id at index {}".format(invariant_id, idx))
            continue
        source_semver = _parse_semver(source_version)
        target_semver = _parse_semver(target_version)
        if source_semver is None or target_semver is None:
            violations.append("{}: invalid semver route {} {} -> {}".format(
                invariant_id, schema_id, source_version, target_version
            ))
            continue
        if source_semver >= target_semver:
            violations.append("{}: non-forward migration route {} {} -> {}".format(
                invariant_id, schema_id, source_version, target_version
            ))
        key = (schema_id, source_version, target_version)
        if key in route_keys:
            violations.append("{}: duplicate migration route {} {} -> {}".format(
                invariant_id, schema_id, source_version, target_version
            ))
        route_keys.add(key)

        if not process_id:
            violations.append("{}: missing migration_process_id for {} {} -> {}".format(
                invariant_id, schema_id, source_version, target_version
            ))
        elif process_id not in process_ids:
            violations.append("{}: migration process not in process registry: {}".format(invariant_id, process_id))
        if not function_ref or "::" not in function_ref:
            violations.append("{}: invalid migration_function for {} {} -> {}".format(
                invariant_id, schema_id, source_version, target_version
            ))
        else:
            rel_file = function_ref.split("::", 1)[0]
            if not os.path.isfile(os.path.join(repo_root, rel_file)):
                violations.append("{}: migration function file missing: {}".format(invariant_id, rel_file))
        if invocation != "explicit":
            violations.append("{}: migration invocation must be explicit for {} {} -> {}".format(
                invariant_id, schema_id, source_version, target_version
            ))
        if not isinstance(data_loss, str) or not data_loss:
            violations.append("{}: data_loss missing for {} {} -> {}".format(
                invariant_id, schema_id, source_version, target_version
            ))

    changed_files = get_changed_files(repo_root)
    if changed_files is None:
        violations.append("{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(
            invariant_id
        ))
        return violations

    baseline = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    schema_files = [path for path in changed_files if path.startswith("schema/") and path.endswith(".schema")]
    for rel in schema_files:
        baseline_blob = run_git(["show", "{}:{}".format(baseline, rel)], repo_root)
        if baseline_blob is None:
            continue
        current_text = read_text(os.path.join(repo_root, rel)) or ""
        old_version_match = SCHEMA_VERSION_RE.search(baseline_blob)
        new_version_match = SCHEMA_VERSION_RE.search(current_text)
        old_schema_id_match = SCHEMA_ID_RE.search(baseline_blob)
        new_schema_id_match = SCHEMA_ID_RE.search(current_text)
        if not old_version_match or not new_version_match or not old_schema_id_match or not new_schema_id_match:
            continue
        old_version = old_version_match.group(1).strip()
        new_version = new_version_match.group(1).strip()
        old_schema_id = old_schema_id_match.group(1).strip()
        new_schema_id = new_schema_id_match.group(1).strip()
        if old_schema_id != new_schema_id:
            violations.append("{}: schema_id changed in {}".format(invariant_id, rel))
            continue
        old_semver = _parse_semver(old_version)
        new_semver = _parse_semver(new_version)
        if old_semver is None or new_semver is None:
            continue
        if old_semver[0] != new_semver[0]:
            if not _migration_route_exists(routes, new_schema_id, old_version, new_version):
                violations.append("{}: missing migration route for {} {} -> {}".format(
                    invariant_id, new_schema_id, old_version, new_version
                ))

    return violations


def check_schema_no_implicit_defaults(repo_root):
    invariant_id = "INV-SCHEMA-NO-IMPLICIT-DEFAULTS"
    if is_override_active(repo_root, invariant_id):
        return []
    added = get_diff_added_lines(repo_root)
    if added is None:
        return ["{}: unable to determine changed lines; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    violations = []
    default_re = re.compile(r"\bdefault\b", re.IGNORECASE)
    for rel_path, lines in added.items():
        rel = rel_path.replace("\\", "/")
        if not rel.startswith("schema/") or not rel.endswith(".schema"):
            continue
        for idx, line in enumerate(lines, start=1):
            if default_re.search(line):
                violations.append("{}: implicit default token in {} (added line {})".format(
                    invariant_id, rel, idx
                ))
    return violations


def check_unversioned_schema_references(repo_root):
    invariant_id = "INV-SCHEMA-VERSION-REF"
    if is_override_active(repo_root, invariant_id):
        return []
    added = get_diff_added_lines(repo_root)
    if added is None:
        return ["{}: unable to determine changed lines; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    violations = []
    for rel_path, lines in added.items():
        rel = rel_path.replace("\\", "/")
        if not any(rel.startswith(prefix) for prefix in ("engine/", "game/", "client/", "server/", "tools/", "scripts/")):
            continue
        for idx, line in enumerate(lines, start=1):
            for match in SCHEMA_ID_LITERAL_RE.finditer(line):
                schema_id = match.group(1)
                # New schema-id literals in code must carry an explicit version reference.
                if "schema_version" not in line and "@" not in line:
                    violations.append("{}: unversioned schema reference {}:{} -> {}".format(
                        invariant_id, rel, idx, schema_id
                    ))
    return violations


def _manifest_record(payload):
    if isinstance(payload, dict) and isinstance(payload.get("record"), dict):
        return payload.get("record")
    if isinstance(payload, dict):
        return payload
    return {}


def _extract_capability_ids(values):
    output = []
    if not isinstance(values, list):
        return output
    for entry in values:
        if isinstance(entry, dict):
            capability_id = entry.get("capability_id")
        else:
            capability_id = entry
        if isinstance(capability_id, str):
            output.append(capability_id)
    return output


def check_pack_capability_metadata(repo_root):
    invariant_id = "INV-CAPABILITY-PACK-METADATA"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    legacy_keys = ("requires" + "_stage", "provides" + "_stage", "stage" + "_features")
    roots = [
        os.path.join(repo_root, "data", "packs"),
        os.path.join(repo_root, "data", "worldgen"),
        os.path.join(repo_root, "tests", "fixtures"),
        os.path.join(repo_root, "tests", "distribution", "fixtures"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, [".json"]):
            if os.path.basename(path) != "pack_manifest.json":
                continue
            rel = repo_rel(repo_root, path)
            payload = _load_json_file(path)
            if payload is None:
                violations.append("{}: invalid json {}".format(invariant_id, rel))
                continue
            record = _manifest_record(payload)
            for key in legacy_keys:
                if key in record:
                    violations.append("{}: legacy gating key '{}' present in {}".format(invariant_id, key, rel))

            requires_caps = _extract_capability_ids(record.get("requires_capabilities"))
            provides_caps = _extract_capability_ids(record.get("provides_capabilities"))
            entitlements = _extract_capability_ids(record.get("entitlements"))

            if not isinstance(record.get("requires_capabilities"), list):
                violations.append("{}: requires_capabilities missing in {}".format(invariant_id, rel))
            if not isinstance(record.get("provides_capabilities"), list):
                violations.append("{}: provides_capabilities missing in {}".format(invariant_id, rel))
            if not isinstance(record.get("entitlements"), list):
                violations.append("{}: entitlements missing in {}".format(invariant_id, rel))

            for capability_id in requires_caps + provides_caps + entitlements:
                if PACK_CAPABILITY_RE.match(capability_id) is None:
                    violations.append("{}: invalid capability_id '{}' in {}".format(invariant_id, capability_id, rel))

            if len(provides_caps) == 0:
                violations.append("{}: provides_capabilities empty in {}".format(invariant_id, rel))
    return violations


def _collect_prealpha_pack_ids(repo_root):
    pack_ids = set()
    root = os.path.join(repo_root, "data", "packs")
    if not os.path.isdir(root):
        return pack_ids

    for path in iter_files([root], DEFAULT_EXCLUDES, [".json"]):
        if os.path.basename(path) != "pack_manifest.json":
            continue
        payload = _load_json_file(path)
        if payload is None:
            continue
        record = _manifest_record(payload)
        pack_id = str(record.get("pack_id", "")).strip()
        if not pack_id:
            continue
        tags = set([str(value) for value in (record.get("pack_tags") or []) if isinstance(value, str)])
        extensions = record.get("extensions") if isinstance(record.get("extensions"), dict) else {}
        maturity = str(extensions.get("maturity", "")).strip()
        stability = str(extensions.get("stability", "")).strip()
        if PREALPHA_MATURITY_TAG in tags or maturity == "prealpha":
            pack_ids.add(pack_id)
        if PREALPHA_STABILITY_TAG in tags or stability == "disposable":
            # Stability markers alone are not enough; keep this branch explicit for policy diagnostics.
            continue
    return pack_ids


def check_prealpha_pack_isolation(repo_root):
    invariant_id = "INV-PREALPHA-PACK-ISOLATION"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    prealpha_pack_ids = _collect_prealpha_pack_ids(repo_root)
    if not prealpha_pack_ids:
        return violations

    packs_root = os.path.join(repo_root, "data", "packs")
    for path in iter_files([packs_root], DEFAULT_EXCLUDES, [".json"]):
        if os.path.basename(path) != "pack_manifest.json":
            continue
        rel = repo_rel(repo_root, path)
        payload = _load_json_file(path)
        if payload is None:
            continue
        record = _manifest_record(payload)
        pack_id = str(record.get("pack_id", "")).strip()
        if pack_id not in prealpha_pack_ids:
            continue
        tags = set([str(value) for value in (record.get("pack_tags") or []) if isinstance(value, str)])
        extensions = record.get("extensions") if isinstance(record.get("extensions"), dict) else {}
        maturity = str(extensions.get("maturity", "")).strip()
        stability = str(extensions.get("stability", "")).strip()
        if PREALPHA_MATURITY_TAG not in tags or maturity != "prealpha":
            violations.append("{}: prealpha pack missing explicit maturity marker in {}".format(invariant_id, rel))
        if PREALPHA_STABILITY_TAG not in tags or stability != "disposable":
            violations.append("{}: prealpha pack missing explicit disposable stability marker in {}".format(invariant_id, rel))

    runtime_roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "setup"),
        os.path.join(repo_root, "libs"),
        os.path.join(repo_root, "tools"),
    ]
    for path in iter_files(runtime_roots, DEFAULT_EXCLUDES, SOURCE_EXTS + [".py"]):
        rel = repo_rel(repo_root, path)
        rel_norm = normalize_path(rel)
        if rel_norm.startswith("tests/"):
            continue
        text = read_text(path) or ""
        for pack_id in prealpha_pack_ids:
            if pack_id in text:
                violations.append("{}: runtime path references prealpha pack id '{}' in {}".format(
                    invariant_id, pack_id, rel_norm
                ))
    return violations


def check_bugreport_resolution(repo_root):
    invariant_id = "INV-BUGREPORT-RESOLUTION"
    if is_override_active(repo_root, invariant_id):
        return []
    root = os.path.join(repo_root, "data", "logs", "bugreports")
    if not os.path.isdir(root):
        return []

    violations = []
    for path in iter_files([root], DEFAULT_EXCLUDES, [".json"]):
        rel = repo_rel(repo_root, path)
        payload = _load_json_file(path)
        if payload is None:
            violations.append("{}: invalid json {}".format(invariant_id, rel))
            continue
        record = _manifest_record(payload)
        status = str(record.get("status", "")).strip().lower()
        if status != "resolved":
            continue
        regression_test = str(record.get("regression_test", "")).strip()
        deferred_reason = str(record.get("deferred_reason", "")).strip()
        if not regression_test and not deferred_reason:
            violations.append(
                "{}: resolved bugreport missing regression_test or deferred_reason in {}".format(
                    invariant_id, rel
                )
            )
    return violations


def _iter_pkg_manifest_sidecars(repo_root):
    root = os.path.join(repo_root, DIST_PKG_ROOT_REL)
    if not os.path.isdir(root):
        return []
    sidecars = []
    for path in iter_files([root], DEFAULT_EXCLUDES, [".json"]):
        rel = repo_rel(repo_root, path)
        rel_norm = normalize_path(rel)
        if rel_norm.endswith(".dompkg.manifest.json"):
            sidecars.append((rel_norm, path))
    sidecars.sort(key=lambda item: item[0])
    return sidecars


def _load_json_required(path, invariant_id):
    payload = _load_json_file(path)
    if payload is None:
        return None, ["{}: invalid json {}".format(invariant_id, normalize_path(path))]
    if not isinstance(payload, dict):
        return None, ["{}: payload must be object {}".format(invariant_id, normalize_path(path))]
    return payload, []


def _json_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("1", "true", "yes", "on"):
            return True
    return False


def check_pkg_manifest_fields(repo_root):
    invariant_id = "INV-PKG-MANIFEST-FIELDS"
    if is_override_active(repo_root, invariant_id):
        return []
    violations = []
    for rel, abs_path in _iter_pkg_manifest_sidecars(repo_root):
        payload = _load_json_file(abs_path)
        if not isinstance(payload, dict):
            violations.append("{}: invalid manifest json {}".format(invariant_id, rel))
            continue
        for field in PKG_MANIFEST_REQUIRED_FIELDS:
            if field not in payload:
                violations.append("{}: missing field '{}' in {}".format(invariant_id, field, rel))
    return violations


def check_pkg_capability_metadata(repo_root):
    invariant_id = "INV-PKG-CAPABILITY-METADATA"
    if is_override_active(repo_root, invariant_id):
        return []
    violations = []
    for rel, abs_path in _iter_pkg_manifest_sidecars(repo_root):
        payload = _load_json_file(abs_path)
        if not isinstance(payload, dict):
            continue
        requires = payload.get("requires_capabilities")
        provides = payload.get("provides_capabilities")
        if not isinstance(requires, list):
            violations.append("{}: requires_capabilities must be list in {}".format(invariant_id, rel))
            continue
        if not isinstance(provides, list):
            violations.append("{}: provides_capabilities must be list in {}".format(invariant_id, rel))
            continue
        if not provides:
            violations.append("{}: provides_capabilities empty in {}".format(invariant_id, rel))
        for field_name, values in (("requires_capabilities", requires), ("provides_capabilities", provides)):
            for value in values:
                cap_id = value if isinstance(value, str) else value.get("capability_id") if isinstance(value, dict) else ""
                if not isinstance(cap_id, str) or not PACK_CAPABILITY_RE.match(cap_id):
                    violations.append("{}: invalid capability '{}' in {} field {}".format(
                        invariant_id, cap_id, rel, field_name
                    ))
    return violations


def check_pkg_signature_policy(repo_root):
    invariant_id = "INV-PKG-SIGNATURE-POLICY"
    if is_override_active(repo_root, invariant_id):
        return []
    release_required = _json_bool(os.environ.get("DOM_RELEASE_BUILD", "0"))
    if not release_required:
        return []
    violations = []
    for rel, abs_path in _iter_pkg_manifest_sidecars(repo_root):
        payload = _load_json_file(abs_path)
        if not isinstance(payload, dict):
            continue
        signature = payload.get("signature")
        if not isinstance(signature, dict):
            violations.append("{}: signature missing for release package {}".format(invariant_id, rel))
    return violations


def check_dist_sys_shipping(repo_root):
    invariant_id = "INV-DIST-SYS-SHIPPING"
    if is_override_active(repo_root, invariant_id):
        return []
    changed = get_changed_files(repo_root)
    if changed is None:
        return ["{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    has_sys = False
    has_shipping = False
    for rel in changed:
        rel_norm = normalize_path(rel)
        if rel_norm.startswith("dist/sys/"):
            has_sys = True
        if rel_norm.startswith("dist/pkg/") or rel_norm.startswith("dist/meta/"):
            has_shipping = True
    if has_sys and not has_shipping:
        return ["{}: dist/sys changed without dist/pkg or dist/meta updates".format(invariant_id)]
    return []


def check_derived_pkg_index_freshness(repo_root):
    invariant_id = "INV-DERIVED-PKG-INDEX-FRESHNESS"
    if is_override_active(repo_root, invariant_id):
        return []
    changed = get_changed_files(repo_root)
    if changed is None:
        return ["{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    pkg_changes = []
    has_index_refresh = False
    for rel in changed:
        rel_norm = normalize_path(rel)
        if rel_norm.startswith("dist/pkg/") and ("/pkgs/" in rel_norm or rel_norm.endswith(".dompkg.manifest.json")):
            pkg_changes.append(rel_norm)
        if "/index/pkg_index." in rel_norm or "/build_manifest." in rel_norm:
            has_index_refresh = True
    if pkg_changes and not has_index_refresh:
        return ["{}: package artifacts changed without pkg index/build manifest refresh".format(invariant_id)]
    return []


def check_platform_registry(repo_root):
    invariant_id = "INV-PLATFORM-REGISTRY"
    if is_override_active(repo_root, invariant_id):
        return []
    abs_path = os.path.join(repo_root, PLATFORM_REGISTRY_REL)
    payload = _load_json_file(abs_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, PLATFORM_REGISTRY_REL)]
    if payload.get("schema_id") != PLATFORM_REGISTRY_SCHEMA_ID:
        return ["{}: schema_id mismatch in {}".format(invariant_id, PLATFORM_REGISTRY_REL)]
    record = payload.get("record")
    if not isinstance(record, dict):
        return ["{}: record missing in {}".format(invariant_id, PLATFORM_REGISTRY_REL)]
    platforms = record.get("platforms")
    if not isinstance(platforms, list) or not platforms:
        return ["{}: platforms missing in {}".format(invariant_id, PLATFORM_REGISTRY_REL)]
    tuples = set()
    violations = []
    for entry in platforms:
        if not isinstance(entry, dict):
            violations.append("{}: invalid platform entry in {}".format(invariant_id, PLATFORM_REGISTRY_REL))
            continue
        platform = str(entry.get("platform", "")).strip()
        arch = str(entry.get("arch", "")).strip()
        abi_id = str(entry.get("abi_id", "")).strip()
        if not platform or not arch or not abi_id:
            violations.append("{}: incomplete platform entry in {}".format(invariant_id, PLATFORM_REGISTRY_REL))
            continue
        tuples.add((platform, arch, abi_id))
    for rel, abs_manifest in _iter_pkg_manifest_sidecars(repo_root):
        payload = _load_json_file(abs_manifest)
        if not isinstance(payload, dict):
            continue
        key = (str(payload.get("platform", "")).strip(), str(payload.get("arch", "")).strip(), str(payload.get("abi", "")).strip())
        if all(key) and key not in tuples:
            violations.append("{}: package tuple not declared in platform registry {} ({}/{}/{})".format(
                invariant_id, rel, key[0], key[1], key[2]
            ))
    return violations


def _iter_directories(path):
    if not os.path.isdir(path):
        return []
    items = []
    try:
        for name in sorted(os.listdir(path)):
            abs_path = os.path.join(path, name)
            if os.path.isdir(abs_path):
                items.append(name)
    except OSError:
        return []
    return items


def check_platform_id_canonical(repo_root):
    invariant_id = "INV-PLATFORM-ID-CANONICAL"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    abs_registry = os.path.join(repo_root, PLATFORM_REGISTRY_REL)
    payload = _load_json_file(abs_registry)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, PLATFORM_REGISTRY_REL)]
    record = payload.get("record")
    if not isinstance(record, dict):
        return ["{}: record missing in {}".format(invariant_id, PLATFORM_REGISTRY_REL)]

    declared_platforms = set()
    for entry in record.get("platforms") or []:
        if not isinstance(entry, dict):
            continue
        platform = str(entry.get("platform", "")).strip()
        if not platform:
            continue
        declared_platforms.add(platform)
        if platform in FORBIDDEN_PLATFORM_ALIASES:
            violations.append("{}: forbidden alias '{}' in {}".format(
                invariant_id, platform, PLATFORM_REGISTRY_REL.replace("\\", "/")
            ))
        if platform not in CANONICAL_PLATFORM_IDS:
            violations.append("{}: non-canonical platform '{}' in {}".format(
                invariant_id, platform, PLATFORM_REGISTRY_REL.replace("\\", "/")
            ))

    for forbidden in FORBIDDEN_PLATFORM_ALIASES:
        if forbidden in declared_platforms:
            violations.append("{}: forbidden alias '{}' declared in platform registry".format(
                invariant_id, forbidden
            ))

    for rel_root in DIST_PLATFORM_CANON_ROOTS:
        abs_root = os.path.join(repo_root, rel_root)
        for name in _iter_directories(abs_root):
            name_norm = normalize_path(name)
            rel = normalize_path(os.path.join(rel_root, name))
            if name_norm in FORBIDDEN_PLATFORM_ALIASES:
                violations.append("{}: forbidden platform alias directory {}".format(invariant_id, rel))
                continue
            # Dist platform roots should use canonical platform IDs only.
            if rel_root != os.path.join("dist", "redist") and name_norm not in CANONICAL_PLATFORM_IDS:
                violations.append("{}: non-canonical platform directory {}".format(invariant_id, rel))

    for rel, abs_manifest in _iter_pkg_manifest_sidecars(repo_root):
        payload = _load_json_file(abs_manifest)
        if not isinstance(payload, dict):
            continue
        platform = str(payload.get("platform", "")).strip()
        if not platform:
            continue
        if platform in FORBIDDEN_PLATFORM_ALIASES:
            violations.append("{}: manifest uses forbidden platform alias {} ({})".format(
                invariant_id, platform, rel
            ))
        elif platform not in CANONICAL_PLATFORM_IDS:
            violations.append("{}: manifest uses non-canonical platform {} ({})".format(
                invariant_id, platform, rel
            ))

    mode_payload = _load_json_file(os.path.join(repo_root, MODE_BACKEND_REL))
    if isinstance(mode_payload, dict):
        mode_record = mode_payload.get("record")
        if isinstance(mode_record, dict):
            for idx, entry in enumerate(mode_record.get("entries") or []):
                if not isinstance(entry, dict):
                    continue
                platform = str(entry.get("platform", "")).strip()
                if not platform:
                    continue
                if platform in FORBIDDEN_PLATFORM_ALIASES:
                    violations.append("{}: mode backend entry {} uses forbidden alias '{}'".format(
                        invariant_id, idx, platform
                    ))
                elif platform not in CANONICAL_PLATFORM_IDS:
                    violations.append("{}: mode backend entry {} uses non-canonical platform '{}'".format(
                        invariant_id, idx, platform
                    ))
    return violations


def check_product_graph_constraints(repo_root):
    invariant_id = "INV-PRODUCT-GRAPH-CONSTRAINTS"
    if is_override_active(repo_root, invariant_id):
        return []
    abs_path = os.path.join(repo_root, PRODUCT_GRAPH_REL)
    payload = _load_json_file(abs_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, PRODUCT_GRAPH_REL)]
    if payload.get("schema_id") != PRODUCT_GRAPH_SCHEMA_ID:
        return ["{}: schema_id mismatch in {}".format(invariant_id, PRODUCT_GRAPH_REL)]
    record = payload.get("record")
    if not isinstance(record, dict):
        return ["{}: record missing in {}".format(invariant_id, PRODUCT_GRAPH_REL)]
    nodes = record.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return ["{}: nodes missing in {}".format(invariant_id, PRODUCT_GRAPH_REL)]

    node_ids = set()
    violations = []
    for node in nodes:
        if not isinstance(node, dict):
            violations.append("{}: invalid node entry in {}".format(invariant_id, PRODUCT_GRAPH_REL))
            continue
        product_id = str(node.get("product_id", "")).strip()
        if not product_id:
            violations.append("{}: node missing product_id in {}".format(invariant_id, PRODUCT_GRAPH_REL))
            continue
        if product_id in node_ids:
            violations.append("{}: duplicate product_id '{}' in {}".format(invariant_id, product_id, PRODUCT_GRAPH_REL))
            continue
        node_ids.add(product_id)
        if product_id in ("dominium.product.sdk.engine", "dominium.product.sdk.game"):
            requires_exports = [str(value) for value in (node.get("requires_exports") or [])]
            if "export:bin.setup" in requires_exports or "export:bin.launcher" in requires_exports:
                violations.append("{}: sdk product depends on setup/launcher export {}".format(invariant_id, product_id))
    return violations


def check_mode_backend_registry(repo_root):
    invariant_id = "INV-MODE-BACKEND-REGISTRY"
    if is_override_active(repo_root, invariant_id):
        return []
    mode_path = os.path.join(repo_root, MODE_BACKEND_REL)
    mode_payload = _load_json_file(mode_path)
    if not isinstance(mode_payload, dict):
        return ["{}: invalid json {}".format(invariant_id, MODE_BACKEND_REL)]
    if mode_payload.get("schema_id") != MODE_BACKEND_SCHEMA_ID:
        return ["{}: schema_id mismatch in {}".format(invariant_id, MODE_BACKEND_REL)]
    record = mode_payload.get("record")
    if not isinstance(record, dict):
        return ["{}: record missing in {}".format(invariant_id, MODE_BACKEND_REL)]
    entries = record.get("entries")
    if not isinstance(entries, list) or not entries:
        return ["{}: entries missing in {}".format(invariant_id, MODE_BACKEND_REL)]

    platform_payload = _load_json_file(os.path.join(repo_root, PLATFORM_REGISTRY_REL))
    platform_tuples = set()
    if isinstance(platform_payload, dict):
        platform_record = platform_payload.get("record")
        if isinstance(platform_record, dict):
            for item in platform_record.get("platforms") or []:
                if isinstance(item, dict):
                    platform_tuples.add((str(item.get("platform", "")).strip(), str(item.get("arch", "")).strip(), str(item.get("abi_id", "")).strip()))

    violations = []
    for entry in entries:
        if not isinstance(entry, dict):
            violations.append("{}: invalid mode backend entry in {}".format(invariant_id, MODE_BACKEND_REL))
            continue
        key = (str(entry.get("platform", "")).strip(), str(entry.get("arch", "")).strip(), str(entry.get("abi", "")).strip())
        if key not in platform_tuples:
            violations.append("{}: mode backend tuple not in platform registry ({}/{}/{})".format(
                invariant_id, key[0], key[1], key[2]
            ))
        fallback_order = entry.get("fallback_order")
        if not isinstance(fallback_order, list) or "cli" not in [str(value) for value in fallback_order]:
            violations.append("{}: fallback_order must include cli for tuple ({}/{}/{})".format(
                invariant_id, key[0], key[1], key[2]
            ))
    return violations


def check_dist_sys_derived(repo_root):
    invariant_id = "INV-DIST-SYS-DERIVED"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    cmake_path = os.path.join(repo_root, "CMakeLists.txt")
    cmake_text = read_text(cmake_path) or ""
    block = re.search(r"add_custom_target\(pkg_pack_all(.*?)\)\s*\n", cmake_text, re.S)
    if block:
        body = block.group(1)
        disallowed_tokens = (
            "DOM_DIST_LEAF",
            "DOM_DIST_BIN_LAUNCH",
            "DOM_DIST_BIN_GAME",
            "DOM_DIST_BIN_ENGINE",
            "DOM_DIST_BIN_REND",
            "DOM_DIST_BIN_SHARE",
            "dist/sys/",
            "dist\\sys\\",
        )
        for token in disallowed_tokens:
            if token in body:
                violations.append("{}: pkg_pack_all consumes dist/sys runtime path token '{}'".format(
                    invariant_id, token
                ))
                break
    else:
        violations.append("{}: unable to locate pkg_pack_all in CMakeLists.txt".format(invariant_id))

    pack_script_rel = os.path.join("tools", "distribution", "pkg_pack_all.py")
    pack_script = read_text(os.path.join(repo_root, pack_script_rel)) or ""
    if "dist/sys" in pack_script.replace("\\", "/"):
        violations.append("{}: tools/distribution/pkg_pack_all.py references dist/sys as packaging input".format(
            invariant_id
        ))
    return violations


def check_mode_backend_selection_contract(repo_root):
    invariant_id = "INV-MODE-BACKEND-SELECTION"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    runtime_roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "setup"),
        os.path.join(repo_root, "libs"),
        os.path.join(repo_root, "app"),
        os.path.join(repo_root, "tools"),
    ]
    backend_literal_re = re.compile(r"dominium\.backend\.[a-z0-9_.-]+")
    for path in iter_files(runtime_roots, DEFAULT_EXCLUDES, SOURCE_EXTS + [".py"]):
        rel = repo_rel(repo_root, path)
        rel_norm = normalize_path(rel)
        if rel_norm == normalize_path(MODE_BACKEND_REL):
            continue
        if rel_norm.startswith("tests/"):
            continue
        text = read_text(path) or ""
        for match in backend_literal_re.finditer(text):
            violations.append("{}: hardcoded mode backend literal '{}' in {}".format(
                invariant_id, match.group(0), rel_norm
            ))
    return violations


def check_portable_run_contract(repo_root):
    invariant_id = "INV-PORTABLE-RUN-CONTRACT"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    setup_rel = normalize_path(os.path.join("tools", "setup", "setup_cli.py"))
    launcher_rel = normalize_path(os.path.join("tools", "launcher", "launcher_cli.py"))
    setup_text = read_text(os.path.join(repo_root, setup_rel.replace("/", os.sep))) or ""
    launcher_text = read_text(os.path.join(repo_root, launcher_rel.replace("/", os.sep))) or ""

    if "--install-root" not in setup_text:
        violations.append("{}: tools/setup/setup_cli.py missing --install-root contract".format(invariant_id))
    if "--lockfile" not in launcher_text:
        violations.append("{}: tools/launcher/launcher_cli.py missing --lockfile contract".format(invariant_id))
    if "--mode" not in launcher_text and "--run-mode" not in launcher_text:
        violations.append("{}: tools/launcher/launcher_cli.py missing mode selector contract".format(invariant_id))
    if "--mode" not in setup_text and "--ui-mode" not in setup_text:
        violations.append("{}: tools/setup/setup_cli.py missing mode selector contract".format(invariant_id))
    return violations


def _iter_tool_invocation_scan_files(repo_root):
    roots = [
        os.path.join(repo_root, "scripts"),
        os.path.join(repo_root, "tests"),
        os.path.join(repo_root, "tools"),
        os.path.join(repo_root, "cmake"),
        os.path.join(repo_root, ".github"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, TOOL_SCAN_EXTS):
            rel = normalize_path(repo_rel(repo_root, path))
            if any(rel.startswith(prefix) for prefix in TOOL_SCAN_SKIP_PREFIXES):
                continue
            yield path
    root_cmake = os.path.join(repo_root, "CMakeLists.txt")
    if os.path.isfile(root_cmake):
        yield root_cmake


def check_tool_name_only(repo_root):
    invariant_id = "INV-TOOL-NAME-ONLY"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    tool_tokens = tuple(str(tool_id).strip() for tool_id in CANONICAL_TOOL_IDS if str(tool_id).strip())
    tool_tokens_lower = tuple(token.lower() for token in tool_tokens)
    target_markers = tuple("target_file:{}".format(token).lower() for token in tool_tokens)
    scan_markers = tool_tokens_lower + target_markers
    token_res = {
        tool_id: re.compile(r"([A-Za-z0-9_./\\:-]*{}(?:\.exe)?)".format(re.escape(tool_id)), re.IGNORECASE)
        for tool_id in tool_tokens
    }
    for path in _iter_tool_invocation_scan_files(repo_root):
        rel = repo_rel(repo_root, path)
        text = read_text(path) or ""
        text_lower = text.lower()
        if not any(marker in text_lower for marker in scan_markers):
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            stripped_lower = stripped.lower()
            if not any(marker in stripped_lower for marker in scan_markers):
                continue
            for tool_id in tool_tokens:
                marker = "target_file:{}".format(tool_id).lower()
                if marker in stripped_lower:
                    violations.append(
                        "{}: {}:{} path-indirection invocation forbidden ({})".format(
                            invariant_id, rel, idx, "TARGET_FILE:{}".format(tool_id)
                        )
                    )
                for match in token_res[tool_id].finditer(stripped):
                    token = match.group(1)
                    token_lower = token.lower()
                    if "/" in token or "\\" in token or token_lower.startswith(".") or ":" in token_lower:
                        violations.append(
                            "{}: {}:{} path-based tool invocation forbidden ({})".format(
                                invariant_id, rel, idx, token
                            )
                        )
    return sorted(set(violations))


def check_tools_dir_exists(repo_root):
    invariant_id = "INV-TOOLS-DIR-EXISTS"
    if is_override_active(repo_root, invariant_id):
        return []

    tool_dir, detail = _resolve_canonical_tools_dir(repo_root)
    if not tool_dir:
        return ["{}: unable to resolve canonical tools path ({})".format(invariant_id, detail)]
    if not os.path.isdir(tool_dir):
        return [
            "INV-TOOLS-DIR-MISSING: canonical tools directory missing {} (build tools to {} via target ui_bind_phase or tools target)".format(
                normalize_path(tool_dir), normalize_path(tool_dir)
            )
        ]

    env_path = os.environ.get("PATH", "")
    if not _path_contains_dir(env_path, tool_dir):
        return ["{}: canonical tools directory not active in process PATH {}".format(invariant_id, normalize_path(tool_dir))]

    dom_tools_path = os.environ.get("DOM_TOOLS_PATH", "")
    if dom_tools_path and os.path.normcase(os.path.normpath(dom_tools_path)) != os.path.normcase(os.path.normpath(tool_dir)):
        return [
            "{}: DOM_TOOLS_PATH mismatch (expected {}, got {})".format(
                invariant_id, normalize_path(tool_dir), normalize_path(dom_tools_path)
            )
        ]
    return []


def check_tool_unresolvable(repo_root):
    invariant_id = "INV-TOOL-UNRESOLVABLE"
    if is_override_active(repo_root, invariant_id):
        return []

    tool_dir, detail = _resolve_canonical_tools_dir(repo_root)
    if not tool_dir:
        return ["{}: unable to resolve canonical tools path ({})".format(invariant_id, detail)]
    if not os.path.isdir(tool_dir):
        return ["{}: canonical tools directory missing {}".format(invariant_id, normalize_path(tool_dir))]

    violations = []
    resolved = {}
    for tool_id in CANONICAL_TOOL_IDS:
        tool_path = resolve_tool(tool_id, os.environ)
        if not tool_path:
            violations.append("{}: tool not discoverable by PATH {}".format(invariant_id, tool_id))
            continue
        resolved[tool_id] = tool_path

    bind_path = resolved.get("tool_ui_bind")
    if bind_path:
        try:
            probe = subprocess.run(
                [bind_path, "--help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                check=False,
            )
        except OSError as exc:
            violations.append("{}: tool_ui_bind help probe failed: {}".format(invariant_id, exc))
        except subprocess.TimeoutExpired:
            violations.append("{}: tool_ui_bind help probe timeout".format(invariant_id))
        else:
            if probe.returncode != 0:
                violations.append(
                    "{}: tool_ui_bind help probe returned {} ({})".format(
                        invariant_id, probe.returncode, probe.stdout.strip()
                    )
                )
    return violations


def _iter_direct_gate_scan_files(repo_root):
    roots = [os.path.join(repo_root, rel_root) for rel_root in DIRECT_GATE_SCAN_ROOTS]
    excludes = DEFAULT_EXCLUDES + [".git", "out", "build", "dist"]
    for path in iter_files(roots, excludes, DIRECT_GATE_SCAN_EXTS):
        rel = normalize_path(repo_rel(repo_root, path))
        if rel in DIRECT_GATE_ALLOWLIST:
            continue
        yield rel, path


def check_no_direct_gate_calls(repo_root):
    invariant_id = "INV-NO-DIRECT-GATE-CALLS"
    if is_override_active(repo_root, invariant_id):
        return []

    repox_direct_re = re.compile(r"\bscripts[\\/]+ci[\\/]+check_repox_rules\.py\b", re.IGNORECASE)
    ui_bind_direct_re = re.compile(r"(^|\\s)tool_ui_bind(?:\\.exe)?\\b", re.IGNORECASE)
    ctest_direct_re = re.compile(r"(^|\\s)ctest\\b", re.IGNORECASE)
    allowed_forwarders = (
        "scripts/dev/gate.py",
        "scripts/dev/gate_shim.py",
        "scripts/dev/run_repox.py",
        "scripts/dev/run_testx.py",
        "scripts/dev/testx_proof_engine.py",
    )

    violations = []
    for rel, path in _iter_direct_gate_scan_files(repo_root):
        text = read_text(path) or ""
        for idx, line in enumerate(text.splitlines(), start=1):
            normalized = line.replace("\\", "/")
            stripped = normalized.strip()
            if not stripped:
                continue

            if repox_direct_re.search(normalized):
                if not any(token in normalized for token in allowed_forwarders):
                    violations.append(
                        "{}: {}:{} direct RepoX invocation forbidden; use scripts/dev/run_repox.py or gate.py".format(
                            invariant_id, rel, idx
                        )
                    )

            if ui_bind_direct_re.search(normalized):
                if "tool_ui_bind --help" in normalized.lower():
                    continue
                violations.append(
                    "{}: {}:{} direct tool_ui_bind call forbidden; route through gate.py or scripts/dev/dev.py".format(
                        invariant_id, rel, idx
                    )
                )

            if ctest_direct_re.search(normalized):
                violations.append(
                    "{}: {}:{} direct ctest invocation forbidden; route through scripts/dev/run_testx.py or gate.py".format(
                        invariant_id, rel, idx
                    )
                )

    return sorted(set(violations))


def _preset_cache_value(preset_map, preset_name, key):
    seen = set()
    current = preset_name
    while current and current not in seen:
        seen.add(current)
        preset = preset_map.get(current)
        if not isinstance(preset, dict):
            return None
        cache = preset.get("cacheVariables")
        if isinstance(cache, dict) and key in cache:
            return str(cache.get(key))
        inherits = preset.get("inherits")
        if isinstance(inherits, list):
            current = str(inherits[0]) if inherits else ""
        elif isinstance(inherits, str):
            current = inherits
        else:
            current = ""
    return None


def check_build_preset_contract(repo_root):
    invariant_id = "INV-BUILD-PRESET-CONTRACT"
    if is_override_active(repo_root, invariant_id):
        return []

    presets_rel = "CMakePresets.json"
    presets_path = os.path.join(repo_root, presets_rel)
    payload = _load_json_file(presets_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, presets_rel)]

    configure = payload.get("configurePresets")
    build = payload.get("buildPresets")
    if not isinstance(configure, list) or not isinstance(build, list):
        return ["{}: missing configurePresets/buildPresets in {}".format(invariant_id, presets_rel)]

    configure_map = {}
    build_map = {}
    for entry in configure:
        if isinstance(entry, dict):
            name = str(entry.get("name", "")).strip()
            if name:
                configure_map[name] = entry
    for entry in build:
        if isinstance(entry, dict):
            name = str(entry.get("name", "")).strip()
            if name:
                build_map[name] = entry

    violations = []
    for preset_name in BUILD_PRESET_CONTRACT_CONFIGURE:
        if preset_name not in configure_map:
            violations.append("{}: missing configure preset {}".format(invariant_id, preset_name))
        if preset_name not in build_map:
            violations.append("{}: missing build preset {}".format(invariant_id, preset_name))

    for preset_name, expected_target in BUILD_PRESET_CONTRACT_TARGETS.items():
        build_entry = build_map.get(preset_name)
        if not isinstance(build_entry, dict):
            continue
        targets = build_entry.get("targets")
        if not isinstance(targets, list):
            violations.append("{}: build preset {} missing targets list".format(invariant_id, preset_name))
            continue
        normalized = [str(item).strip() for item in targets if str(item).strip()]
        if expected_target not in normalized:
            violations.append(
                "{}: build preset {} missing target {} (got {})".format(
                    invariant_id, preset_name, expected_target, ",".join(normalized)
                )
            )

    for release_preset in ("release-winnt-x86_64", "release-linux-x86_64", "release-macos-arm64"):
        build_kind = _preset_cache_value(configure_map, release_preset, "DOM_BUILD_KIND")
        if build_kind != "release":
            violations.append(
                "{}: configure preset {} must set DOM_BUILD_KIND=release".format(invariant_id, release_preset)
            )

    vscode_tasks_rel = ".vscode/tasks.json"
    vscode_tasks_path = os.path.join(repo_root, vscode_tasks_rel)
    tasks_payload = _load_json_file(vscode_tasks_path)
    if not isinstance(tasks_payload, dict):
        violations.append("{}: invalid json {}".format(invariant_id, vscode_tasks_rel))
        return violations
    tasks = tasks_payload.get("tasks")
    if not isinstance(tasks, list):
        violations.append("{}: missing tasks in {}".format(invariant_id, vscode_tasks_rel))
        return violations

    build_task_ok = False
    test_task_ok = False
    for task in tasks:
        if not isinstance(task, dict):
            continue
        label = str(task.get("label", "")).strip()
        args = task.get("args")
        if not isinstance(args, list):
            continue
        args_norm = [str(value).strip() for value in args]
        if label == "Build (MSVC DEV DEBUG)" and "msvc-dev-debug" in args_norm:
            build_task_ok = True
        if label == "Test (VERIFY FAST)" and "verify_fast" in args_norm:
            test_task_ok = True
    if not build_task_ok:
        violations.append("{}: missing VSCode default build task for msvc-dev-debug".format(invariant_id))
    if not test_task_ok:
        violations.append("{}: missing VSCode default test task for verify_fast".format(invariant_id))

    return violations


def check_dist_release_lane_gate(repo_root):
    invariant_id = "INV-DIST-RELEASE-LANE-GATE"
    if is_override_active(repo_root, invariant_id):
        return []

    cmake_rel = "CMakeLists.txt"
    cmake_text = read_text(os.path.join(repo_root, cmake_rel)) or ""
    violations = []

    if "add_custom_target(dom_dist_release_lane_guard" not in cmake_text:
        violations.append("{}: {} missing dom_dist_release_lane_guard target".format(invariant_id, cmake_rel))
    if "cmake/check_release_lane.cmake" not in cmake_text:
        violations.append("{}: {} missing check_release_lane.cmake hook".format(invariant_id, cmake_rel))

    for target_name in ("dist_pack", "dist_index", "dist_verify", "dist_smoke"):
        pattern = re.compile(r"add_custom_target\(\s*{}\s+DEPENDS\s+dom_dist_release_lane_guard".format(target_name))
        if not pattern.search(cmake_text):
            violations.append(
                "{}: {} target {} must depend on dom_dist_release_lane_guard".format(
                    invariant_id, cmake_rel, target_name
                )
            )
    if "add_custom_target(dist_all DEPENDS dist_pack dist_index dist_verify dist_build_manifest dist_smoke)" not in cmake_text:
        violations.append("{}: {} dist_all target contract mismatch".format(invariant_id, cmake_rel))

    if "add_dependencies(testx_all pkg_verify_all" in cmake_text:
        violations.append("{}: {} testx_all must not hard-depend on dist packaging targets".format(invariant_id, cmake_rel))

    guard_rel = "cmake/check_release_lane.cmake"
    guard_path = os.path.join(repo_root, guard_rel.replace("/", os.sep))
    guard_text = read_text(guard_path) or ""
    for marker in (
        "DIST_RELEASE_ONLY|build_kind_missing",
        "DIST_RELEASE_ONLY|invalid_build_kind",
        "DIST_RELEASE_ONLY|missing_gbn",
    ):
        if marker not in guard_text:
            violations.append("{}: {} missing marker {}".format(invariant_id, guard_rel, marker))

    return violations


def _parse_command_registry_entries(text):
    entries = []
    current = []
    collecting = False
    for line in text.splitlines():
        if not collecting and re.search(r"^\s*\{\s*DOM_APP_CMD_", line):
            collecting = True
            current = [line]
            if "}" in line:
                entries.append(" ".join(current))
                collecting = False
            continue
        if collecting:
            current.append(line)
            if "}" in line:
                entries.append(" ".join(current))
                collecting = False
    return entries


def _parse_command_names(text):
    names = set()
    for entry in _parse_command_registry_entries(text):
        match = re.search(r"\{\s*DOM_APP_CMD_[^,]+,\s*\"([^\"]+)\"", entry)
        if match:
            names.add(match.group(1))
    return names


def check_command_capability_metadata(repo_root):
    invariant_id = "INV-COMMAND-CAPABILITY-METADATA"
    if is_override_active(repo_root, invariant_id):
        return []

    path = os.path.join(repo_root, COMMAND_REGISTRY_REL)
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, COMMAND_REGISTRY_REL.replace("\\", "/"))]
    text = read_text(path) or ""
    entries = _parse_command_registry_entries(text)
    if not entries:
        return ["{}: no command entries found".format(invariant_id)]

    violations = []
    capability_ref_re = re.compile(r",\s*(k_[A-Za-z0-9_]+)\s*,\s*(\d+)u\s*,\s*DOM_EPISTEMIC_SCOPE_[A-Z_]+")
    scope_re = re.compile(r"DOM_EPISTEMIC_SCOPE_[A-Z_]+")
    for entry in entries:
        name_match = re.search(r"\{\s*DOM_APP_CMD_[^,]+,\s*\"([^\"]+)\"", entry)
        cmd_name = name_match.group(1) if name_match else "<unknown>"
        capability_match = capability_ref_re.search(entry)
        scope_match = scope_re.search(entry)
        if not capability_match:
            violations.append("{}: required_capabilities missing for command {}".format(invariant_id, cmd_name))
            continue
        if not scope_match:
            violations.append("{}: epistemic_scope missing for command {}".format(invariant_id, cmd_name))
    return violations


def check_ui_canonical_command_bindings(repo_root):
    invariant_id = "INV-UI-CANONICAL-COMMAND"
    if is_override_active(repo_root, invariant_id):
        return []

    registry_path = os.path.join(repo_root, COMMAND_REGISTRY_REL)
    binding_path = os.path.join(repo_root, UI_BIND_TABLE_REL)
    if not os.path.isfile(registry_path):
        return ["{}: missing {}".format(invariant_id, COMMAND_REGISTRY_REL.replace("\\", "/"))]
    if not os.path.isfile(binding_path):
        return ["{}: missing {}".format(invariant_id, UI_BIND_TABLE_REL.replace("\\", "/"))]

    registry_text = read_text(registry_path) or ""
    binding_text = read_text(binding_path) or ""
    command_names = _parse_command_names(registry_text)
    if not command_names:
        return ["{}: command registry empty".format(invariant_id)]

    violations = []
    binding_re = re.compile(r"\{\s*\"[^\"]+\",\s*\"[^\"]+\",\s*\"([^\"]+)\",\s*\d+\s*\}")
    for match in binding_re.finditer(binding_text):
        action_key = match.group(1)
        if action_key not in command_names:
            violations.append("{}: UI action key not in canonical command registry: {}".format(
                invariant_id, action_key
            ))
    return violations


def _line_with_token(text, token):
    for idx, line in enumerate(text.splitlines(), start=1):
        if token in line:
            return idx
    return 0


def check_camera_blueprint_command_metadata(repo_root):
    invariant_id = "INV-CAMERA-BLUEPRINT-METADATA"
    if is_override_active(repo_root, invariant_id):
        return []

    path = os.path.join(repo_root, COMMAND_REGISTRY_REL)
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, COMMAND_REGISTRY_REL.replace("\\", "/"))]
    text = read_text(path) or ""
    entries = _parse_command_registry_entries(text)
    if not entries:
        return ["{}: no command entries found".format(invariant_id)]

    arr_re = re.compile(r"static const char\* (k_[A-Za-z0-9_]+)\[\] = \{([^}]*)\};")
    cap_arrays = {}
    for match in arr_re.finditer(text):
        cap_arrays[match.group(1)] = re.findall(r'"([^\"]+)"', match.group(2))

    meta_re = re.compile(
        r",\s*(k_[A-Za-z0-9_]+)\s*,\s*(\d+)u\s*,\s*(k_[A-Za-z0-9_]+)\s*,\s*(\d+)u\s*,\s*"
        r"(k_[A-Za-z0-9_]+)\s*,\s*(\d+)u\s*,\s*(DOM_EPISTEMIC_SCOPE_[A-Z_]+)\s*\}"
    )
    violations = []
    found = {}
    for entry in entries:
        name_match = re.search(r"\{\s*DOM_APP_CMD_[^,]+,\s*\"([^\"]+)\"", entry)
        if not name_match:
            continue
        cmd_name = name_match.group(1)
        if cmd_name not in CAMERA_BLUEPRINT_COMMAND_EXPECTATIONS:
            continue
        expected = CAMERA_BLUEPRINT_COMMAND_EXPECTATIONS[cmd_name]
        line_no = _line_with_token(text, "\"{}\"".format(cmd_name))
        rel = COMMAND_REGISTRY_REL.replace("\\", "/")
        found[cmd_name] = 1
        meta_match = meta_re.search(entry)
        if not meta_match:
            violations.append(
                "{}: {}:{} missing command metadata for {}".format(
                    invariant_id, rel, line_no or 1, cmd_name
                )
            )
            continue
        failure_ref = meta_match.group(1)
        cap_ref = meta_match.group(5)
        cap_count = int(meta_match.group(6))
        scope = meta_match.group(7)
        caps = cap_arrays.get(cap_ref, [])
        if cap_count <= 0:
            violations.append(
                "{}: {}:{} required_capabilities empty for {}".format(
                    invariant_id, rel, line_no or 1, cmd_name
                )
            )
        for capability_id in expected["required_capabilities"]:
            if capability_id not in caps:
                violations.append(
                    "{}: {}:{} missing required capability {} for {}".format(
                        invariant_id, rel, line_no or 1, capability_id, cmd_name
                    )
                )
        if scope != expected["epistemic_scope"]:
            violations.append(
                "{}: {}:{} epistemic_scope mismatch for {} (expected {}, got {})".format(
                    invariant_id, rel, line_no or 1, cmd_name, expected["epistemic_scope"], scope
                )
            )
        if failure_ref != expected["failure_ref"]:
            violations.append(
                "{}: {}:{} failure code set mismatch for {} (expected {}, got {})".format(
                    invariant_id, rel, line_no or 1, cmd_name, expected["failure_ref"], failure_ref
                )
            )

    for cmd_name in CAMERA_BLUEPRINT_COMMAND_EXPECTATIONS:
        if cmd_name not in found:
            violations.append("{}: missing canonical command {}".format(invariant_id, cmd_name))
    return violations


def check_observer_freecam_entitlement_gate(repo_root):
    invariant_id = "INV-OBSERVER-FREECAM-ENTITLEMENT"
    if is_override_active(repo_root, invariant_id):
        return []

    rel = "client/shell/client_shell.c"
    path = os.path.join(repo_root, "client", "shell", "client_shell.c")
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, rel)]

    text = read_text(path) or ""
    line_mode = _line_with_token(text, "camera.set_mode")
    line_set_camera = _line_with_token(text, "static int dom_client_shell_set_camera")
    line_policy = _line_with_token(text, "dom_shell_camera_allowed(&shell->world.summary.camera")
    line_refusal = _line_with_token(text, "CAMERA_REFUSE_ENTITLEMENT")
    line_assignment = _line_with_token(text, "strncpy(shell->world.camera_mode, resolved_camera_id")
    violations = []
    if line_mode <= 0:
        violations.append("{}: {} missing camera.set_mode parser branch".format(invariant_id, rel))
    if line_set_camera <= 0:
        violations.append("{}: {} missing dom_client_shell_set_camera handler".format(invariant_id, rel))
    if line_policy <= 0:
        violations.append("{}: {} missing dom_shell_camera_allowed policy gate".format(invariant_id, rel))
    for capability_id in CAMERA_MODE_RUNTIME_CAPABILITIES:
        line_cap = _line_with_token(text, capability_id)
        if line_cap <= 0:
            violations.append("{}: {} missing runtime capability gate for {}".format(invariant_id, rel, capability_id))
        elif line_policy > 0 and line_cap > line_policy:
            violations.append(
                "{}: {} capability gate for {} appears after policy selection".format(
                    invariant_id, rel, capability_id
                )
            )
    for entitlement_id in OBSERVER_TOOL_ENTITLEMENTS:
        line_entitlement = _line_with_token(text, entitlement_id)
        if line_entitlement <= 0:
            violations.append("{}: {} missing entitlement gate {}".format(invariant_id, rel, entitlement_id))
        elif line_policy > 0 and line_entitlement > line_policy:
            violations.append(
                "{}: {} entitlement gate for {} appears after policy selection".format(
                    invariant_id, rel, entitlement_id
                )
            )
    if line_refusal <= 0:
        violations.append("{}: {} missing CAMERA_REFUSE_ENTITLEMENT refusal".format(invariant_id, rel))
    if _line_with_token(text, "result=refused reason=entitlement mode=observer") <= 0:
        violations.append("{}: {} missing observer entitlement refusal event".format(invariant_id, rel))
    if line_assignment <= 0:
        violations.append("{}: {} missing camera mode assignment".format(invariant_id, rel))

    observer_guard_re = re.compile(
        r"observer_mode\s*&&\s*!dom_shell_capability_allowed\s*\(\s*shell\s*,\s*\"ui\.camera\.mode\.observer\"\s*\)",
        re.S,
    )
    if not observer_guard_re.search(text):
        violations.append("{}: {} missing observer-mode capability guard expression".format(invariant_id, rel))

    memory_guard_re = re.compile(
        r"DOM_SHELL_CAMERA_MEMORY\s*\)\s*==\s*0\s*&&\s*!dom_shell_capability_allowed\s*\(\s*shell\s*,\s*\"ui\.camera\.mode\.memory\"\s*\)",
        re.S,
    )
    if not memory_guard_re.search(text):
        violations.append("{}: {} missing memory-mode capability guard expression".format(invariant_id, rel))

    entitlement_guard_re = re.compile(
        r"!dom_shell_capability_allowed\s*\(\s*shell\s*,\s*\"tool\.truth\.view\"\s*\)\s*\|\|\s*"
        r"!dom_shell_capability_allowed\s*\(\s*shell\s*,\s*\"tool\.observation\.stream\"\s*\)\s*\|\|\s*"
        r"!dom_shell_capability_allowed\s*\(\s*shell\s*,\s*\"tool\.memory\.read\"\s*\)",
        re.S,
    )
    if not entitlement_guard_re.search(text):
        violations.append("{}: {} missing full observer entitlement conjunction".format(invariant_id, rel))
    if line_assignment > 0:
        for capability_id in CAMERA_MODE_RUNTIME_CAPABILITIES:
            line_cap = _line_with_token(text, capability_id)
            if line_cap > 0 and line_cap > line_assignment:
                violations.append(
                    "{}: {} capability gate for {} appears after camera mode assignment".format(
                        invariant_id, rel, capability_id
                    )
                )
        for entitlement_id in OBSERVER_TOOL_ENTITLEMENTS:
            line_ent = _line_with_token(text, entitlement_id)
            if line_ent > 0 and line_ent > line_assignment:
                violations.append(
                    "{}: {} entitlement gate for {} appears after camera mode assignment".format(
                        invariant_id, rel, entitlement_id
                    )
                )
    return violations


def check_runtime_command_capability_guards(repo_root):
    invariant_id = "INV-RUNTIME-CAPABILITY-GUARDS"
    if is_override_active(repo_root, invariant_id):
        return []

    rel = "client/shell/client_shell.c"
    path = os.path.join(repo_root, "client", "shell", "client_shell.c")
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, rel)]

    text = read_text(path) or ""
    required_tokens = (
        "dom_shell_capability_allowed(shell, \"ui.camera.mode.embodied\")",
        "dom_shell_capability_allowed(shell, \"ui.camera.mode.memory\")",
        "dom_shell_capability_allowed(shell, \"ui.camera.mode.observer\")",
        "const char* required_capability = preview ? \"ui.blueprint.preview\" : \"ui.blueprint.place\"",
        "dom_shell_capability_allowed(shell, required_capability)",
        "dom_shell_capability_allowed(shell, \"tool.truth.view\")",
        "dom_shell_capability_allowed(shell, \"tool.observation.stream\")",
        "dom_shell_capability_allowed(shell, \"tool.memory.read\")",
        "BLUEPRINT_REFUSE_CAPABILITY",
        "CAMERA_REFUSE_ENTITLEMENT",
    )
    violations = []
    for token in required_tokens:
        line_no = _line_with_token(text, token)
        if line_no <= 0:
            violations.append("{}: {} missing required guard token {}".format(invariant_id, rel, token))

    line_blueprint_func = _line_with_token(text, "static int dom_shell_interaction_place_internal")
    line_blueprint_cap = _line_with_token(text, "const char* required_capability = preview ? \"ui.blueprint.preview\" : \"ui.blueprint.place\"")
    line_camera_parser = _line_with_token(text, "strcmp(token, \"camera.set_mode\")")
    line_camera_dispatch = _line_with_token(text, "return dom_client_shell_set_camera(shell, camera_id")
    line_pose_dispatch = _line_with_token(text, "return dom_client_shell_set_camera_pose(shell, x, y, z, has_pose")
    if line_blueprint_func > 0 and line_blueprint_cap > 0 and line_blueprint_cap < line_blueprint_func:
        violations.append("{}: {} blueprint capability selection outside interaction handler".format(invariant_id, rel))
    if line_camera_parser <= 0 or line_camera_dispatch <= 0:
        violations.append("{}: {} camera command parser/dispatch branch missing".format(invariant_id, rel))
    elif line_camera_dispatch < line_camera_parser:
        violations.append("{}: {} camera command dispatch appears before parser branch".format(invariant_id, rel))
    if line_pose_dispatch <= 0:
        violations.append("{}: {} camera.set_pose dispatch missing".format(invariant_id, rel))
    return violations


def check_client_canonical_bridge(repo_root):
    invariant_id = "INV-CLIENT-CANONICAL-BRIDGE"
    if is_override_active(repo_root, invariant_id):
        return []

    bridge_rel = "client/core/client_command_bridge.c"
    registry_rel = "client/core/client_commands_registry.c"
    runtime_rel = "client/app/main_client.c"
    mode_files = (
        "client/modes/client_mode_cli.c",
        "client/modes/client_mode_tui.c",
        "client/modes/client_mode_gui.c",
    )
    required_commands = (
        "client.boot.start",
        "client.menu.open",
        "client.menu.select.singleplayer",
        "client.menu.select.multiplayer",
        "client.world.create",
        "client.world.inspect",
        "client.world.modify",
        "client.world.delete",
        "client.world.play",
        "client.server.list",
        "client.server.connect",
        "client.options.get",
        "client.settings.get",
        "client.settings.set",
        "client.settings.reset",
        "client.about.show",
        "client.diag.show_build_identity",
        "client.replay.export",
    )

    violations = []
    for rel in (bridge_rel, registry_rel, runtime_rel):
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            violations.append("{}: missing {}".format(invariant_id, rel))
    for rel in mode_files:
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            violations.append("{}: missing mode adapter {}".format(invariant_id, rel))
    if violations:
        return violations

    bridge_text = read_text(os.path.join(repo_root, bridge_rel.replace("/", os.sep))) or ""
    registry_text = read_text(os.path.join(repo_root, registry_rel.replace("/", os.sep))) or ""
    runtime_text = read_text(os.path.join(repo_root, runtime_rel.replace("/", os.sep))) or ""

    for command in required_commands:
        if "\"{}\"".format(command) not in registry_text:
            violations.append("{}: {} missing command {}".format(invariant_id, registry_rel, command))
    for marker in (
        "client_command_bridge_prepare(",
        "client_collect_capabilities(",
        "client_state_machine_init(",
    ):
        if marker not in runtime_text:
            violations.append("{}: {} missing runtime bridge marker {}".format(invariant_id, runtime_rel, marker))
    for marker in (
        "REFUSE_CAPABILITY_MISSING",
        "REFUSE_UNAVAILABLE",
        "client.server.",
        "client.world.",
    ):
        if marker not in bridge_text:
            violations.append("{}: {} missing bridge marker {}".format(invariant_id, bridge_rel, marker))
    return violations


def check_settings_ownership_boundaries(repo_root):
    invariant_id = "INV-SETTINGS-OWNERSHIP"
    if is_override_active(repo_root, invariant_id):
        return []

    boundary_rules = (
        ("client/", ("setup/",), "client sources must not include setup mutators directly"),
        ("launcher/", ("client/", "setup/"), "launcher sources must not include client/setup implementation headers"),
        ("setup/", ("client/", "launcher/"), "setup sources must not include client/launcher implementation headers"),
    )
    violations = []

    roots = (
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "setup"),
    )
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path).replace("\\", "/")
        text = read_text(path) or ""
        for idx, line in enumerate(text.splitlines(), start=1):
            match = INCLUDE_DIRECTIVE_RE.match(line)
            if not match:
                continue
            include_path = match.group(1).replace("\\", "/")
            for prefix, forbidden_includes, message in boundary_rules:
                if not rel.startswith(prefix):
                    continue
                for forbidden in forbidden_includes:
                    if include_path.startswith(forbidden):
                        violations.append(
                            "{}: {}:{} {} (include={})".format(
                                invariant_id, rel, idx, message, include_path
                            )
                        )
                        break
                else:
                    continue
                break
    return violations


def check_no_engine_settings(repo_root):
    invariant_id = "INV-NO-ENGINE-SETTINGS"
    if is_override_active(repo_root, invariant_id):
        return []

    roots = (
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
    )
    forbidden_include_prefixes = (
        "client/",
        "launcher/",
        "setup/",
        "dominium/app/",
    )
    forbidden_setting_literals = (
        "client.settings.",
        "launcher.settings.",
        "setup.settings.",
        "tools.settings.",
    )

    violations = []
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path).replace("\\", "/")
        text = read_text(path) or ""
        for idx, line in enumerate(text.splitlines(), start=1):
            include_match = INCLUDE_DIRECTIVE_RE.match(line)
            if include_match:
                include_path = include_match.group(1).replace("\\", "/")
                for prefix in forbidden_include_prefixes:
                    if include_path.startswith(prefix):
                        violations.append(
                            "{}: {}:{} forbidden include in engine/game ({})".format(
                                invariant_id, rel, idx, include_path
                            )
                        )
                        break
            stripped = strip_c_comments_and_strings(line)
            for token in forbidden_setting_literals:
                if token in stripped:
                    violations.append(
                        "{}: {}:{} forbidden user settings literal {}".format(
                            invariant_id, rel, idx, token
                        )
                    )
    return violations


def check_no_hardcoded_mode_branch(repo_root):
    invariant_id = "INV-NO-HARDCODED-MODE-BRANCH"
    if is_override_active(repo_root, invariant_id):
        return []

    roots = (
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "setup"),
        os.path.join(repo_root, "tools"),
        os.path.join(repo_root, "libs"),
        os.path.join(repo_root, "scripts"),
    )
    forbidden_tokens = (
        "survival" + "_" + "mode",
        "creative" + "_" + "mode",
        "hardcore" + "_" + "mode",
        "spectator" + "_" + "mode",
    )
    branch_re = re.compile(
        r"\bif\s*\([^)]*\b(?:is_)?(?:survival|creative|hardcore|spectator)\b[^)]*\)",
        re.IGNORECASE,
    )
    violations = []
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path).replace("\\", "/")
        text = (read_text(path) or "").lower()
        for token in forbidden_tokens:
            if token in text:
                violations.append(
                    "{}: {} contains forbidden hardcoded mode token {}".format(
                        invariant_id, rel, token
                    )
                )
                break
        if branch_re.search(text):
            violations.append(
                "{}: {} contains mode-branch conditional pattern".format(
                    invariant_id, rel
                )
            )
    return violations


def check_authority_context_required(repo_root):
    invariant_id = "INV-AUTHORITY-CONTEXT-REQUIRED"
    if is_override_active(repo_root, invariant_id):
        return []

    session_rel = "schema/session/session_spec.schema"
    authority_rel = "schema/authority/authority_context.schema"
    required_session_fields = (
        "universe_id",
        "save_id",
        "experience_id",
        "parameter_bundle_id",
        "authority_context",
    )
    required_authority_fields = (
        "authority_origin",
        "experience_id",
        "law_profile_id",
        "entitlements",
    )

    violations = []
    session_path = os.path.join(repo_root, session_rel.replace("/", os.sep))
    authority_path = os.path.join(repo_root, authority_rel.replace("/", os.sep))

    if not os.path.isfile(session_path):
        violations.append("{}: missing {}".format(invariant_id, session_rel))
    if not os.path.isfile(authority_path):
        violations.append("{}: missing {}".format(invariant_id, authority_rel))
    if violations:
        return violations

    session_text = read_text(session_path) or ""
    authority_text = read_text(authority_path) or ""
    for field in required_session_fields:
        if field not in session_text:
            violations.append("{}: {} missing required field {}".format(invariant_id, session_rel, field))
    for field in required_authority_fields:
        if field not in authority_text:
            violations.append("{}: {} missing required field {}".format(invariant_id, authority_rel, field))
    return violations


def check_glossary_term_canon(repo_root):
    invariant_id = "INV-GLOSSARY-TERM-CANON"
    warn_id = "WARN-GLOSSARY-TERM-CANON"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_path = os.path.join(repo_root, GLOSSARY_SCHEMA_REL)
    registry_path = os.path.join(repo_root, GLOSSARY_REGISTRY_REL)
    glossary_doc_rel = "docs/architecture/TERMINOLOGY_GLOSSARY.md"
    glossary_doc_path = os.path.join(repo_root, glossary_doc_rel.replace("/", os.sep))
    violations = []

    if not os.path.isfile(schema_path):
        violations.append("{}: missing {}".format(invariant_id, normalize_path(GLOSSARY_SCHEMA_REL)))
        return violations
    if not os.path.isfile(registry_path):
        violations.append("{}: missing {}".format(invariant_id, normalize_path(GLOSSARY_REGISTRY_REL)))
        return violations
    if not os.path.isfile(glossary_doc_path):
        violations.append("{}: missing {}".format(invariant_id, glossary_doc_rel))
        return violations

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(GLOSSARY_REGISTRY_REL))]

    terms = ((payload.get("record") or {}).get("terms") or [])
    if not isinstance(terms, list):
        return ["{}: terms must be list in {}".format(invariant_id, normalize_path(GLOSSARY_REGISTRY_REL))]

    forbidden_pairs = []
    for row in terms:
        if not isinstance(row, dict):
            continue
        display_name = str(row.get("display_name", "")).strip()
        forbidden = row.get("forbidden_synonyms") or []
        if not display_name:
            violations.append("{}: term missing display_name in {}".format(
                invariant_id, normalize_path(GLOSSARY_REGISTRY_REL)
            ))
            continue
        if display_name not in (read_text(glossary_doc_path) or ""):
            violations.append("{}: glossary doc missing term '{}'".format(invariant_id, display_name))
        if not isinstance(forbidden, list):
            continue
        for synonym in forbidden:
            text = str(synonym).strip().lower()
            # Canonical enforcement is initially limited to explicit token-like aliases
            # to avoid broad natural-language false positives in historical docs.
            if text and ("_" in text or "." in text or ":" in text):
                forbidden_pairs.append((display_name, text))

    canonical_roots = (
        os.path.join(repo_root, "docs", "architecture"),
        os.path.join(repo_root, "docs", "governance"),
    )
    all_doc_root = os.path.join(repo_root, "docs")
    scan_exts = [".md"]

    for path in iter_files(canonical_roots, DEFAULT_EXCLUDES, scan_exts):
        rel = normalize_path(repo_rel(repo_root, path))
        if rel == glossary_doc_rel:
            continue
        text = (read_text(path) or "").lower()
        for display_name, synonym in forbidden_pairs:
            if synonym in text:
                violations.append("{}: {} uses forbidden synonym '{}' for {}".format(
                    invariant_id, rel, synonym, display_name
                ))

    for path in iter_files([all_doc_root], DEFAULT_EXCLUDES, scan_exts):
        rel = normalize_path(repo_rel(repo_root, path))
        if rel.startswith("docs/architecture/") or rel.startswith("docs/governance/"):
            continue
        if rel.startswith("docs/archive/"):
            continue
        if rel == glossary_doc_rel:
            continue
        text = (read_text(path) or "").lower()
        for display_name, synonym in forbidden_pairs:
            if synonym in text:
                violations.append("{}: {} uses forbidden synonym '{}' for {}".format(
                    warn_id, rel, synonym, display_name
                ))
                break
    return violations


def check_universe_identity_immutability(repo_root):
    invariant_id = "INV-UNIVERSE_IDENTITY_IMMUTABLE"
    if is_override_active(repo_root, invariant_id):
        return []

    identity_rel = "schema/universe/universe_identity.schema"
    state_rel = "schema/universe/universe_state.schema"
    identity_path = os.path.join(repo_root, identity_rel.replace("/", os.sep))
    state_path = os.path.join(repo_root, state_rel.replace("/", os.sep))
    violations = []

    if not os.path.isfile(identity_path):
        violations.append("{}: missing {}".format(invariant_id, identity_rel))
    if not os.path.isfile(state_path):
        violations.append("{}: missing {}".format(invariant_id, state_rel))
    if violations:
        return violations

    identity_text = read_text(identity_path) or ""
    state_text = read_text(state_path) or ""
    identity_required = (
        "universe_id",
        "global_seed",
        "domain_binding_ids",
        "physics_profile_id",
        "base_scenario_id",
        "compatibility_schema_refs",
        "immutable_after_create: bool",
    )
    state_required = (
        "universe_id",
        "time_ref",
        "refinement_state_refs",
        "agent_state_refs",
        "law_state_refs",
        "save_checkpoint_refs",
        "history_log_anchors",
    )
    for field in identity_required:
        if field not in identity_text:
            violations.append("{}: {} missing required field {}".format(invariant_id, identity_rel, field))
    for field in state_required:
        if field not in state_text:
            violations.append("{}: {} missing required field {}".format(invariant_id, state_rel, field))

    roots = (
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "setup"),
    )
    mutation_tokens = (
        "set_universe_identity(",
        "update_universe_identity(",
        "mutate_universe_identity(",
        "rewrite_universe_identity(",
    )
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = normalize_path(repo_rel(repo_root, path))
        text = read_text(path) or ""
        lowered = text.lower()
        for token in mutation_tokens:
            if token in lowered:
                violations.append("{}: forbidden identity mutation token {} in {}".format(
                    invariant_id, token, rel
                ))
                break
    return violations


def check_survival_no_nondiegetic_lenses(repo_root):
    invariant_id = "INV-SURVIVAL-NO-NONDIEGETIC-LENSES"
    if is_override_active(repo_root, invariant_id):
        return []

    rel = "data/registries/law_profiles.json"
    path = os.path.join(repo_root, rel.replace("/", os.sep))
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, rel)]

    payload = _load_json_file(path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, rel)]

    profiles = ((payload.get("record") or {}).get("profiles") or [])
    if not isinstance(profiles, list):
        return ["{}: profiles must be list in {}".format(invariant_id, rel)]

    required_ids = (
        "law.survival.default",
        "law.survival.softcore",
        "law.survival.hardcore",
        "survival.softcore",
    )
    by_id = {}
    for row in profiles:
        if isinstance(row, dict):
            law_id = str(row.get("law_profile_id", "")).strip()
            if law_id:
                by_id[law_id] = row

    violations = []
    for law_id in required_ids:
        profile = by_id.get(law_id)
        if not isinstance(profile, dict):
            violations.append("{}: missing law profile {}".format(invariant_id, law_id))
            continue
        allowed = profile.get("allowed_lenses")
        forbidden = profile.get("forbidden_lenses")
        if not isinstance(allowed, list):
            violations.append("{}: {} allowed_lenses must be list".format(invariant_id, law_id))
            continue
        if not isinstance(forbidden, list):
            violations.append("{}: {} forbidden_lenses must be list".format(invariant_id, law_id))
            continue
        if "lens.diegetic.*" not in [str(item).strip() for item in allowed]:
            violations.append("{}: {} must allow lens.diegetic.*".format(invariant_id, law_id))
        if not any(str(item).strip().startswith("lens.nondiegetic") for item in forbidden):
            violations.append("{}: {} must forbid lens.nondiegetic.*".format(invariant_id, law_id))
    return violations


def check_survival_diegetic_contract(repo_root):
    invariant_id = "INV-SURVIVAL-DIEGETIC-CONTRACT"
    if is_override_active(repo_root, invariant_id):
        return []

    law_rel = "data/registries/law_profiles.json"
    bridge_rel = "client/core/client_command_bridge.c"
    law_path = os.path.join(repo_root, law_rel.replace("/", os.sep))
    bridge_path = os.path.join(repo_root, bridge_rel.replace("/", os.sep))
    if not os.path.isfile(law_path):
        return ["{}: missing {}".format(invariant_id, law_rel)]
    if not os.path.isfile(bridge_path):
        return ["{}: missing {}".format(invariant_id, bridge_rel)]

    payload = _load_json_file(law_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, law_rel)]

    profiles = ((payload.get("record") or {}).get("profiles") or [])
    if not isinstance(profiles, list):
        return ["{}: profiles must be list in {}".format(invariant_id, law_rel)]

    survival_ids = ("law.survival.default", "law.survival.softcore", "law.survival.hardcore", "survival.softcore")
    by_id = {}
    for row in profiles:
        if isinstance(row, dict):
            law_id = str(row.get("law_profile_id", "")).strip()
            if law_id:
                by_id[law_id] = row

    violations = []
    forbidden_entitlements = ("ui.console.command.read_only", "ui.console.command.read_write", "camera.mode.observer_truth")
    for law_id in survival_ids:
        row = by_id.get(law_id)
        if not isinstance(row, dict):
            violations.append("{}: missing law profile {}".format(invariant_id, law_id))
            continue
        allowed = [str(item).strip() for item in (row.get("allowed_lenses") or [])]
        forbidden = [str(item).strip() for item in (row.get("forbidden_lenses") or [])]
        entitlements = [str(item).strip() for item in (row.get("entitlements_granted") or [])]
        if "lens.diegetic.*" not in allowed:
            violations.append("{}: {} must allow lens.diegetic.*".format(invariant_id, law_id))
        if not any(item.startswith("lens.nondiegetic") for item in forbidden):
            violations.append("{}: {} must forbid nondiegetic lenses".format(invariant_id, law_id))
        for entitlement in forbidden_entitlements:
            if entitlement in entitlements:
                violations.append("{}: {} must not grant {}".format(invariant_id, law_id, entitlement))

    bridge_text = read_text(bridge_path) or ""
    required_bindings = (
        "{ \"exp.survival\", \"law.survival.softcore\", 1, 0, 0, 0, 0, 0 }",
        "{ \"exp.hardcore\", \"law.survival.hardcore\", 1, 0, 0, 0, 0, 0 }",
        "refuse.entitlement_required",
    )
    for marker in required_bindings:
        if marker not in bridge_text:
            violations.append("{}: {} missing marker {}".format(invariant_id, bridge_rel, marker))

    return violations


def check_authority_context_required_for_intents(repo_root):
    invariant_id = "INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_rel = "schema/authority/authority_context.schema"
    client_rel = "client/core/client_command_bridge.c"
    server_h_rel = "server/authority/dom_server_authority.h"
    server_cpp_rel = "server/authority/dom_server_authority.cpp"
    schema_path = os.path.join(repo_root, schema_rel.replace("/", os.sep))
    client_path = os.path.join(repo_root, client_rel.replace("/", os.sep))
    server_h_path = os.path.join(repo_root, server_h_rel.replace("/", os.sep))
    server_cpp_path = os.path.join(repo_root, server_cpp_rel.replace("/", os.sep))
    violations = []

    for rel, path in ((schema_rel, schema_path),
                      (client_rel, client_path),
                      (server_h_rel, server_h_path),
                      (server_cpp_rel, server_cpp_path)):
        if not os.path.isfile(path):
            violations.append("{}: missing {}".format(invariant_id, rel))
    if violations:
        return violations

    schema_text = read_text(schema_path) or ""
    for marker in ("authority_origin", "experience_id", "law_profile_id", "entitlements",
                   "capability_set_hash", "epistemic_scope_id", "server_authoritative"):
        if marker not in schema_text:
            violations.append("{}: {} missing {}".format(invariant_id, schema_rel, marker))

    client_text = read_text(client_path) or ""
    for marker in ("authority_context_id", "ctx.unset", "refuse.authority_context_required"):
        if marker not in client_text:
            violations.append("{}: {} missing marker {}".format(invariant_id, client_rel, marker))

    server_h_text = read_text(server_h_path) or ""
    server_cpp_text = read_text(server_cpp_path) or ""
    for marker in ("dom_authority_context", "dom_server_authority_check_with_context"):
        if marker not in server_h_text and marker not in server_cpp_text:
            violations.append("{}: server authority missing marker {}".format(invariant_id, marker))
    if "server_authoritative" not in server_cpp_text:
        violations.append("{}: {} missing server_authoritative enforcement marker".format(
            invariant_id, server_cpp_rel
        ))
    return violations


def check_session_spec_required_for_run(repo_root):
    invariant_id = "INV-SESSION_SPEC_REQUIRED_FOR_RUN"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_rel = "schema/session/session_spec.schema"
    registry_rel = "data/registries/session_defaults.json"
    bridge_rel = "client/core/client_command_bridge.c"
    commands_rel = "client/core/client_commands_registry.c"
    violations = []
    schema_path = os.path.join(repo_root, schema_rel.replace("/", os.sep))
    registry_path = os.path.join(repo_root, registry_rel.replace("/", os.sep))
    bridge_path = os.path.join(repo_root, bridge_rel.replace("/", os.sep))
    commands_path = os.path.join(repo_root, commands_rel.replace("/", os.sep))

    for rel, path in ((schema_rel, schema_path), (bridge_rel, bridge_path), (commands_rel, commands_path)):
        if not os.path.isfile(path):
            violations.append("{}: missing {}".format(invariant_id, rel))
    if violations:
        return violations

    schema_text = read_text(schema_path) or ""
    required_fields = (
        "session_id",
        "universe_id",
        "experience_id",
        "parameter_bundle_id",
        "pack_lock_hash",
        "authority_context",
        "budget_policy_id",
        "fidelity_policy_id",
        "deterministic_seed_bundle",
    )
    for field in required_fields:
        if field not in schema_text:
            violations.append("{}: {} missing required field {}".format(invariant_id, schema_rel, field))

    bridge_text = read_text(bridge_path) or ""
    command_text = read_text(commands_path) or ""
    for marker in ("client.session.create_from_selection", "session_id=session.selected", "authority_context_id="):
        if marker not in bridge_text and marker not in command_text:
            violations.append("{}: missing session-spec marker '{}'".format(invariant_id, marker))

    if os.path.isfile(registry_path):
        payload = _load_json_file(registry_path)
        if not isinstance(payload, dict):
            violations.append("{}: invalid json {}".format(invariant_id, registry_rel))
        else:
            if str(payload.get("schema_id", "")).strip() != "dominium.schema.session.defaults":  # schema_version: 1.0.0
                violations.append("{}: schema_id mismatch in {}".format(invariant_id, registry_rel))
            template = ((payload.get("record") or {}).get("default_session_spec_template") or {})
            if not isinstance(template, dict):
                violations.append("{}: default_session_spec_template missing in {}".format(invariant_id, registry_rel))
            else:
                for key in ("session_id_prefix", "universe_id", "experience_id", "parameter_bundle_id", "authority_context"):
                    if key not in template:
                        violations.append("{}: {} missing template key {}".format(invariant_id, registry_rel, key))

    return violations


def check_mode_as_profiles(repo_root):
    invariant_id = "INV-MODE-AS-PROFILES"
    if is_override_active(repo_root, invariant_id):
        return []

    law_rel = "data/registries/law_profiles.json"
    exp_rel = "data/registries/experience_profiles.json"
    param_rel = "data/registries/parameter_bundles.json"
    violations = []

    law_path = os.path.join(repo_root, law_rel.replace("/", os.sep))
    exp_path = os.path.join(repo_root, exp_rel.replace("/", os.sep))
    param_path = os.path.join(repo_root, param_rel.replace("/", os.sep))

    for rel, path in ((law_rel, law_path), (exp_rel, exp_path), (param_rel, param_path)):
        if not os.path.isfile(path):
            violations.append("{}: missing {}".format(invariant_id, rel))
    if violations:
        return violations

    law_payload = _load_json_file(law_path)
    exp_payload = _load_json_file(exp_path)
    param_payload = _load_json_file(param_path)
    if not isinstance(law_payload, dict):
        violations.append("{}: invalid json {}".format(invariant_id, law_rel))
        return violations
    if not isinstance(exp_payload, dict):
        violations.append("{}: invalid json {}".format(invariant_id, exp_rel))
        return violations
    if not isinstance(param_payload, dict):
        violations.append("{}: invalid json {}".format(invariant_id, param_rel))
        return violations

    laws = ((law_payload.get("record") or {}).get("profiles") or [])
    experiences = ((exp_payload.get("record") or {}).get("profiles") or [])
    bundles = ((param_payload.get("record") or {}).get("bundles") or [])
    if not isinstance(laws, list):
        violations.append("{}: profiles must be list in {}".format(invariant_id, law_rel))
        return violations
    if not isinstance(experiences, list):
        violations.append("{}: profiles must be list in {}".format(invariant_id, exp_rel))
        return violations
    if not isinstance(bundles, list):
        violations.append("{}: bundles must be list in {}".format(invariant_id, param_rel))
        return violations

    law_ids = set()
    bundle_ids = set()
    for row in laws:
        if not isinstance(row, dict):
            continue
        law_id = str(row.get("law_profile_id", "")).strip()
        if law_id:
            law_ids.add(law_id)
    for row in bundles:
        if not isinstance(row, dict):
            continue
        bundle_id = str(row.get("parameter_bundle_id", "")).strip()
        if bundle_id:
            bundle_ids.add(bundle_id)

    for row in experiences:
        if not isinstance(row, dict):
            violations.append("{}: non-object experience profile in {}".format(invariant_id, exp_rel))
            continue
        exp_id = str(row.get("experience_id", "")).strip()
        law_id = str(row.get("law_profile_id", "")).strip()
        default_bundle_id = str(row.get("default_parameter_bundle_id", "")).strip()
        if not exp_id:
            violations.append("{}: experience entry missing experience_id in {}".format(invariant_id, exp_rel))
            continue
        if not law_id:
            violations.append("{}: {} missing law_profile_id for {}".format(invariant_id, exp_rel, exp_id))
        elif law_id not in law_ids:
            violations.append("{}: {} references unknown law_profile_id '{}' for {}".format(
                invariant_id, exp_rel, law_id, exp_id
            ))
        if not default_bundle_id:
            violations.append("{}: {} missing default_parameter_bundle_id for {}".format(
                invariant_id, exp_rel, exp_id
            ))
        elif default_bundle_id not in bundle_ids:
            violations.append("{}: {} references unknown parameter bundle '{}' for {}".format(
                invariant_id, exp_rel, default_bundle_id, exp_id
            ))
    return violations


def check_ui_entitlement_gating(repo_root):
    invariant_id = "INV-UI-ENTITLEMENT-GATING"
    if is_override_active(repo_root, invariant_id):
        return []

    rel = "client/core/client_commands_registry.c"
    bridge_rel = "client/core/client_command_bridge.c"
    path = os.path.join(repo_root, rel.replace("/", os.sep))
    bridge_path = os.path.join(repo_root, bridge_rel.replace("/", os.sep))
    violations = []
    text = read_text(path) or ""
    bridge_text = read_text(bridge_path) or ""
    if not text:
        return ["{}: missing {}".format(invariant_id, rel)]
    if not bridge_text:
        return ["{}: missing {}".format(invariant_id, bridge_rel)]

    required_pairs = (
        ("client.ui.hud.show", "ui.hud.basic"),
        ("client.ui.overlay.world_layers.show", "ui.overlay.world_layers"),
        ("client.console.open", "ui.console.command.read_only"),
        ("client.console.open.readwrite", "ui.console.command.read_write"),
        ("client.camera.freecam.enable", "camera.mode.observer_truth"),
    )
    for command_id, entitlement in required_pairs:
        if command_id not in text:
            violations.append("{}: missing command {} in {}".format(invariant_id, command_id, rel))
        if entitlement not in text:
            violations.append("{}: missing entitlement {} in {}".format(invariant_id, entitlement, rel))

    if "refuse.entitlement_required" not in bridge_text:
        violations.append("{}: missing refusal {} in {}".format(
            invariant_id, "refuse.entitlement_required", bridge_rel
        ))
    if ("refuse.profile_not_selected" not in bridge_text and
            "refuse.authority_context_required" not in bridge_text):
        violations.append("{}: missing refusal {} or {} in {}".format(
            invariant_id,
            "refuse.profile_not_selected",
            "refuse.authority_context_required",
            bridge_rel,
        ))
    return violations


def check_presentation_matrix_integrity(repo_root):
    invariant_id = "INV-PRESENTATION-MATRIX-INTEGRITY"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_path = os.path.join(repo_root, PRESENTATION_MATRIX_SCHEMA_REL)
    registry_path = os.path.join(repo_root, PRESENTATION_MATRIX_REGISTRY_REL)
    law_path = os.path.join(repo_root, "data", "registries", "law_profiles.json")
    lens_path = os.path.join(repo_root, "data", "registries", "lenses.json")

    violations = []
    if not os.path.isfile(schema_path):
        violations.append("{}: missing schema {}".format(invariant_id, normalize_path(PRESENTATION_MATRIX_SCHEMA_REL)))
        return violations
    if not os.path.isfile(registry_path):
        violations.append("{}: missing registry {}".format(invariant_id, normalize_path(PRESENTATION_MATRIX_REGISTRY_REL)))
        return violations
    if not os.path.isfile(law_path):
        violations.append("{}: missing data/registries/law_profiles.json".format(invariant_id))
        return violations
    if not os.path.isfile(lens_path):
        violations.append("{}: missing data/registries/lenses.json".format(invariant_id))
        return violations

    payload = _load_json_file(registry_path)
    laws_payload = _load_json_file(law_path)
    lenses_payload = _load_json_file(lens_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(PRESENTATION_MATRIX_REGISTRY_REL))]
    if not isinstance(laws_payload, dict) or not isinstance(lenses_payload, dict):
        return ["{}: invalid law/lens registries".format(invariant_id)]

    if str(payload.get("schema_id", "")).strip() != PRESENTATION_MATRIX_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(PRESENTATION_MATRIX_REGISTRY_REL)))

    rows = ((payload.get("record") or {}).get("rows") or [])
    if not isinstance(rows, list):
        return violations + ["{}: rows must be list in {}".format(invariant_id, normalize_path(PRESENTATION_MATRIX_REGISTRY_REL))]

    law_rows = ((laws_payload.get("record") or {}).get("profiles") or [])
    lens_rows = ((lenses_payload.get("record") or {}).get("lenses") or [])
    known_laws = {str(row.get("law_profile_id", "")).strip() for row in law_rows if isinstance(row, dict)}
    known_lenses = {str(row.get("lens_id", "")).strip() for row in lens_rows if isinstance(row, dict)}
    seen_laws = set()

    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: row {} must be object".format(invariant_id, idx))
            continue
        law_id = str(row.get("law_profile_id", "")).strip()
        if not law_id:
            violations.append("{}: row {} missing law_profile_id".format(invariant_id, idx))
            continue
        if law_id not in known_laws:
            violations.append("{}: unknown law_profile_id '{}'".format(invariant_id, law_id))
        if law_id in seen_laws:
            violations.append("{}: duplicate law_profile_id '{}'".format(invariant_id, law_id))
        seen_laws.add(law_id)

        allowed_lenses = [str(item).strip() for item in (row.get("allowed_lenses") or []) if str(item).strip()]
        allowed_panels = [str(item).strip() for item in (row.get("allowed_panels") or []) if str(item).strip()]
        required_entitlements = {str(item).strip() for item in (row.get("required_entitlements") or []) if str(item).strip()}
        if not allowed_lenses:
            violations.append("{}: {} must declare allowed_lenses".format(invariant_id, law_id))

        for lens in allowed_lenses:
            if lens.endswith(".*"):
                prefix = lens[:-2]
                if not any(item.startswith(prefix + ".") or item == prefix for item in known_lenses):
                    violations.append("{}: {} references unknown lens prefix '{}'".format(invariant_id, law_id, lens))
            elif lens not in known_lenses:
                violations.append("{}: {} references unknown lens '{}'".format(invariant_id, law_id, lens))

        if law_id.startswith("law.survival") or law_id == "survival.softcore":
            if any(item.startswith("lens.nondiegetic") for item in allowed_lenses):
                violations.append("{}: {} must not allow nondiegetic lenses".format(invariant_id, law_id))
            forbidden_panels = ("panel.console", "panel.overlay.debug", "panel.freecam")
            for panel in forbidden_panels:
                if panel in allowed_panels:
                    violations.append("{}: {} must not expose {}".format(invariant_id, law_id, panel))

        if "panel.console" in allowed_panels and not (
            "ui.console.command.read_only" in required_entitlements
            or "ui.console.command.read_write" in required_entitlements
        ):
            violations.append("{}: {} exposes panel.console without console entitlement".format(invariant_id, law_id))

        if "panel.overlay.world_layers" in allowed_panels and "ui.overlay.world_layers" not in required_entitlements:
            violations.append("{}: {} exposes world overlay panel without ui.overlay.world_layers entitlement".format(
                invariant_id, law_id
            ))

        if law_id == "law.observer.default" and row.get("watermark_required") is not True:
            violations.append("{}: law.observer.default requires watermark_required=true".format(invariant_id))

    return violations


def check_defaults_optional(repo_root):
    invariant_id = "INV-DEFAULTS-OPTIONAL"
    if is_override_active(repo_root, invariant_id):
        return []

    rel = "data/registries/bundle_profiles.json"
    path = os.path.join(repo_root, rel.replace("/", os.sep))
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, rel)]

    payload = _load_json_file(path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, rel)]

    bundles = ((payload.get("record") or {}).get("bundles") or [])
    if not isinstance(bundles, list):
        return ["{}: bundles must be list in {}".format(invariant_id, rel)]

    violations = []
    seen_core = False
    for row in bundles:
        if not isinstance(row, dict):
            violations.append("{}: non-object bundle entry in {}".format(invariant_id, rel))
            continue
        bundle_id = str(row.get("bundle_id", "")).strip()
        optional_flag = ((row.get("extensions") or {}).get("optional"))
        if bundle_id == "bundle.core.runtime":
            seen_core = True
            if optional_flag is not False:
                violations.append("{}: bundle.core.runtime must set extensions.optional=false".format(
                    invariant_id
                ))
        elif bundle_id == "bundle.default_core":
            if optional_flag is not False:
                violations.append("{}: bundle.default_core must set extensions.optional=false".format(
                    invariant_id
                ))
        elif bundle_id:
            if optional_flag is not True:
                violations.append("{}: non-core bundle {} must set extensions.optional=true".format(
                    invariant_id, bundle_id
                ))

    if not seen_core:
        violations.append("{}: missing bundle.core.runtime in {}".format(invariant_id, rel))
    return violations


def check_renderer_no_truth_access(repo_root):
    invariant_id = "INV-RENDER-NO-TRUTH-ACCESS"
    if is_override_active(repo_root, invariant_id):
        return []

    roots = [
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "libs", "appcore"),
    ]
    violations = []
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path)
        text = read_text(path) or ""
        for idx, line in enumerate(text.splitlines(), start=1):
            for token in FORBIDDEN_RENDER_TRUTH_TOKENS:
                if token in line:
                    violations.append(
                        "{}: {}:{} forbidden truth-access token {}".format(
                            invariant_id, rel, idx, token
                        )
                    )

    command_registry_path = os.path.join(repo_root, COMMAND_REGISTRY_REL)
    command_registry_text = read_text(command_registry_path) or ""
    if command_registry_text:
        for entry in _parse_command_registry_entries(command_registry_text):
            name_match = re.search(r"\{\s*DOM_APP_CMD_[^,]+,\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"", entry)
            scope_match = re.search(r"(DOM_EPISTEMIC_SCOPE_[A-Z_]+)", entry)
            if not name_match or not scope_match:
                continue
            command_name = name_match.group(1)
            app_name = name_match.group(2)
            scope_name = scope_match.group(1)
            if app_name == "client" and scope_name == "DOM_EPISTEMIC_SCOPE_FULL":
                violations.append(
                    "{}: {} command {} exposes full epistemic scope to client".format(
                        invariant_id, COMMAND_REGISTRY_REL.replace("\\", "/"), command_name
                    )
                )

    freecam_test_rel = os.path.join("tests", "integration", "freecam_epistemics_tests.py")
    freecam_test_path = os.path.join(repo_root, freecam_test_rel)
    if not os.path.isfile(freecam_test_path):
        violations.append("{}: missing {}".format(invariant_id, freecam_test_rel.replace("\\", "/")))
    else:
        freecam_text = read_text(freecam_test_path) or ""
        required_markers = (
            "CAMERA_REFUSE_ENTITLEMENT",
            "camera.set_mode observer",
            "truth_snapshot_stream",
            "authoritative_world_state",
            "hidden_truth_cache",
        )
        for marker in required_markers:
            if marker not in freecam_text:
                violations.append(
                    "{}: {} missing semantic anti-cheat marker {}".format(
                        invariant_id, freecam_test_rel.replace("\\", "/"), marker
                    )
                )

    capability_test_rel = os.path.join("tests", "integration", "capability_runtime_enforcement_tests.py")
    capability_test_path = os.path.join(repo_root, capability_test_rel)
    if not os.path.isfile(capability_test_path):
        violations.append("{}: missing {}".format(invariant_id, capability_test_rel.replace("\\", "/")))
    else:
        capability_text = read_text(capability_test_path) or ""
        capability_markers = (
            "camera.set_mode observer",
            "CAMERA_REFUSE_ENTITLEMENT",
            "BLUEPRINT_REFUSE_CAPABILITY",
        )
        for marker in capability_markers:
            if marker not in capability_text:
                violations.append(
                    "{}: {} missing runtime capability marker {}".format(
                        invariant_id, capability_test_rel.replace("\\", "/"), marker
                    )
                )

    frame_graph_rel = os.path.join("client", "presentation", "frame_graph_builder.h")
    frame_graph_path = os.path.join(repo_root, frame_graph_rel)
    if not os.path.isfile(frame_graph_path):
        violations.append("{}: missing {}".format(invariant_id, frame_graph_rel.replace("\\", "/")))
    else:
        frame_graph_text = read_text(frame_graph_path) or ""
        required_fields = (
            "packed_view_set_id",
            "visibility_mask_set_id",
            "instance_count",
        )
        for field in required_fields:
            if field not in frame_graph_text:
                violations.append(
                    "{}: {} missing render artifact field {}".format(
                        invariant_id, frame_graph_rel.replace("\\", "/"), field
                    )
                )
        for forbidden in ("authoritative_world_state", "truth_snapshot_stream", "hidden_truth_cache"):
            if forbidden in frame_graph_text:
                violations.append(
                    "{}: {} includes forbidden truth token {}".format(
                        invariant_id, frame_graph_rel.replace("\\", "/"), forbidden
                    )
                )

    render_prep_rel = os.path.join("client", "presentation", "render_prep_system.cpp")
    render_prep_path = os.path.join(repo_root, render_prep_rel)
    if not os.path.isfile(render_prep_path):
        violations.append("{}: missing {}".format(invariant_id, render_prep_rel.replace("\\", "/")))
    else:
        render_prep_text = read_text(render_prep_path) or ""
        if "RenderPrepSystem::is_sim_affecting() const" not in render_prep_text or "return D_FALSE;" not in render_prep_text:
            violations.append(
                "{}: {} must declare presentation-only non-sim-affecting behavior".format(
                    invariant_id, render_prep_rel.replace("\\", "/")
                )
            )
    return violations


def check_capability_matrix_integrity(repo_root):
    invariant_id = "INV-CAPABILITY-MATRIX"
    if is_override_active(repo_root, invariant_id):
        return []

    matrix_path = os.path.join(repo_root, CAPABILITY_MATRIX_REL)
    if not os.path.isfile(matrix_path):
        return ["{}: missing {}".format(invariant_id, CAPABILITY_MATRIX_REL.replace("\\", "/"))]

    data = _load_json_file(matrix_path)
    if not isinstance(data, dict):
        return ["{}: invalid matrix format {}".format(invariant_id, CAPABILITY_MATRIX_REL.replace("\\", "/"))]

    sets = data.get("capability_sets")
    if not isinstance(sets, list):
        return ["{}: capability_sets missing from {}".format(invariant_id, CAPABILITY_MATRIX_REL.replace("\\", "/"))]

    violations = []
    seen = set()
    fixture_paths = set()
    test_paths = set()

    for entry in sets:
        if not isinstance(entry, dict):
            violations.append(
                "{}: invalid capability set entry in {}".format(
                    invariant_id, CAPABILITY_MATRIX_REL.replace("\\", "/")
                )
            )
            continue
        bundle_id = entry.get("bundle_id")
        if bundle_id not in CAPABILITY_SET_IDS:
            violations.append("{}: invalid capability set id in matrix: {}".format(invariant_id, bundle_id))
            continue
        if bundle_id in seen:
            violations.append("{}: duplicate capability set id in matrix: {}".format(invariant_id, bundle_id))
            continue
        seen.add(bundle_id)

        capability_dir = CAPABILITY_SET_TO_DIR.get(bundle_id)
        fixture = entry.get("fixture")
        expected_fixture = "tests/fixtures/worlds/{}/world_capabilities.json".format(capability_dir)
        if fixture != expected_fixture:
            violations.append("{}: fixture mismatch for {} (expected {})".format(
                invariant_id, bundle_id, expected_fixture
            ))
        if not isinstance(fixture, str):
            violations.append("{}: fixture missing for {}".format(invariant_id, bundle_id))
        else:
            fixture_paths.add(fixture.replace("\\", "/"))
            if not os.path.isfile(os.path.join(repo_root, fixture)):
                violations.append("{}: matrix fixture does not exist: {}".format(invariant_id, fixture))

        suites = entry.get("required_test_suites") or []
        if suites != list(CAPABILITY_MATRIX_SUITE_NAMES):
            violations.append("{}: required_test_suites mismatch for {}".format(invariant_id, bundle_id))

        tests = entry.get("tests")
        if not isinstance(tests, list):
            violations.append("{}: tests list missing for {}".format(invariant_id, bundle_id))
            continue

        expected_tests = [
            "tests/testx/capability_sets/{}/{}.py".format(capability_dir, suite_name)
            for suite_name in CAPABILITY_MATRIX_SUITE_NAMES
        ]
        if tests != expected_tests:
            violations.append("{}: tests paths mismatch for {}".format(invariant_id, bundle_id))

        for rel in tests:
            rel_norm = rel.replace("\\", "/")
            test_paths.add(rel_norm)
            if not os.path.isfile(os.path.join(repo_root, rel_norm)):
                violations.append("{}: matrix test file does not exist: {}".format(invariant_id, rel_norm))

    for bundle_id in CAPABILITY_SET_IDS:
        if bundle_id not in seen:
            violations.append("{}: missing matrix entry for {}".format(invariant_id, bundle_id))

    fixture_root = os.path.join(repo_root, CAPABILITY_FIXTURE_ROOT)
    if os.path.isdir(fixture_root):
        for root, _, files in os.walk(fixture_root):
            for name in files:
                if name != "world_capabilities.json":
                    continue
                rel = repo_rel(repo_root, os.path.join(root, name))
                if rel.replace("\\", "/") not in fixture_paths:
                    violations.append("{}: fixture missing matrix entry: {}".format(invariant_id, rel))

    test_root = os.path.join(repo_root, CAPABILITY_TESTX_ROOT)
    if os.path.isdir(test_root):
        for root, _, files in os.walk(test_root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                rel = repo_rel(repo_root, os.path.join(root, name)).replace("\\", "/")
                if rel not in test_paths:
                    violations.append("{}: capability test missing matrix entry: {}".format(invariant_id, rel))

    regression = data.get("regression_tests")
    if not isinstance(regression, list):
        violations.append("{}: regression_tests missing from {}".format(invariant_id, CAPABILITY_MATRIX_REL.replace("\\", "/")))
    else:
        for rel in regression:
            if not isinstance(rel, str):
                violations.append("{}: invalid regression test path in matrix".format(invariant_id))
                continue
            if not os.path.isfile(os.path.join(repo_root, rel)):
                violations.append("{}: regression test missing: {}".format(invariant_id, rel))
        regression_root = os.path.join(repo_root, CAPABILITY_REGRESSION_ROOT)
        if os.path.isdir(regression_root):
            for name in os.listdir(regression_root):
                rel = normalize_path(os.path.join("tests", "testx", "capability_regression", name))
                if name.endswith(".py") and rel not in [item.replace("\\", "/") for item in regression]:
                    violations.append("{}: regression test missing matrix entry: {}".format(invariant_id, rel))

    return violations


def check_forbidden_legacy_gating_tokens(repo_root):
    invariant_id = "INV-CAPABILITY-NO-LEGACY-GATING-TOKENS"
    if is_override_active(repo_root, invariant_id):
        return []

    roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "setup"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "tools"),
        os.path.join(repo_root, "libs"),
        os.path.join(repo_root, "schema"),
        os.path.join(repo_root, "tests"),
        os.path.join(repo_root, "scripts"),
        os.path.join(repo_root, "ci"),
    ]
    exts = [
        ".c", ".cc", ".cpp", ".h", ".hpp", ".inl",
        ".py", ".json", ".schema", ".yaml", ".yml", ".toml", ".txt", ".cmake",
    ]
    violations = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, exts):
            rel = repo_rel(repo_root, path)
            if rel.startswith("docs/"):
                continue
            text = read_text(path) or ""
            for idx, line in enumerate(text.splitlines(), start=1):
                if FORBIDDEN_LEGACY_GATING_TOKEN_RE.search(line):
                    violations.append("{}: forbidden token in {}:{}".format(invariant_id, rel, idx))
                    break
    return violations


def check_solver_registry_contracts(repo_root):
    invariant_id = "INV-SOLVER-CONTRACTS"
    if is_override_active(repo_root, invariant_id):
        return []

    path = os.path.join(repo_root, SOLVER_REGISTRY_REL)
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, SOLVER_REGISTRY_REL.replace("\\", "/"))]

    payload = _load_json_file(path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, SOLVER_REGISTRY_REL.replace("\\", "/"))]

    violations = []
    if payload.get("schema_id") != SOLVER_REGISTRY_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, SOLVER_REGISTRY_REL.replace("\\", "/")))
    if _parse_semver(payload.get("schema_version")) is None:
        violations.append("{}: invalid schema_version in {}".format(invariant_id, SOLVER_REGISTRY_REL.replace("\\", "/")))

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        violations.append("{}: records missing or empty in {}".format(invariant_id, SOLVER_REGISTRY_REL.replace("\\", "/")))
        return violations

    seen_solver_ids = set()
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            violations.append("{}: invalid record at index {}".format(invariant_id, idx))
            continue

        solver_id = record.get("solver_id")
        if not isinstance(solver_id, str) or not solver_id:
            violations.append("{}: missing solver_id at index {}".format(invariant_id, idx))
            continue
        if not solver_id.startswith("solver."):
            violations.append("{}: non-namespaced solver_id '{}'".format(invariant_id, solver_id))
        if solver_id in seen_solver_ids:
            violations.append("{}: duplicate solver_id '{}'".format(invariant_id, solver_id))
        seen_solver_ids.add(solver_id)

        if record.get("cost_class") not in SOLVER_COST_CLASS_SET:
            violations.append("{}: invalid cost_class for {}".format(invariant_id, solver_id))
        if record.get("resolution") not in SOLVER_RESOLUTION_SET:
            violations.append("{}: invalid resolution for {}".format(invariant_id, solver_id))

        guarantees = record.get("guarantees")
        if not isinstance(guarantees, list) or not guarantees:
            violations.append("{}: guarantees missing for {}".format(invariant_id, solver_id))
        elif not all(isinstance(item, str) and item for item in guarantees):
            violations.append("{}: guarantees must be non-empty string list for {}".format(invariant_id, solver_id))

        transitions = record.get("supports_transitions")
        if not isinstance(transitions, list) or not transitions:
            violations.append("{}: supports_transitions missing for {}".format(invariant_id, solver_id))
        else:
            transition_set = set(item for item in transitions if isinstance(item, str))
            if "collapse" not in transition_set or "expand" not in transition_set:
                violations.append("{}: supports_transitions must include collapse+expand for {}".format(invariant_id, solver_id))

        numeric_bounds = record.get("numeric_bounds")
        if not isinstance(numeric_bounds, dict):
            violations.append("{}: numeric_bounds missing for {}".format(invariant_id, solver_id))
        else:
            if not isinstance(numeric_bounds.get("max_error"), str) or not numeric_bounds.get("max_error"):
                violations.append("{}: numeric_bounds.max_error missing for {}".format(invariant_id, solver_id))
            if numeric_bounds.get("bounded") is not True:
                violations.append("{}: numeric_bounds.bounded must be true for {}".format(invariant_id, solver_id))

        refusal_codes = record.get("refusal_codes")
        if not isinstance(refusal_codes, list) or not refusal_codes:
            violations.append("{}: refusal_codes missing for {}".format(invariant_id, solver_id))
        elif not all(isinstance(code, str) and code for code in refusal_codes):
            violations.append("{}: refusal_codes must be non-empty string list for {}".format(invariant_id, solver_id))

        conformance_refs = record.get("conformance_bundle_refs")
        if not isinstance(conformance_refs, list) or not conformance_refs:
            violations.append("{}: conformance_bundle_refs missing for {}".format(invariant_id, solver_id))

    conformance_schema_rel = os.path.join("schema", "conformance.bundle.schema").replace("\\", "/")
    conformance_schema_path = os.path.join(repo_root, "schema", "conformance.bundle.schema")
    if not os.path.isfile(conformance_schema_path):
        violations.append("{}: missing {}".format(invariant_id, conformance_schema_rel))
    else:
        text = read_text(conformance_schema_path) or ""
        for token in ("allowed_solvers", "invariant_checks", "test_vectors"):
            if token not in text:
                violations.append("{}: {} missing token '{}'".format(invariant_id, conformance_schema_rel, token))

    return violations


def _collect_process_defs(repo_root, violations):
    defs = {}
    packs_root = os.path.join(repo_root, "data", "packs")
    if not os.path.isdir(packs_root):
        violations.append("INV-PROCESS-REGISTRY: missing data/packs")
        return defs
    for path in iter_files([packs_root], DEFAULT_EXCLUDES, [".json"]):
        if "process" not in os.path.basename(path).lower():
            continue
        data = _load_json_file(path)
        if not isinstance(data, dict):
            continue
        schema_id = data.get("schema_id")
        if not schema_id and isinstance(data.get("record"), dict):
            schema_id = data["record"].get("schema_id")
        if schema_id != PROCESS_SCHEMA_ID:
            continue
        records = data.get("records")
        if records is None and isinstance(data.get("record"), dict):
            records = data["record"].get("records")
        if not isinstance(records, list):
            violations.append("INV-PROCESS-REGISTRY: invalid process records in {}".format(repo_rel(repo_root, path)))
            continue
        rel_path = repo_rel(repo_root, path)
        parts = rel_path.split("/")
        pack_id = parts[2] if len(parts) > 2 and parts[0] == "data" and parts[1] == "packs" else ""
        for record in records:
            if not isinstance(record, dict):
                violations.append("INV-PROCESS-REGISTRY: invalid process record in {}".format(rel_path))
                continue
            process_id = record.get("process_id")
            if not process_id:
                violations.append("INV-PROCESS-REGISTRY: missing process_id in {}".format(rel_path))
                continue
            if process_id in defs:
                violations.append("INV-PROCESS-REGISTRY: duplicate process_id {} in {}".format(process_id, rel_path))
                continue
            defs[process_id] = {
                "record": record,
                "pack_id": pack_id,
                "path": rel_path,
            }
    return defs


def _collect_fixture_process_ids(repo_root, violations):
    ids = set()
    for rel_path in PROCESS_FIXTURE_PATHS:
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            continue
        data = _load_json_file(path)
        if data is None:
            violations.append("INV-PROCESS-REGISTRY: unable to read fixture {}".format(rel_path))
            continue
        _collect_process_ids(data, ids)
    return ids


def _collect_process_ids(node, ids):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "process_id" and isinstance(value, str):
                ids.add(value)
            else:
                _collect_process_ids(value, ids)
    elif isinstance(node, list):
        for item in node:
            _collect_process_ids(item, ids)


def check_process_registry(repo_root):
    invariant_id = "INV-PROCESS-REGISTRY"
    if is_override_active(repo_root, invariant_id):
        return []
    violations = []
    registry_path = os.path.join(repo_root, PROCESS_REGISTRY_REL)
    if not os.path.isfile(registry_path):
        return ["{}: missing {}".format(invariant_id, PROCESS_REGISTRY_REL)]
    registry = _load_json_file(registry_path)
    if not isinstance(registry, dict):
        return ["{}: invalid json {}".format(invariant_id, PROCESS_REGISTRY_REL)]
    if registry.get("schema_id") != PROCESS_REGISTRY_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, PROCESS_REGISTRY_REL))
    records = registry.get("records")
    if not isinstance(records, list):
        return ["{}: records missing or invalid in {}".format(invariant_id, PROCESS_REGISTRY_REL)]

    registry_entries = {}
    registry_ids = []
    for entry in records:
        if not isinstance(entry, dict):
            violations.append("{}: invalid record in {}".format(invariant_id, PROCESS_REGISTRY_REL))
            continue
        process_id = entry.get("process_id")
        if not process_id:
            violations.append("{}: missing process_id entry".format(invariant_id))
            continue
        if process_id in registry_entries:
            violations.append("{}: duplicate process_id {}".format(invariant_id, process_id))
            continue
        registry_entries[process_id] = entry
        registry_ids.append(process_id)

    for process_id, entry in registry_entries.items():
        notes = entry.get("determinism_notes") or []
        if not isinstance(notes, list) or not notes:
            violations.append("{}: missing determinism_notes for {}".format(invariant_id, process_id))

    process_defs = _collect_process_defs(repo_root, violations)
    fixture_ids = _collect_fixture_process_ids(repo_root, violations)

    for process_id in fixture_ids:
        if process_id not in registry_entries:
            violations.append("{}: fixture process_id missing from registry: {}".format(invariant_id, process_id))

    for process_id, info in process_defs.items():
        entry = registry_entries.get(process_id)
        if not entry:
            violations.append("{}: missing registry entry for {}".format(invariant_id, process_id))
            continue
        pack_id = info.get("pack_id")
        rel_path = info.get("path", "")
        record = info.get("record", {})
        ext = entry.get("extensions") if isinstance(entry.get("extensions"), dict) else {}
        source_pack = ext.get("source_pack")
        if pack_id and source_pack != pack_id:
            violations.append("{}: source_pack mismatch for {} ({} != {})".format(
                invariant_id, process_id, source_pack, pack_id
            ))
        if rel_path and rel_path not in (entry.get("description") or ""):
            violations.append("{}: description missing source path for {}".format(invariant_id, process_id))

        required_authority = record.get("required_authority_tags") or []
        required_law = entry.get("required_law_checks") or []
        missing_law = [tag for tag in required_authority if tag not in required_law]
        if missing_law:
            violations.append("{}: required_law_checks missing {} for {}".format(
                invariant_id, ", ".join(missing_law), process_id
            ))

        failure_tags = record.get("failure_mode_tags") or []
        failure_modes = entry.get("failure_modes") or []
        missing_failures = [tag for tag in failure_tags if tag not in failure_modes]
        if missing_failures:
            violations.append("{}: failure_modes missing {} for {}".format(
                invariant_id, ", ".join(missing_failures), process_id
            ))

        not_defined = (record.get("extensions") or {}).get("not_defined") or []
        if "no_truth_mutation" in not_defined:
            if entry.get("affected_fields") or entry.get("affected_assemblies"):
                violations.append("{}: no_truth_mutation requires empty affected scope for {}".format(
                    invariant_id, process_id
                ))

    for process_id, entry in registry_entries.items():
        ext = entry.get("extensions") if isinstance(entry.get("extensions"), dict) else {}
        if ext.get("source_pack") and process_id not in process_defs:
            violations.append("{}: registry entry missing source pack definition: {}".format(
                invariant_id, process_id
            ))

    return violations


def check_process_runtime_literals(repo_root):
    invariant_id = "INV-PROCESS-RUNTIME-ID"
    if is_override_active(repo_root, invariant_id):
        return []

    registry = _load_json_file(os.path.join(repo_root, PROCESS_REGISTRY_REL))
    if not isinstance(registry, dict):
        return ["{}: unable to parse {}".format(invariant_id, PROCESS_REGISTRY_REL)]
    records = registry.get("records")
    if not isinstance(records, list):
        return ["{}: records missing in {}".format(invariant_id, PROCESS_REGISTRY_REL)]

    process_ids = set()
    for entry in records:
        if isinstance(entry, dict):
            process_id = entry.get("process_id")
            if isinstance(process_id, str) and process_id:
                process_ids.add(process_id)

    roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "client"),
    ]
    mutation_token_res = (
        re.compile(r"\bapply_writes\s*\("),
        re.compile(r"\bapply_write\s*\("),
        re.compile(r"\bapply_reduce\s*\("),
        re.compile(r"\bdom_ecs_write_op\b"),
        re.compile(r"\bdom_ecs_write_buffer\b"),
    )
    mutation_allow_dirs = (
        os.path.join("engine", "modules", "ecs").replace("\\", "/"),
        os.path.join("engine", "modules", "execution").replace("\\", "/"),
    )
    mutation_allow_files = (
        os.path.join("engine", "include", "domino", "ecs", "ecs_storage_iface.h").replace("\\", "/"),
    )
    violations = []
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path)
        if rel.startswith("engine/tests/") or rel.startswith("game/tests/") or rel.startswith("tests/"):
            continue
        text = read_text(path) or ""
        for idx, line in enumerate(text.splitlines(), start=1):
            for match in PROCESS_ID_LITERAL_RE.finditer(line):
                process_id = match.group(1)
                if process_id in PROCESS_ID_LITERAL_ALLOW:
                    continue
                if process_id not in process_ids:
                    violations.append(
                        "{}: unregistered process literal {}:{} -> {}".format(
                            invariant_id,
                            rel,
                            idx,
                            process_id,
                        )
                    )

        allow_mutation = False
        if rel in mutation_allow_files:
            allow_mutation = True
        if not allow_mutation:
            for allow_dir in mutation_allow_dirs:
                if rel.startswith(allow_dir + "/"):
                    allow_mutation = True
                    break
        if allow_mutation:
            continue

        stripped = strip_c_comments_and_strings(text)
        for idx, line in enumerate(stripped.splitlines(), start=1):
            for token_re in mutation_token_res:
                if token_re.search(line):
                    violations.append(
                        "{}: mutation token outside process execution allowlist {}:{} -> {}".format(
                            invariant_id,
                            rel,
                            idx,
                            token_re.pattern,
                        )
                    )
    return violations


def check_process_guard_runtime_contract(repo_root):
    invariant_id = "INV-PROCESS-GUARD-RUNTIME"
    if is_override_active(repo_root, invariant_id):
        return []

    header_rel = os.path.join("engine", "include", "domino", "core", "process_guard.h").replace("\\", "/")
    impl_rel = os.path.join("engine", "modules", "core", "process_guard.c").replace("\\", "/")
    test_rel = os.path.join("engine", "tests", "process_guard_tests.c").replace("\\", "/")
    tests_invariant_rel = os.path.join("tests", "invariant", "process_only_mutation_tests.py").replace("\\", "/")

    header = read_text(os.path.join(repo_root, header_rel)) or ""
    impl = read_text(os.path.join(repo_root, impl_rel)) or ""
    guard_test = read_text(os.path.join(repo_root, test_rel)) or ""
    invariant_test = read_text(os.path.join(repo_root, tests_invariant_rel)) or ""

    violations = []
    if "DOM_PROCESS_GUARD_MUTATION()" not in header:
        violations.append("{}: {} missing DOM_PROCESS_GUARD_MUTATION macro".format(invariant_id, header_rel))
    required_impl = (
        "dom_process_guard_enter",
        "dom_process_guard_exit",
        "dom_process_guard_note_mutation",
        "g_process_guard_violations",
        "g_process_guard_mutations",
    )
    for token in required_impl:
        if token not in impl:
            violations.append("{}: {} missing runtime guard token {}".format(invariant_id, impl_rel, token))

    required_guard_tests = (
        "dom_process_guard_note_mutation",
        "dom_process_guard_violation_count() == 1u",
        "dom_process_guard_enter(\"test.process\")",
    )
    for token in required_guard_tests:
        if token not in guard_test:
            violations.append("{}: {} missing guard runtime assertion {}".format(invariant_id, test_rel, token))

    if "INV-PROCESS-ONLY-MUTATION" not in invariant_test:
        violations.append(
            "{}: {} missing process-only mutation invariant linkage".format(
                invariant_id, tests_invariant_rel
            )
        )
    return violations


def check_process_registry_immutability(repo_root):
    invariant_id = "INV-PROCESS-REGISTRY-IMMUTABLE"
    if is_override_active(repo_root, invariant_id):
        return []
    changed_files = get_changed_files(repo_root)
    if changed_files is None:
        return ["{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    if PROCESS_REGISTRY_REL.replace("\\", "/") not in [path.replace("\\", "/") for path in changed_files]:
        return []
    baseline = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    baseline_blob = run_git(["show", "{}:{}".format(baseline, PROCESS_REGISTRY_REL.replace("\\", "/"))], repo_root)
    if baseline_blob is None:
        return []
    try:
        baseline_data = json.loads(baseline_blob)
    except ValueError:
        return ["{}: unable to parse baseline {}".format(invariant_id, PROCESS_REGISTRY_REL)]
    baseline_ids = {entry.get("process_id") for entry in baseline_data.get("records", []) if isinstance(entry, dict)}
    current = _load_json_file(os.path.join(repo_root, PROCESS_REGISTRY_REL))
    if not isinstance(current, dict):
        return ["{}: unable to parse current {}".format(invariant_id, PROCESS_REGISTRY_REL)]
    current_ids = {entry.get("process_id") for entry in current.get("records", []) if isinstance(entry, dict)}
    removed = sorted(pid for pid in baseline_ids if pid and pid not in current_ids)
    if removed:
        return ["{}: process_id removed from registry: {}".format(invariant_id, ", ".join(removed))]
    return []


def check_compliance_report_canon(repo_root):
    invariant_id = "INV-REPORT-CANON"
    if is_override_active(repo_root, invariant_id):
        return []
    path = os.path.join(repo_root, "scripts", "ci", "compliance_report.py")
    text = read_text(path) or ""
    if "CANON_COMPLIANCE_REPORT" not in text:
        return ["{}: compliance_report.py missing canon section".format(invariant_id)]
    return []


def check_frozen_contract_modifications(repo_root, changed_files):
    invariant_id = "INV-LOCKLIST-FROZEN"
    if is_override_active(repo_root, invariant_id):
        return []
    if changed_files is None:
        return ["{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    frozen_paths = set(load_frozen_paths(repo_root))
    if not frozen_paths:
        return ["{}: no frozen contract paths found".format(invariant_id)]
    violations = []
    for path in changed_files:
        if path in frozen_paths:
            violations.append("{}: frozen contract modified: {}".format(invariant_id, path))
    return violations


def check_authoritative_symbols(repo_root):
    violations = []
    skip_rng = is_override_active(repo_root, "INV-DET-NO-ANON-RNG")
    skip_time = is_override_active(repo_root, "INV-DET-NO-WALLCLOCK")
    skip_float = is_override_active(repo_root, "INV-FP-AUTH-BAN")
    skip_content = is_override_active(repo_root, "INV-NO-HARDCODED-CONTENT")

    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, SOURCE_EXTS):
            rel = repo_rel(repo_root, path)
            text = read_text(path)
            if text is None:
                continue
            stripped = strip_c_comments_and_strings(text)
            for idx, line in enumerate(stripped.splitlines(), start=1):
                if not skip_rng and FORBIDDEN_RNG_CALL_RE.search(line):
                    violations.append("INV-DET-NO-ANON-RNG: {}:{}: forbidden RNG call".format(rel, idx))
                if not skip_time and (FORBIDDEN_TIME_CALL_RE.search(line) or FORBIDDEN_TIME_TOKEN_RE.search(line) or FORBIDDEN_CHRONO_RE.search(line)):
                    violations.append("INV-DET-NO-WALLCLOCK: {}:{}: forbidden time call".format(rel, idx))
                if not skip_float and FORBIDDEN_FLOAT_RE.search(line):
                    violations.append("INV-FP-AUTH-BAN: {}:{}: forbidden floating point".format(rel, idx))
            if not skip_content:
                for match in REVERSE_DNS_RE.finditer(text):
                    token = match.group(1)
                    token_l = token.lower()
                    if token_l.startswith(ALLOWED_REVERSE_DNS_PREFIXES):
                        continue
                    violations.append("INV-NO-HARDCODED-CONTENT: {}: content id literal '{}'".format(rel, token))
    return violations


def check_remediation_playbooks(repo_root):
    invariant_id = "INV-REMEDIATION-PLAYBOOKS"
    schema_path = os.path.join(repo_root, REMEDIATION_PLAYBOOK_SCHEMA_REL)
    registry_path = os.path.join(repo_root, REMEDIATION_PLAYBOOK_REGISTRY_REL)
    violations = []

    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(REMEDIATION_PLAYBOOK_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(REMEDIATION_PLAYBOOK_REGISTRY_REL))]

    try:
        with open(registry_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(REMEDIATION_PLAYBOOK_REGISTRY_REL))]

    schema_id = str(payload.get("schema_id", "")).strip()
    if schema_id != REMEDIATION_PLAYBOOK_SCHEMA_ID:
        violations.append(
            "{}: schema_id mismatch {} (expected {})".format(
                invariant_id,
                schema_id or "<missing>",
                REMEDIATION_PLAYBOOK_SCHEMA_ID,
            )
        )

    record = payload.get("record")
    if not isinstance(record, dict):
        return ["{}: missing record object".format(invariant_id)]

    entries = record.get("playbooks")
    if not isinstance(entries, list) or not entries:
        return ["{}: playbooks list missing or empty".format(invariant_id)]

    seen_ids = set()
    seen_blockers = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            violations.append("{}: playbook {} is not an object".format(invariant_id, idx))
            continue
        playbook_id = str(entry.get("playbook_id", "")).strip()
        blocker = str(entry.get("blocker_type", "")).strip()
        strategies = entry.get("strategy_classes")
        if not playbook_id:
            violations.append("{}: playbook {} missing playbook_id".format(invariant_id, idx))
        elif playbook_id in seen_ids:
            violations.append("{}: duplicate playbook_id {}".format(invariant_id, playbook_id))
        else:
            seen_ids.add(playbook_id)
        if not blocker:
            violations.append("{}: playbook {} missing blocker_type".format(invariant_id, playbook_id or idx))
        else:
            seen_blockers.add(blocker)
        if not isinstance(strategies, list) or not [item for item in strategies if str(item).strip()]:
            violations.append(
                "{}: playbook {} has no strategy classes".format(invariant_id, playbook_id or idx)
            )

    missing_blockers = sorted(set(REMEDIATION_PLAYBOOK_REQUIRED_BLOCKERS) - seen_blockers)
    if missing_blockers:
        violations.append(
            "{}: missing required blocker playbooks {}".format(invariant_id, ", ".join(missing_blockers))
        )
    return violations


def _collect_testx_names(repo_root):
    cmake_paths = (
        os.path.join(repo_root, "tests", "invariant", "CMakeLists.txt"),
        os.path.join(repo_root, "tests", "tools", "CMakeLists.txt"),
        os.path.join(repo_root, "tests", "regression", "historical_blockers", "CMakeLists.txt"),
    )
    names = set()
    marker = "dom_add_testx(NAME "
    for path in cmake_paths:
        text = read_text(path)
        if not text:
            continue
        offset = 0
        while True:
            idx = text.find(marker, offset)
            if idx < 0:
                break
            start = idx + len(marker)
            end = text.find("\n", start)
            if end < 0:
                break
            token = text[start:end].strip().split()
            if token:
                names.add(token[0])
            offset = end + 1
    return names


def check_failure_class_registry(repo_root):
    invariant_id = "INV-FAILURE-CLASS-COVERAGE"
    schema_path = os.path.join(repo_root, FAILURE_CLASS_SCHEMA_REL)
    registry_path = os.path.join(repo_root, FAILURE_CLASS_REGISTRY_REL)
    playbook_path = os.path.join(repo_root, REMEDIATION_PLAYBOOK_REGISTRY_REL)
    violations = []

    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(FAILURE_CLASS_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(FAILURE_CLASS_REGISTRY_REL))]
    if not os.path.isfile(playbook_path):
        return ["{}: missing playbook registry {}".format(invariant_id, normalize_path(REMEDIATION_PLAYBOOK_REGISTRY_REL))]

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(FAILURE_CLASS_REGISTRY_REL))]
    if str(payload.get("schema_id", "")).strip() != FAILURE_CLASS_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(FAILURE_CLASS_REGISTRY_REL)))

    playbook_payload = _load_json_file(playbook_path)
    if not isinstance(playbook_payload, dict):
        return violations + ["{}: invalid json {}".format(invariant_id, normalize_path(REMEDIATION_PLAYBOOK_REGISTRY_REL))]
    playbook_rows = playbook_payload.get("record", {}).get("playbooks", [])
    playbook_ids = set()
    for row in playbook_rows if isinstance(playbook_rows, list) else []:
        if isinstance(row, dict):
            playbook_ids.add(str(row.get("playbook_id", "")).strip())

    rows = payload.get("record", {}).get("classes", [])
    if not isinstance(rows, list) or not rows:
        return violations + ["{}: classes list missing or empty".format(invariant_id)]

    known_tests = _collect_testx_names(repo_root)
    seen_ids = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: class {} is not an object".format(invariant_id, idx))
            continue
        failure_class_id = str(row.get("failure_class_id", "")).strip()
        playbook_id = str(row.get("remediation_playbook_id", "")).strip()
        explanation_doc = str(row.get("explanation_doc", "")).strip()
        tests = row.get("regression_tests")

        if not failure_class_id:
            violations.append("{}: class {} missing failure_class_id".format(invariant_id, idx))
            continue
        if failure_class_id in seen_ids:
            violations.append("{}: duplicate failure_class_id {}".format(invariant_id, failure_class_id))
        seen_ids.add(failure_class_id)

        if not playbook_id:
            violations.append("{}: {} missing remediation_playbook_id".format(invariant_id, failure_class_id))
        elif playbook_id not in playbook_ids:
            violations.append("{}: {} references unknown playbook {}".format(invariant_id, failure_class_id, playbook_id))

        if not explanation_doc:
            violations.append("{}: {} missing explanation_doc".format(invariant_id, failure_class_id))
        else:
            doc_path = explanation_doc.split("#", 1)[0].strip()
            if doc_path:
                abs_doc = os.path.join(repo_root, doc_path.replace("/", os.sep))
                if not os.path.isfile(abs_doc):
                    violations.append("{}: {} explanation_doc not found {}".format(invariant_id, failure_class_id, explanation_doc))

        if not isinstance(tests, list) or not [item for item in tests if str(item).strip()]:
            violations.append("{}: {} missing regression_tests".format(invariant_id, failure_class_id))
        else:
            for test_name in tests:
                token = str(test_name).strip()
                if token and token not in known_tests:
                    violations.append("{}: {} references unknown regression test {}".format(
                        invariant_id, failure_class_id, token
                    ))
    return violations


def check_identity_fingerprint(repo_root):
    invariant_id = "INV-IDENTITY-FINGERPRINT"
    explain_id = "INV-IDENTITY-CHANGE-EXPLANATION"
    path = os.path.join(repo_root, IDENTITY_FINGERPRINT_REL)
    explanation = os.path.join(repo_root, IDENTITY_EXPLANATION_REL)
    violations = []

    if not os.path.isfile(path):
        return ["{}: missing artifact {}".format(invariant_id, normalize_path(IDENTITY_FINGERPRINT_REL))]
    if not os.path.isfile(explanation):
        violations.append("{}: missing explanation {}".format(explain_id, normalize_path(IDENTITY_EXPLANATION_REL)))

    try:
        with open(path, "r", encoding="utf-8") as handle:
            current = json.load(handle)
    except (OSError, ValueError):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(IDENTITY_FINGERPRINT_REL))]

    expected = identity_fingerprint_lib.build_identity_payload(repo_root)
    if current != expected:
        violations.append("{}: stale identity fingerprint {}".format(invariant_id, normalize_path(IDENTITY_FINGERPRINT_REL)))

    return violations


def check_forbidden_enum_tokens(repo_root):
    invariant_id = "INV-ENUM-NO-OTHER"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, SOURCE_EXTS):
            rel = repo_rel(repo_root, path)
            text = read_text(path)
            if text is None:
                continue
            stripped = strip_c_comments_and_strings(text)
            lines = stripped.split("\n")
            in_enum = False
            pending_enum = False
            brace_depth = 0
            for idx, line in enumerate(lines, start=1):
                if "HYGIENE_ALLOW_UNKNOWN_ENUM" in line or "PARSER_ONLY_UNKNOWN" in line:
                    continue
                if not in_enum:
                    if pending_enum:
                        if "{" in line:
                            in_enum = True
                            pending_enum = False
                            brace_depth += line.count("{") - line.count("}")
                    elif re.search(r"\benum\b", line):
                        if "{" in line:
                            in_enum = True
                            brace_depth += line.count("{") - line.count("}")
                        else:
                            pending_enum = True
                    continue

                for match in ENUM_TOKEN_RE.finditer(line):
                    violations.append("{}: {}:{}: forbidden enum token {}".format(invariant_id, rel, idx, match.group(0)))

                brace_depth += line.count("{") - line.count("}")
                if brace_depth <= 0:
                    in_enum = False
                    pending_enum = False
                    brace_depth = 0
    return violations


def check_raw_paths(repo_root):
    invariant_id = "INV-NO-RAW-PATHS"
    if is_override_active(repo_root, invariant_id):
        return []

    roots = [
        os.path.join(repo_root, "data", "packs"),
        os.path.join(repo_root, "data", "world"),
        os.path.join(repo_root, "data", "worldgen"),
        os.path.join(repo_root, "schema"),
        os.path.join(repo_root, "tests", "fixtures"),
    ]
    text_exts = [".md", ".schema", ".json", ".toml", ".yaml", ".yml", ".txt", ".replay", ".worlddef", ".save", ".pack", ".manifest", ".ini", ".cfg"]
    violations = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, text_exts):
            rel = repo_rel(repo_root, path)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                    for idx, line in enumerate(handle, start=1):
                        if ABS_WIN_RE.search(line):
                            violations.append("{}: {}:{}: windows absolute path".format(invariant_id, rel, idx))
                            break
                        if ABS_UNIX_RE.search(line):
                            violations.append("{}: {}:{}: unix absolute path".format(invariant_id, rel, idx))
                            break
                        if ABS_UNC_RE.search(line):
                            violations.append("{}: {}:{}: UNC absolute path".format(invariant_id, rel, idx))
                            break
            except OSError:
                continue
    return violations


def check_magic_numbers(repo_root):
    invariant_id = "INV-MAGIC-NO-LITERALS"
    if is_override_active(repo_root, invariant_id):
        return []

    added_lines = get_diff_added_lines(repo_root)
    if added_lines is None:
        return ["{}: unable to determine changed lines; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]

    target_prefixes = tuple(path.replace("\\", "/") + "/" for path in AUTHORITATIVE_DIRS)
    allow_context_re = re.compile(r"^\s*#\s*define\b|\bconst\b|\benum\b")
    numeric_re = re.compile(r"\b(0x[0-9a-fA-F]+|\d+(?:\.\d+)?)\b")
    allow_line_tokens = ("d_q16_16_from_", "d_fixed_", "for (", "for(", "[", "]")

    violations = []
    for rel_path, lines in added_lines.items():
        rel_norm = rel_path.replace("\\", "/")
        if not rel_norm.startswith(target_prefixes):
            continue
        ext = os.path.splitext(rel_norm)[1].lower()
        if ext not in SOURCE_EXTS:
            continue
        for line in lines:
            stripped = strip_c_comments_and_strings(line)
            if not stripped.strip():
                continue
            if allow_context_re.search(stripped):
                continue
            if "<<" in stripped:
                continue
            if any(token in stripped for token in allow_line_tokens):
                continue
            for match in numeric_re.finditer(stripped):
                value = match.group(1)
                if value.startswith("0x"):
                    continue
                if "." in value:
                    violations.append("{}: {}: magic number '{}'".format(invariant_id, rel_norm, value))
                    continue
                try:
                    num_value = int(value)
                except ValueError:
                    num_value = None
                if num_value is not None and num_value <= 16:
                    continue
                violations.append("{}: {}: magic number '{}'".format(invariant_id, rel_norm, value))
    return violations


def _runtime_scope_prefixes():
    return (
        "engine/",
        "game/",
        "client/",
        "server/",
        "launcher/",
        "setup/",
        "libs/appcore/",
        "tools/",
    )


def _is_runtime_source(rel):
    rel_norm = normalize_path(rel)
    if os.path.splitext(rel_norm)[1].lower() not in SOURCE_EXTS:
        return False
    for prefix in _runtime_scope_prefixes():
        if rel_norm.startswith(prefix):
            return True
    return False


def _has_marker(repo_root, rel, marker):
    path = os.path.join(repo_root, rel.replace("/", os.sep))
    text = read_text(path) or ""
    return marker in text


def check_data_first_behavior(repo_root):
    invariant_id = "DATA_FIRST_BEHAVIOR"
    changed = get_changed_files(repo_root)
    if changed is None:
        return ["{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]

    added = get_diff_added_lines(repo_root) or {}
    runtime_changed = []
    for rel, lines in added.items():
        rel_norm = normalize_path(rel)
        if not _is_runtime_source(rel_norm):
            continue
        if any(line.strip() for line in lines):
            runtime_changed.append(rel_norm)

    if not runtime_changed:
        return []

    data_first_roots = ("schema/", "data/", "docs/", "repo/", "tests/fixtures/")
    has_data_first_change = False
    for rel in changed:
        rel_norm = normalize_path(rel)
        if rel_norm.startswith(data_first_roots):
            has_data_first_change = True
            break
    if has_data_first_change:
        return []

    violations = []
    for rel in sorted(set(runtime_changed)):
        if _has_marker(repo_root, rel, MECHANISM_ONLY_MARKER):
            continue
        violations.append(
            "{}: runtime behavior change without schema/data anchor {} (add {} if mechanism-only)".format(
                invariant_id, rel, MECHANISM_ONLY_MARKER
            )
        )
    return violations


def check_no_silent_defaults(repo_root):
    invariant_id = "NO_SILENT_DEFAULTS"
    added = get_diff_added_lines(repo_root)
    if added is None:
        return ["{}: unable to determine changed lines; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]

    default_like = (
        re.compile(r"\bvalue_or\s*\("),
        re.compile(r"\bget_or_default\s*\("),
        re.compile(r"\bor_default\s*\("),
        re.compile(r"\bdefault\s*[:=]"),
    )
    violations = []
    for rel_path, lines in added.items():
        rel = normalize_path(rel_path)
        if not _is_runtime_source(rel):
            continue
        for idx, line in enumerate(lines, start=1):
            stripped = strip_c_comments_and_strings(line)
            if not stripped.strip():
                continue
            if "REFUSE_" in stripped or "refusal" in stripped.lower() or "reject" in stripped.lower():
                continue
            for pattern in default_like:
                if pattern.search(stripped):
                    violations.append(
                        "{}: {} added line {} uses defaulting without explicit refusal".format(
                            invariant_id, rel, idx
                        )
                    )
                    break
    return violations


def _collect_schema_tokens(repo_root):
    tokens = set()
    roots = [os.path.join(repo_root, "schema")]
    token_re = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{1,}")
    for path in iter_files(roots, DEFAULT_EXCLUDES, [".schema", ".json", ".yaml", ".yml", ".md"]):
        text = read_text(path) or ""
        for token in token_re.findall(text):
            tokens.add(token)
    return tokens


def check_schema_anchor_required(repo_root):
    invariant_id = "SCHEMA_ANCHOR_REQUIRED"
    added = get_diff_added_lines(repo_root)
    if added is None:
        return ["{}: unable to determine changed lines; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    schema_tokens = _collect_schema_tokens(repo_root)
    key_call_re = re.compile(
        r"\b(?:json|tlv|manifest|pack|schema|config|cfg|kv)[A-Za-z0-9_]*\s*\([^)]*\"([a-z][a-z0-9_.-]+)\""
    )
    violations = []
    for rel_path, lines in added.items():
        rel = normalize_path(rel_path)
        if not _is_runtime_source(rel):
            continue
        for idx, line in enumerate(lines, start=1):
            stripped = strip_c_comments_and_strings(line)
            if not stripped.strip():
                continue
            for match in key_call_re.finditer(stripped):
                key = match.group(1)
                if key not in schema_tokens:
                    violations.append(
                        "{}: {} added line {} references key '{}' not declared in schema".format(
                            invariant_id, rel, idx, key
                        )
                    )
    return violations


def _count_non_test_occurrences(repo_root, symbol):
    roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "setup"),
        os.path.join(repo_root, "libs"),
        os.path.join(repo_root, "tools"),
    ]
    count = 0
    sym_re = re.compile(r"\b{}\b".format(re.escape(symbol)))
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = normalize_path(repo_rel(repo_root, path))
        if "/tests/" in rel or rel.startswith("tests/"):
            continue
        text = read_text(path) or ""
        if sym_re.search(text):
            count += 1
    return count


def check_no_single_use_code_paths(repo_root):
    invariant_id = "NO_SINGLE_USE_CODE_PATHS"
    added = get_changed_files(repo_root, diff_filter="A")
    if added is None:
        return ["{}: unable to determine added files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]

    violations = []
    for rel in added:
        rel_norm = normalize_path(rel)
        if not _is_runtime_source(rel_norm):
            continue
        if _has_marker(repo_root, rel_norm, PROTOTYPE_MARKER):
            continue
        base = os.path.splitext(os.path.basename(rel_norm))[0]
        refs = _count_non_test_occurrences(repo_root, base)
        if refs <= 1:
            violations.append(
                "{}: {} appears single-use ({} non-test reference); annotate {} when intentional".format(
                    invariant_id, rel_norm, refs, PROTOTYPE_MARKER
                )
            )
    return violations


def check_duplicate_logic_pressure(repo_root):
    invariant_id = "DUPLICATE_LOGIC_PRESSURE"
    added = get_diff_added_lines(repo_root)
    if added is None:
        return ["{}: unable to determine changed lines; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]

    line_map = {}
    for rel_path, lines in added.items():
        rel = normalize_path(rel_path)
        if not _is_runtime_source(rel):
            continue
        if _has_marker(repo_root, rel, DUPLICATION_MARKER):
            continue
        for line in lines:
            stripped = strip_c_comments_and_strings(line).strip()
            if len(stripped) < 64:
                continue
            if stripped.startswith("#"):
                continue
            line_map.setdefault(stripped, set()).add(rel)

    violations = []
    for snippet, files in line_map.items():
        if len(files) >= 2:
            files_sorted = sorted(files)
            violations.append(
                "{}: duplicated added logic across {} (snippet hash {})".format(
                    invariant_id, ", ".join(files_sorted), hashlib.sha1(snippet.encode("utf-8")).hexdigest()[:12]
                )
            )
    return violations


def check_new_feature_requires_data_first(repo_root):
    invariant_id = "NEW_FEATURE_REQUIRES_DATA_FIRST"
    changed = get_changed_files(repo_root)
    if changed is None:
        return ["{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]

    runtime_changes = [normalize_path(rel) for rel in changed if _is_runtime_source(rel)]
    if not runtime_changes:
        return []

    data_touch = False
    for rel in changed:
        rel_norm = normalize_path(rel)
        if rel_norm.startswith("data/") or rel_norm.startswith("schema/") or rel_norm.startswith("docs/"):
            data_touch = True
            break
    if data_touch:
        return []

    violations = []
    for rel in sorted(set(runtime_changes)):
        if _has_marker(repo_root, rel, INFRA_ONLY_MARKER):
            continue
        violations.append(
            "{}: runtime feature touched without data/schema/docs anchor {} (file {})".format(
                invariant_id, INFRA_ONLY_MARKER, rel
            )
        )
    return violations


def check_ambiguous_new_dirs(repo_root):
    invariant_id = "INV-REPOX-AMBIGUOUS-DIRS"
    if is_override_active(repo_root, invariant_id):
        return []
    added = get_changed_files(repo_root, diff_filter="A")
    if added is None:
        return ["{}: unable to determine added files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id)]
    violations = []
    for path in added:
        path_norm = path.replace("\\", "/")
        if path_norm.startswith("tmp/"):
            continue
        parts = [part for part in path_norm.split("/") if part]
        for part in parts[:-1]:
            if part.lower() in AMBIGUOUS_DIR_NAMES:
                violations.append("{}: new ambiguous directory '{}' in {}".format(invariant_id, part, path_norm))
                break
    return violations


def check_root_module_shims(repo_root):
    invariant_id = "INV-ROOT-MODULE-SHIM"
    if is_override_active(repo_root, invariant_id):
        return []

    tracked_dirs_out = run_git(["ls-tree", "-d", "--name-only", "HEAD"], repo_root)
    tracked_files_out = run_git(["ls-tree", "-r", "--name-only", "HEAD"], repo_root)
    if tracked_dirs_out is None or tracked_files_out is None:
        return ["{}: unable to enumerate tracked root directories".format(invariant_id)]

    tracked_dirs = [normalize_path(item) for item in tracked_dirs_out.splitlines() if item.strip()]
    tracked_files = [normalize_path(item) for item in tracked_files_out.splitlines() if item.strip()]
    violations = []

    for root_dir in sorted(tracked_dirs):
        if "/" in root_dir:
            continue
        cmake_rel = normalize_path(os.path.join(root_dir, "CMakeLists.txt"))
        if cmake_rel not in tracked_files:
            continue

        files_under = [path for path in tracked_files if path.startswith(root_dir + "/")]
        cmake_text = read_text(os.path.join(repo_root, cmake_rel.replace("/", os.sep))) or ""
        redirect_only = (
            "add_subdirectory(" in cmake_text
            and "add_library(" not in cmake_text
            and "add_executable(" not in cmake_text
        )
        shared_prefix = root_dir.startswith("shared_")
        if shared_prefix or (len(files_under) <= 3 and redirect_only):
            shape = "shared_prefix" if shared_prefix else "redirect_only"
            violations.append(
                "{}: root module shim detected {} (shape={}, files={})".format(
                    invariant_id, root_dir, shape, len(files_under)
                )
            )
    return violations


def check_compat_matrix_registry(repo_root):
    invariant_id = "INV-COMPAT-MATRIX-VALID"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_path = os.path.join(repo_root, COMPAT_MATRIX_SCHEMA_REL)
    registry_path = os.path.join(repo_root, COMPAT_MATRIX_REGISTRY_REL)
    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(COMPAT_MATRIX_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(COMPAT_MATRIX_REGISTRY_REL))]

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(COMPAT_MATRIX_REGISTRY_REL))]

    violations = []
    if str(payload.get("schema_id", "")).strip() != COMPAT_MATRIX_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(COMPAT_MATRIX_REGISTRY_REL)))
    if _parse_semver(payload.get("schema_version")) is None:
        violations.append("{}: invalid schema_version in {}".format(invariant_id, normalize_path(COMPAT_MATRIX_REGISTRY_REL)))

    record = payload.get("record")
    if not isinstance(record, dict):
        return violations + ["{}: missing record object in {}".format(invariant_id, normalize_path(COMPAT_MATRIX_REGISTRY_REL))]
    rows = record.get("entries")
    if not isinstance(rows, list):
        return violations + ["{}: entries must be list in {}".format(invariant_id, normalize_path(COMPAT_MATRIX_REGISTRY_REL))]

    seen = set()
    compat_types = {"forward", "backward", "full", "none"}
    component_types = {"schema", "pack", "save", "replay", "protocol", "api", "abi", "identity"}
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: entry {} must be object".format(invariant_id, idx))
            continue
        component_type = str(row.get("component_type", "")).strip()
        component_id = str(row.get("component_id", "")).strip()
        version_from = str(row.get("version_from", "")).strip()
        version_to = str(row.get("version_to", "")).strip()
        compatibility_type = str(row.get("compatibility_type", "")).strip()
        migration_required = row.get("migration_required")
        migration_id = str(row.get("migration_id", "")).strip()

        if component_type not in component_types:
            violations.append("{}: invalid component_type '{}' at entry {}".format(invariant_id, component_type, idx))
        if not component_id:
            violations.append("{}: missing component_id at entry {}".format(invariant_id, idx))
        if _parse_semver(version_from) is None or _parse_semver(version_to) is None:
            violations.append("{}: invalid versions at entry {}".format(invariant_id, idx))
        if compatibility_type not in compat_types:
            violations.append("{}: invalid compatibility_type '{}' at entry {}".format(invariant_id, compatibility_type, idx))
        if not isinstance(migration_required, bool):
            violations.append("{}: migration_required must be bool at entry {}".format(invariant_id, idx))
        if migration_required is True and not migration_id:
            violations.append("{}: migration_id required at entry {}".format(invariant_id, idx))

        key = (component_type, component_id, version_from, version_to)
        if key in seen:
            violations.append("{}: duplicate transition {} {} {} -> {}".format(
                invariant_id, component_type, component_id, version_from, version_to
            ))
        seen.add(key)

    return violations


def check_compat_migration_registry(repo_root):
    invariant_id = "INV-COMPAT-MIGRATIONS-VALID"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_path = os.path.join(repo_root, COMPAT_MIGRATION_SCHEMA_REL)
    registry_path = os.path.join(repo_root, COMPAT_MIGRATION_REGISTRY_REL)
    matrix_path = os.path.join(repo_root, COMPAT_MATRIX_REGISTRY_REL)
    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(COMPAT_MIGRATION_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(COMPAT_MIGRATION_REGISTRY_REL))]

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(COMPAT_MIGRATION_REGISTRY_REL))]

    violations = []
    if str(payload.get("schema_id", "")).strip() != COMPAT_MIGRATION_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(COMPAT_MIGRATION_REGISTRY_REL)))
    if _parse_semver(payload.get("schema_version")) is None:
        violations.append("{}: invalid schema_version in {}".format(invariant_id, normalize_path(COMPAT_MIGRATION_REGISTRY_REL)))

    record = payload.get("record")
    if not isinstance(record, dict):
        return violations + ["{}: missing record object in {}".format(invariant_id, normalize_path(COMPAT_MIGRATION_REGISTRY_REL))]
    rows = record.get("migrations")
    if not isinstance(rows, list):
        return violations + ["{}: migrations must be list in {}".format(invariant_id, normalize_path(COMPAT_MIGRATION_REGISTRY_REL))]

    migration_ids = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: migration {} must be object".format(invariant_id, idx))
            continue
        migration_id = str(row.get("migration_id", "")).strip()
        from_version = str(row.get("from_version", "")).strip()
        to_version = str(row.get("to_version", "")).strip()
        migration_tool = str(row.get("migration_tool", "")).strip()
        deterministic_required = row.get("deterministic_required")
        if not migration_id:
            violations.append("{}: migration {} missing migration_id".format(invariant_id, idx))
            continue
        if migration_id in migration_ids:
            violations.append("{}: duplicate migration_id '{}'".format(invariant_id, migration_id))
        migration_ids.add(migration_id)
        if _parse_semver(from_version) is None or _parse_semver(to_version) is None:
            violations.append("{}: invalid version route for '{}'".format(invariant_id, migration_id))
        if not isinstance(deterministic_required, bool):
            violations.append("{}: deterministic_required must be bool for '{}'".format(invariant_id, migration_id))
        if not migration_tool:
            violations.append("{}: migration_tool missing for '{}'".format(invariant_id, migration_id))
        else:
            rel_file = migration_tool.split("::", 1)[0]
            if not os.path.isfile(os.path.join(repo_root, rel_file.replace("/", os.sep))):
                violations.append("{}: migration tool file missing for '{}' -> {}".format(
                    invariant_id, migration_id, normalize_path(rel_file)
                ))

    matrix_payload = _load_json_file(matrix_path) if os.path.isfile(matrix_path) else None
    if isinstance(matrix_payload, dict):
        matrix_record = matrix_payload.get("record")
        matrix_rows = matrix_record.get("entries") if isinstance(matrix_record, dict) else None
        if isinstance(matrix_rows, list):
            for idx, row in enumerate(matrix_rows):
                if not isinstance(row, dict):
                    continue
                if row.get("migration_required") is not True:
                    continue
                migration_id = str(row.get("migration_id", "")).strip()
                if not migration_id:
                    violations.append("{}: compat matrix entry {} missing migration_id".format(invariant_id, idx))
                elif migration_id not in migration_ids:
                    violations.append("{}: missing migration '{}' referenced by compat matrix entry {}".format(
                        invariant_id, migration_id, idx
                    ))
    return violations


def check_schema_version_policy_registry(repo_root):
    invariant_id = "INV-SCHEMA-VERSION-POLICY"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_path = os.path.join(repo_root, COMPAT_SCHEMA_POLICY_SCHEMA_REL)
    registry_path = os.path.join(repo_root, COMPAT_SCHEMA_POLICY_REGISTRY_REL)
    matrix_path = os.path.join(repo_root, COMPAT_MATRIX_REGISTRY_REL)
    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(COMPAT_SCHEMA_POLICY_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(COMPAT_SCHEMA_POLICY_REGISTRY_REL))]

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(COMPAT_SCHEMA_POLICY_REGISTRY_REL))]

    violations = []
    if str(payload.get("schema_id", "")).strip() != COMPAT_SCHEMA_POLICY_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(COMPAT_SCHEMA_POLICY_REGISTRY_REL)))
    if _parse_semver(payload.get("schema_version")) is None:
        violations.append("{}: invalid schema_version in {}".format(invariant_id, normalize_path(COMPAT_SCHEMA_POLICY_REGISTRY_REL)))

    record = payload.get("record")
    if not isinstance(record, dict):
        return violations + ["{}: missing record object in {}".format(invariant_id, normalize_path(COMPAT_SCHEMA_POLICY_REGISTRY_REL))]
    rows = record.get("policies")
    if not isinstance(rows, list):
        return violations + ["{}: policies must be list in {}".format(invariant_id, normalize_path(COMPAT_SCHEMA_POLICY_REGISTRY_REL))]

    matrix_components = set()
    matrix_payload = _load_json_file(matrix_path) if os.path.isfile(matrix_path) else None
    if isinstance(matrix_payload, dict):
        matrix_record = matrix_payload.get("record")
        matrix_rows = matrix_record.get("entries") if isinstance(matrix_record, dict) else None
        if isinstance(matrix_rows, list):
            for row in matrix_rows:
                if not isinstance(row, dict):
                    continue
                component_id = str(row.get("component_id", "")).strip()
                if component_id:
                    matrix_components.add(component_id)

    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: policy {} must be object".format(invariant_id, idx))
            continue
        schema_id = str(row.get("schema_id", "")).strip()
        current_version = str(row.get("current_version", "")).strip()
        allowed_backward = row.get("allowed_backward")
        allowed_forward = row.get("allowed_forward")
        breaking = row.get("breaking_change_requires_migration")
        deprecation_policy = str(row.get("deprecation_policy", "")).strip()
        deprecated_fields = row.get("deprecated_fields")

        if not schema_id:
            violations.append("{}: policy {} missing schema_id".format(invariant_id, idx))
        if _parse_semver(current_version) is None:
            violations.append("{}: policy {} invalid current_version".format(invariant_id, idx))
        if not isinstance(allowed_backward, list):
            violations.append("{}: policy {} allowed_backward must be list".format(invariant_id, idx))
        if not isinstance(allowed_forward, list):
            violations.append("{}: policy {} allowed_forward must be list".format(invariant_id, idx))
        if not isinstance(breaking, bool):
            violations.append("{}: policy {} breaking_change_requires_migration must be bool".format(invariant_id, idx))
        if not deprecation_policy:
            violations.append("{}: policy {} missing deprecation_policy".format(invariant_id, idx))
        if deprecated_fields is not None and not isinstance(deprecated_fields, list):
            violations.append("{}: policy {} deprecated_fields must be list".format(invariant_id, idx))

        short_id = schema_id.rsplit(".", 1)[-1] if schema_id else ""
        if matrix_components and schema_id and short_id not in matrix_components and schema_id not in matrix_components:
            violations.append("{}: policy '{}' missing schema component transition in {}".format(
                invariant_id, schema_id, normalize_path(COMPAT_MATRIX_REGISTRY_REL)
            ))
    return violations


def check_schema_deprecated_fields(repo_root):
    invariant_id = "WARN-SCHEMA-DEPRECATED-FIELDS"
    if is_override_active(repo_root, invariant_id):
        return []

    registry_path = os.path.join(repo_root, COMPAT_SCHEMA_POLICY_REGISTRY_REL)
    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return []
    record = payload.get("record")
    rows = record.get("policies") if isinstance(record, dict) else None
    if not isinstance(rows, list):
        return []

    deprecated_tokens = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        fields = row.get("deprecated_fields")
        if not isinstance(fields, list):
            continue
        for token in fields:
            value = str(token).strip()
            if value:
                deprecated_tokens.add(value)
    if not deprecated_tokens:
        return []

    changed_files = get_changed_files(repo_root)
    if changed_files is None:
        return []
    candidates = [path for path in changed_files if path.startswith("schema/") or path.startswith("data/")]
    violations = []
    for rel in sorted(candidates):
        diff = run_git(["diff", "--unified=0", "--", rel], repo_root)
        if diff is None:
            continue
        for token in sorted(deprecated_tokens):
            pattern = re.compile(r"^\+[^+].*\b{}\b".format(re.escape(token)))
            if pattern.search(diff):
                violations.append("{}: deprecated field token '{}' added in {}".format(invariant_id, token, rel))
    return violations


def check_securex_trust_policy_registry(repo_root):
    invariant_id = "INV-SECUREX-TRUST-POLICY-VALID"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_path = os.path.join(repo_root, SECUREX_TRUST_POLICY_SCHEMA_REL)
    registry_path = os.path.join(repo_root, SECUREX_TRUST_POLICY_REGISTRY_REL)
    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(SECUREX_TRUST_POLICY_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(SECUREX_TRUST_POLICY_REGISTRY_REL))]

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(SECUREX_TRUST_POLICY_REGISTRY_REL))]

    violations = []
    if str(payload.get("schema_id", "")).strip() != SECUREX_TRUST_POLICY_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(SECUREX_TRUST_POLICY_REGISTRY_REL)))
    if _parse_semver(payload.get("schema_version")) is None:
        violations.append("{}: invalid schema_version in {}".format(invariant_id, normalize_path(SECUREX_TRUST_POLICY_REGISTRY_REL)))

    record = payload.get("record")
    if not isinstance(record, dict):
        return violations + ["{}: missing record object in {}".format(invariant_id, normalize_path(SECUREX_TRUST_POLICY_REGISTRY_REL))]
    rows = record.get("entries")
    if not isinstance(rows, list):
        return violations + ["{}: entries must be list in {}".format(invariant_id, normalize_path(SECUREX_TRUST_POLICY_REGISTRY_REL))]

    required_subsystems = {
        "engine_core",
        "game_logic",
        "client_renderer",
        "server_authority",
        "tools",
        "packs",
        "controlx",
    }
    seen = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: entry {} must be object".format(invariant_id, idx))
            continue
        subsystem = str(row.get("subsystem", "")).strip()
        trust_level = str(row.get("trust_level", "")).strip()
        allowed = row.get("allowed_actions")
        forbidden = row.get("forbidden_actions")
        escalation = row.get("escalation_required")
        if not subsystem:
            violations.append("{}: entry {} missing subsystem".format(invariant_id, idx))
            continue
        seen.add(subsystem)
        if trust_level not in {"root", "authoritative", "bounded", "untrusted"}:
            violations.append("{}: entry {} invalid trust_level '{}'".format(invariant_id, idx, trust_level))
        if not isinstance(allowed, list) or not allowed:
            violations.append("{}: entry {} allowed_actions must be non-empty list".format(invariant_id, idx))
        if not isinstance(forbidden, list) or not forbidden:
            violations.append("{}: entry {} forbidden_actions must be non-empty list".format(invariant_id, idx))
        if not isinstance(escalation, bool):
            violations.append("{}: entry {} escalation_required must be bool".format(invariant_id, idx))

    missing = sorted(required_subsystems - seen)
    if missing:
        violations.append("{}: missing required subsystems {}".format(invariant_id, ", ".join(missing)))
    return violations


def check_securex_privilege_model(repo_root):
    invariant_id = "INV-SECUREX-PRIVILEGE-MODEL"
    if is_override_active(repo_root, invariant_id):
        return []

    schema_path = os.path.join(repo_root, SECUREX_PRIVILEGE_MODEL_SCHEMA_REL)
    registry_path = os.path.join(repo_root, SECUREX_PRIVILEGE_MODEL_REGISTRY_REL)
    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(SECUREX_PRIVILEGE_MODEL_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(SECUREX_PRIVILEGE_MODEL_REGISTRY_REL))]

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(SECUREX_PRIVILEGE_MODEL_REGISTRY_REL))]

    violations = []
    if str(payload.get("schema_id", "")).strip() != SECUREX_PRIVILEGE_MODEL_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(SECUREX_PRIVILEGE_MODEL_REGISTRY_REL)))
    if _parse_semver(payload.get("schema_version")) is None:
        violations.append("{}: invalid schema_version in {}".format(invariant_id, normalize_path(SECUREX_PRIVILEGE_MODEL_REGISTRY_REL)))

    record = payload.get("record")
    if not isinstance(record, dict):
        return violations + ["{}: missing record object in {}".format(invariant_id, normalize_path(SECUREX_PRIVILEGE_MODEL_REGISTRY_REL))]
    rows = record.get("roles")
    if not isinstance(rows, list):
        return violations + ["{}: roles must be list in {}".format(invariant_id, normalize_path(SECUREX_PRIVILEGE_MODEL_REGISTRY_REL))]

    required_roles = {"role.observer", "role.creator", "role.mission_player"}
    seen = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: role {} must be object".format(invariant_id, idx))
            continue
        role_id = str(row.get("role_id", "")).strip()
        law_profile_id = str(row.get("law_profile_id", "")).strip()
        entitlements = row.get("entitlements")
        watermark = str(row.get("watermark_policy", "")).strip()
        if not role_id:
            violations.append("{}: role {} missing role_id".format(invariant_id, idx))
            continue
        seen.add(role_id)
        if not law_profile_id:
            violations.append("{}: role '{}' missing law_profile_id".format(invariant_id, role_id))
        if not isinstance(entitlements, list):
            violations.append("{}: role '{}' entitlements must be list".format(invariant_id, role_id))
            entitlements = []
        entitlement_set = {str(item).strip() for item in entitlements if str(item).strip()}
        if role_id == "role.observer":
            required = {"camera.mode.observer_truth", "ui.overlay.world_layers"}
            missing = sorted(required - entitlement_set)
            if missing:
                violations.append("{}: observer role missing entitlements {}".format(invariant_id, ", ".join(missing)))
            if watermark == "none":
                violations.append("{}: observer role must set watermark_policy".format(invariant_id))
        if role_id == "role.creator" and watermark == "none":
            violations.append("{}: creator role must set watermark_policy".format(invariant_id))
        if watermark not in {"none", "observer", "dev"}:
            violations.append("{}: role '{}' invalid watermark_policy '{}'".format(invariant_id, role_id, watermark))
    missing_roles = sorted(required_roles - seen)
    if missing_roles:
        violations.append("{}: missing required roles {}".format(invariant_id, ", ".join(missing_roles)))
    return violations


def check_unlocked_dependency(repo_root):
    invariant_id = "INV-UNLOCKED-DEPENDENCY"
    if is_override_active(repo_root, invariant_id):
        return []

    violations = []
    requirements_files = ("requirements.txt", "requirements-dev.txt")
    for rel in requirements_files:
        path = os.path.join(repo_root, rel)
        if not os.path.isfile(path):
            continue
        text = read_text(path) or ""
        for idx, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "==" in stripped:
                continue
            if any(token in stripped for token in (">=", "<=", "~=", ">", "<")):
                violations.append("{}: unlocked dependency '{}' at {}:{}".format(
                    invariant_id, stripped, rel, idx
                ))

    package_json_path = os.path.join(repo_root, "package.json")
    if os.path.isfile(package_json_path):
        payload = _load_json_file(package_json_path)
        if isinstance(payload, dict):
            for section in ("dependencies", "devDependencies", "optionalDependencies"):
                deps = payload.get(section)
                if not isinstance(deps, dict):
                    continue
                for name, version in deps.items():
                    version_text = str(version).strip()
                    if not version_text:
                        continue
                    if version_text[0] in {"^", "~", ">", "<", "*"}:
                        violations.append("{}: package.json {} '{}' uses unlocked range '{}'".format(
                            invariant_id, section, name, version_text
                        ))
    return violations


def check_tool_version_mismatch(repo_root):
    invariant_id = "INV-TOOL-VERSION-MISMATCH"
    if is_override_active(repo_root, invariant_id):
        return []

    manifest_path = os.path.join(repo_root, SECUREX_INTEGRITY_MANIFEST_REL)
    if not os.path.isfile(manifest_path):
        return ["{}: missing {}".format(invariant_id, normalize_path(SECUREX_INTEGRITY_MANIFEST_REL))]
    payload = _load_json_file(manifest_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(SECUREX_INTEGRITY_MANIFEST_REL))]

    violations = []
    if str(payload.get("schema_id", "")).strip() != SECUREX_INTEGRITY_MANIFEST_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(invariant_id, normalize_path(SECUREX_INTEGRITY_MANIFEST_REL)))
    record = payload.get("record")
    if not isinstance(record, dict):
        return violations + ["{}: missing record object in {}".format(invariant_id, normalize_path(SECUREX_INTEGRITY_MANIFEST_REL))]
    tool_hashes = record.get("tool_hashes")
    if not isinstance(tool_hashes, list):
        return violations + ["{}: tool_hashes must be list in {}".format(invariant_id, normalize_path(SECUREX_INTEGRITY_MANIFEST_REL))]

    for idx, row in enumerate(tool_hashes):
        if not isinstance(row, dict):
            violations.append("{}: tool_hashes entry {} must be object".format(invariant_id, idx))
            continue
        source = normalize_path(str(row.get("source", "")).strip())
        expected_sha = str(row.get("sha256", "")).strip().lower()
        if not source or not expected_sha:
            violations.append("{}: tool_hashes entry {} missing source/sha256".format(invariant_id, idx))
            continue
        abs_source = os.path.join(repo_root, source.replace("/", os.sep))
        if not os.path.isfile(abs_source):
            violations.append("{}: tool source missing {}".format(invariant_id, source))
            continue
        actual_sha = _sha256_file(abs_source)
        if actual_sha != expected_sha:
            violations.append("{}: hash mismatch for {} (expected {}, got {})".format(
                invariant_id, source, expected_sha, actual_sha
            ))
    return violations


def check_derived_artifact_contract(repo_root):
    invariant_id = "INV-DERIVED-ARTIFACT-CONTRACT"
    schema_path = os.path.join(repo_root, DERIVED_ARTIFACT_CONTRACT_SCHEMA_REL)
    registry_path = os.path.join(repo_root, DERIVED_ARTIFACT_REGISTRY_REL)
    violations = []

    if not os.path.isfile(schema_path):
        return ["{}: missing schema {}".format(invariant_id, normalize_path(DERIVED_ARTIFACT_CONTRACT_SCHEMA_REL))]
    if not os.path.isfile(registry_path):
        return ["{}: missing registry {}".format(invariant_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL))]

    payload = _load_json_file(registry_path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL))]

    schema_id = str(payload.get("schema_id", "")).strip()
    if schema_id != DERIVED_ARTIFACT_SCHEMA_ID:
        violations.append(
            "{}: registry schema_id mismatch in {} (found {})".format(
                invariant_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL), schema_id
            )
        )

    record = payload.get("record")
    if not isinstance(record, dict):
        return violations + ["{}: missing record object in {}".format(
            invariant_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL)
        )]

    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list):
        return violations + ["{}: artifacts must be a list in {}".format(
            invariant_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL)
        )]

    seen_ids = set()
    seen_paths = set()
    for entry in artifacts:
        if not isinstance(entry, dict):
            violations.append("{}: non-object artifact entry in {}".format(
                invariant_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL)
            ))
            continue

        artifact_id = str(entry.get("artifact_id", "")).strip()
        path = normalize_path(str(entry.get("path", "")).strip())
        artifact_class = str(entry.get("artifact_class", "")).strip()
        canonical_hash_required = entry.get("canonical_hash_required")
        used_for_gating = entry.get("used_for_gating")

        if not artifact_id:
            violations.append("{}: artifact entry missing artifact_id in {}".format(
                invariant_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL)
            ))
            continue
        if artifact_id in seen_ids:
            violations.append("{}: duplicate artifact_id '{}' in {}".format(
                invariant_id, artifact_id, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL)
            ))
        seen_ids.add(artifact_id)

        if not path:
            violations.append("{}: artifact '{}' missing path".format(invariant_id, artifact_id))
        elif path in seen_paths:
            violations.append("{}: duplicate artifact path '{}' in {}".format(
                invariant_id, path, normalize_path(DERIVED_ARTIFACT_REGISTRY_REL)
            ))
        seen_paths.add(path)

        if artifact_class not in DERIVED_ARTIFACT_CLASSES:
            violations.append("{}: artifact '{}' has invalid artifact_class '{}'".format(
                invariant_id, artifact_id, artifact_class
            ))
        if not isinstance(canonical_hash_required, bool):
            violations.append("{}: artifact '{}' canonical_hash_required must be bool".format(
                invariant_id, artifact_id
            ))
        if not isinstance(used_for_gating, bool):
            violations.append("{}: artifact '{}' used_for_gating must be bool".format(
                invariant_id, artifact_id
            ))

        if artifact_class == "CANONICAL" and canonical_hash_required is not True:
            violations.append("{}: artifact '{}' must require canonical hash".format(
                invariant_id, artifact_id
            ))
        if artifact_class == "RUN_META" and used_for_gating is True:
            violations.append("{}: RUN_META artifact '{}' cannot be gating input".format(
                invariant_id, artifact_id
            ))
        if artifact_class == "DERIVED_VIEW":
            ext = entry.get("extensions")
            regen_tool = ""
            if isinstance(ext, dict):
                regen_tool = str(ext.get("regeneration_tool", "")).strip()
            if not regen_tool:
                violations.append("{}: DERIVED_VIEW artifact '{}' missing extensions.regeneration_tool".format(
                    invariant_id, artifact_id
                ))

        artifact_abs = os.path.join(repo_root, path.replace("/", os.sep))
        if artifact_class == "CANONICAL" and path.endswith(".json"):
            if os.path.isfile(artifact_abs):
                artifact_payload = _load_json_file(artifact_abs)
                if isinstance(artifact_payload, dict):
                    stack = [artifact_payload]
                    while stack:
                        node = stack.pop()
                        if isinstance(node, dict):
                            for key, value in node.items():
                                if key in DERIVED_ARTIFACT_CANONICAL_FORBIDDEN_KEYS:
                                    violations.append(
                                        "{}: canonical artifact '{}' contains forbidden run-meta key '{}'".format(
                                            invariant_id, artifact_id, key
                                        )
                                    )
                                stack.append(value)
                        elif isinstance(node, list):
                            stack.extend(node)

    missing_required_ids = sorted(set(DERIVED_ARTIFACT_REQUIRED_IDS) - seen_ids)
    if missing_required_ids:
        violations.append("{}: missing required artifact ids {}".format(
            invariant_id, ", ".join(missing_required_ids)
        ))

    return violations


def check_auditx_artifact_headers(repo_root):
    invariant_id = "INV-AUDITX-ARTIFACT-HEADERS"
    output_root = os.path.join(repo_root, "docs", "audit", "auditx")
    if not os.path.isdir(output_root):
        return []

    expected_md = (
        "docs/audit/auditx/README.md",
        "docs/audit/auditx/FINDINGS.md",
        "docs/audit/auditx/SUMMARY.md",
    )
    expected_json = AUDITX_CANONICAL_ARTIFACTS

    violations = []
    for rel in expected_md:
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            violations.append("{}: missing artifact {}".format(invariant_id, rel))
            continue
        text = read_text(path) or ""
        header = parse_doc_header(text)
        if not header:
            violations.append("{}: missing doc header {}".format(invariant_id, rel))
            continue
        status = header.get("status", "")
        if status != "DERIVED":
            violations.append("{}: expected DERIVED status in {} (found {})".format(invariant_id, rel, status))
        reviewed = header.get("reviewed", "")
        if not _parse_date(reviewed):
            violations.append("{}: invalid Last Reviewed '{}' in {}".format(invariant_id, reviewed, rel))

    for rel in expected_json:
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            violations.append("{}: missing artifact {}".format(invariant_id, rel))
            continue
        payload = _load_json_file(path)
        if payload is None:
            violations.append("{}: invalid json {}".format(invariant_id, rel))
            continue
        artifact_class = str(payload.get("artifact_class", "")).strip()
        if artifact_class != "CANONICAL":
            violations.append("{}: expected CANONICAL artifact_class in {} (found {})".format(
                invariant_id, rel, artifact_class
            ))

        stack = [payload]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in AUDITX_CANONICAL_FORBIDDEN_KEYS:
                        violations.append("{}: forbidden run-meta key '{}' in {}".format(invariant_id, key, rel))
                    stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)

    run_meta_path = os.path.join(repo_root, AUDITX_RUN_META_ARTIFACT.replace("/", os.sep))
    if os.path.isfile(run_meta_path):
        payload = _load_json_file(run_meta_path)
        if payload is None:
            violations.append("{}: invalid json {}".format(invariant_id, AUDITX_RUN_META_ARTIFACT))
        else:
            artifact_class = str(payload.get("artifact_class", "")).strip()
            if artifact_class != "RUN_META":
                violations.append("{}: expected RUN_META artifact_class in {} (found {})".format(
                    invariant_id, AUDITX_RUN_META_ARTIFACT, artifact_class
                ))
            status = str(payload.get("status", "")).strip()
            if status != "DERIVED":
                violations.append("{}: expected DERIVED status in {} (found {})".format(
                    invariant_id, AUDITX_RUN_META_ARTIFACT, status
                ))
            generated = str(payload.get("generated_utc", "")).strip()
            if not generated:
                violations.append("{}: missing generated_utc in {}".format(
                    invariant_id, AUDITX_RUN_META_ARTIFACT
                ))

    return violations


def check_auditx_deterministic_contract(repo_root):
    invariant_id = "INV-AUDITX-DETERMINISM"
    checks = (
        ("tools/auditx/auditx.py", ("sort_findings(", "compute_fingerprint(", "build_analysis_graph(", "build_cache_context(")),
        ("tools/auditx/model/serialization.py", ("sort_keys=True", "sha256(")),
        ("tools/auditx/graph/analysis_graph.py", ("stable_hash(", "sort_keys=True")),
        ("tools/auditx/output/writers.py", ("sort_keys=True", "_build_invariant_map(", "_build_promotion_candidates(", "_build_trends(")),
        ("tools/auditx/canonicalize.py", ("canonical_json_string(", "canonicalize_json_payload(")),
        ("tools/auditx/cache_engine.py", ("build_cache_context(", "changed_paths_from_state(")),
    )

    violations = []
    for rel, tokens in checks:
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        text = read_text(path)
        if not text:
            violations.append("{}: missing file {}".format(invariant_id, rel))
            continue
        for token in tokens:
            if token not in text:
                violations.append("{}: missing deterministic token '{}' in {}".format(invariant_id, token, rel))
    return violations


def check_auditx_nonruntime_leak(repo_root):
    invariant_id = "INV-AUDITX-NONRUNTIME"
    roots = [
        os.path.join(repo_root, "engine"),
        os.path.join(repo_root, "game"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
        os.path.join(repo_root, "launcher"),
        os.path.join(repo_root, "setup"),
        os.path.join(repo_root, "libs"),
    ]
    violations = []
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path)
        text = read_text(path) or ""
        lowered = text.lower()
        if "tools/auditx" in lowered or "tools\\auditx" in lowered or "auditx.py" in lowered:
            violations.append(
                "{}: runtime source references AuditX implementation {}".format(invariant_id, rel)
            )
    return violations


def check_auditx_output_staleness(repo_root):
    invariant_id = "INV-AUDITX-OUTPUT-STALE"
    tracked = "docs/audit/auditx/FINDINGS.json"
    tracked_path = os.path.join(repo_root, tracked.replace("/", os.sep))
    if not os.path.isfile(tracked_path):
        return []

    latest_commit = run_git(["log", "-n", "1", "--format=%H", "--", tracked], repo_root)
    if not latest_commit:
        return ["{}: unable to locate git history for {}".format(invariant_id, tracked)]
    distance = run_git(["rev-list", "--count", "{}..HEAD".format(latest_commit)], repo_root)
    try:
        delta = int(distance or "0")
    except ValueError:
        return ["{}: invalid revision distance '{}'".format(invariant_id, distance)]
    if delta <= 30:
        return []
    return [
        "{}: audit outputs may be stale ({} commits since {})".format(
            invariant_id, delta, tracked
        )
    ]


def check_auditx_promotion_candidates(repo_root):
    invariant_id = "INV-AUDITX-PROMOTION-CANDIDATE-SHAPE"
    rel = "docs/audit/auditx/PROMOTION_CANDIDATES.json"
    path = os.path.join(repo_root, rel.replace("/", os.sep))
    if not os.path.isfile(path):
        return []

    payload = _load_json_file(path)
    if not isinstance(payload, dict):
        return ["{}: invalid json {}".format(invariant_id, rel)]
    if str(payload.get("artifact_class", "")).strip() != "CANONICAL":
        return ["{}: expected CANONICAL artifact_class in {}".format(invariant_id, rel)]
    rows = payload.get("candidates")
    if not isinstance(rows, list):
        return ["{}: candidates must be list in {}".format(invariant_id, rel)]

    violations = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append("{}: candidate {} must be object in {}".format(invariant_id, idx, rel))
            continue
        for key in ("rule_type", "rationale", "evidence_paths", "suggested_ruleset", "risk_score"):
            if key not in row:
                violations.append("{}: candidate {} missing key '{}' in {}".format(invariant_id, idx, key, rel))
        if row.get("auto_activate") is True:
            violations.append("{}: candidate {} sets forbidden auto_activate=true in {}".format(invariant_id, idx, rel))
        suggested_ruleset = normalize_path(str(row.get("suggested_ruleset", "")).strip())
        if suggested_ruleset and "/" not in suggested_ruleset:
            expected = normalize_path(os.path.join("repo", "repox", "rulesets", suggested_ruleset))
            if not os.path.isfile(os.path.join(repo_root, expected.replace("/", os.sep))):
                violations.append("{}: candidate {} references unknown ruleset '{}'".format(
                    invariant_id, idx, suggested_ruleset
                ))
    return violations


def check_auditx_promotion_policy_present(repo_root):
    invariant_id = "INV-AUDITX-PROMOTION-POLICY-PRESENT"
    if is_override_active(repo_root, invariant_id):
        return []

    rel = normalize_path(AUDITX_PROMOTION_POLICY_REL)
    path = os.path.join(repo_root, rel.replace("/", os.sep))
    if not os.path.isfile(path):
        return ["{}: missing {}".format(invariant_id, rel)]

    text = read_text(path) or ""
    header = parse_doc_header(text)
    if not header:
        return ["{}: missing doc status header in {}".format(invariant_id, rel)]
    if header.get("status") != "CANONICAL":
        return ["{}: expected CANONICAL status in {} (found {})".format(invariant_id, rel, header.get("status", ""))]

    required_tokens = (
        "AuditX -> RepoX Promotion Policy",
        "## Thresholds",
        "## Promotion Flow",
        "## Human Sign-Off Requirements",
        "## Invariant Retirement",
    )
    violations = []
    for token in required_tokens:
        if token not in text:
            violations.append("{}: missing section '{}' in {}".format(invariant_id, token, rel))
    return violations


def check_repo_health_snapshot_finalization(repo_root, changed_files):
    invariant_id = "INV-REPO-HEALTH-SNAPSHOT-FINALIZATION"
    if is_override_active(repo_root, invariant_id):
        return []

    normalized_changed = {normalize_path(str(item)) for item in (changed_files or []) if str(item).strip()}
    final_report_rel = normalize_path(GOVERNANCE_FINAL_REPORT_REL)
    if final_report_rel not in normalized_changed:
        return []

    snapshot_json_rel = normalize_path(REPO_HEALTH_SNAPSHOT_JSON_REL)
    snapshot_md_rel = normalize_path(REPO_HEALTH_SNAPSHOT_MD_REL)
    violations = []
    if snapshot_json_rel not in normalized_changed:
        violations.append("{}: governance final report update requires snapshot json update ({})".format(
            invariant_id, snapshot_json_rel
        ))
    if snapshot_md_rel not in normalized_changed:
        violations.append("{}: governance final report update requires snapshot markdown update ({})".format(
            invariant_id, snapshot_md_rel
        ))

    snapshot_json_path = os.path.join(repo_root, snapshot_json_rel.replace("/", os.sep))
    if not os.path.isfile(snapshot_json_path):
        violations.append("{}: missing {}".format(invariant_id, snapshot_json_rel))
        return violations
    payload = _load_json_file(snapshot_json_path)
    if not isinstance(payload, dict):
        violations.append("{}: invalid json {}".format(invariant_id, snapshot_json_rel))
        return violations
    if str(payload.get("artifact_class", "")).strip() != "CANONICAL":
        violations.append("{}: {} must declare artifact_class=CANONICAL".format(
            invariant_id, snapshot_json_rel
        ))
    if payload.get("git_status_clean") is not True:
        violations.append("{}: {} requires git_status_clean=true for finalization".format(
            invariant_id, snapshot_json_rel
        ))
    return violations


def _sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_merkle_roots(
    repo_root,
    subtrees=None,
    include_artifact_classes=None,
    exclude_artifact_classes=("RUN_META", "DERIVED_VIEW"),
    extra_excluded_prefixes=None,
):
    try:
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from tools.xstack.core.merkle_tree import compute_repo_state_hash
    except Exception:
        return {}
    payload = compute_repo_state_hash(
        repo_root,
        subtrees=list(subtrees) if subtrees else None,
        include_artifact_classes=tuple(include_artifact_classes) if include_artifact_classes else None,
        exclude_artifact_classes=tuple(exclude_artifact_classes) if exclude_artifact_classes else None,
        extra_excluded_prefixes=tuple(extra_excluded_prefixes) if extra_excluded_prefixes else None,
    )
    roots = payload.get("roots") or {}
    return roots if isinstance(roots, dict) else {}


def _impacted_roots(changed_files):
    impacted = set()
    for rel in changed_files:
        norm = normalize_path(rel).strip("/")
        if not norm:
            continue
        head = norm.split("/")[0].lower()
        if head in {"engine", "game", "client", "server", "tools", "schema", "data", "docs", "scripts", "repo", "tests"}:
            impacted.add(head)
            continue
        if head in {"cmake", ".github", "ci"}:
            impacted.add("scripts")
            continue
        impacted.add("repo")
    return impacted


def _repox_cache_path(repo_root, group_id, cache_key):
    root = os.path.join(repo_root, ".xstack_cache", "repox", normalize_path(group_id).replace("/", "_"))
    if not os.path.isdir(root):
        os.makedirs(root, exist_ok=True)
    return os.path.join(root, "{}.json".format(cache_key))


def _load_group_cache(repo_root, group_id, cache_key):
    path = _repox_cache_path(repo_root, group_id, cache_key)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _store_group_cache(repo_root, group_id, cache_key, payload):
    path = _repox_cache_path(repo_root, group_id, cache_key)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _group_dep_hash(roots, deps):
    rows = []
    for dep in sorted(set(str(item).strip().lower() for item in deps if str(item).strip())):
        row = roots.get(dep, {})
        rows.append("{}:{}".format(dep, str(row.get("hash", ""))))
    return _sha256_text("|".join(rows))


def _run_check_group(
    repo_root,
    group_id,
    scope_subtrees,
    artifact_classes,
    profile,
    impacted_roots,
    roots,
    checks,
):
    input_hash = _group_dep_hash(roots, scope_subtrees)
    cache_key = _sha256_text(json.dumps({"group_id": group_id, "input_hash": input_hash}, sort_keys=True))

    should_execute = True
    if profile in {"FAST", "STRICT"} and scope_subtrees:
        if not (set(dep.lower() for dep in scope_subtrees) & set(impacted_roots)):
            should_execute = False

    cached = _load_group_cache(repo_root, group_id, cache_key)
    if cached is not None:
        return {
            "group_id": group_id,
            "duration_ms": int(cached.get("duration_ms", 0)),
            "cache_hit": True,
            "dep_hash": input_hash,
            "scope_subtrees": list(scope_subtrees),
            "artifact_classes": list(artifact_classes),
            "violations": list(cached.get("violations") or []),
        }

    started = datetime.utcnow()
    violations = []
    for check in checks:
        rows = check()
        if rows:
            violations.extend(rows)
    duration_ms = int((datetime.utcnow() - started).total_seconds() * 1000.0)

    _store_group_cache(
        repo_root,
        group_id,
        cache_key,
        {
            "schema_version": "1.0.0",
            "group_id": group_id,
            "input_hash": input_hash,
            "scope_subtrees": list(scope_subtrees),
            "artifact_classes": list(artifact_classes),
            "duration_ms": duration_ms,
            "violations": list(violations),
        },
    )
    return {
        "group_id": group_id,
        "duration_ms": duration_ms,
        "cache_hit": False,
        "dep_hash": input_hash,
        "scope_subtrees": list(scope_subtrees),
        "artifact_classes": list(artifact_classes),
        "violations": violations,
    }


def _write_repox_profile(repo_root, profile, changed_files, impacted_roots, group_rows, total_ms):
    out_rel = normalize_path(REPOX_PROFILE_REL)
    out_path = os.path.join(repo_root, out_rel.replace("/", os.sep))
    parent = os.path.dirname(out_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    payload = {
        "artifact_class": "RUN_META",
        "status": "DERIVED",
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "profile": profile,
        "changed_files": sorted(set(changed_files)),
        "impacted_roots": sorted(set(impacted_roots)),
        "total_duration_ms": int(total_ms),
        "cache_hits": sum(1 for row in group_rows if row.get("cache_hit")),
        "cache_misses": sum(1 for row in group_rows if not row.get("cache_hit")),
        "groups": group_rows,
    }
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX governance rules enforcement.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--proof-manifest-out", default=PROOF_MANIFEST_DEFAULT)
    parser.add_argument("--profile", default="STRICT", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()
    if args.repo_root:
        repo_root = os.path.abspath(args.repo_root)
    else:
        repo_root = detect_repo_root(os.getcwd(), __file__)
    _canonicalize_tools_path(repo_root)

    started = datetime.utcnow()
    changed_files = get_changed_files(repo_root)
    impacted_roots = _impacted_roots(changed_files)
    roots = _load_merkle_roots(repo_root)
    allowed = load_allowed_top_level(repo_root)
    canon_index = load_canon_index(repo_root)

    groups = [
        {
            "group_id": "repox.structure.code",
            "scope_subtrees": ("engine", "game", "client", "server"),
            "artifact_classes": ("CANONICAL",),
            "checks": [
                lambda: check_authoritative_symbols(repo_root),
            ],
        },
        {
            "group_id": "repox.structure.schema",
            "scope_subtrees": ("schema", "data", "tests"),
            "artifact_classes": ("CANONICAL",),
            "checks": [
                lambda: check_failure_class_registry(repo_root),
            ],
        },
        {
            "group_id": "repox.structure.ruleset",
            "scope_subtrees": ("repo", "scripts"),
            "artifact_classes": ("CANONICAL",),
            "checks": [
                lambda: check_top_level(repo_root, allowed),
                lambda: check_archived_paths(repo_root),
                lambda: check_tool_name_only(repo_root),
                lambda: check_tools_dir_exists(repo_root),
                lambda: check_tool_unresolvable(repo_root),
                lambda: check_no_direct_gate_calls(repo_root),
            ],
        },
        {
            "group_id": "repox.docs.canon",
            "scope_subtrees": ("docs", "repo"),
            "artifact_classes": ("CANONICAL", "DERIVED_VIEW"),
            "checks": [
                lambda: check_canon_index_entries(repo_root, canon_index),
                lambda: check_canon_state(repo_root),
                lambda: check_doc_headers(repo_root, canon_index),
                lambda: check_doc_references(repo_root, canon_index),
                lambda: check_code_doc_references(repo_root, canon_index),
                lambda: check_glossary_term_canon(repo_root),
                lambda: check_auditx_promotion_policy_present(repo_root),
                lambda: check_frozen_contract_modifications(repo_root, changed_files),
                lambda: check_remediation_playbooks(repo_root),
                lambda: check_identity_fingerprint(repo_root),
                lambda: check_repo_health_snapshot_finalization(repo_root, changed_files),
                lambda: check_auditx_artifact_headers(repo_root),
                lambda: check_auditx_promotion_candidates(repo_root),
                lambda: check_auditx_output_staleness(repo_root),
            ],
        },
        {
            "group_id": "repox.schema.compat",
            "scope_subtrees": ("schema", "data", "docs"),
            "artifact_classes": ("CANONICAL", "DERIVED_VIEW"),
            "checks": [
                lambda: check_schema_version_bumps(repo_root),
                lambda: check_schema_migration_routes(repo_root),
                lambda: check_schema_no_implicit_defaults(repo_root),
                lambda: check_unversioned_schema_references(repo_root),
                lambda: check_compat_matrix_registry(repo_root),
                lambda: check_compat_migration_registry(repo_root),
                lambda: check_schema_version_policy_registry(repo_root),
                lambda: check_schema_deprecated_fields(repo_root),
                lambda: check_securex_trust_policy_registry(repo_root),
                lambda: check_securex_privilege_model(repo_root),
                lambda: check_unlocked_dependency(repo_root),
                lambda: check_tool_version_mismatch(repo_root),
                lambda: check_derived_artifact_contract(repo_root),
            ],
        },
        {
            "group_id": "repox.dist.platform",
            "scope_subtrees": ("data", "schema", "scripts", "dist"),
            "artifact_classes": ("CANONICAL", "DERIVED_VIEW"),
            "checks": [
                lambda: check_pkg_manifest_fields(repo_root),
                lambda: check_pkg_capability_metadata(repo_root),
                lambda: check_pkg_signature_policy(repo_root),
                lambda: check_dist_sys_shipping(repo_root),
                lambda: check_derived_pkg_index_freshness(repo_root),
                lambda: check_platform_registry(repo_root),
                lambda: check_platform_id_canonical(repo_root),
                lambda: check_dist_sys_derived(repo_root),
                lambda: check_product_graph_constraints(repo_root),
                lambda: check_mode_backend_registry(repo_root),
                lambda: check_mode_backend_selection_contract(repo_root),
                lambda: check_portable_run_contract(repo_root),
                lambda: check_build_preset_contract(repo_root),
                lambda: check_dist_release_lane_gate(repo_root),
            ],
        },
        {
            "group_id": "repox.runtime.policy",
            "scope_subtrees": ("client", "server", "engine", "game", "data", "schema"),
            "artifact_classes": ("CANONICAL",),
            "checks": [
                lambda: check_pack_capability_metadata(repo_root),
                lambda: check_prealpha_pack_isolation(repo_root),
                lambda: check_bugreport_resolution(repo_root),
                lambda: check_command_capability_metadata(repo_root),
                lambda: check_camera_blueprint_command_metadata(repo_root),
                lambda: check_ui_canonical_command_bindings(repo_root),
                lambda: check_observer_freecam_entitlement_gate(repo_root),
                lambda: check_runtime_command_capability_guards(repo_root),
                lambda: check_client_canonical_bridge(repo_root),
                lambda: check_settings_ownership_boundaries(repo_root),
                lambda: check_no_engine_settings(repo_root),
                lambda: check_no_hardcoded_mode_branch(repo_root),
                lambda: check_authority_context_required(repo_root),
                lambda: check_survival_no_nondiegetic_lenses(repo_root),
                lambda: check_survival_diegetic_contract(repo_root),
                lambda: check_authority_context_required_for_intents(repo_root),
                lambda: check_session_spec_required_for_run(repo_root),
                lambda: check_mode_as_profiles(repo_root),
                lambda: check_ui_entitlement_gating(repo_root),
                lambda: check_presentation_matrix_integrity(repo_root),
                lambda: check_defaults_optional(repo_root),
                lambda: check_renderer_no_truth_access(repo_root),
                lambda: check_capability_matrix_integrity(repo_root),
                lambda: check_solver_registry_contracts(repo_root),
                lambda: check_forbidden_legacy_gating_tokens(repo_root),
            ],
        },
        {
            "group_id": "repox.runtime.heavy_scans",
            "scope_subtrees": ("engine", "game", "client", "server", "tools", "schema", "data", "tests", "docs"),
            "artifact_classes": ("CANONICAL", "DERIVED_VIEW"),
            "checks": [
                lambda: check_forbidden_enum_tokens(repo_root),
                lambda: check_raw_paths(repo_root),
                lambda: check_magic_numbers(repo_root),
                lambda: check_data_first_behavior(repo_root),
                lambda: check_no_silent_defaults(repo_root),
                lambda: check_schema_anchor_required(repo_root),
                lambda: check_no_single_use_code_paths(repo_root),
                lambda: check_duplicate_logic_pressure(repo_root),
                lambda: check_new_feature_requires_data_first(repo_root),
                lambda: check_ambiguous_new_dirs(repo_root),
                lambda: check_root_module_shims(repo_root),
                lambda: check_universe_identity_immutability(repo_root),
                lambda: check_process_registry(repo_root),
                lambda: check_process_runtime_literals(repo_root),
                lambda: check_process_guard_runtime_contract(repo_root),
                lambda: check_process_registry_immutability(repo_root),
                lambda: check_compliance_report_canon(repo_root),
                lambda: check_auditx_deterministic_contract(repo_root),
                lambda: check_auditx_nonruntime_leak(repo_root),
            ],
        },
    ]

    profile = str(args.profile).strip().upper()
    group_rows = []
    violations = []
    scoped_roots_cache = {}
    for group in groups:
        group_id = str(group.get("group_id", "")).strip()
        scope_subtrees = tuple(group.get("scope_subtrees") or ())
        artifact_classes = tuple(group.get("artifact_classes") or ())
        checks = list(group.get("checks") or [])
        group_roots = roots
        if group_id.startswith("repox.structure."):
            cache_key = (
                tuple(sorted(scope_subtrees)),
                tuple(sorted(str(item).strip().upper() for item in artifact_classes if str(item).strip())),
                tuple(sorted(STRUCTURE_SCOPE_EXCLUDED_PREFIXES)),
            )
            if cache_key not in scoped_roots_cache:
                scoped_roots_cache[cache_key] = _load_merkle_roots(
                    repo_root,
                    subtrees=scope_subtrees,
                    include_artifact_classes=artifact_classes,
                    exclude_artifact_classes=("RUN_META", "DERIVED_VIEW"),
                    extra_excluded_prefixes=STRUCTURE_SCOPE_EXCLUDED_PREFIXES,
                )
            group_roots = scoped_roots_cache[cache_key]
        row = _run_check_group(
            repo_root=repo_root,
            group_id=group_id,
            scope_subtrees=scope_subtrees,
            artifact_classes=artifact_classes,
            profile=profile,
            impacted_roots=impacted_roots,
            roots=group_roots,
            checks=checks,
        )
        group_rows.append(
            {
                "group_id": row.get("group_id"),
                "duration_ms": int(row.get("duration_ms", 0)),
                "cache_hit": bool(row.get("cache_hit")),
                "dep_hash": str(row.get("dep_hash", "")),
                "scope_subtrees": sorted(set(str(item) for item in (row.get("scope_subtrees") or []) if str(item).strip())),
                "artifact_classes": sorted(set(str(item) for item in (row.get("artifact_classes") or []) if str(item).strip())),
                "violation_count": len(row.get("violations") or []),
            }
        )
        violations.extend(row.get("violations") or [])

    failures, warnings = _apply_ruleset_policy(repo_root, violations)
    write_proof_manifest(repo_root, args.proof_manifest_out, warnings, failures)
    total_ms = int((datetime.utcnow() - started).total_seconds() * 1000.0)
    _write_repox_profile(repo_root, profile, changed_files, impacted_roots, group_rows, total_ms)

    for item in warnings:
        print("WARN: {}".format(item))

    if failures:
        for item in failures:
            print(item)
        return 1

    print("RepoX governance rules OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

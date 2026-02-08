#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date

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
FORBIDDEN_STAGE_TOKEN_PARTS = (
    "S" + "TAGE_",
    "requires" + "_stage",
    "provides" + "_stage",
    "stage" + "_features",
    "required" + "_stage",
)
FORBIDDEN_STAGE_TOKEN_RE = re.compile(
    r"\b(" + "|".join(re.escape(token) for token in FORBIDDEN_STAGE_TOKEN_PARTS) + r")\b"
)
COMMAND_REGISTRY_REL = os.path.join("libs", "appcore", "command", "command_registry.c")
UI_BIND_TABLE_REL = os.path.join("libs", "appcore", "ui_bind", "ui_command_binding_table.c")
CAPABILITY_MATRIX_REL = os.path.join("tests", "testx", "CAPABILITY_MATRIX.yaml")
CAPABILITY_FIXTURE_ROOT = os.path.join("tests", "fixtures", "worlds")
CAPABILITY_TESTX_ROOT = os.path.join("tests", "testx", "stages")
CAPABILITY_REGRESSION_ROOT = os.path.join("tests", "testx", "stage_regression")
CAPABILITY_MATRIX_SUITE_NAMES = (
    "test_load_and_validate",
    "test_command_surface",
    "test_pack_gating",
    "test_epistemics",
    "test_determinism_smoke",
    "test_replay_hash",
)
CAPABILITY_SET_TO_DIR = {
    "CAPSET_WORLD_NONBIO": "stage_0_nonbio",
    "CAPSET_WORLD_LIFE_NONINTELLIGENT": "stage_1_nonintelligent_life",
    "CAPSET_WORLD_LIFE_INTELLIGENT": "stage_2_intelligent_pre_tool",
    "CAPSET_WORLD_PRETOOL": "stage_3_pre_tool_world",
    "CAPSET_SOCIETY_INSTITUTIONS": "stage_4_pre_industry",
    "CAPSET_INFRASTRUCTURE_INDUSTRY": "stage_5_pre_present",
    "CAPSET_FUTURE_AFFORDANCES": "stage_6_future",
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
    try:
        result = subprocess.run(
            ["git"] + args,
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
        path = line[3:].strip()
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
        expected_fixture = "tests/fixtures/worlds/{}/world_stage.json".format(capability_dir)
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
            "tests/testx/stages/{}/{}.py".format(capability_dir, suite_name)
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
                if name != "world_stage.json":
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
                rel = normalize_path(os.path.join("tests", "testx", "stage_regression", name))
                if name.endswith(".py") and rel not in [item.replace("\\", "/") for item in regression]:
                    violations.append("{}: regression test missing matrix entry: {}".format(invariant_id, rel))

    return violations


def check_forbidden_stage_tokens(repo_root):
    invariant_id = "INV-CAPABILITY-NO-STAGE-TOKENS"
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
                if FORBIDDEN_STAGE_TOKEN_RE.search(line):
                    violations.append("{}: forbidden token in {}:{}".format(invariant_id, rel, idx))
                    break
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
        os.path.join(repo_root, "engine", "modules", "world"),
        os.path.join(repo_root, "game", "rules"),
    ]
    violations = []
    for path in iter_files(roots, DEFAULT_EXCLUDES, SOURCE_EXTS):
        rel = repo_rel(repo_root, path)
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


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX governance rules enforcement.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []
    allowed = load_allowed_top_level(repo_root)
    violations.extend(check_top_level(repo_root, allowed))
    violations.extend(check_archived_paths(repo_root))

    changed_files = get_changed_files(repo_root)
    violations.extend(check_frozen_contract_modifications(repo_root, changed_files))

    violations.extend(check_authoritative_symbols(repo_root))
    violations.extend(check_forbidden_enum_tokens(repo_root))
    violations.extend(check_raw_paths(repo_root))
    violations.extend(check_magic_numbers(repo_root))
    violations.extend(check_ambiguous_new_dirs(repo_root))
    canon_index = load_canon_index(repo_root)
    violations.extend(check_canon_index_entries(repo_root, canon_index))
    violations.extend(check_canon_state(repo_root))
    violations.extend(check_doc_headers(repo_root, canon_index))
    violations.extend(check_doc_references(repo_root, canon_index))
    violations.extend(check_code_doc_references(repo_root, canon_index))
    violations.extend(check_schema_version_bumps(repo_root))
    violations.extend(check_schema_migration_routes(repo_root))
    violations.extend(check_schema_no_implicit_defaults(repo_root))
    violations.extend(check_unversioned_schema_references(repo_root))
    violations.extend(check_pack_capability_metadata(repo_root))
    violations.extend(check_command_capability_metadata(repo_root))
    violations.extend(check_ui_canonical_command_bindings(repo_root))
    violations.extend(check_capability_matrix_integrity(repo_root))
    violations.extend(check_forbidden_stage_tokens(repo_root))
    violations.extend(check_process_registry(repo_root))
    violations.extend(check_process_runtime_literals(repo_root))
    violations.extend(check_process_registry_immutability(repo_root))
    violations.extend(check_compliance_report_canon(repo_root))

    if violations:
        for item in sorted(set(violations)):
            print(item)
        return 1

    print("RepoX governance rules OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

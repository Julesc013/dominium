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


def run_arch_audit(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    check_order = [
        "truth_purity_scan",
        "renderer_truth_access_scan",
        "duplicate_semantics_scan",
        "determinism_scan",
        "float_in_truth_scan",
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
    "scan_archive_determinism",
    "scan_contract_pins",
    "scan_compiler_flags",
    "scan_dist_bundle_composition",
    "scan_determinism",
    "scan_duplicate_semantics",
    "scan_float_in_truth",
    "scan_noncanonical_numeric_serialization",
    "scan_pack_compat",
    "scan_parallel_output_canonicalization",
    "scan_parallel_truth",
    "scan_renderer_truth_access",
    "scan_stability_markers",
    "scan_target_matrix",
    "scan_trust_bypass",
    "scan_truth_atomic_usage",
    "scan_truth_purity",
    "scan_update_model",
    "write_arch_audit_outputs",
]

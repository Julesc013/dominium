"""Deterministic ARCH-AUDIT-0 report helpers."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.stability import validate_all_registries, validate_pack_compat  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


ARCH_AUDIT_ID = "arch.audit.v1"
DEFAULT_REPORT_MD_REL = os.path.join("docs", "audit", "ARCH_AUDIT_REPORT.md")
DEFAULT_REPORT_JSON_REL = os.path.join("data", "audit", "arch_audit_report.json")
DEFAULT_BASELINE_DOC_REL = os.path.join("docs", "audit", "ARCH_AUDIT_BASELINE.md")

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
) -> dict:
    return {
        "category": str(category).strip(),
        "classification": str(classification).strip() or "blocking",
        "severity": str(severity).strip() or "RISK",
        "path": _norm(path),
        "line": int(line or 0),
        "message": str(message).strip(),
        "snippet": str(snippet or "").strip()[:200],
    }


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


def run_arch_audit(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    check_order = [
        "truth_purity_scan",
        "renderer_truth_access_scan",
        "duplicate_semantics_scan",
        "determinism_scan",
        "stability_marker_scan",
        "contract_pin_scan",
        "pack_compat_scan",
    ]
    checks = {
        "truth_purity_scan": scan_truth_purity(repo_root_abs),
        "renderer_truth_access_scan": scan_renderer_truth_access(repo_root_abs),
        "duplicate_semantics_scan": scan_duplicate_semantics(repo_root_abs),
        "determinism_scan": scan_determinism(repo_root_abs),
        "stability_marker_scan": scan_stability_markers(repo_root_abs),
        "contract_pin_scan": scan_contract_pins(repo_root_abs),
        "pack_compat_scan": scan_pack_compat(repo_root_abs),
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


def write_arch_audit_outputs(
    repo_root: str,
    *,
    report: Mapping[str, object],
    report_path: str = DEFAULT_REPORT_MD_REL,
    json_path: str = DEFAULT_REPORT_JSON_REL,
    baseline_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    written = {
        "report_path": _write_text(_repo_abs(repo_root_abs, report_path), render_arch_audit_report(report)),
        "json_path": _write_canonical_json(_repo_abs(repo_root_abs, json_path), report),
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
    "DEFAULT_BASELINE_DOC_REL",
    "DEFAULT_REPORT_JSON_REL",
    "DEFAULT_REPORT_MD_REL",
    "load_json_if_present",
    "load_or_run_arch_audit_report",
    "render_arch_audit_baseline",
    "render_arch_audit_report",
    "run_arch_audit",
    "scan_contract_pins",
    "scan_determinism",
    "scan_duplicate_semantics",
    "scan_pack_compat",
    "scan_renderer_truth_access",
    "scan_stability_markers",
    "scan_truth_purity",
    "write_arch_audit_outputs",
]

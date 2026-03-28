"""Deterministic XI-5a-v4 dangerous-shadow execution helpers."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402

install_src_aliases(REPO_ROOT_HINT)


from tools.review.xi4z_fix1_common import _has_source_like_segment  # noqa: E402
from tools.review.xi4z_fix3_common import (  # noqa: E402
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
    XI5_READINESS_CONTRACT_V4_REL,
    XI_4Z_FIX3_FINAL_REL,
    XI_5A_EXECUTION_INPUTS_REL,
    _ensure_parent,
    _norm_rel,
    _repo_abs,
    _repo_root,
    _token,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL = "data/restructure/src_domain_mapping_target_paths_v4.json"
SRC_DOMAIN_MAPPING_ATTIC_APPROVED_REL = "data/restructure/src_domain_mapping_attic_approved.json"
SRC_DOMAIN_MAPPING_DEFERRED_REL = "data/restructure/src_domain_mapping_deferred.json"
ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
MODULE_REGISTRY_REL = "data/architecture/module_registry.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"
INCLUDE_GRAPH_REL = "data/audit/include_graph.json"
SYMBOL_INDEX_REL = "data/audit/symbol_index.json"
XI_4_FINAL_REL = "docs/audit/XI_4_FINAL.md"
XI_4B_FINAL_REL = "docs/audit/XI_4B_FINAL.md"
XI_4Z_FINAL_REL = "docs/audit/XI_4Z_FINAL.md"
XI_4Z_FIX_FINAL_REL = "docs/audit/XI_4Z_FIX_FINAL.md"
DEPRECATIONS_REL = "docs/refactor/DEPRECATIONS.md"

XI5A_MOVE_MAP_REL = "data/restructure/xi5a_move_map.json"
XI5A_ATTIC_MAP_REL = "data/restructure/xi5a_attic_map.json"
XI5A_EXECUTION_LOG_REL = "data/restructure/xi5a_execution_log.json"
XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL = "data/restructure/xi5a_postmove_residual_src_report.json"
XI_5A_MOVE_PLAN_REL = "docs/restructure/XI_5A_MOVE_PLAN.md"
XI_5A_EXECUTION_LOG_DOC_REL = "docs/restructure/XI_5A_EXECUTION_LOG.md"
XI_5A_POSTMOVE_REPORT_REL = "docs/restructure/XI_5A_POSTMOVE_REPORT.md"
XI_5A_ATTIC_REPORT_REL = "docs/restructure/XI_5A_ATTIC_REPORT.md"
XI_5A_FINAL_REL = "docs/audit/XI_5A_FINAL.md"
XI5A_PREFLIGHT_REPAIR_REL = "data/audit/xi5a_preflight_repair.json"

TEMP_ROOT_REL = "build/tmp/xi5a_v4"
PROGRESS_LOG_REL = TEMP_ROOT_REL + "/progress.json"
DANGEROUS_ROOTS = ("app/src", "src")
TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".cmake",
    ".cmd",
    ".cpp",
    ".cs",
    ".h",
    ".hh",
    ".hpp",
    ".ini",
    ".json",
    ".md",
    ".props",
    ".ps1",
    ".py",
    ".pyi",
    ".rst",
    ".sln",
    ".sh",
    ".targets",
    ".toml",
    ".txt",
    ".vcxproj",
    ".xml",
    ".yaml",
    ".yml",
}
TEXT_FILENAMES = {"CMakeLists.txt", "meson.build", "SConstruct"}
PREVIEW_TOKENS = ('"src"', "'src'", "src.", "src/")
EXCLUDED_TOP_LEVEL_DIRS = {
    ".git",
    ".venv",
    ".xstack_cache",
    "attic",
    "build",
    "dist",
    "external",
    "out",
    "tmp",
}
EXCLUDED_PREFIXES = (
    "data/analysis/",
    "data/audit/",
    "data/blueprint/",
    "data/regression/",
    "data/refactor/",
    "data/restructure/",
    "docs/archive/",
    "docs/audit/",
    "docs/blueprint/",
    "docs/guides/",
    "docs/refactor/",
    "docs/restructure/",
    "tmp_",
)
GATE_MUTABLE_PREFIXES = (
    "data/audit/",
    "data/baselines/",
    "data/regression/",
    "docs/audit/",
)


class Xi5aV4InputsMissing(RuntimeError):
    """Raised when the XI-5a-v4 execution inputs are missing."""


class Xi5aV4ExecutionFailure(RuntimeError):
    """Raised when XI-5a-v4 cannot complete safely."""

    def __init__(self, code: str, details: Mapping[str, object]):
        super().__init__(code)
        self.code = str(code or "").strip()
        self.details = dict(details or {})


def _read_json_required(repo_root: str, rel_path: str) -> dict[str, object]:
    abs_path = _repo_abs(repo_root, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        payload = None
    if not isinstance(payload, dict) or not payload:
        raise Xi5aV4InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi5a.missing_v2_lock",
                    "missing_inputs": [rel_path],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return payload


def _required_input_paths() -> tuple[str, ...]:
    return (
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
        XI5_READINESS_CONTRACT_V4_REL,
        SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL,
        SRC_DOMAIN_MAPPING_ATTIC_APPROVED_REL,
        SRC_DOMAIN_MAPPING_DEFERRED_REL,
        XI_5A_EXECUTION_INPUTS_REL,
        "docs/restructure/XI_4Z_TARGET_NORMALIZATION_REPORT.md",
        "docs/restructure/XI_4Z_XI5_READINESS.md",
        XI_4Z_FIX3_FINAL_REL,
        ARCHITECTURE_GRAPH_REL,
        MODULE_REGISTRY_REL,
        BUILD_GRAPH_REL,
        INCLUDE_GRAPH_REL,
        SYMBOL_INDEX_REL,
        XI_4_FINAL_REL,
        XI_4B_FINAL_REL,
        XI_4Z_FINAL_REL,
        XI_4Z_FIX_FINAL_REL,
        DEPRECATIONS_REL,
        "data/audit/validation_report_FAST.json",
        "data/audit/validation_report_STRICT.json",
    )


def _ensure_inputs(repo_root: str) -> None:
    missing = []
    for rel_path in _required_input_paths():
        if not os.path.exists(_repo_abs(repo_root, rel_path)):
            missing.append(rel_path)
    if missing:
        raise Xi5aV4InputsMissing(
            json.dumps(
                {
                    "code": "refusal.xi5a.missing_v2_lock",
                    "missing_inputs": sorted(set(missing)),
                },
                indent=2,
                sort_keys=True,
            )
        )


def _load_validation_report(repo_root: str, rel_path: str) -> dict[str, object]:
    return _read_json_required(repo_root, rel_path)


def _python_env(repo_root: str) -> dict[str, str]:
    env = os.environ.copy()
    import_roots = [repo_root]
    existing_pythonpath = str(env.get("PYTHONPATH") or "").strip()
    if existing_pythonpath:
        import_roots.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(import_roots)
    return env


def _ensure_preflight_green(repo_root: str) -> dict[str, str]:
    for profile in ("FAST", "STRICT"):
        subprocess.run(
            ["python", "tools/validation/tool_run_validation.py", "--repo-root", ".", "--profile", profile],
            cwd=repo_root,
            env=_python_env(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    fast = _load_validation_report(repo_root, "data/audit/validation_report_FAST.json")
    strict = _load_validation_report(repo_root, "data/audit/validation_report_STRICT.json")
    if _token(fast.get("result")) != "complete" or _token(strict.get("result")) != "complete":
        raise Xi5aV4ExecutionFailure(
            "refusal.xi5a.baseline_gates_red",
            {
                "fast_result": _token(fast.get("result")),
                "strict_result": _token(strict.get("result")),
            },
        )
    return {
        "FAST": _token(fast.get("deterministic_fingerprint")),
        "STRICT": _token(strict.get("deterministic_fingerprint")),
    }


def _load_resume_preflight_hashes(repo_root: str) -> dict[str, str]:
    try:
        payload = _read_json_required(repo_root, XI5A_PREFLIGHT_REPAIR_REL)
    except Xi5aV4InputsMissing:
        payload = {}
    after = dict(payload.get("after") or {})
    fast = _token(dict(after.get("fast") or {}).get("validation_fingerprint"))
    strict = _token(dict(after.get("strict") or {}).get("validation_fingerprint"))
    if fast and strict:
        return {"FAST": fast, "STRICT": strict}
    return {"FAST": "resume_from_partial_batch", "STRICT": "resume_from_partial_batch"}


def _load_execution_inputs(repo_root: str) -> dict[str, object]:
    _ensure_inputs(repo_root)
    return {
        "lock": _read_json_required(repo_root, SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL),
        "readiness": _read_json_required(repo_root, XI5_READINESS_CONTRACT_V4_REL),
        "target_paths": _read_json_required(repo_root, SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL),
    }


def _has_partial_batch_application(repo_root: str, rows: Iterable[Mapping[str, object]]) -> bool:
    for row in rows:
        source_abs = _repo_abs(repo_root, _source_path(row))
        target_abs = _repo_abs(repo_root, _target_path(row))
        if not os.path.exists(source_abs) and os.path.exists(target_abs):
            return True
    return False


def _source_path(row: Mapping[str, object]) -> str:
    return _norm_rel(row.get("source_path") or row.get("file_path"))


def _target_path(row: Mapping[str, object]) -> str:
    return _norm_rel(row.get("target_path"))


def _is_non_bytecode_runtime_file(rel_path: str) -> bool:
    norm = _norm_rel(rel_path)
    if not norm:
        return False
    parts = [part for part in norm.split("/") if part]
    if "__pycache__" in parts:
        return False
    if norm.endswith(".pyc") or norm.endswith(".pyo"):
        return False
    return any(norm.startswith(root + "/") or norm == root for root in DANGEROUS_ROOTS)


def _scan_dangerous_roots(repo_root: str) -> list[str]:
    rows: list[str] = []
    for root_rel in DANGEROUS_ROOTS:
        root_abs = _repo_abs(repo_root, root_rel)
        if not os.path.isdir(root_abs):
            continue
        for current_root, dirnames, filenames in os.walk(root_abs):
            dirnames[:] = [name for name in sorted(dirnames) if name != "__pycache__"]
            rel_root = _norm_rel(os.path.relpath(current_root, repo_root))
            if rel_root == ".":
                rel_root = ""
            for filename in sorted(filenames):
                rel_path = _norm_rel(os.path.join(rel_root, filename))
                if _is_non_bytecode_runtime_file(rel_path):
                    rows.append(rel_path)
    return sorted(set(rows))


def _surprise_detection(repo_root: str, lock_payload: Mapping[str, object]) -> dict[str, list[str]]:
    approved = {_source_path(row) for row in list(lock_payload.get("approved_for_xi5") or [])}
    attic = {_source_path(row) for row in list(lock_payload.get("approved_to_attic") or [])}
    deferred = {_source_path(row) for row in list(lock_payload.get("deferred_to_xi5b") or [])}
    live = _scan_dangerous_roots(repo_root)
    unexpected = [path for path in live if path not in approved and path not in attic and path not in deferred]
    return {
        "approved": sorted(approved),
        "attic": sorted(attic),
        "deferred": sorted(deferred),
        "live": live,
        "unexpected": unexpected,
    }


def _python_module_name(rel_path: str) -> str:
    norm = _norm_rel(rel_path)
    if not norm.endswith(".py"):
        return ""
    token = norm[:-3].replace("/", ".")
    if token.endswith(".__init__"):
        token = token[: -len(".__init__")]
    return token


def _build_replacement_maps(rows: Iterable[Mapping[str, object]]) -> dict[str, list[tuple[str, str]]]:
    path_map: dict[str, str] = {}
    dotted_map: dict[str, str] = {}
    segment_patterns: dict[str, tuple[str, ...]] = {}
    for row in rows:
        source_path = _source_path(row)
        target_path = _target_path(row)
        if not source_path or not target_path:
            continue
        path_map[source_path] = target_path
        source_parts = tuple(part for part in source_path.split("/") if part)
        target_parts = tuple(part for part in target_path.split("/") if part)
        if source_parts and target_parts:
            pattern_chunks = []
            for index, part in enumerate(source_parts):
                if index == 0:
                    pattern_chunks.append(r"(?P<q>[\"'])" + re.escape(part) + r"(?P=q)")
                else:
                    pattern_chunks.append(r"(?P=q)" + re.escape(part) + r"(?P=q)")
            segment_patterns[r"\s*,\s*".join(pattern_chunks)] = target_parts
        if "/src/" in source_path:
            prefix, source_tail = source_path.split("/src/", 1)
            if prefix and target_path.startswith(prefix + "/"):
                target_tail = target_path[len(prefix) + 1 :]
                path_map.setdefault("src/" + source_tail, target_tail)
        old_module = _python_module_name(source_path)
        new_module = _python_module_name(target_path)
        if old_module and new_module:
            if old_module != "src" and new_module != "__init__":
                dotted_map[old_module] = new_module
            if source_path.startswith("src/"):
                source_parts = source_path[len("src/") : -3].split("/")[:-1]
                target_parts = target_path[:-3].split("/")[:-1]
                if source_parts:
                    offset = len(target_parts) - len(source_parts)
                    for depth in range(1, len(source_parts) + 1):
                        old_pkg = "src." + ".".join(source_parts[:depth])
                        span = depth + offset
                        if span <= 0 or span > len(target_parts):
                            continue
                        new_pkg = ".".join(target_parts[:span])
                        if old_pkg and new_pkg:
                            dotted_map.setdefault(old_pkg, new_pkg)
    path_rows = sorted(path_map.items(), key=lambda item: (-len(item[0]), item[0], item[1]))
    dotted_rows = sorted(dotted_map.items(), key=lambda item: (-len(item[0]), item[0], item[1]))
    segment_rows = [
        {
            "pattern": pattern,
            "replacement_parts": list(parts),
        }
        for pattern, parts in sorted(segment_patterns.items(), key=lambda item: (-len(item[0]), item[0], item[1]))
    ]
    return {"path": path_rows, "dotted": dotted_rows, "segment_literal": segment_rows}


def _is_text_candidate(rel_path: str) -> bool:
    norm = _norm_rel(rel_path)
    if not norm:
        return False
    if any(norm.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    top = norm.split("/", 1)[0]
    if top in EXCLUDED_TOP_LEVEL_DIRS:
        return False
    parts = [part for part in norm.split("/") if part]
    if "__pycache__" in parts:
        return False
    filename = parts[-1]
    if filename in TEXT_FILENAMES:
        return True
    return os.path.splitext(filename)[1].lower() in TEXT_EXTENSIONS


def _iter_text_files(repo_root: str) -> list[str]:
    rows: list[str] = []
    for current_root, dirnames, filenames in os.walk(repo_root):
        rel_root = _norm_rel(os.path.relpath(current_root, repo_root))
        if rel_root == ".":
            rel_root = ""
        parts = [part for part in rel_root.split("/") if part and part != "."]
        if parts and parts[0] in EXCLUDED_TOP_LEVEL_DIRS:
            dirnames[:] = []
            continue
        if not parts:
            dirnames[:] = [name for name in sorted(dirnames) if name not in EXCLUDED_TOP_LEVEL_DIRS and name != "__pycache__"]
        else:
            dirnames[:] = [name for name in sorted(dirnames) if name != "__pycache__"]
        for filename in sorted(filenames):
            rel_path = _norm_rel(os.path.join(rel_root, filename))
            if _is_text_candidate(rel_path):
                rows.append(rel_path)
    return sorted(set(rows))


def _read_text(rel_path: str, repo_root: str) -> str | None:
    abs_path = _repo_abs(repo_root, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return handle.read()
    except UnicodeDecodeError:
        return None
    except OSError:
        return None


def _apply_replacements(text: str, replacements: Mapping[str, list[tuple[str, str]]]) -> str:
    updated = text
    for old, new in replacements.get("path", []):
        if old:
            updated = updated.replace(old, new)
    for old, new in replacements.get("dotted", []):
        if old:
            updated = updated.replace(old, new)
    for row in list(replacements.get("segment_literal") or []):
        item = dict(row or {})
        pattern = _token(item.get("pattern"))
        replacement_parts = [str(part) for part in list(item.get("replacement_parts") or []) if _token(part)]
        if not pattern or not replacement_parts:
            continue
        updated = re.sub(
            pattern,
            lambda match: ", ".join(f"{match.group('q')}{part}{match.group('q')}" for part in replacement_parts),
            updated,
        )
    return updated


def _contains_preview_token(text: str) -> bool:
    for token in PREVIEW_TOKENS:
        if token in text:
            return True
    return False


def _preview_text_updates(repo_root: str, replacements: Mapping[str, list[tuple[str, str]]]) -> dict[str, str]:
    changes: dict[str, str] = {}
    for rel_path in _iter_text_files(repo_root):
        original = _read_text(rel_path, repo_root)
        if original is None:
            continue
        if not _contains_preview_token(original):
            continue
        updated = _apply_replacements(original, replacements)
        if updated != original:
            changes[rel_path] = updated
    return changes


def _backup_paths(repo_root: str, backup_root: str, rel_paths: Iterable[str]) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []
    for rel_path in sorted({_norm_rel(path) for path in rel_paths if _token(path)}):
        abs_path = _repo_abs(repo_root, rel_path)
        backup_path = _repo_abs(backup_root, rel_path)
        exists_before = os.path.exists(abs_path)
        manifest.append(
            {
                "backup_path": _norm_rel(os.path.relpath(backup_path, backup_root)),
                "exists_before": bool(exists_before),
                "path": rel_path,
            }
        )
        if exists_before and os.path.isfile(abs_path):
            _ensure_parent(backup_path)
            shutil.copy2(abs_path, backup_path)
    return manifest


def _gate_mutable_paths(repo_root: str) -> list[str]:
    rows: list[str] = []
    for prefix in GATE_MUTABLE_PREFIXES:
        root_abs = _repo_abs(repo_root, prefix)
        if not os.path.isdir(root_abs):
            continue
        for current_root, _, filenames in os.walk(root_abs):
            rel_root = _norm_rel(os.path.relpath(current_root, repo_root))
            for filename in sorted(filenames):
                rows.append(_norm_rel(os.path.join(rel_root, filename)))
    return sorted(set(rows))


def _remove_file_or_tree(path: str) -> None:
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def _prune_empty_parents(repo_root: str, rel_path: str) -> None:
    current = os.path.dirname(_repo_abs(repo_root, rel_path))
    repo_root_abs = _repo_root(repo_root)
    while current and current != repo_root_abs:
        try:
            os.rmdir(current)
        except OSError:
            break
        current = os.path.dirname(current)


def _restore_from_backup(repo_root: str, backup_root: str, manifest: Iterable[Mapping[str, object]]) -> None:
    for row in sorted((dict(item or {}) for item in manifest), key=lambda item: item.get("path", ""), reverse=True):
        rel_path = _norm_rel(row.get("path"))
        exists_before = bool(row.get("exists_before"))
        abs_path = _repo_abs(repo_root, rel_path)
        backup_path = os.path.normpath(os.path.join(backup_root, _norm_rel(row.get("backup_path")).replace("/", os.sep)))
        if exists_before and os.path.isfile(backup_path):
            _ensure_parent(abs_path)
            shutil.copy2(backup_path, abs_path)
        elif not exists_before:
            _remove_file_or_tree(abs_path)
            _prune_empty_parents(repo_root, rel_path)


def _safe_move(repo_root: str, source_path: str, target_path: str) -> None:
    source_abs = _repo_abs(repo_root, source_path)
    target_abs = _repo_abs(repo_root, target_path)
    _ensure_parent(target_abs)
    result = subprocess.run(
        ["git", "mv", "--", source_path, target_path],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(result.returncode) == 0:
        return
    shutil.move(source_abs, target_abs)


def _write_text(abs_path: str, text: str) -> None:
    _ensure_parent(abs_path)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\r\n", "\n"))


def _cleanup_bytecode(repo_root: str, roots: Iterable[str]) -> None:
    for root_rel in sorted({_norm_rel(path) for path in roots if _token(path)}):
        root_abs = _repo_abs(repo_root, root_rel)
        if not os.path.exists(root_abs):
            continue
        for current_root, dirnames, filenames in os.walk(root_abs, topdown=False):
            for filename in filenames:
                if filename.endswith((".pyc", ".pyo")):
                    _remove_file_or_tree(os.path.join(current_root, filename))
            for dirname in dirnames:
                if dirname == "__pycache__":
                    _remove_file_or_tree(os.path.join(current_root, dirname))


def _reconcile_git_after_restore(repo_root: str, source_paths: Iterable[str], target_paths: Iterable[str]) -> None:
    normalized_sources = sorted({_norm_rel(path) for path in source_paths if _token(path)})
    normalized_targets = sorted({_norm_rel(path) for path in target_paths if _token(path)})
    batch_size = 128
    for start in range(0, len(normalized_targets), batch_size):
        batch = normalized_targets[start : start + batch_size]
        subprocess.run(
            ["git", "rm", "--cached", "--ignore-unmatch", "--quiet", "--", *batch],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    existing_sources = [path for path in normalized_sources if os.path.exists(_repo_abs(repo_root, path))]
    for start in range(0, len(existing_sources), batch_size):
        batch = existing_sources[start : start + batch_size]
        subprocess.run(
            ["git", "add", "--", *batch],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )


def _run_gate(repo_root: str, command: list[str], gate_id: str) -> dict[str, object]:
    started = time.time()
    result = subprocess.run(
        command,
        cwd=repo_root,
        env=_python_env(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    elapsed_ms = int(round((time.time() - started) * 1000.0))
    output = str(result.stdout or "")
    lines = [line for line in output.replace("\r\n", "\n").splitlines() if line.strip()]
    payload = {
        "command": command,
        "duration_ms": elapsed_ms,
        "gate_id": gate_id,
        "output_excerpt": lines[-20:],
        "returncode": int(result.returncode),
        "status": "pass" if int(result.returncode) == 0 else "fail",
    }
    if payload["status"] != "pass" and gate_id in {"validate_fast", "validate_strict"}:
        profile = "FAST" if gate_id.endswith("fast") else "STRICT"
        report_rel = f"data/audit/validation_report_{profile}.json"
        report_abs = _repo_abs(repo_root, report_rel)
        if os.path.isfile(report_abs):
            try:
                with open(report_abs, "r", encoding="utf-8") as handle:
                    report_payload = json.load(handle)
            except (OSError, ValueError):
                report_payload = {}
            if isinstance(report_payload, dict):
                payload["validation_error_excerpt"] = list(report_payload.get("errors") or [])[:25]
                payload["validation_suite_excerpt"] = list(report_payload.get("suite_results") or [])[:20]
    return payload


def _gate_plan() -> list[tuple[str, list[str]]]:
    return [
        ("build_verify", ["cmake", "--build", "--preset", "verify", "--config", "Debug", "--target", "all_runtime"]),
        ("validate_fast", ["python", "tools/validation/tool_run_validation.py", "--repo-root", ".", "--profile", "FAST"]),
        ("validate_strict", ["python", "tools/validation/tool_run_validation.py", "--repo-root", ".", "--profile", "STRICT"]),
        ("arch_audit_2", ["python", "tools/audit/tool_run_arch_audit.py", "--repo-root", "."]),
        ("omega_1_worldgen_lock", ["python", "tools/worldgen/tool_verify_worldgen_lock.py", "--repo-root", "."]),
        ("omega_2_baseline_universe", ["python", "tools/mvp/tool_verify_baseline_universe.py", "--repo-root", "."]),
        ("omega_3_gameplay_loop", ["python", "tools/mvp/tool_verify_gameplay_loop.py", "--repo-root", "."]),
        ("omega_4_disaster_suite", ["python", "tools/mvp/tool_run_disaster_suite.py", "--repo-root", "."]),
        ("omega_5_ecosystem_verify", ["python", "tools/mvp/tool_verify_ecosystem.py", "--repo-root", "."]),
        ("omega_6_update_sim", ["python", "tools/mvp/tool_run_update_sim.py", "--repo-root", "."]),
        ("trust_strict_suite", ["python", "tools/security/tool_run_trust_strict_suite.py", "--repo-root", "."]),
    ]


def _batch_rows(lock_payload: Mapping[str, object]) -> list[dict[str, object]]:
    rows = [dict(item or {}) for item in list(lock_payload.get("approved_for_xi5") or [])]
    return sorted(rows, key=lambda item: (_source_path(item), _target_path(item)))


def _build_move_map(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    move_rows = []
    for row in rows:
        payload = {
            "from": _source_path(row),
            "to": _target_path(row),
            "module_id": _token(row.get("approved_module_id")),
            "reason": "approved_for_xi5",
            "decision_provenance": dict(row.get("decision_provenance") or {}),
            "category": _token(row.get("category")),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        move_rows.append(payload)
    doc = {
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
        "readiness_contract_path": XI5_READINESS_CONTRACT_V4_REL,
        "report_id": "xi.5a.move_map.v4",
        "rows": move_rows,
        "deterministic_fingerprint": "",
    }
    doc["deterministic_fingerprint"] = canonical_sha256(dict(doc, deterministic_fingerprint=""))
    return doc


def _build_empty_attic_map() -> dict[str, object]:
    payload = {
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
        "readiness_contract_path": XI5_READINESS_CONTRACT_V4_REL,
        "report_id": "xi.5a.attic_map.v4",
        "rows": [],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _residual_report(repo_root: str, lock_payload: Mapping[str, object]) -> dict[str, object]:
    deferred_rows = []
    for row in list(lock_payload.get("deferred_to_xi5b") or []):
        source_path = _source_path(row)
        if source_path and os.path.exists(_repo_abs(repo_root, source_path)):
            deferred_rows.append(
                {
                    "deferred_phase_class": _token(row.get("deferred_phase_class")),
                    "reason": _token(row.get("reason")),
                    "source_path": source_path,
                    "target_path": _target_path(row),
                }
            )
    live = _scan_dangerous_roots(repo_root)
    deferred_paths = {_token(row.get("source_path")) for row in deferred_rows}
    unexpected = [path for path in live if path not in deferred_paths]
    payload = {
        "dangerous_shadow_roots": list(DANGEROUS_ROOTS),
        "deferred_to_xi5b_remaining": sorted(deferred_rows, key=lambda row: row["source_path"]),
        "deterministic_fingerprint": "",
        "report_id": "xi.5a.postmove_residual_src_report.v4",
        "unexpected_remaining_src_paths": unexpected,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _render_move_plan(move_map: Mapping[str, object], residual_report: Mapping[str, object]) -> str:
    rows = list(move_map.get("rows") or [])
    deferred_rows = list(residual_report.get("deferred_to_xi5b_remaining") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a execution log and final audit report",
        "",
        "# XI-5A Move Plan",
        "",
        f"- approved lock: `{SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL}`",
        f"- readiness contract: `{XI5_READINESS_CONTRACT_V4_REL}`",
        "- batching model: single deterministic dangerous-shadow batch",
        "  reason: the approved Python move surface has cross-package import coupling, so partial category batches would introduce transient import breakage unrelated to the approved lock.",
        f"- approved moves in this pass: `{len(rows)}`",
        f"- approved attic routes in this pass: `0`",
        f"- deferred rows left untouched: `{len(deferred_rows)}`",
    ]
    if deferred_rows:
        lines.append("")
        lines.append("## Deferred Dangerous-Root Residuals")
        for row in deferred_rows:
            if row.get("source_path", "").startswith("src/") or row.get("source_path", "").startswith("app/src/"):
                lines.append(
                    f"- `{row.get('source_path')}` remains deferred because `{row.get('reason')}`"
                )
    return "\n".join(lines) + "\n"


def _render_execution_log(execution_log: Mapping[str, object]) -> str:
    batch = dict((list(execution_log.get("batches") or [{}]) or [{}])[0])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5a final audit report",
        "",
        "# XI-5A Execution Log",
        "",
        f"- consumed lock: `{execution_log.get('approved_lock_path', '')}`",
        f"- consumed readiness contract: `{execution_log.get('readiness_contract_path', '')}`",
        f"- batch id: `{batch.get('batch_id', '')}`",
        f"- moved rows: `{batch.get('moved_count', 0)}`",
        f"- rewritten text files: `{batch.get('rewritten_files_count', 0)}`",
        "",
        "## Gates",
    ]
    for gate in list(batch.get("gate_runs") or []):
        lines.append(f"- `{gate.get('gate_id', '')}`: `{gate.get('status', '')}`")
    return "\n".join(lines) + "\n"


def _render_postmove_report(move_map: Mapping[str, object], residual_report: Mapping[str, object], ready_for_xi6: bool) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-5b and XI-6 follow-on reports",
        "",
        "# XI-5A Postmove Report",
        "",
        f"- moved rows: `{len(list(move_map.get('rows') or []))}`",
        f"- deferred rows still present under dangerous roots: `{len(list(residual_report.get('deferred_to_xi5b_remaining') or []))}`",
        f"- unexpected dangerous-root residuals: `{len(list(residual_report.get('unexpected_remaining_src_paths') or []))}`",
        f"- Xi-6 readiness: `{'yes' if ready_for_xi6 else 'no'}`",
    ]
    for row in list(residual_report.get("deferred_to_xi5b_remaining") or []):
        lines.append(f"- deferred: `{row.get('source_path', '')}`")
    return "\n".join(lines) + "\n"


def _render_attic_report(attic_map: Mapping[str, object]) -> str:
    return "\n".join(
        [
            "Status: DERIVED",
            "Last Reviewed: 2026-03-28",
            "Stability: provisional",
            "Future Series: XI-5",
            "Replacement Target: later Xi attic-routing phases",
            "",
            "# XI-5A Attic Report",
            "",
            "- approved attic routes executed in this pass: `0`",
            f"- consumed lock: `{attic_map.get('approved_lock_path', '')}`",
        ]
    ) + "\n"


def _render_final_doc(move_map: Mapping[str, object], residual_report: Mapping[str, object], execution_log: Mapping[str, object], ready_for_xi6: bool) -> str:
    batch = dict((list(execution_log.get("batches") or [{}]) or [{}])[0])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-28",
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-6 freeze report after Xi-5b/Xi-5c",
        "",
        "# XI-5A Final",
        "",
        "## Result",
        "",
        "- selected option consumed: `C`",
        f"- approved rows executed: `{len(list(move_map.get('rows') or []))}`",
        "- approved attic rows routed: `0`",
        f"- deferred rows left untouched: `{len(list(residual_report.get('deferred_to_xi5b_remaining') or []))}` dangerous-root residuals, plus later Xi-5b/Xi-5c deferred rows outside this pass",
        f"- unexpected runtime-critical src paths remaining: `{len(list(residual_report.get('unexpected_remaining_src_paths') or []))}`",
        "",
        "## Gates",
        "",
    ]
    for gate in list(batch.get("gate_runs") or []):
        lines.append(f"- `{gate.get('gate_id', '')}`: `{gate.get('status', '')}`")
    lines.extend(
        [
            "",
            "## Xi-6 Readiness",
            "",
            "Ready for Ξ-6 as previously generated" if ready_for_xi6 else "Blocked pending Ξ-5b",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_json(repo_root: str, rel_path: str, payload: Mapping[str, object]) -> None:
    abs_path = _repo_abs(repo_root, rel_path)
    _ensure_parent(abs_path)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload)))
        handle.write("\n")


def _write_progress(repo_root: str, payload: Mapping[str, object]) -> None:
    _write_json(repo_root, PROGRESS_LOG_REL, payload)


def _write_doc(repo_root: str, rel_path: str, text: str) -> None:
    abs_path = _repo_abs(repo_root, rel_path)
    _write_text(abs_path, text if text.endswith("\n") else text + "\n")


def build_xi5a_v4_plan(repo_root: str) -> dict[str, object]:
    repo_root_abs = _repo_root(repo_root)
    inputs = _load_execution_inputs(repo_root_abs)
    lock_payload = dict(inputs["lock"] or {})
    readiness = dict(inputs["readiness"] or {})
    if _token(readiness.get("approved_lock_path")) != SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL:
        raise Xi5aV4ExecutionFailure(
            "refusal.xi5a.missing_v2_lock",
            {"approved_lock_path": _token(readiness.get("approved_lock_path"))},
        )
    surprises = _surprise_detection(repo_root_abs, lock_payload)
    if surprises["unexpected"]:
        raise Xi5aV4ExecutionFailure(
            "refusal.xi5a.unmapped_runtime_src",
            {"unexpected_paths": surprises["unexpected"]},
        )
    rows = _batch_rows(lock_payload)
    replacements = _build_replacement_maps(rows)
    preview_changes = _preview_text_updates(repo_root_abs, replacements)
    move_map = _build_move_map(rows)
    residual_preview = {
        "deferred_to_xi5b_remaining": sorted(
            [
                {
                    "deferred_phase_class": _token(row.get("deferred_phase_class")),
                    "reason": _token(row.get("reason")),
                    "source_path": _source_path(row),
                    "target_path": _target_path(row),
                }
                for row in list(lock_payload.get("deferred_to_xi5b") or [])
                if _source_path(row).startswith("src/") or _source_path(row).startswith("app/src/")
            ],
            key=lambda row: row["source_path"],
        ),
        "unexpected_remaining_src_paths": [],
    }
    return {
        "lock": lock_payload,
        "move_map": move_map,
        "preview_changed_file_count": len(preview_changes),
        "preview_changed_files": sorted(preview_changes.keys()),
        "preview_changes": preview_changes,
        "readiness": readiness,
        "residual_preview": residual_preview,
        "replacements": replacements,
        "rows": rows,
        "surprises": surprises,
    }


def execute_xi5a_v4(repo_root: str) -> dict[str, object]:
    repo_root_abs = _repo_root(repo_root)
    plan = build_xi5a_v4_plan(repo_root_abs)
    rows = [dict(item or {}) for item in list(plan.get("rows") or [])]
    resume_mode = _has_partial_batch_application(repo_root_abs, rows)
    preflight_hashes = _load_resume_preflight_hashes(repo_root_abs) if resume_mode else _ensure_preflight_green(repo_root_abs)
    temp_root_abs = _repo_abs(repo_root_abs, TEMP_ROOT_REL)
    backup_root_abs = os.path.join(temp_root_abs, "batch_1_backup")
    if os.path.isdir(temp_root_abs):
        shutil.rmtree(temp_root_abs, ignore_errors=True)
    os.makedirs(temp_root_abs, exist_ok=True)
    progress_payload = {
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
        "current_gate_id": "",
        "deterministic_fingerprint": "",
        "gate_runs": [],
        "readiness_contract_path": XI5_READINESS_CONTRACT_V4_REL,
        "report_id": "xi.5a.progress.v4",
        "rewritten_files_count": 0,
        "row_count": 0,
        "status": "planning",
    }
    progress_payload["deterministic_fingerprint"] = canonical_sha256(dict(progress_payload, deterministic_fingerprint=""))
    _write_progress(repo_root_abs, progress_payload)

    lock_payload = dict(plan["lock"] or {})
    preview_changes = dict(plan.get("preview_changes") or {})
    progress_payload["rewritten_files_count"] = len(preview_changes)
    progress_payload["row_count"] = len(rows)
    progress_payload["status"] = "backing_up"
    progress_payload["deterministic_fingerprint"] = canonical_sha256(dict(progress_payload, deterministic_fingerprint=""))
    _write_progress(repo_root_abs, progress_payload)

    source_to_target = {_source_path(row): _target_path(row) for row in rows}
    cleanup_roots = set(DANGEROUS_ROOTS)
    restore_source_paths = set()
    restore_target_paths = set()
    for row in rows:
        source_path = _source_path(row)
        target_path = _target_path(row)
        restore_source_paths.add(source_path)
        restore_target_paths.add(target_path)
        if target_path:
            cleanup_roots.add(target_path.split("/", 1)[0])
    backup_paths = set(preview_changes.keys())
    backup_paths.update(_gate_mutable_paths(repo_root_abs))
    for row in rows:
        backup_paths.add(_source_path(row))
        backup_paths.add(_target_path(row))
    manifest = _backup_paths(repo_root_abs, backup_root_abs, backup_paths)

    moved_rows = []
    gate_runs: list[dict[str, object]] = []
    try:
        for row in rows:
            source_path = _source_path(row)
            target_path = _target_path(row)
            source_abs = _repo_abs(repo_root_abs, source_path)
            target_abs = _repo_abs(repo_root_abs, target_path)
            if not os.path.exists(source_abs):
                if os.path.exists(target_abs):
                    moved_rows.append(dict(row))
                    continue
                raise Xi5aV4ExecutionFailure(
                    "refusal.xi5a.unmapped_runtime_src",
                    {"missing_source_path": source_path},
                )
            if _has_source_like_segment(target_path):
                raise Xi5aV4ExecutionFailure(
                    "refusal.xi5a.target_path_ambiguity",
                    {"target_path": target_path},
                )
            _safe_move(repo_root_abs, source_path, target_path)
            moved_rows.append(dict(row))

        for current_path, updated_text in sorted(preview_changes.items()):
            destination_path = source_to_target.get(current_path, current_path)
            _write_text(_repo_abs(repo_root_abs, destination_path), updated_text)

        _cleanup_bytecode(repo_root_abs, cleanup_roots)

        for gate_id, command in _gate_plan():
            progress_payload["current_gate_id"] = gate_id
            progress_payload["gate_runs"] = gate_runs
            progress_payload["status"] = "running"
            progress_payload["deterministic_fingerprint"] = canonical_sha256(dict(progress_payload, deterministic_fingerprint=""))
            _write_progress(repo_root_abs, progress_payload)
            gate_result = _run_gate(repo_root_abs, command, gate_id)
            gate_runs.append(gate_result)
            progress_payload["gate_runs"] = gate_runs
            progress_payload["status"] = "running" if gate_result["status"] == "pass" else "failed"
            progress_payload["deterministic_fingerprint"] = canonical_sha256(dict(progress_payload, deterministic_fingerprint=""))
            _write_progress(repo_root_abs, progress_payload)
            if gate_result["status"] != "pass":
                raise Xi5aV4ExecutionFailure(
                    "refusal.xi5a.batch_gate_failed",
                    {
                        "failed_gate": gate_id,
                        "gate_result": gate_result,
                    },
                )
    except Xi5aV4ExecutionFailure:
        progress_payload["gate_runs"] = gate_runs
        progress_payload["status"] = "failed"
        progress_payload["deterministic_fingerprint"] = canonical_sha256(dict(progress_payload, deterministic_fingerprint=""))
        _write_progress(repo_root_abs, progress_payload)
        _restore_from_backup(repo_root_abs, backup_root_abs, manifest)
        _reconcile_git_after_restore(repo_root_abs, restore_source_paths, restore_target_paths)
        _cleanup_bytecode(repo_root_abs, cleanup_roots)
        raise
    except Exception as exc:
        progress_payload["gate_runs"] = gate_runs
        progress_payload["status"] = "failed"
        progress_payload["exception"] = repr(exc)
        progress_payload["deterministic_fingerprint"] = canonical_sha256(dict(progress_payload, deterministic_fingerprint=""))
        _write_progress(repo_root_abs, progress_payload)
        _restore_from_backup(repo_root_abs, backup_root_abs, manifest)
        _reconcile_git_after_restore(repo_root_abs, restore_source_paths, restore_target_paths)
        _cleanup_bytecode(repo_root_abs, cleanup_roots)
        raise Xi5aV4ExecutionFailure(
            "refusal.xi5a.batch_gate_failed",
            {"exception": repr(exc)},
        ) from exc

    move_map = _build_move_map(moved_rows)
    attic_map = _build_empty_attic_map()
    residual_report = _residual_report(repo_root_abs, lock_payload)
    ready_for_xi6 = not bool(list(residual_report.get("unexpected_remaining_src_paths") or [])) and not bool(
        list(residual_report.get("deferred_to_xi5b_remaining") or [])
    )
    execution_log = {
        "approved_lock_path": SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
        "baseline_validation_fingerprints": preflight_hashes,
        "batches": [
            {
                "batch_id": "batch_1_dangerous_shadow",
                "gate_runs": gate_runs,
                "moved_count": len(moved_rows),
                "rewritten_files_count": len(preview_changes),
                "row_count": len(rows),
                "status": "pass",
            }
        ],
        "consumed_lock_report_id": _token(lock_payload.get("report_id")),
        "deterministic_fingerprint": "",
        "readiness_contract_path": XI5_READINESS_CONTRACT_V4_REL,
        "ready_for_xi6": bool(ready_for_xi6),
        "report_id": "xi.5a.execution_log.v4",
        "rewritten_files": sorted(preview_changes.keys()),
        "unexpected_runtime_src_paths": list(residual_report.get("unexpected_remaining_src_paths") or []),
    }
    execution_log["deterministic_fingerprint"] = canonical_sha256(dict(execution_log, deterministic_fingerprint=""))
    progress_payload["current_gate_id"] = ""
    progress_payload["gate_runs"] = gate_runs
    progress_payload["status"] = "complete"
    progress_payload["deterministic_fingerprint"] = canonical_sha256(dict(progress_payload, deterministic_fingerprint=""))
    _write_progress(repo_root_abs, progress_payload)

    docs = {
        XI_5A_MOVE_PLAN_REL: _render_move_plan(move_map, residual_report),
        XI_5A_EXECUTION_LOG_DOC_REL: _render_execution_log(execution_log),
        XI_5A_POSTMOVE_REPORT_REL: _render_postmove_report(move_map, residual_report, ready_for_xi6),
        XI_5A_ATTIC_REPORT_REL: _render_attic_report(attic_map),
        XI_5A_FINAL_REL: _render_final_doc(move_map, residual_report, execution_log, ready_for_xi6),
    }

    _write_json(repo_root_abs, XI5A_MOVE_MAP_REL, move_map)
    _write_json(repo_root_abs, XI5A_ATTIC_MAP_REL, attic_map)
    _write_json(repo_root_abs, XI5A_EXECUTION_LOG_REL, execution_log)
    _write_json(repo_root_abs, XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL, residual_report)
    for rel_path, text in docs.items():
        _write_doc(repo_root_abs, rel_path, text)

    shutil.rmtree(temp_root_abs, ignore_errors=True)
    return {
        "attic_map": attic_map,
        "execution_log": execution_log,
        "move_map": move_map,
        "residual_report": residual_report,
    }

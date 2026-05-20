#!/usr/bin/env python3
"""Validate high-confidence repository dependency-direction law."""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:  # Python 3.11+
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover - exercised on Python 3.8
    tomllib = None


CONTRACT_REL = Path("contracts/repo/dependency_directions.contract.toml")
EXCEPTIONS_REL = Path("contracts/repo/dependency_direction_exceptions.toml")

CANONICAL_ROOTS = {
    "apps",
    "engine",
    "game",
    "runtime",
    "contracts",
    "content",
    "docs",
    "tests",
    "tools",
    "scripts",
    "cmake",
    "external",
    "release",
    "archive",
}
ACTIVE_SOURCE_ROOTS = {"apps", "engine", "game", "runtime", "contracts", "content"}
NON_RUNTIME_CONTEXT_ROOTS = {"docs", "tests", "tools", "archive", "release", "scripts", "cmake", "external"}
PRODUCT_RUNTIME_ROOTS = {"apps", "engine", "game", "runtime"}
GENERATED_LOCAL_ROOTS = {".aide.local", ".dominium.local", "build", "out", "dist", "tmp", "__pycache__"}
SKIP_PREFIXES = tuple(root + "/" for root in sorted(GENERATED_LOCAL_ROOTS)) + (
    ".git/",
    ".vs/",
    ".vscode/",
)

STRICT_EDGE_TYPES = {"include", "import"}
SOURCE_EXTS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".ipp",
    ".inc",
    ".inl",
}
PY_EXTS = {".py"}
TEXT_EXTS = SOURCE_EXTS | PY_EXTS | {".cmake", ".txt", ".toml", ".json", ".md", ".yml", ".yaml"}

INCLUDE_RE = re.compile(r"^\s*#\s*include\s*[<\"]([^\">]+)[\">]")
PY_IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z_][A-Za-z0-9_\.]*)")
PY_FROM_RE = re.compile(r"^\s*from\s+([A-Za-z_][A-Za-z0-9_\.]*)\s+import\b")
ROOT_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"(apps|engine|game|runtime|contracts|content|docs|tests|tools|scripts|cmake|external|release|archive)"
    r"/[A-Za-z0-9_./-]+"
)

FORBIDDEN_PAIRS = {
    ("engine", "runtime"),
    ("engine", "game"),
    ("engine", "apps"),
    ("engine", "content"),
    ("engine", "tools"),
    ("engine", "release"),
    ("engine", "archive"),
    ("runtime", "apps"),
    ("runtime", "tools"),
    ("runtime", "archive"),
    ("game", "apps"),
    ("game", "tools"),
    ("game", "archive"),
    ("contracts", "apps"),
    ("contracts", "engine"),
    ("contracts", "game"),
    ("contracts", "runtime"),
    ("contracts", "tools"),
    ("contracts", "content"),
    ("contracts", "archive"),
    ("content", "apps"),
    ("content", "engine"),
    ("content", "game"),
    ("content", "runtime"),
    ("content", "tools"),
    ("content", "archive"),
}

ALLOWED_PAIRS = {
    ("apps", "runtime"),
    ("apps", "game"),
    ("apps", "contracts"),
    ("runtime", "engine"),
    ("runtime", "contracts"),
    ("runtime", "external"),
    ("game", "engine"),
    ("game", "contracts"),
    ("engine", "contracts"),
    ("engine", "external"),
}


def normalize(value: Any) -> str:
    return str(value or "").replace("\\", "/").strip()


def norm_rel(path: Path, repo_root: Path) -> str:
    return normalize(path.relative_to(repo_root)).strip("/")


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    out: List[str] = []
    for ch in line:
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            out.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            out.append(ch)
            continue
        if ch == "#" and not in_quote:
            break
        out.append(ch)
    return "".join(out).strip()


def _split_array_items(raw: str) -> List[str]:
    items: List[str] = []
    current: List[str] = []
    in_quote = False
    escaped = False
    for ch in raw:
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_quote:
            current.append(ch)
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            current.append(ch)
            continue
        if ch == "," and not in_quote:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
            continue
        current.append(ch)
    item = "".join(current).strip()
    if item:
        items.append(item)
    return items


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"')
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_parse_value(item) for item in _split_array_items(inner)]
    try:
        return int(raw)
    except ValueError:
        return raw


def _minimal_toml_load(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    current: Dict[str, Any] = root
    for lineno, original in enumerate(text.splitlines(), 1):
        line = _strip_comment(original)
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            section = line[2:-2].strip()
            current = {}
            root.setdefault(section, []).append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            current = root
            for part in section.split("."):
                current = current.setdefault(part, {})
            continue
        if "=" not in line:
            raise ValueError("invalid TOML line {0}: {1}".format(lineno, original))
        key, raw_value = line.split("=", 1)
        current[key.strip()] = _parse_value(raw_value)
    return root


def load_toml(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if tomllib is not None:
        return tomllib.loads(text)
    return _minimal_toml_load(text)


def tracked_files(repo_root: Path) -> List[str]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files"],
            cwd=str(repo_root),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        files: List[str] = []
        for root, dirs, names in os.walk(str(repo_root)):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "__pycache__")
            for name in sorted(names):
                rel = normalize(os.path.relpath(os.path.join(root, name), str(repo_root))).strip("/")
                files.append(rel)
        return sorted(files)
    return sorted(line.strip().replace("\\", "/") for line in output.splitlines() if line.strip())


def should_scan(rel: str) -> bool:
    rel = normalize(rel).strip("/")
    if not rel:
        return False
    for prefix in SKIP_PREFIXES:
        if rel == prefix.rstrip("/") or rel.startswith(prefix):
            return False
    return True


def root_for_path(rel: str) -> str:
    rel = normalize(rel).strip("/")
    if not rel:
        return "repo"
    first = rel.split("/", 1)[0]
    if first in GENERATED_LOCAL_ROOTS:
        return first
    if first in CANONICAL_ROOTS:
        return first
    if rel == "CMakeLists.txt":
        return "cmake"
    return "repo"


def context_for_path(rel: str) -> str:
    root = root_for_path(rel)
    if root in {"docs", "tests", "tools", "archive", "release", "scripts", "cmake", "external"}:
        return root
    if rel.endswith("CMakeLists.txt") or rel.endswith(".cmake"):
        return "cmake"
    if root in ACTIVE_SOURCE_ROOTS:
        return "active_source"
    return "other"


def text_lines(repo_root: Path, rel: str) -> List[str]:
    path = repo_root / rel
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []


def ext_for_path(rel: str) -> str:
    return Path(rel).suffix.lower()


def canonical_target_root(raw_target: str, rel: str) -> Tuple[Optional[str], str]:
    target = normalize(raw_target).strip()
    target = target.strip("<>\"'")
    if not target:
        return None, "empty"
    first = target.split("/", 1)[0]
    if first in CANONICAL_ROOTS or first in GENERATED_LOCAL_ROOTS:
        return first, "root_path"

    rel_dir = normalize(posixpath.dirname(rel))
    joined = normalize(posixpath.normpath(posixpath.join(rel_dir, target)))
    if not joined.startswith("../"):
        first_joined = joined.split("/", 1)[0]
        if first_joined in CANONICAL_ROOTS or first_joined in GENERATED_LOCAL_ROOTS:
            return first_joined, "relative_root"

    if first == "domino":
        return "engine", "namespace_alias"
    if first == "dominium":
        return "game", "namespace_alias"
    if first == "dom_contracts":
        return "contracts", "namespace_alias"
    return None, "external_or_system"


def python_target_root(module: str) -> Tuple[Optional[str], str]:
    top = module.split(".", 1)[0]
    if top in CANONICAL_ROOTS:
        return top, "python_module"
    if top in GENERATED_LOCAL_ROOTS:
        return top, "python_module"
    return None, "external_or_system"


def finding(
    level: str,
    code: str,
    rel: str,
    line: int,
    from_root: str,
    to_root: str,
    edge_type: str,
    target: str,
    message: str,
    confidence: str,
) -> Dict[str, Any]:
    return {
        "level": level,
        "code": code,
        "path": rel,
        "line": line,
        "from_root": from_root,
        "to_root": to_root,
        "edge_type": edge_type,
        "target": target,
        "message": message,
        "confidence": confidence,
    }


def evaluate_edge(
    rel: str,
    line: int,
    from_root: str,
    to_root: str,
    edge_type: str,
    target: str,
    confidence: str,
    include_path_references: bool,
) -> Optional[Dict[str, Any]]:
    if not to_root or from_root == to_root:
        return None

    context = context_for_path(rel)
    if context in {"docs", "tests", "tools", "archive"}:
        return None
    if context == "release":
        return None
    if context in {"scripts", "cmake"} and edge_type != "include":
        return None

    if to_root in GENERATED_LOCAL_ROOTS and from_root in ACTIVE_SOURCE_ROOTS:
        return finding(
            "error",
            "active_source_to_generated_local",
            rel,
            line,
            from_root,
            to_root,
            edge_type,
            target,
            "active source must not depend on generated/local output roots",
            confidence,
        )

    if (from_root, to_root) in FORBIDDEN_PAIRS:
        if edge_type in STRICT_EDGE_TYPES:
            if from_root == "contracts" and confidence == "namespace_alias":
                return finding(
                    "warning",
                    "contracts_public_namespace_reference",
                    rel,
                    line,
                    from_root,
                    to_root,
                    edge_type,
                    target,
                    "contracts reference a public namespace alias; stable promotion needs explicit contract ownership",
                    confidence,
                )
            return finding(
                "error",
                "forbidden_dependency_direction",
                rel,
                line,
                from_root,
                to_root,
                edge_type,
                target,
                "forbidden high-confidence dependency direction",
                confidence,
            )
        if include_path_references:
            return finding(
                "warning",
                "forbidden_path_reference",
                rel,
                line,
                from_root,
                to_root,
                edge_type,
                target,
                "path reference crosses a forbidden dependency direction but is not a runtime edge",
                confidence,
            )
        return None

    if to_root == "archive" and from_root in ACTIVE_SOURCE_ROOTS:
        return finding(
            "error" if edge_type in STRICT_EDGE_TYPES else "warning",
            "active_source_to_archive",
            rel,
            line,
            from_root,
            to_root,
            edge_type,
            target,
            "active source must not depend on archive",
            confidence,
        )

    if from_root in PRODUCT_RUNTIME_ROOTS and to_root == "tools" and edge_type in STRICT_EDGE_TYPES:
        return finding(
            "error",
            "runtime_to_tools",
            rel,
            line,
            from_root,
            to_root,
            edge_type,
            target,
            "product/runtime/engine/game code must not depend on tools",
            confidence,
        )

    if edge_type in STRICT_EDGE_TYPES and from_root in ACTIVE_SOURCE_ROOTS:
        if (from_root, to_root) not in ALLOWED_PAIRS and to_root in CANONICAL_ROOTS:
            return finding(
                "warning",
                "unlisted_active_dependency",
                rel,
                line,
                from_root,
                to_root,
                edge_type,
                target,
                "dependency is not listed as an allowed broad edge; review before stable promotion",
                confidence,
            )

    return None


def detect_edges(repo_root: Path, rel: str, include_path_references: bool) -> List[Dict[str, Any]]:
    from_root = root_for_path(rel)
    ext = ext_for_path(rel)
    lines = text_lines(repo_root, rel)
    findings: List[Dict[str, Any]] = []

    for line_no, line in enumerate(lines, 1):
        if ext in SOURCE_EXTS:
            match = INCLUDE_RE.match(line)
            if match:
                target = normalize(match.group(1))
                to_root, confidence = canonical_target_root(target, rel)
                if to_root:
                    item = evaluate_edge(
                        rel,
                        line_no,
                        from_root,
                        to_root,
                        "include",
                        target,
                        confidence,
                        include_path_references,
                    )
                    if item:
                        findings.append(item)
                continue

        if ext in PY_EXTS:
            import_match = PY_IMPORT_RE.match(line)
            from_match = PY_FROM_RE.match(line)
            module = ""
            if import_match:
                module = import_match.group(1)
            elif from_match:
                module = from_match.group(1)
            if module:
                to_root, confidence = python_target_root(module)
                if to_root:
                    item = evaluate_edge(
                        rel,
                        line_no,
                        from_root,
                        to_root,
                        "import",
                        module,
                        confidence,
                        include_path_references,
                    )
                    if item:
                        findings.append(item)
                continue

        is_cmake = rel.endswith("CMakeLists.txt") or rel.endswith(".cmake")
        if is_cmake:
            for match in ROOT_PATH_RE.finditer(line):
                target = normalize(match.group(0))
                to_root = target.split("/", 1)[0]
                item = evaluate_edge(
                    rel,
                    line_no,
                    from_root,
                    to_root,
                    "build_reference",
                    target,
                    "path_token",
                    include_path_references,
                )
                if item:
                    findings.append(item)

        if include_path_references and ext in TEXT_EXTS and not context_for_path(rel) == "docs":
            for match in ROOT_PATH_RE.finditer(line):
                target = normalize(match.group(0))
                to_root = target.split("/", 1)[0]
                item = evaluate_edge(
                    rel,
                    line_no,
                    from_root,
                    to_root,
                    "path_reference",
                    target,
                    "path_token",
                    include_path_references,
                )
                if item:
                    findings.append(item)

    return findings


def load_exceptions(repo_root: Path, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    path = repo_root / EXCEPTIONS_REL
    if not path.exists():
        errors.append(
            finding(
                "error",
                "missing_exception_file",
                str(EXCEPTIONS_REL),
                0,
                "contracts",
                "contracts",
                "contract_reference",
                str(EXCEPTIONS_REL),
                "dependency direction exception file is missing",
                "contract",
            )
        )
        return []
    try:
        data = load_toml(path)
    except Exception as exc:
        errors.append(
            finding(
                "error",
                "exception_parse_error",
                str(EXCEPTIONS_REL),
                0,
                "contracts",
                "contracts",
                "contract_reference",
                str(EXCEPTIONS_REL),
                "failed to parse exception file: {0}".format(exc),
                "contract",
            )
        )
        return []
    raw = data.get("exception", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def exception_matches(exception: Dict[str, Any], item: Dict[str, Any]) -> bool:
    return (
        normalize(exception.get("path")).strip("/") == normalize(item.get("path")).strip("/")
        and str(exception.get("from_root")) == str(item.get("from_root"))
        and str(exception.get("to_root")) == str(item.get("to_root"))
        and str(exception.get("edge_type")) == str(item.get("edge_type"))
    )


def apply_exceptions(
    findings: List[Dict[str, Any]],
    exceptions: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    remaining: List[Dict[str, Any]] = []
    used: List[Dict[str, Any]] = []
    used_ids: Set[str] = set()
    for item in findings:
        matched = None
        for exception in exceptions:
            if exception_matches(exception, item):
                matched = exception
                break
        if matched:
            used.append(matched)
            used_ids.add(str(matched.get("id", "<missing-id>")))
            item = dict(item)
            item["level"] = "warning"
            item["code"] = "exception_applied"
            item["exception_id"] = str(matched.get("id", "<missing-id>"))
            remaining.append(item)
        else:
            remaining.append(item)
    unused = [item for item in exceptions if str(item.get("id", "<missing-id>")) not in used_ids]
    return remaining, used, unused


def validate_contract_files(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    contract_path = repo_root / CONTRACT_REL
    if not contract_path.exists():
        findings.append(
            finding(
                "error",
                "missing_contract",
                str(CONTRACT_REL),
                0,
                "contracts",
                "contracts",
                "contract_reference",
                str(CONTRACT_REL),
                "dependency direction contract is missing",
                "contract",
            )
        )
        return findings
    try:
        data = load_toml(contract_path)
    except Exception as exc:
        findings.append(
            finding(
                "error",
                "contract_parse_error",
                str(CONTRACT_REL),
                0,
                "contracts",
                "contracts",
                "contract_reference",
                str(CONTRACT_REL),
                "failed to parse dependency direction contract: {0}".format(exc),
                "contract",
            )
        )
        return findings
    root_section = data.get("root", {})
    if not isinstance(root_section, dict):
        findings.append(
            finding(
                "error",
                "contract_missing_roots",
                str(CONTRACT_REL),
                0,
                "contracts",
                "contracts",
                "contract_reference",
                str(CONTRACT_REL),
                "contract must define root entries",
                "contract",
            )
        )
    for required in ["apps", "engine", "game", "runtime", "contracts", "content", "tools", "tests", "archive"]:
        if not isinstance(root_section, dict) or required not in root_section:
            findings.append(
                finding(
                    "error",
                    "contract_missing_root",
                    str(CONTRACT_REL),
                    0,
                    "contracts",
                    "contracts",
                    "contract_reference",
                    required,
                    "contract missing required root entry: {0}".format(required),
                    "contract",
                )
            )
    return findings


def scan(repo_root: Path, include_path_references: bool) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    files = [rel for rel in tracked_files(repo_root) if should_scan(rel)]
    roots_seen: Set[str] = set()
    findings: List[Dict[str, Any]] = []
    files_scanned = 0
    for rel in files:
        ext = ext_for_path(rel)
        is_cmake = rel.endswith("CMakeLists.txt") or rel.endswith(".cmake")
        if ext not in TEXT_EXTS and not is_cmake:
            continue
        roots_seen.add(root_for_path(rel))
        files_scanned += 1
        findings.extend(detect_edges(repo_root, rel, include_path_references))
    stats = {
        "files_considered": len(files),
        "files_scanned": files_scanned,
        "roots_scanned": sorted(roots_seen),
    }
    return findings, stats


def summarize(
    repo_root: Path,
    findings: List[Dict[str, Any]],
    stats: Dict[str, Any],
    exceptions: List[Dict[str, Any]],
    exceptions_used: List[Dict[str, Any]],
    exceptions_unused: List[Dict[str, Any]],
    contract_findings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    all_findings = contract_findings + findings
    violations = [item for item in all_findings if item.get("level") == "error"]
    warnings = [item for item in all_findings if item.get("level") == "warning"]
    return {
        "schema_version": "dominium.repo.dependency_direction_scan.v1",
        "validator": "tools/validators/repo/check_dependency_directions.py",
        "repo_root": str(repo_root),
        "status": "fail" if violations else "pass",
        "summary": {
            "roots_scanned": len(stats.get("roots_scanned", [])),
            "files_considered": stats.get("files_considered", 0),
            "files_scanned": stats.get("files_scanned", 0),
            "violations": len(violations),
            "warnings": len(warnings),
            "exceptions_active": len(exceptions),
            "exceptions_used": len(exceptions_used),
            "exceptions_unused": len(exceptions_unused),
        },
        "roots_scanned": stats.get("roots_scanned", []),
        "violations": violations,
        "warnings": warnings,
        "exceptions_used": exceptions_used,
        "exceptions_unused": exceptions_unused,
    }


def print_rules() -> None:
    print("Canonical roots:")
    for root in sorted(CANONICAL_ROOTS):
        print("  - {0}".format(root))
    print("Generated/local roots:")
    for root in sorted(GENERATED_LOCAL_ROOTS):
        print("  - {0}".format(root))
    print("Forbidden high-confidence pairs:")
    for from_root, to_root in sorted(FORBIDDEN_PAIRS):
        print("  - {0} -> {1}".format(from_root, to_root))


def print_human(summary: Dict[str, Any], max_findings: Optional[int]) -> None:
    stats = summary["summary"]
    print(
        "dependency direction validation: {0} ({1} files scanned, {2} violations, {3} warnings)".format(
            str(summary["status"]).upper(),
            stats["files_scanned"],
            stats["violations"],
            stats["warnings"],
        )
    )
    items = summary.get("violations", []) + summary.get("warnings", [])
    if max_findings is not None:
        items = items[:max_findings]
    for item in items:
        print(
            "{level}: {path}:{line}: {code}: {from_root}->{to_root} {edge_type} {target}".format(
                **item
            )
        )
        print("  {0}".format(item.get("message", "")))
    if summary.get("exceptions_unused"):
        print("unused exceptions: {0}".format(len(summary["exceptions_unused"])))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate repository dependency direction law.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--list-rules", action="store_true")
    parser.add_argument("--include-path-references", action="store_true")
    parser.add_argument("--max-findings", type=int, default=None)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()

    if args.list_rules:
        print_rules()
        return 0

    contract_findings = validate_contract_files(repo_root)
    exception_errors: List[Dict[str, Any]] = []
    exceptions = load_exceptions(repo_root, exception_errors)
    contract_findings.extend(exception_errors)
    raw_findings, stats = scan(repo_root, args.include_path_references)
    findings, exceptions_used, exceptions_unused = apply_exceptions(raw_findings, exceptions)
    if exceptions_unused:
        for exception in exceptions_unused:
            contract_findings.append(
                finding(
                    "warning",
                    "unused_exception",
                    str(EXCEPTIONS_REL),
                    0,
                    str(exception.get("from_root", "contracts")),
                    str(exception.get("to_root", "contracts")),
                    str(exception.get("edge_type", "unknown")),
                    str(exception.get("id", "<missing-id>")),
                    "declared dependency-direction exception was not used by the scan",
                    "exception",
                )
            )

    summary = summarize(
        repo_root,
        findings,
        stats,
        exceptions,
        exceptions_used,
        exceptions_unused,
        contract_findings,
    )

    if args.json_output:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_human(summary, args.max_findings)

    if args.strict and summary["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

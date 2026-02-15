#!/usr/bin/env python3
"""Minimal deterministic RepoX policy scan for XStack profile runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from typing import Dict, Iterable, List, Tuple


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
    "tools/xstack/bundle_list.py",
    "tools/xstack/bundle_validate.py",
    "tools/xstack/session_create.py",
    "tools/xstack/session_boot.py",
    "schemas",
    "packs",
    "bundles",
    "docs/contracts",
    "docs/testing",
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
    ".txt",
    ".yaml",
    ".yml",
}

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')
RENDERER_TRUTH_INCLUDE_FORBIDDEN = {
    "domino/truth_model_v1.h",
    "domino/truth_model.h",
}


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
    for token in FORBIDDEN_IDENTIFIERS:
        pattern = r"\b{}\b".format(re.escape(token))
        if re.search(pattern, lower):
            severity = "refusal"
            if token == "sandbox" and profile == "FAST":
                severity = "warn"
            findings.append(
                _finding(
                    severity=severity,
                    file_path=rel_path,
                    line_number=line_no,
                    snippet=line.strip()[:140],
                    message="forbidden identifier '{}' detected".format(token),
                    rule_id="repox.forbidden_identifier",
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
    severity = "warn" if profile == "FAST" else "refusal"
    findings.append(
        _finding(
            severity=severity,
            file_path=rel_path,
            line_number=line_no,
            snippet=line.strip()[:140],
            message="mode-flag heuristic matched '{}'".format(lhs),
            rule_id="repox.mode_flag_heuristic",
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


def run_repox_check(repo_root: str, profile: str) -> Dict[str, object]:
    token = str(profile or "").strip().upper() or "FAST"
    files = _scan_files(repo_root)
    findings: List[Dict[str, object]] = []

    for rel_path in files:
        for line_no, line in _iter_lines(repo_root, rel_path):
            _append_forbidden_identifier_findings(findings, rel_path, line_no, line, token)
            _append_mode_flag_findings(findings, rel_path, line_no, line, token)
            _append_reserved_misuse_findings(findings, rel_path, line_no, line, token)
            _append_strict_placeholder_findings(findings, rel_path, line_no, line, token)
            _append_renderer_truth_boundary_findings(findings, rel_path, line_no, line, token)

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

"""Client/server and trust boundary heuristics."""

from __future__ import annotations

import os
from typing import Dict, Iterable, List


SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".py", ".json", ".md")


def _iter_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "out", "dist", "__pycache__"}]
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() not in SOURCE_EXTS:
                continue
            yield os.path.join(dirpath, filename)


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _scan_forbidden_tokens(paths: Iterable[str], tokens: Iterable[str], refusal_prefix: str) -> List[str]:
    issues: List[str] = []
    token_set = [str(token).strip() for token in tokens if str(token).strip()]
    for path in sorted(paths):
        text = _read(path).lower()
        if not text:
            continue
        rel = path.replace("\\", "/")
        for token in token_set:
            if token.lower() in text:
                issues.append("{}.{}@{}".format(refusal_prefix, token, rel))
    return sorted(set(issues))


def validate_boundaries(repo_root: str, trust_entries: List[Dict[str, object]]) -> List[str]:
    client_root = os.path.join(repo_root, "client")
    server_root = os.path.join(repo_root, "server")
    runtime_roots = [os.path.join(repo_root, item) for item in ("client", "server", "engine", "game")]

    issues: List[str] = []
    if not os.path.isdir(client_root):
        issues.append("refuse.boundary.client_root_missing")
    if not os.path.isdir(server_root):
        issues.append("refuse.boundary.server_root_missing")

    if any(str(entry.get("subsystem", "")).strip() == "client_renderer" for entry in trust_entries):
        client_files = list(_iter_files(client_root)) if os.path.isdir(client_root) else []
        issues.extend(
            _scan_forbidden_tokens(
                client_files,
                tokens=("override_authority_state", "force_server_state", "server_only_truth_access"),
                refusal_prefix="refuse.boundary.client_override",
            )
        )

    runtime_files: List[str] = []
    for root in runtime_roots:
        if os.path.isdir(root):
            runtime_files.extend(list(_iter_files(root)))
    issues.extend(
        _scan_forbidden_tokens(
            runtime_files,
            tokens=("bypass_law_profile", "disable_epistemic_guard"),
            refusal_prefix="refuse.boundary.law_bypass",
        )
    )

    return sorted(set(issues))


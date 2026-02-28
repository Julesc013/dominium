#!/usr/bin/env python3
"""Generate deterministic migration status report from governance deprecations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Iterable, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.governance.tool_deprecation_check import (  # noqa: E402
    DEFAULT_DEPRECATIONS_REL,
    DEFAULT_TOPOLOGY_MAP_REL,
    _norm,
    _read_json,
    validate_deprecation_registry,
)


TEXT_EXTENSIONS = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".json", ".md", ".schema", ".schema.json")


def _write_text(path: str, text: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.rstrip() + "\n")


def _semver_tuple(value: str) -> Tuple[int, int, int]:
    token = str(value or "").strip()
    parts = token.split(".")
    if len(parts) != 3:
        return (9999, 9999, 9999)
    out: List[int] = []
    for item in parts:
        try:
            out.append(int(item))
        except ValueError:
            return (9999, 9999, 9999)
    return (out[0], out[1], out[2])


def _collect_reference_paths(repo_root: str, deprecated_id: str) -> List[str]:
    token = str(deprecated_id or "").strip()
    if not token:
        return []
    out: List[str] = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = sorted(name for name in dirs if not name.startswith(".") and name != "__pycache__")
        for name in sorted(files):
            if not name.endswith(TEXT_EXTENSIONS):
                continue
            abs_path = os.path.join(root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if rel_path == DEFAULT_DEPRECATIONS_REL:
                continue
            try:
                text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if token in text:
                out.append(rel_path)
    return sorted(set(out))


def _build_markdown(
    *,
    entries: List[Dict[str, object]],
    validation_result: Dict[str, object],
    topology_path: str,
    reference_map: Dict[str, List[str]],
) -> str:
    status_counts: Dict[str, int] = {}
    for row in entries:
        status = str(row.get("status", "")).strip()
        if not status:
            continue
        status_counts[status] = int(status_counts.get(status, 0) or 0) + 1

    lines: List[str] = [
        "Status: DERIVED",
        "Version: 1.0.0",
        "",
        "# Migration Status",
        "",
        "- deprecations_registry: `{}`".format(DEFAULT_DEPRECATIONS_REL),
        "- topology_map: `{}`".format(topology_path),
        "- registry_validation: `{}`".format(str(validation_result.get("result", "unknown"))),
        "",
        "## Lifecycle Counts",
    ]
    for key in sorted(status_counts.keys()):
        lines.append("- {}: {}".format(key, int(status_counts.get(key, 0) or 0)))
    if not status_counts:
        lines.append("- none: 0")

    lines.extend(
        [
            "",
            "## Deadlines",
        ]
    )
    by_deadline = sorted(
        entries,
        key=lambda row: (
            _semver_tuple(str(row.get("removal_target_version", ""))),
            str(row.get("deprecated_id", "")),
        ),
    )
    for row in by_deadline:
        lines.append(
            "- `{}` -> target `{}` ({})".format(
                str(row.get("deprecated_id", "")),
                str(row.get("removal_target_version", "")),
                str(row.get("status", "")),
            )
        )
    if not by_deadline:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Deprecated and Quarantined",
        ]
    )
    hot_status = {"deprecated", "quarantined"}
    hot_rows = [row for row in entries if str(row.get("status", "")).strip() in hot_status]
    for row in sorted(hot_rows, key=lambda item: str(item.get("deprecated_id", ""))):
        lines.append(
            "- `{}` ({}) -> `{}`".format(
                str(row.get("deprecated_id", "")),
                str(row.get("status", "")),
                str(row.get("replacement_id", "")),
            )
        )
    if not hot_rows:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Remaining References",
        ]
    )
    for row in sorted(entries, key=lambda item: str(item.get("deprecated_id", ""))):
        deprecated_id = str(row.get("deprecated_id", "")).strip()
        refs = list(reference_map.get(deprecated_id) or [])
        lines.append("- `{}`: {}".format(deprecated_id, len(refs)))
        for ref in refs[:12]:
            lines.append("  - `{}`".format(ref))
    if not entries:
        lines.append("- none")

    errors = list(validation_result.get("errors") or [])
    lines.extend(
        [
            "",
            "## Validation Errors",
        ]
    )
    if errors:
        for row in errors:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- `{}` {} ({})".format(
                    str(row.get("code", "")),
                    str(row.get("message", "")),
                    str(row.get("path", "")),
                )
            )
    else:
        lines.append("- none")

    return "\n".join(lines)


def generate_migration_report(
    *,
    repo_root: str,
    deprecations_rel: str = DEFAULT_DEPRECATIONS_REL,
    topology_map_rel: str = DEFAULT_TOPOLOGY_MAP_REL,
    out_rel: str = "docs/audit/MIGRATION_STATUS.md",
) -> Dict[str, object]:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    deprecations_rel = _norm(deprecations_rel) or DEFAULT_DEPRECATIONS_REL
    topology_map_rel = _norm(topology_map_rel) or DEFAULT_TOPOLOGY_MAP_REL
    out_rel = _norm(out_rel) or "docs/audit/MIGRATION_STATUS.md"

    payload = _read_json(os.path.join(repo_root, deprecations_rel.replace("/", os.sep)))
    rows = [
        row
        for row in list(payload.get("entries") or [])
        if isinstance(row, dict)
    ]
    rows = sorted(rows, key=lambda item: str(item.get("deprecated_id", "")))

    validation = validate_deprecation_registry(
        repo_root=repo_root,
        deprecations_rel=deprecations_rel,
        topology_map_rel=topology_map_rel,
    )

    reference_map: Dict[str, List[str]] = {}
    for row in rows:
        deprecated_id = str(row.get("deprecated_id", "")).strip()
        reference_map[deprecated_id] = _collect_reference_paths(repo_root, deprecated_id)

    markdown = _build_markdown(
        entries=rows,
        validation_result=validation,
        topology_path=topology_map_rel,
        reference_map=reference_map,
    )
    out_abs = os.path.join(repo_root, out_rel.replace("/", os.sep))
    _write_text(out_abs, markdown)
    return {
        "result": "complete",
        "entries": len(rows),
        "out_path": out_rel,
        "validation_result": str(validation.get("result", "")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic migration status report from deprecations.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--deprecations", default=DEFAULT_DEPRECATIONS_REL)
    parser.add_argument("--topology-map", default=DEFAULT_TOPOLOGY_MAP_REL)
    parser.add_argument("--out", default="docs/audit/MIGRATION_STATUS.md")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = generate_migration_report(
        repo_root=repo_root,
        deprecations_rel=str(args.deprecations or DEFAULT_DEPRECATIONS_REL),
        topology_map_rel=str(args.topology_map or DEFAULT_TOPOLOGY_MAP_REL),
        out_rel=str(args.out or "docs/audit/MIGRATION_STATUS.md"),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


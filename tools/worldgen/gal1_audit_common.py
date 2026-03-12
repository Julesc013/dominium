"""Shared deterministic GAL-1 audit helpers."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Mapping, Tuple


GAL1_SCOPE_PATHS: Tuple[str, ...] = (
    "docs/audit/GAL1_RETRO_AUDIT.md",
    "docs/worldgen/GALAXY_COMPACT_OBJECT_STUBS.md",
    "schema/worldgen/galaxy_object_stub.schema",
    "schemas/galaxy_object_stub.schema.json",
    "data/registries/object_kind_registry.json",
    "src/worldgen/galaxy",
    "tools/worldgen/gal1_audit_common.py",
    "tools/worldgen/gal1_probe.py",
    "tools/worldgen/tool_replay_galaxy_objects.py",
)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _registry_rows(payload: Mapping[str, object], row_key: str) -> List[dict]:
    rows = list(_as_map(payload).get(row_key) or [])
    if not rows:
        rows = list(_as_map(_as_map(payload).get("record")).get(row_key) or [])
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def scan_gal1_untagged_stubs(repo_root: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    payload = _load_json(repo_root, "data/registries/object_kind_registry.json")
    rows = _registry_rows(payload, "object_kinds")
    row_by_id = dict(
        (str(row.get("object_kind_id", "")).strip(), dict(row))
        for row in rows
        if str(row.get("object_kind_id", "")).strip()
    )
    for object_kind_id in (
        "kind.black_hole_stub",
        "kind.nebula_stub",
        "kind.supernova_remnant_stub",
    ):
        row = _as_map(row_by_id.get(object_kind_id))
        if not row:
            findings.append(
                {
                    "path": "data/registries/object_kind_registry.json",
                    "line": 1,
                    "token": object_kind_id,
                    "message": "required GAL-1 provisional object kind is missing",
                }
            )
            continue
        stability = _as_map(row.get("stability"))
        stability_class_id = str(stability.get("stability_class_id", "")).strip()
        future_series = str(stability.get("future_series", "")).strip()
        replacement_target = str(stability.get("replacement_target", "")).strip()
        if stability_class_id == "provisional" and future_series == "ASTRO-DOMAIN" and replacement_target:
            continue
        findings.append(
            {
                "path": "data/registries/object_kind_registry.json",
                "line": 1,
                "token": object_kind_id,
                "message": "GAL-1 stub object kinds must be provisional and carry an ASTRO-DOMAIN replacement plan",
            }
        )
    return sorted(findings, key=lambda item: (str(item.get("path", "")), int(item.get("line", 0) or 0), str(item.get("token", ""))))


def scan_gal1_unbounded_generation(repo_root: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    try:
        from tools.worldgen.gal1_probe import bounded_generation_report
    except Exception as exc:
        return [
            {
                "path": "tools/worldgen/gal1_probe.py",
                "line": 1,
                "token": "bounded_generation_report",
                "message": "unable to import GAL-1 bounded generation report ({})".format(str(exc)),
            }
        ]
    report = bounded_generation_report(repo_root)
    if str(report.get("result", "")).strip() == "complete":
        return []
    findings.append(
        {
            "path": "tools/worldgen/gal1_probe.py",
            "line": 1,
            "token": "max_objects_per_cell",
            "message": "GAL-1 object generation exceeded the declared per-cell bound",
        }
    )
    return findings


__all__ = [
    "GAL1_SCOPE_PATHS",
    "scan_gal1_untagged_stubs",
    "scan_gal1_unbounded_generation",
]

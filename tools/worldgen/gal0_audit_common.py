"""Shared deterministic GAL-0 audit helpers."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, Iterable, List, Mapping, Tuple


GAL0_SCOPE_PATHS: Tuple[str, ...] = (
    "docs/audit/GAL0_RETRO_AUDIT.md",
    "docs/worldgen/GALAXY_METADATA_PROXIES.md",
    "data/registries/field_type_registry.json",
    "data/registries/field_binding_registry.json",
    "data/registries/galactic_region_registry.json",
    "src/worldgen/galaxy",
    "src/worldgen/earth/sky/starfield_generator.py",
    "tools/worldgen/gal0_probe.py",
    "tools/worldgen/tool_replay_galaxy_proxies.py",
)

_TEXT_EXTENSIONS = {".json", ".md", ".py", ".schema"}
_CATALOG_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("catalog dependency", re.compile(r"\bcatalog(?:ue)?s?\b", re.IGNORECASE)),
    ("Gaia catalog", re.compile(r"\bgaia\b", re.IGNORECASE)),
    ("Hipparcos catalog", re.compile(r"\bhipparcos\b", re.IGNORECASE)),
    ("Messier catalog", re.compile(r"\bmessier\b", re.IGNORECASE)),
    ("NGC catalog", re.compile(r"\bngc\b", re.IGNORECASE)),
    ("SIMBAD dependency", re.compile(r"\bsimbad\b", re.IGNORECASE)),
)
_ALLOWLIST_FRAGMENTS = (
    "no catalog",
    "no catalogs",
    "no external catalog",
    "must not",
    "do not",
    "without catalog",
    "catalog-free",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _iter_scope_files(repo_root: str) -> Iterable[str]:
    seen = set()
    for rel_path in GAL0_SCOPE_PATHS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            normalized = _norm(rel_path)
            if normalized not in seen:
                seen.add(normalized)
                yield normalized
            continue
        if not os.path.isdir(abs_path):
            continue
        for root, _dirs, files in os.walk(abs_path):
            for name in sorted(files):
                if os.path.splitext(name)[1].lower() not in _TEXT_EXTENSIONS:
                    continue
                rel_file = _norm(os.path.relpath(os.path.join(root, name), repo_root))
                if rel_file not in seen:
                    seen.add(rel_file)
                    yield rel_file


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


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


def scan_gal0_catalog_dependencies(repo_root: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    for rel_path in sorted(_iter_scope_files(repo_root)):
        for line_no, line in _iter_lines(repo_root, rel_path):
            snippet = str(line).strip()
            lowered = snippet.lower()
            if (not snippet) or any(fragment in lowered for fragment in _ALLOWLIST_FRAGMENTS):
                continue
            for token, pattern in _CATALOG_PATTERNS:
                if not pattern.search(snippet):
                    continue
                findings.append(
                    {
                        "path": rel_path,
                        "line": int(line_no),
                        "token": token,
                        "message": "GAL-0 proxy layer must remain catalog-free; remove '{}' from scoped galaxy proxy files".format(token),
                    }
                )
                break
    return sorted(
        findings,
        key=lambda item: (
            _norm(str(item.get("path", ""))),
            int(item.get("line", 0) or 0),
            str(item.get("token", "")),
        ),
    )


def scan_gal0_untagged_stubs(repo_root: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    expected_registry_rows = (
        ("data/registries/field_type_registry.json", "field_types", "field_type_id", [
            "field.stellar_density_proxy",
            "field.metallicity_proxy",
            "field.radiation_background_proxy",
            "field.galactic_region_id",
        ]),
        ("data/registries/field_binding_registry.json", "field_bindings", "field_id", [
            "field.stellar_density_proxy",
            "field.metallicity_proxy",
            "field.radiation_background_proxy",
            "field.galactic_region_id",
        ]),
        ("data/registries/galactic_region_registry.json", "galactic_regions", "region_id", [
            "region.bulge",
            "region.inner_disk",
            "region.outer_disk",
            "region.halo",
        ]),
    )

    for rel_path, row_key, id_key, expected_ids in expected_registry_rows:
        payload = _load_json(repo_root, rel_path)
        row_by_id = dict(
            (str(row.get(id_key, "")).strip(), dict(row))
            for row in _registry_rows(payload, row_key)
            if str(row.get(id_key, "")).strip()
        )
        for expected_id in expected_ids:
            row = _as_map(row_by_id.get(expected_id))
            if not row:
                findings.append(
                    {
                        "path": rel_path,
                        "line": 1,
                        "token": expected_id,
                        "message": "required GAL-0 provisional row is missing",
                    }
                )
                continue
            stability_class_id = str(_as_map(row.get("stability")).get("stability_class_id", "")).strip()
            if stability_class_id == "provisional":
                continue
            findings.append(
                {
                    "path": rel_path,
                    "line": 1,
                    "token": expected_id,
                    "message": "GAL-0 stub rows must be tagged provisional",
                }
            )

    return sorted(
        findings,
        key=lambda item: (
            _norm(str(item.get("path", ""))),
            int(item.get("line", 0) or 0),
            str(item.get("token", "")),
        ),
    )


__all__ = [
    "GAL0_SCOPE_PATHS",
    "scan_gal0_catalog_dependencies",
    "scan_gal0_untagged_stubs",
]

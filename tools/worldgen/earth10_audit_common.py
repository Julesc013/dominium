"""Shared deterministic EARTH-10 audit helpers."""

from __future__ import annotations

import os
import re
from typing import Dict, Iterable, List, Tuple


EARTH10_SCOPE_PATHS: Tuple[str, ...] = (
    "docs/audit/EARTH10_RETRO_AUDIT.md",
    "docs/worldgen/EARTH_MATERIAL_SURFACE_PROXY.md",
    "data/registries/material_proxy_registry.json",
    "data/registries/surface_flag_registry.json",
    "data/registries/field_type_registry.json",
    "data/registries/field_binding_registry.json",
    "data/registries/process_registry.json",
    "src/worldgen/earth/material",
    "src/worldgen/earth/water/water_view_engine.py",
    "src/worldgen/earth/lighting/lighting_view_engine.py",
    "tools/worldgen/earth10_probe.py",
    "tools/worldgen/tool_replay_material_proxy_window.py",
)

_TEXT_EXTENSIONS = {".json", ".md", ".py", ".schema"}
_CHEMISTRY_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("periodic table", re.compile(r"\bperiodic table\b", re.IGNORECASE)),
    ("molecule", re.compile(r"\bmolecules?\b", re.IGNORECASE)),
    ("molecular", re.compile(r"\bmolecular\b", re.IGNORECASE)),
    ("stoichiometry", re.compile(r"\bstoichi\w*\b", re.IGNORECASE)),
    ("molar", re.compile(r"\bmolar\b", re.IGNORECASE)),
    ("compound", re.compile(r"\bcompounds?\b", re.IGNORECASE)),
    ("element token", re.compile(r"\belement\.[A-Z][A-Za-z0-9_]*")),
    ("atomic_number", re.compile(r"\batomic_number\b", re.IGNORECASE)),
    ("chemical_formula", re.compile(r"\bchemical_formula\b", re.IGNORECASE)),
    ("density_kg_m3", re.compile(r"\bdensity_kg_m3\b", re.IGNORECASE)),
    ("viscosity", re.compile(r"\bviscosity\b", re.IGNORECASE)),
)
_ALLOWLIST_FRAGMENTS = (
    "no chemistry",
    "must not",
    "no periodic table",
    "no molecules",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_scope_files(repo_root: str) -> Iterable[str]:
    seen = set()
    for rel_path in EARTH10_SCOPE_PATHS:
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


def scan_earth10_chemistry_leaks(repo_root: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    for rel_path in sorted(_iter_scope_files(repo_root)):
        for line_no, line in _iter_lines(repo_root, rel_path):
            snippet = str(line).strip()
            lowered = snippet.lower()
            if (not snippet) or any(fragment in lowered for fragment in _ALLOWLIST_FRAGMENTS):
                continue
            for token, pattern in _CHEMISTRY_PATTERNS:
                if not pattern.search(snippet):
                    continue
                findings.append(
                    {
                        "path": rel_path,
                        "line": int(line_no),
                        "token": token,
                        "message": "EARTH-10 proxy layer must remain chemistry-free; remove '{}' from scoped proxy files".format(token),
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


__all__ = [
    "EARTH10_SCOPE_PATHS",
    "scan_earth10_chemistry_leaks",
]

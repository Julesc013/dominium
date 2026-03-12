"""Shared SOL-1 audit helpers for RepoX and AuditX."""

from __future__ import annotations

import os
from typing import Iterable


SOL1_SCOPE_PATHS = (
    "src/astro/illumination/",
    "src/worldgen/earth/sky/",
    "src/worldgen/earth/lighting/",
    "tools/astro/",
    "tools/worldgen/",
)

SOL1_RUNTIME_SCAN_FILES = (
    "src/astro/illumination/illumination_geometry_engine.py",
    "src/worldgen/earth/sky/astronomy_proxy_engine.py",
    "src/worldgen/earth/sky/sky_view_engine.py",
    "src/worldgen/earth/lighting/illumination_engine.py",
)


def _iter_lines(repo_root: str, rel_paths: Iterable[str]):
    for rel_path in sorted(str(path).replace("\\", "/") for path in rel_paths):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        try:
            with open(abs_path, "r", encoding="utf-8") as handle:
                lines = handle.readlines()
        except OSError:
            continue
        for line_number, text in enumerate(lines, start=1):
            yield rel_path, line_number, text.rstrip("\n")


def scan_moon_phase_storage(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    for rel_path, line_number, line in _iter_lines(repo_root, SOL1_RUNTIME_SCAN_FILES):
        snippet = str(line).strip()
        if not snippet:
            continue
        if '"lunar_phase"' in snippet or '"moon_phase"' in snippet or "'lunar_phase'" in snippet or "'moon_phase'" in snippet:
            findings.append(
                {
                    "path": rel_path,
                    "line": int(line_number),
                    "message": "Moon phase must not be stored in SOL-1 sky/lighting runtime artifacts",
                    "snippet": snippet,
                }
            )
    return findings


def scan_phase_shortcuts(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    forbidden_fragments = (
        (
            'moon_payload.get("illumination_permille"',
            "EARTH sky must not consume inline Moon illumination shortcuts from the astronomy payload",
        ),
        (
            '"illumination_permille":',
            "astronomy proxy payloads must not store inline illumination shortcut values",
        ),
        (
            "phase_cosine_proxy_permille(phase=lunar_phase_value",
            "Moon illumination must not be derived from a standalone lunar phase cosine shortcut",
        ),
    )
    for rel_path, line_number, line in _iter_lines(repo_root, SOL1_RUNTIME_SCAN_FILES):
        snippet = str(line).strip()
        if not snippet:
            continue
        for fragment, message in forbidden_fragments:
            if fragment not in snippet:
                continue
            findings.append(
                {
                    "path": rel_path,
                    "line": int(line_number),
                    "message": message,
                    "snippet": snippet,
                }
            )
    return findings


def scan_occlusion_policy_violations(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    for rel_path, line_number, line in _iter_lines(repo_root, SOL1_RUNTIME_SCAN_FILES):
        snippet = str(line).strip()
        if "occlusion.future_shadow" not in snippet:
            continue
        findings.append(
            {
                "path": rel_path,
                "line": int(line_number),
                "message": "MVP runtime must use occlusion.none_stub only; eclipse shadow policies remain reserved",
                "snippet": snippet,
            }
        )
    return findings

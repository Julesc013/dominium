"""Shared SOL-2 audit helpers for RepoX and AuditX."""

from __future__ import annotations

import os
from typing import Iterable


SOL2_SCOPE_PATHS = (
    "src/astro/ephemeris/",
    "src/astro/views/",
    "src/client/ui/",
    "tools/astro/",
)

SOL2_RUNTIME_SCAN_FILES = (
    "astro/ephemeris/kepler_proxy_engine.py",
    "astro/views/orbit_view_engine.py",
    "client/ui/viewer_shell.py",
    "tools/astro/sol2_runtime_common.py",
)

SOL2_TRUTH_SCAN_FILES = (
    "tools/xstack/sessionx/process_runtime.py",
    "server/server_boot.py",
    "schema/universe_state.schema",
    "schemas/universe_state.schema.json",
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


def scan_orbit_trace_storage(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    forbidden_fragments = (
        ("orbit_view_artifact", "Orbit view artifacts must remain derived-only and must not be stored in truth payloads"),
        ('"sampled_paths"', "Orbit sampled path traces must not be persisted in truth payloads"),
        ("orbit_trace", "Orbit traces must remain derived-only and must not be persisted in truth payloads"),
        ("trajectory_points", "Trajectory point buffers must remain derived-only and must not be persisted in truth payloads"),
    )
    for rel_path, line_number, line in _iter_lines(repo_root, SOL2_TRUTH_SCAN_FILES):
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


def scan_nbody_leaks(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    forbidden_fragments = (
        ("nbody", "MVP orbit visualization must not introduce N-body solvers"),
        ("n_body", "MVP orbit visualization must not introduce N-body solvers"),
        ("barnes_hut", "MVP orbit visualization must not introduce Barnes-Hut solvers"),
        ("verlet", "MVP orbit visualization must not introduce Verlet integration"),
        ("runge_kutta", "MVP orbit visualization must not introduce Runge-Kutta integration"),
        ("mutual_gravity", "MVP orbit visualization must remain a Kepler proxy without mutual gravity"),
        ("gravitational_force", "MVP orbit visualization must remain a Kepler proxy without force solvers"),
    )
    for rel_path, line_number, line in _iter_lines(repo_root, SOL2_RUNTIME_SCAN_FILES):
        snippet = str(line).strip().lower()
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
                    "snippet": str(line).strip(),
                }
            )
    return findings


__all__ = [
    "SOL2_RUNTIME_SCAN_FILES",
    "SOL2_SCOPE_PATHS",
    "SOL2_TRUTH_SCAN_FILES",
    "scan_nbody_leaks",
    "scan_orbit_trace_storage",
]

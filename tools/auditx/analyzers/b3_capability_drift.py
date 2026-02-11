"""A3 Capability Drift Analyzer."""

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "A3_CAPABILITY_DRIFT"
WATCH_PREFIXES = ("libs/appcore/command/", "tests/testx/capability_sets/", "data/registries/")

CAP_RE = re.compile(r'"([a-z0-9]+(?:\.[a-z0-9_]+){1,})"')


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _cap_tokens(text):
    out = set()
    for token in CAP_RE.findall(text):
        if token.startswith("ui.") or token.startswith("tool.") or token.startswith("camera.") or token.startswith("cap."):
            out.add(token)
    return out


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    command_registry = os.path.join(repo_root, "libs", "appcore", "command", "command_registry.c")
    matrix_root = os.path.join(repo_root, "tests", "testx", "capability_sets")
    matrix_yaml = os.path.join(repo_root, "tests", "testx", "CAPABILITY_MATRIX.yaml")

    command_caps = _cap_tokens(_read(command_registry))
    matrix_caps = set()
    if os.path.isfile(matrix_yaml):
        matrix_caps.update(_cap_tokens(_read(matrix_yaml)))
    if os.path.isdir(matrix_root):
        for root, dirs, files in os.walk(matrix_root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                if not name.lower().endswith((".json", ".yaml", ".yml", ".txt", ".md")):
                    continue
                matrix_caps.update(_cap_tokens(_read(os.path.join(root, name))))

    drift = sorted(cap for cap in command_caps if cap not in matrix_caps)
    findings = []
    for cap in drift[:120]:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="semantic.capability_drift",
                severity="WARN",
                confidence=0.74,
                file_path="libs/appcore/command/command_registry.c",
                evidence=[
                    "Capability referenced by command metadata without TestX matrix coverage.",
                    "Capability token: {}".format(cap),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["INV-CAPABILITY-SCOPE"],
                related_paths=[
                    "libs/appcore/command/command_registry.c",
                    "tests/testx/CAPABILITY_MATRIX.yaml",
                ],
            )
        )
    return findings


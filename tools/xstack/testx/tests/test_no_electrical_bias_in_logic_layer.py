"""FAST test: LOGIC semantics layer stays substrate-agnostic."""

from __future__ import annotations

import os
import re


TEST_ID = "test_no_electrical_bias_in_logic_layer"
TEST_TAGS = ["fast", "logic", "static", "substrate"]


_FORBIDDEN_PATTERNS = (
    re.compile(r"\bvoltage\b", re.IGNORECASE),
    re.compile(r"\bcurrent\b", re.IGNORECASE),
    re.compile(r"\bohm(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bamp(?:ere)?s?\b", re.IGNORECASE),
    re.compile(r"\bpower_factor\b", re.IGNORECASE),
    re.compile(r"\breactive_power\b", re.IGNORECASE),
    re.compile(r"\bpressure(?:_head)?\b", re.IGNORECASE),
    re.compile(r"\bpascal(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bpsi\b", re.IGNORECASE),
)


def _read(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _logic_paths(repo_root: str):
    for rel_path in (
        "schema/logic/signal_type.schema",
        "schema/logic/logic_policy.schema",
        "data/registries/signal_type_registry.json",
    ):
        yield rel_path
    for root_rel in ("src/logic", "tools/logic"):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                rel_lower = rel_path.lower()
                if "transducer" in rel_lower or "carrier" in rel_lower:
                    continue
                yield rel_path


def run(repo_root: str):
    for rel_path in _logic_paths(repo_root):
        text = _read(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in _FORBIDDEN_PATTERNS):
                continue
            return {
                "status": "fail",
                "message": "{}:{} contains substrate-specific unit bias: {}".format(rel_path, line_no, snippet[:120]),
            }
    return {"status": "pass", "message": "LOGIC semantics layer remains substrate-agnostic"}

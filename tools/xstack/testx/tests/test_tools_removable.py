"""FAST test: runtime must stay tools-removable and avoid tools contamination."""

from __future__ import annotations

import os
import re


TEST_ID = "test_tools_removable"
TEST_TAGS = ["fast", "architecture", "tools"]


REQUIRED_CMAKE_TOKENS = (
    'option(DOM_BUILD_TOOLS "Build tools" OFF)',
    "if(DOM_BUILD_TOOLS)",
    "add_subdirectory(tools)",
    "dom_assert_no_link(domino_engine",
    "tools_shared",
    "dominium-tools",
)

RUNTIME_ROOTS = ("src", "engine", "game", "client", "server")
FORBIDDEN_TOOL_PATTERNS = (
    re.compile(r"^\s*from\s+tools\.auditx\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.auditx\b", re.IGNORECASE),
    re.compile(r"^\s*from\s+tools\.governance\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.governance\b", re.IGNORECASE),
    re.compile(r"^\s*from\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]tools/", re.IGNORECASE),
)


def run(repo_root: str):
    cmake_path = os.path.join(repo_root, "CMakeLists.txt")
    if not os.path.isfile(cmake_path):
        return {"status": "fail", "message": "missing CMakeLists.txt"}
    cmake_text = open(cmake_path, "r", encoding="utf-8", errors="ignore").read()
    for token in REQUIRED_CMAKE_TOKENS:
        if token in cmake_text:
            continue
        return {"status": "fail", "message": "missing tools-removability boundary token '{}'".format(token)}

    hits = []
    for root in RUNTIME_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith((".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp")):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                try:
                    lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
                except OSError:
                    continue
                for line_no, line in enumerate(lines, start=1):
                    if not any(pattern.search(line) for pattern in FORBIDDEN_TOOL_PATTERNS):
                        continue
                    hits.append("{}:{}".format(rel_path, line_no))
    if hits:
        return {"status": "fail", "message": "runtime tools contamination detected: {}".format(len(hits))}

    return {"status": "pass", "message": "tools-removable runtime boundaries verified"}

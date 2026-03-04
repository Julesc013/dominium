"""STRICT test: direct cross-shard field access patterns are forbidden."""

from __future__ import annotations

import os
import re


TEST_ID = "test_cross_shard_field_blocked"
TEST_TAGS = ["strict", "fields", "shard", "governance"]

_CROSS_SHARD_FIELD_PATTERNS = (
    re.compile(
        r"(field_(?:layers|cells|sample_rows)|field_boundary).*(target_shard_id|source_shard_id|active_shard_id|owner_shard_id|shard_id)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(target_shard_id|source_shard_id|active_shard_id|owner_shard_id|shard_id).*(field_(?:layers|cells|sample_rows)|field_boundary)",
        re.IGNORECASE,
    ),
)

_SCAN_ROOTS = (
    "src",
    os.path.join("tools", "xstack", "sessionx"),
)

_SKIP_PREFIXES = (
    "docs/",
    "schema/",
    "schemas/",
    "tools/auditx/analyzers/",
    "tools/xstack/testx/tests/",
)

_ALLOWED_FILES = {
    "tools/xstack/sessionx/process_runtime.py",
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(repo_root: str):
    violations = []
    for root_rel in _SCAN_ROOTS:
        root_abs = os.path.join(repo_root, root_rel)
        if not os.path.isdir(root_abs):
            continue
        for walk_root, _dirs, files in os.walk(root_abs):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(_SKIP_PREFIXES):
                    continue
                if rel_path in _ALLOWED_FILES:
                    continue
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _CROSS_SHARD_FIELD_PATTERNS):
                        continue
                    violations.append("{}:{} {}".format(rel_path, line_no, snippet[:120]))
                    break
    if violations:
        return {
            "status": "fail",
            "message": "cross-shard field direct access patterns detected: {}".format("; ".join(violations[:5])),
        }
    return {"status": "pass", "message": "cross-shard field access remains boundary-artifact only"}


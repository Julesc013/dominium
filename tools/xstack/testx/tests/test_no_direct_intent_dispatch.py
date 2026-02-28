"""FAST test: intent envelope construction must remain on whitelisted dispatch paths."""

from __future__ import annotations

import os
import fnmatch
import json


TEST_ID = "test_no_direct_intent_dispatch"
TEST_TAGS = ["fast", "architecture", "control"]


WHITELIST_REGISTRY = "data/registries/intent_dispatch_whitelist.json"
DEFAULT_PATTERNS = (
    "src/net/**",
    "src/control/**",
    "tools/xstack/testx/tests/**",
)
REQUIRED_MARKERS = (
    '"envelope_id"',
    '"payload_schema_id"',
    '"pack_lock_hash"',
    '"authority_summary"',
)
BUILDER_TOKENS = (
    "build_client_intent_envelope(",
    "_build_envelope(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_patterns(repo_root: str):
    abs_path = os.path.join(repo_root, WHITELIST_REGISTRY.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return list(DEFAULT_PATTERNS)
    if not isinstance(payload, dict):
        return list(DEFAULT_PATTERNS)
    record = payload.get("record")
    if not isinstance(record, dict):
        return list(DEFAULT_PATTERNS)
    rows = record.get("allowed_file_patterns")
    if not isinstance(rows, list):
        return list(DEFAULT_PATTERNS)
    patterns = sorted(set(_norm(str(item).strip()) for item in rows if str(item).strip()))
    return patterns or list(DEFAULT_PATTERNS)


def _path_allowed(rel_path: str, patterns) -> bool:
    rel_norm = _norm(rel_path)
    for pattern in list(patterns or []):
        if fnmatch.fnmatch(rel_norm, _norm(pattern)):
            return True
    return False


def run(repo_root: str):
    whitelist_path = os.path.join(repo_root, WHITELIST_REGISTRY.replace("/", os.sep))
    if not os.path.isfile(whitelist_path):
        return {"status": "fail", "message": "missing intent dispatch whitelist registry"}

    patterns = _load_patterns(repo_root)
    hits = []
    for rel_root in ("src",):
        abs_root = os.path.join(repo_root, rel_root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(("tools/xstack/testx/tests/", "tools/xstack/out/", "tools/auditx/analyzers/", "tests/")):
                    continue
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                if not text:
                    continue
                has_literal = all(marker in text for marker in REQUIRED_MARKERS)
                has_builder = any(marker in text for marker in BUILDER_TOKENS)
                if (not has_literal) and (not has_builder):
                    continue
                if _path_allowed(rel_path, patterns):
                    continue
                hits.append(rel_path)
    if hits:
        return {
            "status": "fail",
            "message": "intent envelope construction outside whitelist: {}".format(len(hits)),
        }

    return {"status": "pass", "message": "intent envelope construction remains whitelist-restricted"}

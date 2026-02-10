#!/usr/bin/env python3
"""Identity fingerprint helpers for Dominium governance invariants."""

import hashlib
import json
import os
import re


ONTOLOGY_COMMITMENT = "Assemblies|Fields|Processes|Agents|Law"
CANON_INDEX_REL = os.path.join("docs", "architecture", "CANON_INDEX.md")
RULESET_ROOT_REL = os.path.join("repo", "repox", "rulesets")
GATE_SCRIPT_REL = os.path.join("scripts", "dev", "gate.py")
DOCTRINE_REL = os.path.join("docs", "governance", "UNBOUNDED_AGENTIC_DEVELOPMENT.md")
STATUS_NOW_REL = os.path.join("docs", "STATUS_NOW.md")


def _norm(path):
    return os.path.normpath(path)


def _to_posix(path):
    return path.replace("\\", "/")


def _sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _file_sha256(path):
    if not os.path.isfile(path):
        return ""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _collect_ruleset_hash(repo_root):
    root = os.path.join(repo_root, RULESET_ROOT_REL)
    lines = []
    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            if not name.endswith(".json"):
                continue
            rel = _to_posix(os.path.join(RULESET_ROOT_REL, name))
            digest = _file_sha256(os.path.join(root, name))
            lines.append("{}={}".format(rel, digest))
    return _sha256_text("\n".join(lines))


def _collect_testx_suite_set(repo_root):
    root = os.path.join(repo_root, "tests")
    ids = set()
    pattern = re.compile(r"dom_add_testx\s*\(\s*NAME\s+([A-Za-z0-9_.-]+)")
    for dirpath, _, filenames in os.walk(root):
        if "CMakeLists.txt" not in filenames:
            continue
        path = os.path.join(dirpath, "CMakeLists.txt")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
        except OSError:
            continue
        for match in pattern.finditer(text):
            ids.add(match.group(1))
    ordered = sorted(ids)
    return ordered, _sha256_text("\n".join(ordered))


def identity_input_paths():
    return [
        _to_posix(CANON_INDEX_REL),
        _to_posix(GATE_SCRIPT_REL),
        _to_posix(DOCTRINE_REL),
        _to_posix(STATUS_NOW_REL),
    ]


def build_identity_payload(repo_root):
    repo_root = _norm(os.path.abspath(repo_root))
    test_ids, test_hash = _collect_testx_suite_set(repo_root)
    inputs = {
        "ontology_commitment": {
            "value": ONTOLOGY_COMMITMENT,
            "sha256": _sha256_text(ONTOLOGY_COMMITMENT),
        },
        "canon_index": {
            "path": _to_posix(CANON_INDEX_REL),
            "sha256": _file_sha256(os.path.join(repo_root, CANON_INDEX_REL)),
        },
        "repox_rulesets": {
            "path": _to_posix(RULESET_ROOT_REL),
            "sha256": _collect_ruleset_hash(repo_root),
        },
        "testx_suite_set": {
            "source_root": "tests",
            "suite_count": len(test_ids),
            "sha256": test_hash,
        },
        "gate_runner": {
            "path": _to_posix(GATE_SCRIPT_REL),
            "sha256": _file_sha256(os.path.join(repo_root, GATE_SCRIPT_REL)),
        },
        "unbounded_doctrine": {
            "path": _to_posix(DOCTRINE_REL),
            "sha256": _file_sha256(os.path.join(repo_root, DOCTRINE_REL)),
        },
        "status_now_snapshot": {
            "path": _to_posix(STATUS_NOW_REL),
            "sha256": _file_sha256(os.path.join(repo_root, STATUS_NOW_REL)),
        },
    }
    fingerprint = _sha256_text(json.dumps(inputs, sort_keys=True, separators=(",", ":")))
    return {
        "schema_id": "dominium.audit.identity_fingerprint",
        "schema_version": "1.0.0",
        "inputs": inputs,
        "fingerprint_sha256": fingerprint,
    }

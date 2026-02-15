#!/usr/bin/env python3
"""Deterministic TestX runner with profile selection, sharding, and cache."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


TESTS_ROOT_REL = "tools/xstack/testx/tests"
CACHE_ROOT_REL = ".xstack_cache/xstack_testx"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _read_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid json"


def _file_sha(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _hash_text(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def _run_cmd(repo_root: str, argv: List[str]) -> str:
    result = subprocess.run(
        argv,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(result.returncode) != 0:
        return ""
    return str(result.stdout or "")


def _changed_files(repo_root: str) -> List[str]:
    rows: List[str] = []
    diff_text = _run_cmd(repo_root, ["git", "diff", "--name-only", "--diff-filter=ACMR", "origin/main...HEAD"])
    for line in diff_text.splitlines():
        token = _norm(line.strip())
        if token:
            rows.append(token)
    status_text = _run_cmd(repo_root, ["git", "status", "--porcelain", "-uall"])
    for line in status_text.splitlines():
        token = line[3:].strip() if len(line) >= 3 else line.strip()
        token = _norm(token)
        if token:
            rows.append(token)
    return sorted(set(rows))


def _impacted_tags(changed: List[str]) -> List[str]:
    tags = {"smoke"}
    for path in changed:
        if path.startswith("schemas/"):
            tags.add("schema")
        if path.startswith("packs/"):
            tags.add("pack")
        if path.startswith("bundles/"):
            tags.add("bundle")
        if path.startswith("tools/xstack/pack_"):
            tags.add("pack")
        if path.startswith("tools/xstack/bundle_"):
            tags.add("bundle")
        if path.startswith("tools/xstack/registry_compile/"):
            tags.add("registry")
        if path.startswith("tools/xstack/compatx/"):
            tags.add("schema")
        if path.startswith("tools/xstack/session"):
            tags.add("session")
        if path.startswith("tools/xstack/securex/"):
            tags.add("securex")
        if path.startswith("tools/xstack/repox/"):
            tags.add("repox")
        if path.startswith("tools/xstack/auditx/"):
            tags.add("auditx")
        if path.startswith("tools/xstack/controlx/") or path.startswith("tools/xstack/run"):
            tags.add("runner")
        if path.startswith("tools/xstack/lockfile_"):
            tags.add("lockfile")
    return sorted(tags)


def _discover_tests(repo_root: str) -> List[Dict[str, object]]:
    tests_root = os.path.join(repo_root, TESTS_ROOT_REL.replace("/", os.sep))
    out: List[Dict[str, object]] = []
    if not os.path.isdir(tests_root):
        return out
    for root, _dirs, files in os.walk(tests_root):
        for name in sorted(files):
            if not name.startswith("test_") or not name.endswith(".py"):
                continue
            abs_path = os.path.join(root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            out.append(
                {
                    "abs_path": abs_path,
                    "rel_path": rel_path,
                }
            )
    return sorted(out, key=lambda row: str(row.get("rel_path", "")))


def _load_test_module(module_path: str, module_token: str):
    spec = importlib.util.spec_from_file_location(module_token, module_path)
    if not spec or not spec.loader:
        raise RuntimeError("unable to create module spec for '{}'".format(module_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _test_id(module, rel_path: str) -> str:
    token = str(getattr(module, "TEST_ID", "")).strip()
    if token:
        return token
    return _norm(rel_path).replace("/", ".").replace(".py", "")


def _test_tags(module) -> List[str]:
    raw = getattr(module, "TEST_TAGS", ["smoke"])
    if not isinstance(raw, list):
        return ["smoke"]
    tags = [str(item).strip() for item in raw if str(item).strip()]
    return sorted(set(tags or ["smoke"]))


def _should_include_test(profile: str, tags: List[str], impacted: List[str]) -> bool:
    token = str(profile or "").strip().upper() or "FAST"
    if token in ("STRICT", "FULL"):
        return True
    tag_set = set(tags)
    impacted_set = set(impacted)
    if "smoke" in tag_set:
        return True
    return bool(tag_set.intersection(impacted_set))


def _shard_match(test_id: str, shards: int, shard_index: int) -> bool:
    digest = hashlib.sha256(str(test_id).encode("utf-8")).hexdigest()
    bucket = int(digest, 16) % int(shards)
    return bucket == int(shard_index)


def _repo_state_token(repo_root: str, changed: List[str]) -> str:
    head = _run_cmd(repo_root, ["git", "rev-parse", "HEAD"]).strip()
    dirty = _run_cmd(repo_root, ["git", "status", "--porcelain"])
    changed_hashes = {}
    for rel in sorted(set(changed)):
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if os.path.isfile(abs_path):
            try:
                changed_hashes[rel] = _file_sha(abs_path)
            except OSError:
                changed_hashes[rel] = "<unreadable>"
        else:
            changed_hashes[rel] = "<missing>"
    payload = {
        "head": head,
        "dirty": dirty,
        "changed": changed,
        "changed_hashes": changed_hashes,
    }
    return _hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _cache_path(repo_root: str, cache_key: str) -> str:
    return os.path.join(repo_root, CACHE_ROOT_REL.replace("/", os.sep), "{}.json".format(cache_key))


def _cache_key(profile: str, test_id: str, test_sha: str, repo_state: str, shards: int, shard_index: int) -> str:
    payload = {
        "profile": str(profile).upper(),
        "test_id": str(test_id),
        "test_sha": str(test_sha),
        "repo_state": str(repo_state),
        "shards": int(shards),
        "shard_index": int(shard_index),
    }
    return _hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _result_status(raw: Dict[str, object]) -> str:
    token = str(raw.get("status", "")).strip().lower()
    if token in ("pass", "fail", "refusal"):
        return token
    return "fail"


def _result_message(raw: Dict[str, object], default: str) -> str:
    token = str(raw.get("message", "")).strip()
    return token or default


def run_testx_suite(
    repo_root: str,
    profile: str,
    shards: int = 1,
    shard_index: int = 0,
    cache_enabled: bool = True,
) -> Dict[str, object]:
    token = str(profile or "").strip().upper() or "FAST"
    shard_count = int(shards)
    index = int(shard_index)
    if shard_count < 1:
        return {
            "status": "refusal",
            "message": "invalid shard count {} (must be >= 1)".format(shard_count),
            "findings": [
                {
                    "severity": "refusal",
                    "code": "refuse.testx.invalid_shard_count",
                    "message": "shards must be >= 1",
                }
            ],
            "tests": [],
        }
    if index < 0 or index >= shard_count:
        return {
            "status": "refusal",
            "message": "invalid shard-index {} for shard count {}".format(index, shard_count),
            "findings": [
                {
                    "severity": "refusal",
                    "code": "refuse.testx.invalid_shard_index",
                    "message": "shard-index out of range",
                }
            ],
            "tests": [],
        }

    changed = _changed_files(repo_root)
    impacted = _impacted_tags(changed)
    repo_state = _repo_state_token(repo_root, changed)
    discovered = _discover_tests(repo_root)

    selected: List[Dict[str, object]] = []
    for row in discovered:
        rel_path = str(row.get("rel_path", ""))
        abs_path = str(row.get("abs_path", ""))
        module_token = "xstack_testx_{}".format(_hash_text(rel_path)[:12])
        try:
            module = _load_test_module(abs_path, module_token)
        except Exception as exc:
            selected.append(
                {
                    "id": rel_path,
                    "rel_path": rel_path,
                    "tags": ["smoke"],
                    "module_error": str(exc),
                    "module": None,
                    "test_sha": _file_sha(abs_path),
                }
            )
            continue
        test_id = _test_id(module, rel_path)
        tags = _test_tags(module)
        if not _should_include_test(token, tags, impacted):
            continue
        if not _shard_match(test_id, shard_count, index):
            continue
        selected.append(
            {
                "id": test_id,
                "rel_path": rel_path,
                "tags": tags,
                "module": module,
                "module_error": "",
                "test_sha": _file_sha(abs_path),
            }
        )

    selected = sorted(selected, key=lambda row: str(row.get("id", "")))

    test_rows: List[Dict[str, object]] = []
    findings: List[Dict[str, object]] = []
    cache_hits = 0
    cache_misses = 0
    for row in selected:
        test_id = str(row.get("id", ""))
        module = row.get("module")
        rel_path = str(row.get("rel_path", ""))
        module_error = str(row.get("module_error", ""))
        test_sha = str(row.get("test_sha", ""))
        cache_key = _cache_key(token, test_id, test_sha, repo_state, shard_count, index)
        cache_file = _cache_path(repo_root, cache_key)

        if cache_enabled and os.path.isfile(cache_file):
            payload, cache_error = _read_json(cache_file)
            if not cache_error and isinstance(payload, dict):
                cache_hits += 1
                test_rows.append(
                    {
                        "test_id": test_id,
                        "status": str(payload.get("status", "fail")),
                        "message": str(payload.get("message", "")),
                        "duration_ms": int(payload.get("duration_ms", 0) or 0),
                        "cache": "hit",
                        "rel_path": rel_path,
                    }
                )
                continue
        cache_misses += 1

        started = time.perf_counter()
        if module_error:
            status = "fail"
            message = "module load failed: {}".format(module_error)
        elif not hasattr(module, "run"):
            status = "fail"
            message = "test module missing run(repo_root) entrypoint"
        else:
            try:
                raw = module.run(repo_root)  # type: ignore[attr-defined]
                if not isinstance(raw, dict):
                    raw = {"status": "fail", "message": "test returned non-object payload"}
                status = _result_status(raw)
                message = _result_message(raw, "test executed")
            except Exception as exc:
                status = "fail"
                message = "test execution crashed: {}".format(str(exc))
        elapsed_ms = int((time.perf_counter() - started) * 1000.0)
        test_row = {
            "test_id": test_id,
            "status": status,
            "message": message,
            "duration_ms": elapsed_ms,
            "cache": "miss",
            "rel_path": rel_path,
        }
        test_rows.append(test_row)

        if cache_enabled:
            _write_json(
                cache_file,
                {
                    "status": status,
                    "message": message,
                    "duration_ms": elapsed_ms,
                },
            )

        if status in ("fail", "refusal"):
            findings.append(
                {
                    "severity": "refusal" if status == "refusal" else "fail",
                    "code": "testx.{}".format(status),
                    "message": "{}: {}".format(test_id, message),
                }
            )

    ordered_rows = sorted(test_rows, key=lambda row: (str(row.get("test_id", "")), str(row.get("status", ""))))
    ordered_findings = sorted(
        findings,
        key=lambda row: (str(row.get("severity", "")), str(row.get("code", "")), str(row.get("message", ""))),
    )
    status = "pass"
    if any(str(row.get("status", "")) == "refusal" for row in ordered_rows):
        status = "refusal"
    elif any(str(row.get("status", "")) == "fail" for row in ordered_rows):
        status = "fail"

    return {
        "status": status,
        "message": "testx {} (selected_tests={}, cache_hits={}, cache_misses={})".format(
            "passed" if status == "pass" else "completed_with_findings",
            len(ordered_rows),
            cache_hits,
            cache_misses,
        ),
        "findings": ordered_findings,
        "tests": ordered_rows,
        "selection": {
            "profile": token,
            "impacted_tags": impacted,
            "changed_files": changed,
            "selected_count": len(ordered_rows),
            "shards": shard_count,
            "shard_index": index,
            "cache": "on" if cache_enabled else "off",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic TestX tool-suite tests.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--cache", default="on", choices=("on", "off"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_testx_suite(
        repo_root=repo_root,
        profile=str(args.profile),
        shards=int(args.shards),
        shard_index=int(args.shard_index),
        cache_enabled=str(args.cache).strip().lower() != "off",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    status = str(result.get("status", "error"))
    if status == "pass":
        return 0
    if status == "refusal":
        return 2
    if status == "fail":
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

"""STRICT test: repeated dist builds must be reproducible."""

from __future__ import annotations

import sys


TEST_ID = "testx.packaging.determinism"
TEST_TAGS = ["strict", "registry", "bundle"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.packagingx import build_dist_layout, validate_dist_layout

    out_a = "build/dist.testx.det.a"
    out_b = "build/dist.testx.det.b"
    first = build_dist_layout(repo_root=repo_root, bundle_id="bundle.base.lab", out_dir=out_a, use_cache=True)
    if first.get("result") != "complete":
        return {"status": "fail", "message": "first deterministic packaging build failed"}
    second = build_dist_layout(repo_root=repo_root, bundle_id="bundle.base.lab", out_dir=out_b, use_cache=True)
    if second.get("result") != "complete":
        return {"status": "fail", "message": "second deterministic packaging build failed"}

    check_a = validate_dist_layout(repo_root=repo_root, dist_root=out_a)
    check_b = validate_dist_layout(repo_root=repo_root, dist_root=out_b)
    if check_a.get("result") != "complete" or check_b.get("result") != "complete":
        return {"status": "fail", "message": "deterministic packaging validation failed"}

    keys = ("canonical_content_hash", "manifest_hash", "lockfile_hash", "pack_lock_hash")
    for key in keys:
        if str(check_a.get(key, "")) != str(check_b.get(key, "")):
            return {"status": "fail", "message": "repeated build mismatch for '{}'".format(key)}

    if dict(check_a.get("registry_hashes") or {}) != dict(check_b.get("registry_hashes") or {}):
        return {"status": "fail", "message": "repeated build registry hashes mismatch"}
    return {"status": "pass", "message": "repeated packaging build is deterministic"}


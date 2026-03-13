"""FAST test: release manifest descriptor hashes match emitted descriptors."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "test_descriptor_hash_matches"
TEST_TAGS = ["fast", "release", "descriptor"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.release1_testlib import build_manifest_payload, product_descriptor_hash, release_fixture

    with release_fixture() as dist_root:
        payload = build_manifest_payload(dist_root)
        target = None
        for row in list(payload.get("artifacts") or []):
            item = dict(row or {})
            if str(item.get("artifact_name", "")).strip() == "bin/client":
                target = item
                break
        if not target:
            return {"status": "fail", "message": "client artifact missing from generated manifest"}
        proc = subprocess.run(
            [sys.executable, os.path.join(dist_root, "bin", "client"), "--descriptor"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
            encoding="utf-8",
        )
    if int(proc.returncode or 0) != 0:
        return {"status": "fail", "message": "fixture client descriptor command failed"}
    descriptor = json.loads(proc.stdout)
    expected_hash = canonical_sha256(descriptor)
    if str(target.get("endpoint_descriptor_hash", "")).strip() != expected_hash:
        return {"status": "fail", "message": "manifest endpoint_descriptor_hash does not match emitted descriptor hash"}
    if expected_hash != product_descriptor_hash("client"):
        return {"status": "fail", "message": "fixture descriptor hash helper drifted from emitted descriptor"}
    return {"status": "pass", "message": "descriptor hashes match emitted descriptors"}

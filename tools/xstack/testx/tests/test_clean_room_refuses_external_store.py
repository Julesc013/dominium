"""FAST test: DIST-3 generated-output scan catches external store leaks."""

from __future__ import annotations

import os


TEST_ID = "test_clean_room_refuses_external_store"
TEST_TAGS = ["fast", "dist", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist3_testlib import generated_output_hits, temp_bundle_fixture

    with temp_bundle_fixture(repo_root) as bundle_root:
        leak_path = os.path.join(bundle_root, "store", "logs", "external_store.log")
        os.makedirs(os.path.dirname(leak_path), exist_ok=True)
        with open(leak_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("external path C:\\outside\\store\\leak.txt\n")
        hits = generated_output_hits(bundle_root)
    if not hits:
        return {"status": "fail", "message": "DIST-3 generated-output scan missed an external store path leak"}
    if not any(str(row.get("external", "")).lower() == "true" or bool(row.get("external")) for row in hits):
        return {"status": "fail", "message": "DIST-3 generated-output hits did not classify the leak as external"}
    return {"status": "pass", "message": "DIST-3 generated-output scan detects external store leaks deterministically"}

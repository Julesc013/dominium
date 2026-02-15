"""FAST test: deterministic refusal when source pack is unavailable for import."""

from __future__ import annotations

import os
import sys
import tempfile


TEST_ID = "testx.data.derived_refusal_source_missing"
TEST_TAGS = ["smoke", "pack", "registry"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.data.tool_spice_import import run_import

    temp_root = tempfile.mkdtemp(prefix="dominium_source_missing_")
    missing_source = os.path.join(temp_root, "missing", "org.dominium.sol.spice")
    derived_pack = os.path.join(temp_root, "derived", "org.dominium.sol.ephemeris")
    result = run_import(
        repo_root=repo_root,
        source_pack=missing_source,
        derived_pack=derived_pack,
        pack_lock_hash="hash.lock.test.refusal",
        write_manifest=True,
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "source-missing import did not refuse"}
    first = (result.get("errors") or [{}])[0]
    if str(first.get("code", "")) != "refusal.data_source_missing":
        return {"status": "fail", "message": "unexpected refusal code for source-missing import"}
    return {"status": "pass", "message": "source-missing refusal verified"}


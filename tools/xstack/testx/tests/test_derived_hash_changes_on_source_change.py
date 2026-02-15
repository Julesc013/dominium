"""FAST test: source changes deterministically invalidate derived artifact hashes."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile


TEST_ID = "testx.data.derived_hash_changes_on_source_change"
TEST_TAGS = ["smoke", "pack", "registry"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.data.tool_spice_import import run_import

    temp_root = tempfile.mkdtemp(prefix="dominium_derived_hash_change_")
    try:
        source_pack = os.path.join(temp_root, "source", "org.dominium.sol.spice")
        derived_pack = os.path.join(temp_root, "derived", "org.dominium.sol.ephemeris")
        os.makedirs(os.path.dirname(source_pack), exist_ok=True)
        os.makedirs(os.path.dirname(derived_pack), exist_ok=True)
        shutil.copytree(os.path.join(repo_root, "packs", "source", "org.dominium.sol.spice"), source_pack)

        first = run_import(
            repo_root=repo_root,
            source_pack=source_pack,
            derived_pack=derived_pack,
            pack_lock_hash="hash.lock.test.derived",
            write_manifest=True,
        )
        if first.get("result") != "complete":
            return {"status": "fail", "message": "first import failed in source-change hash test"}

        kernel_path = os.path.join(source_pack, "data", "kernels", "naif0012.tls")
        with open(kernel_path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write("PATCH:deterministic-test-change\n")

        second = run_import(
            repo_root=repo_root,
            source_pack=source_pack,
            derived_pack=derived_pack,
            pack_lock_hash="hash.lock.test.derived",
            write_manifest=True,
        )
        if second.get("result") != "complete":
            return {"status": "fail", "message": "second import failed in source-change hash test"}

        if str(first.get("source_hash", "")) == str(second.get("source_hash", "")):
            return {"status": "fail", "message": "source_hash did not change after source kernel mutation"}
        if str(first.get("output_hash", "")) == str(second.get("output_hash", "")):
            return {"status": "fail", "message": "output_hash did not change after source kernel mutation"}
        return {"status": "pass", "message": "derived hash invalidation on source change verified"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


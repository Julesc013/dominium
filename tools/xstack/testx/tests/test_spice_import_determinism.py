"""FAST test: deterministic SPICE import yields stable derived ephemeris hashes."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile


TEST_ID = "testx.data.spice_import_determinism"
TEST_TAGS = ["smoke", "pack", "registry"]


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.data.tool_spice_import import run_import

    temp_root = tempfile.mkdtemp(prefix="dominium_spice_import_")
    try:
        derived_a = os.path.join(temp_root, "derived_a")
        derived_b = os.path.join(temp_root, "derived_b")
        first = run_import(
            repo_root=repo_root,
            source_pack="packs/source/org.dominium.sol.spice",
            derived_pack=derived_a,
            pack_lock_hash="hash.lock.test.spice",
            write_manifest=True,
        )
        second = run_import(
            repo_root=repo_root,
            source_pack="packs/source/org.dominium.sol.spice",
            derived_pack=derived_b,
            pack_lock_hash="hash.lock.test.spice",
            write_manifest=True,
        )
        if first.get("result") != "complete" or second.get("result") != "complete":
            return {"status": "fail", "message": "SPICE import failed to complete deterministically"}

        if str(first.get("source_hash", "")) != str(second.get("source_hash", "")):
            return {"status": "fail", "message": "SPICE source hash drift detected"}
        if str(first.get("output_hash", "")) != str(second.get("output_hash", "")):
            return {"status": "fail", "message": "SPICE output hash drift detected"}
        if int(first.get("sample_count", 0) or 0) <= 0:
            return {"status": "fail", "message": "SPICE import generated zero samples"}

        a_json = _read_json(os.path.join(derived_a, "data", "sol_ephemeris_table.json"))
        b_json = _read_json(os.path.join(derived_b, "data", "sol_ephemeris_table.json"))
        if a_json != b_json:
            return {"status": "fail", "message": "SPICE derived payload differs across identical imports"}

        prov = dict(a_json.get("provenance") or {})
        if not bool(prov.get("deterministic", False)):
            return {"status": "fail", "message": "SPICE provenance deterministic flag is missing"}
        if str(prov.get("generator_tool_id", "")) != "tools/data/tool_spice_import":
            return {"status": "fail", "message": "SPICE provenance generator_tool_id mismatch"}

        return {"status": "pass", "message": "SPICE import determinism verified"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


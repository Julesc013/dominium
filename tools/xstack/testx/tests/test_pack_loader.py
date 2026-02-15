"""TestX pack loader and contribution parser checks."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.pack.loader"
TEST_TAGS = ["smoke", "pack"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.pack_contrib.parser import parse_contributions
    from tools.xstack.pack_loader.loader import load_pack_set

    loaded = load_pack_set(repo_root=repo_root)
    if loaded.get("result") != "complete":
        return {"status": "fail", "message": "pack load failed"}

    contrib = parse_contributions(repo_root=repo_root, packs=loaded.get("packs") or [])
    if contrib.get("result") != "complete":
        return {"status": "fail", "message": "pack contribution parse failed"}

    if int(loaded.get("pack_count", 0)) <= 0:
        return {"status": "fail", "message": "expected at least one discovered pack"}
    return {"status": "pass", "message": "pack loader checks passed"}


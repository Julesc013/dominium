"""FAST test: worktree hygiene allowlist document is present."""

from __future__ import annotations

import os


TEST_ID = "test_worktree_leftovers_allowlist_present"
TEST_TAGS = ["fast", "governance", "repox"]


def run(repo_root: str):
    rel_path = os.path.join("docs", "audit", "WORKTREE_LEFTOVERS.md")
    abs_path = os.path.join(repo_root, rel_path)
    if not os.path.isfile(abs_path):
        return {
            "status": "fail",
            "message": "worktree leftovers allowlist is missing ({})".format(rel_path),
        }
    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    if "INV-WORKTREE-HYGIENE" not in text:
        return {
            "status": "fail",
            "message": "allowlist doc must mention INV-WORKTREE-HYGIENE",
        }
    return {"status": "pass", "message": "worktree leftovers allowlist present"}


"""FAST test: rollback restores the previous managed component state."""

from __future__ import annotations

import argparse
import os
import tempfile


TEST_ID = "test_rollback_restores_previous_components"
TEST_TAGS = ["fast", "release", "update-model", "rollback"]


def run(repo_root: str):
    del repo_root
    from src.release import append_install_transaction
    from tools.setup.setup_cli import rollback_from_plan, transaction_log_path, write_json

    with tempfile.TemporaryDirectory() as tmp:
        install_root = os.path.join(tmp, "install")
        backup_root = install_root + ".rollback.seed"
        os.makedirs(os.path.join(install_root, "bin"), exist_ok=True)
        os.makedirs(os.path.join(backup_root, "bin"), exist_ok=True)
        with open(os.path.join(install_root, "bin", "client"), "w", encoding="utf-8") as handle:
            handle.write("new\n")
        with open(os.path.join(backup_root, "bin", "client"), "w", encoding="utf-8") as handle:
            handle.write("old\n")
        write_json(os.path.join(install_root, ".dsu", "rollback_index.json"), {"backups": [{"transaction_id": "tx.seed", "path": backup_root}]})
        append_install_transaction(
            transaction_log_path(install_root),
            {
                "transaction_id": "tx.seed",
                "action": "update.apply",
                "from_release_id": "release.old",
                "to_release_id": "release.new",
                "backup_path": backup_root,
                "status": "complete",
                "install_profile_id": "install.profile.full",
            },
        )
        code, _payload = rollback_from_plan(
            {"install_root": install_root, "from_release_id": "release.new", "install_profile_id": "install.profile.full"},
            argparse.Namespace(install_root=install_root, to="release.old"),
            True,
        )
        if int(code) != 0:
            return {"status": "fail", "message": "rollback did not complete successfully"}
        with open(os.path.join(install_root, "bin", "client"), "r", encoding="utf-8") as handle:
            if handle.read() != "old\n":
                return {"status": "fail", "message": "rollback did not restore the previous client binary content"}
    return {"status": "pass", "message": "rollback restores the previous managed component state"}

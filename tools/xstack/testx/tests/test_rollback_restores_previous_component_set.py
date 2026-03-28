"""FAST test: rollback restores prior content and preserves recorded component-set metadata."""

from __future__ import annotations

import argparse
import os
import tempfile


TEST_ID = "test_rollback_restores_previous_component_set"
TEST_TAGS = ["fast", "release", "release-index-policy", "rollback"]


def run(repo_root: str):
    del repo_root
    from release import append_install_transaction, load_install_transaction_log
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
        write_json(
            os.path.join(install_root, ".dsu", "rollback_index.json"),
            {"backups": [{"transaction_id": "tx.seed", "path": backup_root}]},
        )
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
                "resolution_policy_id": "policy.latest_compatible",
                "install_plan_hash": "55" * 32,
                "prior_component_set_hash": "66" * 32,
                "selected_component_ids": ["binary.client", "binary.server"],
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
                return {"status": "fail", "message": "rollback did not restore the previous client content"}
        transactions = list(load_install_transaction_log(transaction_log_path(install_root)).get("transactions") or [])
        rollback_row = dict(transactions[-1] or {}) if transactions else {}
        if str(rollback_row.get("action", "")).strip() != "update.rollback":
            return {"status": "fail", "message": "rollback transaction was not recorded"}
        if str(rollback_row.get("install_plan_hash", "")).strip() != "55" * 32:
            return {"status": "fail", "message": "rollback transaction did not preserve install_plan_hash"}
        if str(rollback_row.get("prior_component_set_hash", "")).strip() != "66" * 32:
            return {"status": "fail", "message": "rollback transaction did not preserve prior_component_set_hash"}
    return {"status": "pass", "message": "rollback restores prior content and preserves component-set metadata"}

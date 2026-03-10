"""FAST test: new semantic contract tokens must be registered explicitly."""

from __future__ import annotations

import os
import sys
import tempfile


TEST_ID = "test_contract_change_requires_registry_update"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "registry"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.compatx.core.semantic_contract_validator import contract_tokens_missing_entries, load_semantic_contract_registry

    payload, error = load_semantic_contract_registry(repo_root)
    if error:
        return {"status": "fail", "message": "semantic contract registry load failed: {}".format(error)}

    build_root = os.path.join(repo_root, "build", "compat_sem0")
    probe_token = "contract.logic.eval." + "v2"
    os.makedirs(build_root, exist_ok=True)
    probe_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".md",
            prefix="semantic_contract_probe_",
            dir=build_root,
            delete=False,
        ) as handle:
            handle.write(probe_token + "\n")
            probe_path = handle.name
        rel_path = os.path.relpath(probe_path, repo_root).replace("\\", "/")
        missing = contract_tokens_missing_entries(repo_root, payload, [rel_path])
        if probe_token not in missing:
            return {"status": "fail", "message": "missing semantic contract token was not detected"}
    finally:
        if probe_path and os.path.isfile(probe_path):
            os.remove(probe_path)
    return {"status": "pass", "message": "unregistered semantic contract token detected deterministically"}

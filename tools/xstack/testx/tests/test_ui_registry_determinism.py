"""FAST test: ui.registry compilation is deterministic."""

from __future__ import annotations

import json
import os
import shutil
import sys


TEST_ID = "testx.ui.registry.determinism"
TEST_TAGS = ["smoke", "registry", "ui"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_text(path: str) -> str:
    return open(path, "r", encoding="utf-8").read()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from testlib import make_temp_repo_with_test_packs
    from tools.xstack.registry_compile.compiler import compile_bundle

    fixture_repo = make_temp_repo_with_test_packs(repo_root)
    try:
        first = compile_bundle(
            repo_root=fixture_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            use_cache=False,
        )
        if first.get("result") != "complete":
            return {"status": "fail", "message": "first compile_bundle failed in fixture repo"}
        ui_path = os.path.join(fixture_repo, "build", "registries", "ui.registry.json")
        if not os.path.isfile(ui_path):
            return {"status": "fail", "message": "missing ui.registry.json after first compile"}
        first_payload = _load_json(ui_path)
        first_text = _load_text(ui_path)

        second = compile_bundle(
            repo_root=fixture_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            use_cache=False,
        )
        if second.get("result") != "complete":
            return {"status": "fail", "message": "second compile_bundle failed in fixture repo"}
        second_payload = _load_json(ui_path)
        second_text = _load_text(ui_path)

        first_hash = str((first.get("registry_hashes") or {}).get("ui_registry_hash", ""))
        second_hash = str((second.get("registry_hashes") or {}).get("ui_registry_hash", ""))
        if not first_hash or not second_hash:
            return {"status": "fail", "message": "ui_registry_hash missing from compile results"}
        if first_hash != second_hash:
            return {"status": "fail", "message": "ui_registry_hash changed across identical fixture compiles"}

        payload_hash = str(first_payload.get("registry_hash", ""))
        if payload_hash != first_hash:
            return {"status": "fail", "message": "ui.registry payload hash does not match compile output hash"}
        if first_text != second_text:
            return {"status": "fail", "message": "ui.registry file text changed across identical fixture compiles"}

        windows = list(second_payload.get("windows") or [])
        ordered = sorted(
            windows,
            key=lambda row: (
                str((row or {}).get("window_id", "")),
                str((row or {}).get("pack_id", "")),
            ),
        )
        if windows != ordered:
            return {"status": "fail", "message": "ui.registry windows are not deterministically ordered"}
    finally:
        shutil.rmtree(fixture_repo, ignore_errors=True)

    return {"status": "pass", "message": "ui.registry determinism checks passed"}

import argparse
import json
import os
import shutil
import sys

from registry_compile_testlib import make_temp_repo_fixture


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: contribution conflicts produce deterministic refusal.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo = os.path.abspath(args.repo_root)
    if source_repo not in sys.path:
        sys.path.insert(0, source_repo)

    from tools.xstack.registry_compile.compiler import compile_bundle

    tmp_repo = make_temp_repo_fixture(source_repo)
    try:
        conflict_pack_dir = os.path.join(tmp_repo, "packs", "tool", "pack.test.conflict")
        _write_json(
            os.path.join(conflict_pack_dir, "pack.json"),
            {
                "schema_version": "1.0.0",
                "pack_id": "pack.test.conflict",
                "version": "1.0.0",
                "compatibility": {
                    "session_spec_min": "1.0.0",
                    "session_spec_max": "1.0.0"
                },
                "dependencies": [
                    "pack.test.base@1.0.0"
                ],
                "contribution_types": [
                    "ui_windows"
                ],
                "contributions": [
                    {
                        "type": "ui_windows",
                        "id": "ui.window.test.lab",
                        "path": "ui/window.conflict.json"
                    }
                ],
                "canonical_hash": "placeholder.pack.test.conflict.v1",
                "signature_status": "signed"
            },
        )
        _write_json(
            os.path.join(conflict_pack_dir, "ui", "window.conflict.json"),
            {
                "window_id": "ui.window.test.lab",
                "required_entitlements": [
                    "ui.map"
                ]
            },
        )

        first = compile_bundle(
            repo_root=tmp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=source_repo,
        )
        second = compile_bundle(
            repo_root=tmp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=source_repo,
        )
        if first.get("result") != "refused" or second.get("result") != "refused":
            print("expected deterministic refusal for duplicate contribution IDs")
            return 1
        if (first.get("errors") or []) != (second.get("errors") or []):
            print("refusal messages are not deterministic across runs")
            return 1
    finally:
        shutil.rmtree(tmp_repo, ignore_errors=True)

    print("registry compile conflict refusal determinism OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


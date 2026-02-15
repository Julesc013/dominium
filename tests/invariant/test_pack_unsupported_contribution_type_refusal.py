import argparse
import os
import sys
import tempfile

from pack_testlib import create_pack, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: unsupported contribution type must refuse.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo = os.path.abspath(args.repo_root)
    if source_repo not in sys.path:
        sys.path.insert(0, source_repo)

    from tools.xstack.pack_loader.loader import load_pack_set
    from tools.xstack.pack_contrib.parser import parse_contributions

    with tempfile.TemporaryDirectory(prefix="pack_bad_contrib_type_") as tmp:
        pack_dir = create_pack(
            tmp,
            "core",
            "pack.test.bad_type",
            contributions=[
                {
                    "type": "registry_entries",
                    "id": "contrib.valid.id",
                    "path": "data/registry.json",
                }
            ],
        )
        # Override manifest contribution type to unsupported value while preserving schema shape.
        manifest_path = os.path.join(pack_dir, "pack.json")
        payload = {
            "schema_version": "1.0.0",
            "pack_id": "pack.test.bad_type",
            "version": "1.0.0",
            "compatibility": {
                "session_spec_min": "1.0.0",
                "session_spec_max": "1.0.0"
            },
            "dependencies": [],
            "contribution_types": [
                "unknown_type"
            ],
            "contributions": [
                {
                    "type": "unknown_type",
                    "id": "contrib.bad.type",
                    "path": "data/registry.json"
                }
            ],
            "canonical_hash": "placeholder.pack.test.bad_type.v1",
            "signature_status": "signed"
        }
        write_json(manifest_path, payload)

        loaded = load_pack_set(repo_root=tmp, schema_repo_root=source_repo)
        if loaded.get("result") != "complete":
            print("load should complete; unsupported type is parser-owned: {}".format(loaded.get("errors", [])))
            return 1
        contrib = parse_contributions(repo_root=tmp, packs=loaded.get("packs") or [])
        if contrib.get("result") != "refused":
            print("expected parser refusal for unsupported contribution type")
            return 1
        contrib_repeat = parse_contributions(repo_root=tmp, packs=loaded.get("packs") or [])
        if (contrib.get("errors") or []) != (contrib_repeat.get("errors") or []):
            print("unsupported contribution type refusal output is not deterministic")
            return 1
        codes = [str(row.get("code", "")) for row in (contrib.get("errors") or [])]
        if "refuse.pack_contrib.unsupported_type" not in codes:
            print("missing unsupported contribution type refusal code: {}".format(codes))
            return 1

    print("unsupported contribution type refusal OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

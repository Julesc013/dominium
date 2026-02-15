import argparse
import os
import sys
import tempfile

from pack_testlib import create_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: duplicate contribution IDs across packs must refuse.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo = os.path.abspath(args.repo_root)
    if source_repo not in sys.path:
        sys.path.insert(0, source_repo)

    from tools.xstack.pack_loader.loader import load_pack_set
    from tools.xstack.pack_contrib.parser import parse_contributions

    with tempfile.TemporaryDirectory(prefix="pack_dup_contrib_") as tmp:
        create_pack(
            tmp,
            "core",
            "pack.test.one",
            contributions=[
                {
                    "type": "registry_entries",
                    "id": "contrib.shared.id",
                    "path": "data/a.json",
                }
            ],
        )
        create_pack(
            tmp,
            "domain",
            "pack.test.two",
            dependencies=["pack.test.one@1.0.0"],
            contributions=[
                {
                    "type": "domain",
                    "id": "contrib.shared.id",
                    "path": "data/b.json",
                }
            ],
        )
        loaded = load_pack_set(repo_root=tmp, schema_repo_root=source_repo)
        if loaded.get("result") != "complete":
            print("load must complete before contribution checks: {}".format(loaded.get("errors", [])))
            return 1
        contrib = parse_contributions(repo_root=tmp, packs=loaded.get("packs") or [])
        if contrib.get("result") != "refused":
            print("expected refusal for duplicate contribution IDs")
            return 1
        codes = [str(row.get("code", "")) for row in (contrib.get("errors") or [])]
        if "refuse.pack_contrib.duplicate_id" not in codes:
            print("missing duplicate contribution ID refusal code: {}".format(codes))
            return 1

    print("duplicate contribution ID refusal OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

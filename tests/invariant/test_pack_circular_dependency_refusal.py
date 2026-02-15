import argparse
import os
import sys
import tempfile

from pack_testlib import create_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: circular pack dependencies must refuse.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo = os.path.abspath(args.repo_root)
    if source_repo not in sys.path:
        sys.path.insert(0, source_repo)

    from tools.xstack.pack_loader.loader import load_pack_set

    with tempfile.TemporaryDirectory(prefix="pack_cycle_") as tmp:
        create_pack(tmp, "core", "pack.test.a", dependencies=["pack.test.b@1.0.0"])
        create_pack(tmp, "domain", "pack.test.b", dependencies=["pack.test.a@1.0.0"])
        result = load_pack_set(repo_root=tmp, schema_repo_root=source_repo)
        if result.get("result") != "refused":
            print("expected refusal for circular dependencies")
            return 1
        codes = [str(row.get("code", "")) for row in (result.get("errors") or [])]
        if "refuse.pack.circular_dependency" not in codes:
            print("missing circular dependency refusal code: {}".format(codes))
            return 1

    print("circular dependency refusal OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

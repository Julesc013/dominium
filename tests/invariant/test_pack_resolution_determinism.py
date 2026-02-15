import argparse
import os
import random
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: pack resolution is deterministic across input order.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.pack_loader.loader import load_pack_set
    from tools.xstack.pack_loader.dependency_resolver import resolve_packs

    loaded = load_pack_set(repo_root=repo_root)
    if loaded.get("result") != "complete":
        print("pack load failed: {}".format(loaded.get("errors", [])))
        return 1

    baseline = resolve_packs(loaded.get("packs") or [], bundle_selection=None)
    if baseline.get("result") != "complete":
        print("baseline resolve failed: {}".format(baseline.get("errors", [])))
        return 1
    expected = list(baseline.get("ordered_pack_ids") or [])
    if not expected:
        print("expected non-empty ordered pack ids")
        return 1

    for seed in (0, 1, 2, 11, 97):
        rows = list(loaded.get("packs") or [])
        random.Random(seed).shuffle(rows)
        got = resolve_packs(rows, bundle_selection=None)
        if got.get("result") != "complete":
            print("resolve failed for seed {}: {}".format(seed, got.get("errors", [])))
            return 1
        current = list(got.get("ordered_pack_ids") or [])
        if current != expected:
            print("non-deterministic order for seed {}: {} != {}".format(seed, current, expected))
            return 1

    print("pack resolution determinism OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


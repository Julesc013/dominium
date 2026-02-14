import argparse
import os
import shutil
import sys


def _load_repox_module(repo_root: str):
    ci_dir = os.path.join(repo_root, "scripts", "ci")
    if ci_dir not in sys.path:
        sys.path.insert(0, ci_dir)
    import check_repox_rules as repox  # pylint: disable=import-error

    return repox


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: RepoX grouped cache path is deterministic.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    repox = _load_repox_module(repo_root)

    cache_root = os.path.join(repo_root, ".xstack_cache", "repox")
    if os.path.isdir(cache_root):
        shutil.rmtree(cache_root)

    roots = {"docs": {"hash": "hash.docs.v1"}}

    def _no_violations():
        return []

    first = repox._run_check_group(  # pylint: disable=protected-access
        repo_root=repo_root,
        group_id="repox.tests.cache_equiv",
        deps=("docs",),
        profile="STRICT",
        impacted_roots={"docs"},
        roots=roots,
        checks=[_no_violations],
    )
    second = repox._run_check_group(  # pylint: disable=protected-access
        repo_root=repo_root,
        group_id="repox.tests.cache_equiv",
        deps=("docs",),
        profile="STRICT",
        impacted_roots={"docs"},
        roots=roots,
        checks=[_no_violations],
    )
    if first.get("dep_hash") != second.get("dep_hash"):
        print("dep hash mismatch between cold/warm runs")
        return 1
    if list(first.get("violations") or []) != list(second.get("violations") or []):
        print("violation list mismatch between cold/warm runs")
        return 1
    if not bool(second.get("cache_hit")):
        print("expected warm run cache_hit=true")
        return 1

    # Build FAST cache entry first.
    repox._run_check_group(  # pylint: disable=protected-access
        repo_root=repo_root,
        group_id="repox.tests.cache_equiv",
        deps=("docs",),
        profile="FAST",
        impacted_roots={"docs"},
        roots=roots,
        checks=[_no_violations],
    )

    # FAST skip path should now reuse cache and avoid executing checks.
    def _must_not_execute():
        raise RuntimeError("check executed unexpectedly")

    skipped = repox._run_check_group(  # pylint: disable=protected-access
        repo_root=repo_root,
        group_id="repox.tests.cache_equiv",
        deps=("docs",),
        profile="FAST",
        impacted_roots=set(),
        roots=roots,
        checks=[_must_not_execute],
    )
    if not bool(skipped.get("cache_hit")):
        print("expected fast unchanged path to reuse cache")
        return 1
    if list(skipped.get("violations") or []) != []:
        print("cached violation payload drifted unexpectedly")
        return 1

    print("repox cache equivalence invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

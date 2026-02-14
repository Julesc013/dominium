import argparse
import os
import shutil
import sys


def _load_cache_module(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.cache_store import load_entry, scan_cache, store_entry

    return load_entry, scan_cache, store_entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: cache invalidates when runner implementation version changes.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    load_entry, scan_cache, store_entry = _load_cache_module(repo_root)

    cache_root = os.path.join(repo_root, ".xstack_cache", "tests", "cache_invalidation")
    if os.path.isdir(cache_root):
        shutil.rmtree(cache_root)

    runner_id = "repox_runner"
    input_hash = "input.hash.a"
    profile_id = "FAST"

    store_entry(
        repo_root=repo_root,
        runner_id=runner_id,
        input_hash=input_hash,
        profile_id=profile_id,
        version_hash="runner.version.a",
        exit_code=0,
        output_hash="output.hash.a",
        artifacts_produced=["docs/audit/proof_manifest.json"],
        timestamp_utc="2026-02-14T00:00:00Z",
        cache_root=cache_root,
    )

    hit = load_entry(
        repo_root=repo_root,
        runner_id=runner_id,
        input_hash=input_hash,
        profile_id=profile_id,
        version_hash="runner.version.a",
        cache_root=cache_root,
    )
    if not hit:
        print("expected cache hit for matching runner version")
        return 1

    miss = load_entry(
        repo_root=repo_root,
        runner_id=runner_id,
        input_hash=input_hash,
        profile_id=profile_id,
        version_hash="runner.version.b",
        cache_root=cache_root,
    )
    if miss:
        print("cache false hit despite runner version change")
        return 1

    report = scan_cache(
        repo_root=repo_root,
        cache_root=cache_root,
        version_resolver=lambda token: "runner.version.b" if str(token) == runner_id else "",
    )
    stale_groups = set(str(item) for item in (report.get("stale_groups") or []))
    if runner_id not in stale_groups:
        print("doctor deep report missing stale group classification")
        return 1

    print("cache invalidation on runner change invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import os
import shutil
import sys


def _load_cache_module(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.cache_store import load_entry, store_entry

    return load_entry, store_entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: XStack cache only hits on exact input hash/profile.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    load_entry, store_entry = _load_cache_module(repo_root)
    cache_root = os.path.join(repo_root, ".xstack_cache", "tests", "cache_correctness")
    if os.path.isdir(cache_root):
        shutil.rmtree(cache_root)

    runner_id = "repox_runner"
    input_hash = "hash.input.a"
    profile_id = "FAST"
    store_entry(
        repo_root=repo_root,
        runner_id=runner_id,
        input_hash=input_hash,
        profile_id=profile_id,
        exit_code=0,
        output_hash="hash.output.a",
        artifacts_produced=["docs/audit/proof_manifest.json"],
        timestamp_utc="2026-02-13T00:00:00Z",
        cache_root=cache_root,
    )

    hit = load_entry(
        repo_root=repo_root,
        runner_id=runner_id,
        input_hash=input_hash,
        profile_id=profile_id,
        cache_root=cache_root,
    )
    if not hit:
        print("expected cache hit but got miss")
        return 1

    miss_input = load_entry(
        repo_root=repo_root,
        runner_id=runner_id,
        input_hash="hash.input.b",
        profile_id=profile_id,
        cache_root=cache_root,
    )
    if miss_input:
        print("cache false hit on mismatched input hash")
        return 1

    miss_profile = load_entry(
        repo_root=repo_root,
        runner_id=runner_id,
        input_hash=input_hash,
        profile_id="STRICT",
        cache_root=cache_root,
    )
    if miss_profile:
        print("cache false hit on mismatched profile")
        return 1

    print("gate cache correctness invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

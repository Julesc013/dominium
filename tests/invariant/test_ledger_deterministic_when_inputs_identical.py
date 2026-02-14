import argparse
import os
import shutil
import sys


def _load_ledger_module(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.execution_ledger import append_entry, build_entry, load_entries

    return append_entry, build_entry, load_entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: execution ledger is deterministic for identical inputs.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    append_entry, build_entry, load_entries = _load_ledger_module(repo_root)

    cache_root = os.path.join(repo_root, ".xstack_cache", "tests", "ledger_determinism")
    if os.path.isdir(cache_root):
        shutil.rmtree(cache_root)

    entry = build_entry(
        repo_state_hash="repo.hash.a",
        plan_hash="plan.hash.a",
        profile="FAST",
        runner_ids=["repox_runner", "testx.group.core.invariants"],
        cache_hits=2,
        cache_misses=0,
        artifact_hashes={"docs/audit/testx/TESTX_SUMMARY.json": "artifact.hash.a"},
        failure_class="",
        duration_s=1.25,
        workspace_id="ws.ledger.test",
    )

    first = append_entry(repo_root, entry, cache_root=cache_root)
    second = append_entry(repo_root, entry, cache_root=cache_root)
    if str(first.get("entry_hash", "")) != str(second.get("entry_hash", "")):
        print("ledger entry hash mismatch for identical inputs")
        return 1
    if str(first.get("entry_path", "")) != str(second.get("entry_path", "")):
        print("ledger entry path mismatch for identical inputs")
        return 1

    rows = load_entries(repo_root, cache_root=cache_root)
    if len(rows) != 1:
        print("expected deterministic single ledger row overwrite, got {}".format(len(rows)))
        return 1
    if str(rows[0].get("entry_hash", "")) != str(first.get("entry_hash", "")):
        print("stored ledger hash mismatch")
        return 1

    print("execution ledger deterministic invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

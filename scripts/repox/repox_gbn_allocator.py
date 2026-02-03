#!/usr/bin/env python3
import argparse
import os
import sys


DEFAULT_COUNTER = 10000


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX GBN allocator (disabled by default).")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--counter-file", default="")
    parser.add_argument("--lock-file", default="")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    counter_path = args.counter_file or os.path.join(repo_root, ".repox", "gbn_counter.txt")
    lock_path = args.lock_file or os.path.join(repo_root, ".repox", "gbn.lock")

    if not args.enable or os.environ.get("REPOX_GBN_ENABLE") != "1":
        sys.stderr.write("GBN allocation disabled until explicitly enabled.\n")
        return 3

    os.makedirs(os.path.dirname(counter_path), exist_ok=True)
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)

    # Stage 2: allocator path exists but must not allocate.
    sys.stderr.write("GBN allocation disabled in Stage 2.\n")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())

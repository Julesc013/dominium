import argparse
import os

from gate_write_policy_common import check_non_snapshot_routing


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: gate full routes outputs away from tracked docs.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    code = check_non_snapshot_routing(repo_root)
    if code != 0:
        return code
    print("gate full no-tracked-write routing invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

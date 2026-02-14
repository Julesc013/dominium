import argparse
import os

from gate_write_policy_common import check_snapshot_passthrough


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: gate snapshot preserves canonical output writers.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    code = check_snapshot_passthrough(repo_root)
    if code != 0:
        return code
    print("gate snapshot write-routing invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

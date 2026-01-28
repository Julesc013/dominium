import argparse
import os
import shutil
import subprocess
import sys


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def copy_run_root(source_root: str, dest_root: str) -> None:
    if os.path.isdir(dest_root):
        shutil.rmtree(dest_root)
    shutil.copytree(source_root, dest_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="PERF-1 budget regression gate.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--temp-root", default=None)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    fixture_run_root = os.path.join(repo_root, "tests", "fixtures", "perf", "run_root")
    budgets_path = os.path.join(repo_root, "docs", "policies", "PERF_BUDGETS.md")
    checker = os.path.join(repo_root, "tools", "ci", "perf_budget_check.py")

    if not os.path.isdir(fixture_run_root):
        print("missing perf fixture run_root: {}".format(fixture_run_root))
        return 1
    if not os.path.isfile(budgets_path):
        print("missing PERF_BUDGETS.md: {}".format(budgets_path))
        return 1
    if not os.path.isfile(checker):
        print("missing perf budget checker: {}".format(checker))
        return 1

    run_root = fixture_run_root
    if args.temp_root:
        temp_root = os.path.abspath(args.temp_root)
        ensure_dir(temp_root)
        run_root = os.path.join(temp_root, "run_root")
        copy_run_root(fixture_run_root, run_root)

    result = subprocess.run(
        [sys.executable, checker, "--run-root", run_root, "--budgets", budgets_path],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

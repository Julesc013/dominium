import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / "tools" / "validators" / "contracts" / "check_command_result_view.py"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo-root", str(REPO_ROOT), *args],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main():
    checks = [
        ("strict", _run("--strict")),
        ("json", _run("--json")),
        ("fixtures", _run("--fixtures")),
        ("inventory", _run("--inventory")),
    ]
    failures = []
    for name, completed in checks:
        if completed.returncode != 0:
            failures.append((name, completed))
    if failures:
        for name, completed in failures:
            print(f"FAIL {name}: rc={completed.returncode}")
            print(completed.stdout)
            print(completed.stderr)
        return 1
    print("Command result view contract tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

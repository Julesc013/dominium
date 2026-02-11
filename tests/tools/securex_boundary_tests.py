import argparse
import os
import subprocess
import sys


def _run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _securex(repo_root, args):
    cmd = [sys.executable, os.path.join(repo_root, "tools", "securex", "securex.py")]
    cmd.extend(args)
    cmd.extend(["--repo-root", repo_root])
    return _run(cmd, repo_root)


def main():
    parser = argparse.ArgumentParser(description="SecureX trust-boundary tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    boundary = _securex(repo_root, ["boundary-check"])
    if boundary.returncode != 0:
        print(boundary.stdout)
        return 1

    verify = _securex(repo_root, ["verify"])
    if verify.returncode != 0:
        print(verify.stdout)
        return 1

    print("securex_boundary_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import json
import os
import subprocess
import sys
import tempfile


def _run(cmd, cwd, env=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _performx(repo_root, cwd, env):
    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "performx", "performx.py"),
        "run",
        "--repo-root",
        repo_root,
    ]
    return _run(cmd, cwd=cwd, env=env)


def case_empty_path(repo_root):
    env = dict(os.environ)
    env["PATH"] = ""
    result = _performx(repo_root, repo_root, env)
    if result.returncode != 0:
        print(result.stdout)
        return 1
    return 0


def case_arbitrary_cwd(repo_root):
    env = dict(os.environ)
    with tempfile.TemporaryDirectory(prefix="performx-cwd-") as temp_dir:
        result = _performx(repo_root, temp_dir, env)
    if result.returncode != 0:
        print(result.stdout)
        return 1
    try:
        payload = json.loads(result.stdout or "{}")
    except ValueError:
        print(result.stdout)
        return 1
    if payload.get("result") != "complete":
        print(result.stdout)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="PerformX environment tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=("empty_path", "arbitrary_cwd"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "empty_path":
        rc = case_empty_path(repo_root)
        if rc == 0:
            print("test_performx_empty_path=ok")
        return rc
    rc = case_arbitrary_cwd(repo_root)
    if rc == 0:
        print("test_performx_arbitrary_cwd=ok")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())


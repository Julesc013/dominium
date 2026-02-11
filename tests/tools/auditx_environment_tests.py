import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def _run_scan(repo_root, cwd, env):
    tool = os.path.join(repo_root, "tools", "auditx", "auditx.py")
    return subprocess.run(
        [sys.executable, tool, "scan", "--repo-root", repo_root, "--format", "json"],
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def case_empty_path(repo_root):
    env = dict(os.environ)
    env["PATH"] = ""
    env.pop("DOM_HOST_PATH", None)
    proc = _run_scan(repo_root, repo_root, env)
    if proc.returncode != 0:
        print(proc.stdout)
        return 1
    print("test_auditx_empty_path=ok")
    return 0


def case_arbitrary_cwd(repo_root):
    env = dict(os.environ)
    tmp_dir = tempfile.mkdtemp(prefix="dom-auditx-cwd-")
    try:
        proc = _run_scan(repo_root, tmp_dir, env)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    if proc.returncode != 0:
        print(proc.stdout)
        return 1
    print("test_auditx_arbitrary_cwd=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="AuditX self-contained environment tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=("empty_path", "arbitrary_cwd"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "empty_path":
        return case_empty_path(repo_root)
    return case_arbitrary_cwd(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())


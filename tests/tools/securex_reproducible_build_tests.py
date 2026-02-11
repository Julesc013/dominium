import argparse
import os
import subprocess
import sys
import tempfile


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


def _write(path, content):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(content)


def main():
    parser = argparse.ArgumentParser(description="SecureX reproducible build checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="securex-repro-a-") as left_dir:
        with tempfile.TemporaryDirectory(prefix="securex-repro-b-") as right_dir:
            left_file = os.path.join(left_dir, "bin", "sample.bin")
            right_file = os.path.join(right_dir, "bin", "sample.bin")
            _write(left_file, b"artifact-1")
            _write(right_file, b"artifact-1")

            ok = _securex(repo_root, ["repro-build-check", "--left", left_file, "--right", right_file])
            if ok.returncode != 0:
                print(ok.stdout)
                return 1

            _write(right_file, b"artifact-2")
            bad = _securex(repo_root, ["repro-build-check", "--left", left_file, "--right", right_file])
            if bad.returncode == 0:
                print("expected hash mismatch to refuse")
                print(bad.stdout)
                return 1

    print("securex_reproducible_build_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

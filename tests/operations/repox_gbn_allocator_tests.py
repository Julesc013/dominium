import argparse
import os
import subprocess
import sys


ALLOCATOR = os.path.join("scripts", "repox", "repox_gbn_allocator.py")


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX GBN allocator tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    cmd = [
        sys.executable,
        ALLOCATOR,
        "--repo-root", repo_root,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode == 0:
        raise AssertionError("allocator should fail when disabled")

    cmd = [
        sys.executable,
        ALLOCATOR,
        "--repo-root", repo_root,
        "--enable",
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode == 0:
        raise AssertionError("allocator should remain disabled in Stage 2")

    print("RepoX GBN allocator tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

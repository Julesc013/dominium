import argparse
import os
import subprocess
import sys


def find_binary(repo_root: str) -> str:
    candidates = []
    if sys.platform.startswith("win"):
        candidates = ["client.exe", "launcher.exe", "server.exe"]
    else:
        candidates = ["client", "launcher", "server"]
    search_roots = [
        os.path.join(repo_root, "out", "build"),
        os.path.join(repo_root, "build"),
    ]
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            filenames.sort()
            for name in candidates:
                if name in filenames:
                    return os.path.join(dirpath, name)
    return ""


def parse_build_info(output: str) -> dict:
    payload = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        payload[key.strip()] = value.strip()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build identity --build-info tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    binary = find_binary(repo_root)
    if not binary:
        raise AssertionError("no primary binary found for --build-info check")

    result = subprocess.run([binary, "--build-info"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        raise AssertionError("build-info command failed: {}".format(result.stdout))

    payload = parse_build_info(result.stdout)
    if not payload.get("build_kind"):
        raise AssertionError("build_kind missing from --build-info")
    if not payload.get("build_bii"):
        raise AssertionError("build_bii missing from --build-info")
    if "build_gbn" not in payload:
        raise AssertionError("build_gbn missing from --build-info")
    if payload.get("build_gbn") != "none":
        raise AssertionError("build_gbn must be 'none' in Stage 2")

    print("Build identity tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import json
import os
import subprocess
import sys


REPOX_RELEASE = os.path.join("scripts", "repox", "repox_release.py")


def run_cmd(cmd, expect=0):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != expect:
        raise AssertionError("command failed: {}\n{}".format(" ".join(cmd), result.stdout))
    return result.stdout


def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX release dry-run tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    # Without --dry-run must fail.
    fail_cmd = [
        sys.executable,
        REPOX_RELEASE,
        "--repo-root", repo_root,
        "--kind", "beta",
        "--channel", "beta",
    ]
    result = subprocess.run(fail_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode == 0:
        raise AssertionError("repox release should fail without --dry-run")

    # Dry-run succeeds and emits preview artifacts.
    ok_cmd = [
        sys.executable,
        REPOX_RELEASE,
        "--repo-root", repo_root,
        "--kind", "beta",
        "--channel", "beta",
        "--dry-run",
        "--ctest-preset", "verify-win-vs2026",
    ]
    run_cmd(ok_cmd, expect=0)

    preview_dir = os.path.join(repo_root, "build")
    changelog = os.path.join(preview_dir, "changelog.preview.md")
    identity = os.path.join(preview_dir, "artifact_identity.preview.json")

    if not os.path.isfile(changelog):
        raise AssertionError("missing preview changelog")
    if not os.path.isfile(identity):
        raise AssertionError("missing preview identity")

    payload = read_json(identity)
    if payload.get("gbn") is not None:
        raise AssertionError("preview identity must not allocate GBN")
    if payload.get("build_kind") != "beta":
        raise AssertionError("preview identity build_kind mismatch")

    print("RepoX release dry-run tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile


REPOX_RELEASE = os.path.join("scripts", "repox", "repox_release.py")


def run_cmd(cmd, expect=0):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != expect:
        raise AssertionError("command failed: {}\n{}".format(" ".join(cmd), result.stdout))
    return result.stdout


def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def snapshot_updates(repo_root: str) -> dict:
    updates_dir = os.path.join(repo_root, "updates")
    snapshot = {}
    if not os.path.isdir(updates_dir):
        return snapshot
    for root, _, files in os.walk(updates_dir):
        files = sorted(files)
        for name in files:
            path = os.path.join(root, name)
            with open(path, "rb") as handle:
                digest = hashlib.sha256(handle.read()).hexdigest()
            rel = os.path.relpath(path, updates_dir)
            snapshot[rel] = digest
    return snapshot


def snapshot_tags(repo_root: str) -> list:
    result = subprocess.run(["git", "tag"], cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise AssertionError("git tag failed: {}".format(result.stderr))
    tags = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(tags)


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX release dry-run tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    repox_release = os.path.join(repo_root, REPOX_RELEASE)

    # Without --dry-run must fail.
    fail_cmd = [
        sys.executable,
        repox_release,
        "--repo-root", repo_root,
        "--kind", "beta",
        "--channel", "beta",
    ]
    result = subprocess.run(fail_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode == 0:
        raise AssertionError("repox release should fail without --dry-run")

    # Publish/tag attempts must fail.
    publish_cmd = fail_cmd + ["--dry-run", "--publish"]
    result = subprocess.run(publish_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode == 0:
        raise AssertionError("repox release should refuse publish in Stage 2")
    tag_cmd = fail_cmd + ["--dry-run", "--tag"]
    result = subprocess.run(tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode == 0:
        raise AssertionError("repox release should refuse tag in Stage 2")

    tag_snapshot = snapshot_tags(repo_root)
    updates_snapshot = snapshot_updates(repo_root)

    # Dry-run succeeds and emits preview artifacts.
    with tempfile.TemporaryDirectory() as tmp_root:
        ok_cmd = [
            sys.executable,
            repox_release,
            "--repo-root", repo_root,
            "--kind", "beta",
            "--channel", "beta",
            "--dry-run",
            "--ctest-preset", "verify-win-vs2026",
            "--output-root", tmp_root,
        ]
        run_cmd(ok_cmd, expect=0)

        preview_dir = os.path.join(tmp_root, "build")
        changelog = os.path.join(preview_dir, "changelog.preview.md")
        identity = os.path.join(preview_dir, "artifact_identity.preview.json")
        plan = os.path.join(preview_dir, "release_plan.preview.json")

        if not os.path.isfile(changelog):
            raise AssertionError("missing preview changelog")
        if not os.path.isfile(identity):
            raise AssertionError("missing preview identity")
        if not os.path.isfile(plan):
            raise AssertionError("missing preview release plan")

        payload = read_json(identity)
        if payload.get("gbn") is not None:
            raise AssertionError("preview identity must not allocate GBN")
        if payload.get("build_kind") != "beta":
            raise AssertionError("preview identity build_kind mismatch")

        plan_payload = read_json(plan)
        if plan_payload.get("gbn") is not None:
            raise AssertionError("preview plan must not allocate GBN")
        if plan_payload.get("kind") != "beta":
            raise AssertionError("preview plan kind mismatch")

    if snapshot_tags(repo_root) != tag_snapshot:
        raise AssertionError("repox release dry-run must not create tags")
    if snapshot_updates(repo_root) != updates_snapshot:
        raise AssertionError("repox release dry-run must not update feeds")

    print("RepoX release dry-run tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

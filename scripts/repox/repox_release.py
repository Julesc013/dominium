#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None


ALLOWED_KINDS = {"beta", "rc", "release", "hotfix"}
ALLOWED_CHANNELS = {"stable", "beta", "pinned"}


def now_timestamp() -> str:
    if os.environ.get("REPOX_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return result.returncode, result.stdout


def load_version(repo_root: str, filename: str) -> str:
    path = os.path.join(repo_root, filename)
    if not os.path.isfile(path):
        return "0.0.0"
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read().strip() or "0.0.0"


def load_release_policy(repo_root: str):
    path = os.path.join(repo_root, "repo", "release_policy.toml")
    if not os.path.isfile(path):
        return {}
    if tomllib is None:
        return {}
    with open(path, "rb") as handle:
        return tomllib.load(handle)


def git_branch(repo_root: str) -> str:
    code, out = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    if code != 0:
        return "unknown"
    return out.strip()


def git_commit(repo_root: str) -> str:
    code, out = run_cmd(["git", "rev-parse", "HEAD"], repo_root)
    if code != 0:
        return "unknown"
    return out.strip()


def check_policy(policy: dict, branch: str, kind: str, channel: str) -> (bool, str):
    rules = policy.get("rules", [])
    for rule in rules:
        branches = rule.get("branches", [])
        kinds = rule.get("kinds", [])
        channels = rule.get("channels", [])
        if branches and branch not in branches:
            continue
        if kinds and kind not in kinds:
            continue
        if channels and channel not in channels:
            continue
        if rule.get("allow", False):
            return True, "allowed by policy"
    return False, "no matching allow rule"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_text(path: str, text: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path: str, payload: dict) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX release (Stage 2 dry-run).")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--kind", required=True)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-root", default="")
    parser.add_argument("--ctest-preset", default="")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    kind = args.kind.strip().lower()
    channel = args.channel.strip().lower()

    if kind not in ALLOWED_KINDS:
        sys.stderr.write("invalid kind: {}\n".format(kind))
        return 2
    if channel not in ALLOWED_CHANNELS:
        sys.stderr.write("invalid channel: {}\n".format(channel))
        return 2

    if not args.dry_run:
        sys.stderr.write("repox release is dry-run only in Stage 2. Use --dry-run.\n")
        return 3

    policy = load_release_policy(repo_root)
    branch = git_branch(repo_root)
    allowed, reason = check_policy(policy, branch, kind, channel)
    if not allowed:
        sys.stderr.write("release policy refused: {}\n".format(reason))
        return 4

    preset = args.ctest_preset
    if not preset:
        if sys.platform.startswith("win"):
            preset = "verify-win-vs2026"
        elif sys.platform == "darwin":
            preset = "verify-macos-xcode"
        else:
            preset = "verify-linux-gcc"
    code, out = run_cmd(["ctest", "--preset", preset, "--output-on-failure"], repo_root)
    if code != 0:
        sys.stderr.write(out)
        return 5

    output_root = os.path.abspath(args.output_root or repo_root)
    preview_dir = os.path.join(output_root, "build")
    ensure_dir(preview_dir)

    changelog_path = os.path.join(preview_dir, "changelog.preview.md")
    changelog_cmd = [
        sys.executable,
        os.path.join(repo_root, "scripts", "repox", "repox_changelog.py"),
        "--repo-root", repo_root,
        "--output", changelog_path,
        "--deterministic" if os.environ.get("REPOX_DETERMINISTIC") == "1" else "",
    ]
    changelog_cmd = [c for c in changelog_cmd if c]
    code, out = run_cmd(changelog_cmd, repo_root)
    if code != 0:
        sys.stderr.write(out)
        return 6

    semver = load_version(repo_root, "VERSION_SUITE")
    artifact_identity = {
        "schema_version": 1,
        "product_id": "dominium",
        "semver": semver,
        "build_kind": kind,
        "bii": git_commit(repo_root)[:12],
        "gbn": None,
        "git_commit": git_commit(repo_root),
        "created_at": now_timestamp(),
        "policy_branch": branch,
        "policy_reason": reason,
        "stage": "stage2-governance-only",
    }
    artifact_path = os.path.join(preview_dir, "artifact_identity.preview.json")
    write_json(artifact_path, artifact_identity)

    sys.stdout.write("repox_release_dry_run=ok\n")
    sys.stdout.write("preview_changelog={}\n".format(changelog_path))
    sys.stdout.write("preview_identity={}\n".format(artifact_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import json
import os
import subprocess
import sys
import tempfile


REPOX_SCRIPT = os.path.join("scripts", "repox", "repox_changelog.py")
FIXTURE_COMMITS = os.path.join("tests", "fixtures", "repox", "commits.txt")
EXPECTED_CHANGELOG = os.path.join("tests", "fixtures", "repox", "expected", "CHANGELOG.md")
EXPECTED_FEED = os.path.join("tests", "fixtures", "repox", "expected", "changelog.json")


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError("command failed: {}\n{}".format(" ".join(cmd), result.stderr))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX changelog generator tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    os.chdir(repo_root)

    expected_changelog = read_text(EXPECTED_CHANGELOG)
    expected_feed = read_json(EXPECTED_FEED)

    with tempfile.TemporaryDirectory() as tmp_root:
        out_changelog = os.path.join(tmp_root, "CHANGELOG.md")
        out_feed = os.path.join(tmp_root, "changelog.json")
        run_cmd([
            sys.executable,
            REPOX_SCRIPT,
            "--repo-root", repo_root,
            "--commits-file", FIXTURE_COMMITS,
            "--output", out_changelog,
            "--feed", out_feed,
            "--deterministic",
        ])

        actual_changelog = read_text(out_changelog)
        if actual_changelog != expected_changelog:
            raise AssertionError("changelog output mismatch")

        actual_feed = read_json(out_feed)
        if actual_feed != expected_feed:
            raise AssertionError("changelog feed output mismatch")

        run_cmd([
            sys.executable,
            REPOX_SCRIPT,
            "--repo-root", repo_root,
            "--commits-file", FIXTURE_COMMITS,
            "--output", out_changelog,
            "--feed", out_feed,
            "--deterministic",
            "--check",
        ])

    print("RepoX changelog tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import os
import subprocess
import sys


NOTES_PATH = os.path.join("docs", "architecture", "SCHEMA_CHANGE_NOTES.md")


def run_git(args, repo_root):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def parse_changed_files(output):
    if not output:
        return []
    return [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]


def get_changed_files(repo_root):
    env_files = os.environ.get("DOM_CHANGED_FILES", "").strip()
    if env_files:
        return [item.strip().replace("\\", "/") for item in env_files.split(";") if item.strip()]

    baseline = os.environ.get("DOM_BASELINE_REF", "").strip() or "origin/main"
    diff_output = run_git(["diff", "--name-only", "--diff-filter=ACMR", f"{baseline}...HEAD"], repo_root)
    if diff_output is not None:
        files = parse_changed_files(diff_output)
        if files:
            return files

    status_output = run_git(["status", "--porcelain"], repo_root)
    if status_output is None:
        return None
    files = []
    for line in status_output.splitlines():
        if not line:
            continue
        path = line[3:].strip()
        if path:
            files.append(path.replace("\\", "/"))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract: schema changes require migration notes.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SCHEMA-CHANGE-NOTES"
    changed = get_changed_files(repo_root)
    if changed is None:
        print("{}: unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF".format(invariant_id))
        return 1

    schema_changed = any(path.startswith("schema/") for path in changed)
    if not schema_changed:
        print("schema change notes not required (no schema changes detected)")
        return 0

    notes_path = os.path.join(repo_root, NOTES_PATH)
    if not os.path.isfile(notes_path):
        print("{}: missing {}".format(invariant_id, NOTES_PATH))
        return 1

    with open(notes_path, "r", encoding="utf-8", errors="ignore") as handle:
        text = handle.read()

    if "INV-SCHEMA-" not in text:
        print("{}: notes must reference INV-SCHEMA-* invariant IDs".format(invariant_id))
        return 1

    print("schema change notes OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

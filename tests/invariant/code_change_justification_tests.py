import argparse
import os
import subprocess
import sys

from invariant_utils import is_override_active


JUSTIFICATION_PATH = "CODE_CHANGE_JUSTIFICATION.md"


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


def parse_justification(text):
    touched = []
    for line in text.splitlines():
        lower = line.lower()
        if lower.startswith("touched:") or lower.startswith("touched paths:") or lower.startswith("scope:"):
            _, _, rest = line.partition(":")
            for part in rest.split(","):
                token = part.strip()
                if token:
                    touched.append(token)
    return touched


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: code change justification required for engine/game.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-CODE-JUSTIFICATION"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    changed = get_changed_files(repo_root)
    if changed is None:
        print("unable to determine changed files; set DOM_CHANGED_FILES or DOM_BASELINE_REF")
        return 1

    requires_justification = any(path.startswith(("engine/", "game/")) for path in changed)
    if not requires_justification:
        print("code-change justification not required (no engine/game changes detected)")
        return 0

    path = os.path.join(repo_root, JUSTIFICATION_PATH)
    if not os.path.isfile(path):
        print("missing {}".format(JUSTIFICATION_PATH))
        return 1

    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        text = handle.read()

    if "Why can this not be data?" not in text:
        print("justification missing required question: 'Why can this not be data?'")
        return 1

    touched = parse_justification(text)
    if not touched:
        print("justification missing touched/scope entries")
        return 1

    if not any(token.startswith(("engine", "engine/", "game", "game/")) for token in touched):
        print("justification does not reference engine/ or game/ in touched/scope entries")
        return 1

    print("code-change justification OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

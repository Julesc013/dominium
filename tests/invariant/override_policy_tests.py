import argparse
import json
import os
import sys
from datetime import date


OVERRIDES_PATH = os.path.join("docs", "architecture", "LOCKLIST_OVERRIDES.json")


def parse_date(value):
    if not value or not isinstance(value, str):
        return None
    parts = value.split("-")
    if len(parts) != 3:
        return None
    try:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def is_release_branch():
    env = {
        "DOM_RELEASE_BRANCH": os.environ.get("DOM_RELEASE_BRANCH", ""),
        "DOM_RELEASE": os.environ.get("DOM_RELEASE", ""),
        "DOM_BRANCH_KIND": os.environ.get("DOM_BRANCH_KIND", ""),
        "CI_RELEASE": os.environ.get("CI_RELEASE", ""),
    }
    for value in env.values():
        val = value.strip().lower()
        if val in ("1", "true", "yes", "release", "stable"):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: override policy enforcement.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    path = os.path.join(repo_root, OVERRIDES_PATH)
    if not os.path.isfile(path):
        print("override policy OK (no overrides file)")
        return 0

    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError) as exc:
        print("invalid overrides file: {}".format(exc))
        return 1

    overrides = payload.get("overrides", [])
    if overrides is None:
        overrides = []
    if not isinstance(overrides, list):
        print("overrides must be a list")
        return 1

    today = date.today()
    violations = []
    for entry in overrides:
        if not isinstance(entry, dict):
            violations.append("override entry must be an object")
            continue
        entry_id = entry.get("id")
        invariant = entry.get("invariant")
        reason = entry.get("reason")
        expires = entry.get("expires")
        if not entry_id:
            violations.append("override missing id")
        if not invariant:
            violations.append("override missing invariant")
        if not reason:
            violations.append("override missing reason")
        expiry = parse_date(expires)
        if not expiry:
            violations.append("override {} missing/invalid expires".format(entry_id or "<unknown>"))
        elif expiry < today:
            violations.append("override {} expired on {}".format(entry_id or "<unknown>", expires))

    if is_release_branch() and overrides:
        violations.append("overrides forbidden on release/stable branches")

    if violations:
        for item in violations:
            print(item)
        return 1

    if overrides:
        print("active overrides:")
        for entry in overrides:
            print("- {} ({}) expires {}".format(entry.get("id"), entry.get("invariant"), entry.get("expires")))

    print("override policy OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

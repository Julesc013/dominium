import argparse
import json
import os
import sys


REG_REL = os.path.join("data", "registries", "auditx_groups.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: AuditX group registry is structurally valid.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    path = os.path.join(repo_root, REG_REL)
    if not os.path.isfile(path):
        print("missing {}".format(REG_REL.replace("\\", "/")))
        return 1
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        print("invalid json {}".format(REG_REL.replace("\\", "/")))
        return 1

    groups = ((payload.get("record") or {}).get("groups") or [])
    if not isinstance(groups, list) or not groups:
        print("auditx groups missing/empty")
        return 1

    required_ids = {"auditx.group.core.policy", "auditx.group.full.semantic"}
    seen = set()
    for row in groups:
        if not isinstance(row, dict):
            print("auditx group entry must be object")
            return 1
        group_id = str(row.get("group_id", "")).strip()
        if not group_id:
            print("auditx group missing group_id")
            return 1
        seen.add(group_id)
        if not isinstance(row.get("paths"), list) or not row.get("paths"):
            print("{} missing path patterns".format(group_id))
            return 1
        if not isinstance(row.get("runner_command"), list) or not row.get("runner_command"):
            print("{} missing runner_command".format(group_id))
            return 1
        command = " ".join(str(item) for item in row.get("runner_command"))
        if "tools/auditx/auditx.py" not in command:
            print("{} runner_command must invoke auditx".format(group_id))
            return 1
    missing = sorted(required_ids - seen)
    if missing:
        print("missing required auditx groups: {}".format(",".join(missing)))
        return 1

    print("auditx group mapping invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

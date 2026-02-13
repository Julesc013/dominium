import argparse
import json
import os
import sys


def _load_plan_module(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.plan import build_execution_plan

    return build_execution_plan


def _canonical(plan_payload: dict) -> str:
    payload = dict(plan_payload)
    payload.pop("plan_path", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: XStack planner is deterministic.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    build_plan = _load_plan_module(repo_root)
    first = build_plan(repo_root=repo_root, gate_command="verify", requested_profile="FAST")
    second = build_plan(repo_root=repo_root, gate_command="verify", requested_profile="FAST")

    if str(first.get("plan_hash", "")) != str(second.get("plan_hash", "")):
        print("plan hash mismatch between identical planner invocations")
        return 1
    if _canonical(first) != _canonical(second):
        print("canonical plan payload mismatch between identical planner invocations")
        return 1
    print("gate planner determinism invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

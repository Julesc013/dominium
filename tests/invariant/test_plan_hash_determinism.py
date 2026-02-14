import argparse
import os
import sys


def _load_plan_module(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.plan import build_execution_plan

    return build_execution_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: plan hash inputs are deterministic and workspace-agnostic.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    build_plan = _load_plan_module(repo_root)

    first = build_plan(
        repo_root=repo_root,
        gate_command="verify",
        requested_profile="FAST",
        workspace_id="ws.alpha",
    )
    second = build_plan(
        repo_root=repo_root,
        gate_command="verify",
        requested_profile="FAST",
        workspace_id="ws.beta",
    )
    third = build_plan(
        repo_root=repo_root,
        gate_command="verify",
        requested_profile="FAST",
        workspace_id="ws.alpha",
    )

    if str(first.get("plan_hash", "")) != str(second.get("plan_hash", "")):
        print("plan hash should not vary with workspace id")
        return 1
    if str(first.get("plan_hash", "")) != str(third.get("plan_hash", "")):
        print("plan hash mismatch on identical repeated invocation")
        return 1

    strict = build_plan(
        repo_root=repo_root,
        gate_command="strict",
        requested_profile="STRICT",
        workspace_id="ws.alpha",
    )
    if str(first.get("plan_hash", "")) == str(strict.get("plan_hash", "")):
        print("plan hash should vary across different profile families")
        return 1

    print("plan hash determinism invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

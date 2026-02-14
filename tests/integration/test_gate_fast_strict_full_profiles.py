import argparse
import os
import sys


def _load_plan(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.plan import build_execution_plan

    return build_execution_plan


def _runner_ids(plan_payload: dict):
    out = []
    for row in plan_payload.get("nodes") or []:
        if isinstance(row, dict):
            out.append(str(row.get("runner_id", "")).strip())
    return out


def run_profiles(repo_root: str) -> int:
    build_plan = _load_plan(repo_root)
    fast = build_plan(repo_root=repo_root, gate_command="verify", requested_profile="FAST")
    strict = build_plan(repo_root=repo_root, gate_command="strict", requested_profile="STRICT")
    full = build_plan(repo_root=repo_root, gate_command="full", requested_profile="FULL")
    full_all = build_plan(repo_root=repo_root, gate_command="full", requested_profile="FULL_ALL")

    if fast.get("profile") != "FAST":
        print("verify should map to FAST profile")
        return 1
    if strict.get("profile") not in {"STRICT_LIGHT", "STRICT_DEEP"}:
        print("strict command should map to strict-light or strict-deep profile")
        return 1
    if full.get("profile") != "FULL":
        print("full command should map to FULL profile")
        return 1
    if full_all.get("profile") != "FULL_ALL":
        print("full all command should map to FULL_ALL profile")
        return 1
    print("gate profile mapping check OK")
    return 0


def run_fast_no_full_suite(repo_root: str) -> int:
    build_plan = _load_plan(repo_root)
    fast = build_plan(repo_root=repo_root, gate_command="verify", requested_profile="FAST")
    runners = set(_runner_ids(fast))
    forbidden = {"testx.group.dist", "performx_runner", "compatx_runner", "securex_runner"}
    hit = sorted(item for item in forbidden if item in runners)
    if hit:
        print("FAST plan must not include full-only runners: {}".format(",".join(hit)))
        return 1
    print("FAST profile excludes full suite runners")
    return 0


def run_full_shards_groups(repo_root: str) -> int:
    build_plan = _load_plan(repo_root)
    full_impacted = build_plan(repo_root=repo_root, gate_command="full", requested_profile="FULL")
    impacted_runners = _runner_ids(full_impacted)
    impacted_testx = sorted(item for item in impacted_runners if item.startswith("testx.group."))
    impacted_auditx = sorted(item for item in impacted_runners if item.startswith("auditx.group."))
    if len(impacted_testx) < 1 and len(impacted_auditx) < 1:
        print("FULL impacted plan should include at least one impacted shard group")
        return 1

    full_all = build_plan(repo_root=repo_root, gate_command="full", requested_profile="FULL_ALL")

    full_all_runners = _runner_ids(full_all)
    full_all_testx = sorted(item for item in full_all_runners if item.startswith("testx.group."))
    full_all_auditx = sorted(item for item in full_all_runners if item.startswith("auditx.group."))
    if len(full_all_testx) < 2:
        print("FULL all-groups mode should include sharded testx groups")
        return 1
    if len(full_all_auditx) < 2:
        print("FULL all-groups mode should include sharded auditx groups")
        return 1
    if len(full_all_testx) < len(impacted_testx):
        print("FULL all-groups mode must not include fewer testx shards than impacted mode")
        return 1
    if len(full_all_auditx) < len(impacted_auditx):
        print("FULL all-groups mode must not include fewer auditx shards than impacted mode")
        return 1
    print("FULL profile sharding check OK (impacted + all-groups)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Integration checks for gate FAST/STRICT/FULL planning.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--case",
        choices=("profiles", "fast_no_full_suite", "full_shards_groups"),
        required=True,
    )
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "profiles":
        return run_profiles(repo_root)
    if args.case == "fast_no_full_suite":
        return run_fast_no_full_suite(repo_root)
    return run_full_shards_groups(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())

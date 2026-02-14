import argparse
import os
import shutil
import sys


def _load_gate_module(repo_root: str):
    dev_dir = os.path.join(repo_root, "scripts", "dev")
    if dev_dir not in sys.path:
        sys.path.insert(0, dev_dir)
    import gate as gate_module  # pylint: disable=import-error

    return gate_module


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: strict cold performance ceiling detection is structural and deterministic.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    gate_module = _load_gate_module(repo_root)

    plan_payload = {
        "profile": "STRICT_DEEP",
        "plan_hash": "plan.hash.performance",
        "nodes": [
            {"node_id": "n1", "runner_id": "repox_runner", "group_id": "repox.structure.code"},
            {"node_id": "n2", "runner_id": "testx.group.runtime.verify", "group_id": "testx.group.runtime.verify"},
        ],
    }
    result = {
        "cache_misses": 2,
        "total_seconds": 180.0,
        "results": [
            {"node_id": "n1", "runner_id": "repox_runner", "cache_hit": False},
            {"node_id": "n2", "runner_id": "testx.group.runtime.verify", "cache_hit": False},
        ],
    }
    if not gate_module._strict_cold_ceiling_exceeded(plan_payload, result, 120.0):  # pylint: disable=protected-access
        print("expected strict cold ceiling detection trigger")
        return 1

    cache_root = os.path.join(repo_root, ".xstack_cache", "tests", "performance_ceiling")
    if os.path.isdir(cache_root):
        shutil.rmtree(cache_root)

    alert = gate_module._write_performance_ceiling_alert(  # pylint: disable=protected-access
        repo_root=repo_root,
        cache_root=cache_root,
        plan_payload=plan_payload,
        result=result,
        threshold_s=120.0,
        snapshot_mode=False,
    )
    cache_alert_path = str(alert.get("cache_alert_path", ""))
    if not cache_alert_path or not os.path.isfile(cache_alert_path):
        print("missing cache alert artifact")
        return 1
    if str(alert.get("snapshot_alert_path", "")):
        print("snapshot alert path should be empty in non-snapshot mode")
        return 1

    merged = gate_module._merge_performance_failure(  # pylint: disable=protected-access
        {"failure_classes": [], "failure_summary": [], "primary_failure_class": ""}
    )
    if "PERFORMANCE" not in set(str(item) for item in (merged.get("failure_classes") or [])):
        print("performance class not merged")
        return 1
    if str(merged.get("primary_failure_class", "")) != "PERFORMANCE":
        print("primary failure class should be PERFORMANCE after merge")
        return 1

    print("performance ceiling detection invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

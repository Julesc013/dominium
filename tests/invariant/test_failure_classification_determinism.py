import argparse
import os
import sys


def _load_failure_module(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.core.failure import aggregate_failure_classes, classify_failure

    return aggregate_failure_classes, classify_failure


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: failure classification is deterministic.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    aggregate_failure_classes, classify_failure = _load_failure_module(repo_root)

    scenarios = [
        ("repox_runner", 1, "refuse.command_unresolvable: tool missing", "MECHANICAL"),
        ("auditx.group.core.policy", 1, "schema version mismatch", "STRUCTURAL"),
        ("securex_runner", 1, "refuse.security.policy", "SECURITY"),
        ("auditx.group.core.policy", 1, "detected drift in canonical output", "DRIFT"),
        ("auditx.group.core.policy", 1, "policy check failed", "POLICY"),
        ("repox_runner", 1, "cache_corruption: entry_hash_mismatch", "CACHE_CORRUPTION"),
        ("repox_runner", 1, "assertion failed in semantic check", "SEMANTIC"),
        ("performx_runner", 1, "performance ceiling exceeded", "PERFORMANCE"),
    ]

    rows = []
    for runner_id, exit_code, output, expected in scenarios:
        first = classify_failure(runner_id=runner_id, exit_code=exit_code, output=output)
        second = classify_failure(runner_id=runner_id, exit_code=exit_code, output=output)
        if first != second:
            print("classification drift for scenario {}".format(expected))
            return 1
        if str(first.get("failure_class", "")) != expected:
            print("unexpected class: expected {} got {}".format(expected, first.get("failure_class", "")))
            return 1
        rows.append({"failure_class": str(first.get("failure_class", ""))})

    left = aggregate_failure_classes(rows)
    right = aggregate_failure_classes(list(reversed(rows)))
    if left != right:
        print("aggregate failure classification order-dependent")
        return 1

    print("failure classification determinism invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

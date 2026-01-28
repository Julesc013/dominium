import argparse
import os
import sys


FAMILIES = {
    "collapse_expand_equivalence": {
        "invariants": [
            "SCALE0-PROJECTION-001",
            "SCALE0-CONSERVE-002",
            "SCALE0-COMMIT-003",
            "SCALE0-NO-EXNIHILO-007",
        ],
        "files": {
            "docs/architecture/COLLAPSE_EXPAND_CONTRACT.md": [
                "macro capsule",
                "collapse must",
                "expansion must",
                "commit boundaries",
                "deterministic",
            ],
            "schema/macro_capsule.schema": [
                "record macro_capsule",
                "invariants",
                "statistics",
                "provenance",
                "reconstruction_seeds",
                "extensions",
            ],
        },
    },
    "invariant_conservation": {
        "invariants": [
            "SCALE0-CONSERVE-002",
        ],
        "files": {
            "docs/architecture/INVARIANTS_AND_TOLERANCES.md": [
                "resource totals",
                "energy balances",
                "population counts",
                "inventory conservation",
                "network topology",
                "committed contracts",
                "authority state",
            ],
        },
    },
    "tolerance_bound": {
        "invariants": [
            "SCALE0-TOLERANCE-005",
        ],
        "files": {
            "docs/architecture/INVARIANTS_AND_TOLERANCES.md": [
                "sufficient statistics",
                "tolerance",
                "stat-scale-prod-dist",
                "stat-scale-cons-dist",
                "stat-scale-fail-rate",
                "stat-scale-belief-dist",
                "stat-scale-wear-dist",
            ],
        },
    },
    "interest_pattern_invariance": {
        "invariants": [
            "SCALE0-INTEREST-006",
            "SCALE0-COMMIT-003",
        ],
        "files": {
            "docs/architecture/INTEREST_MODEL.md": [
                "interest",
                "player possession",
                "agent planning targets",
                "commit boundaries",
                "macro capsule",
            ],
            "docs/architecture/BUDGET_POLICY.md": [
                "defer_collapse",
                "defer_expansion",
                "max active tier-2",
                "max active tier-1",
            ],
        },
    },
    "cross_thread_determinism": {
        "invariants": [
            "SCALE0-DETERMINISM-004",
        ],
        "files": {
            "docs/architecture/MACRO_TIME_MODEL.md": [
                "deterministic event ordering",
                "cross-thread",
                "wall-clock",
            ],
            "docs/architecture/SCALING_MODEL.md": [
                "not different engines",
                "same primitives",
                "determinism",
            ],
        },
    },
    "replay_equivalence": {
        "invariants": [
            "SCALE0-REPLAY-008",
        ],
        "files": {
            "docs/architecture/MACRO_TIME_MODEL.md": [
                "replay",
                "collapse/expand",
                "event ordering",
            ],
            "docs/architecture/SCALING_COMPATIBILITY.md": [
                "replay",
                "mandatory",
                "legacy",
            ],
        },
    },
}


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def check_tokens(path, tokens, failures, repo_root):
    full_path = os.path.join(repo_root, path)
    if not os.path.isfile(full_path):
        failures.append("missing file: {}".format(path))
        return
    text = read_text(full_path).lower()
    for token in tokens:
        if token.lower() not in text:
            failures.append("missing '{}' in {}".format(token, path))


def check_invariants(invariant_ids, failures, repo_root):
    registry_path = os.path.join(repo_root, "docs", "architecture", "INVARIANT_REGISTRY.md")
    invariants_path = os.path.join(repo_root, "docs", "architecture", "INVARIANTS.md")
    if not os.path.isfile(registry_path):
        failures.append("missing invariant registry")
        return
    if not os.path.isfile(invariants_path):
        failures.append("missing invariants doc")
        return
    registry_text = read_text(registry_path)
    invariants_text = read_text(invariants_path)
    for inv_id in invariant_ids:
        if inv_id not in registry_text:
            failures.append("missing invariant id {} in registry".format(inv_id))
        if inv_id not in invariants_text:
            failures.append("missing invariant id {} in invariants doc".format(inv_id))


def main():
    parser = argparse.ArgumentParser(description="SCALE-0 TestX contract checks.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--family", required=True, choices=sorted(FAMILIES.keys()))
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    family = FAMILIES[args.family]
    failures = []

    check_invariants(family["invariants"], failures, repo_root)
    for rel_path, tokens in family["files"].items():
        check_tokens(rel_path, tokens, failures, repo_root)

    if failures:
        for item in failures:
            print("FAIL: {}".format(item))
        return 1

    print("SCALE-0 contracts OK for {}".format(args.family))
    return 0


if __name__ == "__main__":
    sys.exit(main())

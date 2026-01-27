import argparse
import os
import sys


FAMILIES = {
    "shard_ownership_exclusivity": {
        "invariants": [
            "MMO0-UNIVERSE-012",
            "MMO0-OWNERSHIP-013",
        ],
        "files": {
            "docs/arch/DISTRIBUTED_SIM_MODEL.md": [
                "logically single",
                "physically distributed",
                "exactly one shard",
                "commit boundaries",
                "ownership transfers",
                "double ownership",
            ],
            "docs/arch/CROSS_SHARD_LOG.md": [
                "ownership transfer",
                "append-only",
                "commit boundaries",
                "replayable",
            ],
        },
    },
    "cross_shard_message_ordering_determinism": {
        "invariants": [
            "MMO0-LOG-015",
            "MMO0-TIME-016",
        ],
        "files": {
            "docs/arch/CROSS_SHARD_LOG.md": [
                "append-only message logs",
                "deterministic ordering",
                "idempotent",
                "(delivery_tick, causal_key, origin_shard_id, message_id, sequence)",
            ],
            "docs/arch/DISTRIBUTED_TIME_MODEL.md": [
                "logical, not wall-clock",
                "ordering guarantee",
                "physical execution order",
                "identical regardless",
            ],
            "schema/cross_shard_message.schema": [
                "record cross_shard_message",
                "origin_tick",
                "delivery_tick",
                "causal_key",
                "order_key",
                "idempotency_key",
            ],
        },
    },
    "id_collision": {
        "invariants": [
            "MMO0-ID-014",
        ],
        "files": {
            "docs/arch/GLOBAL_ID_MODEL.md": [
                "globally unique identifier",
                "deterministically",
                "namespace",
                "shard_of_origin",
                "local_id",
                "collision-free without coordination",
                "reproducible on replay",
            ],
        },
    },
    "join_resync_determinism": {
        "invariants": [
            "MMO0-RESYNC-017",
        ],
        "files": {
            "docs/arch/JOIN_RESYNC_CONTRACT.md": [
                "worlddefinition",
                "capability lockfile",
                "latest snapshot",
                "macro capsule",
                "event log tail",
                "resync must be deterministic",
                "partial data refusal",
                "inspect-only",
            ],
            "docs/arch/REFUSAL_SEMANTICS.md": [
                "refuse_capability_missing",
                "refuse_invalid_intent",
            ],
        },
    },
    "legacy_sku_compatibility": {
        "invariants": [
            "MMO0-COMPAT-018",
        ],
        "files": {
            "docs/arch/MMO_COMPATIBILITY.md": [
                "single-shard universe",
                "same deterministic engine",
                "same authoritative engine code paths",
                "legacy",
                "frozen or inspect-only",
                "refuse live participation",
                "no forked",
            ],
            "docs/arch/DISTRIBUTED_SIM_MODEL.md": [
                "distribution must not change outcomes",
                "same deterministic code paths",
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
    registry_path = os.path.join(repo_root, "docs", "arch", "INVARIANT_REGISTRY.md")
    invariants_path = os.path.join(repo_root, "docs", "arch", "INVARIANTS.md")
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
    parser = argparse.ArgumentParser(description="MMO-0 distributed contract checks.")
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

    print("MMO-0 contracts OK for {}".format(args.family))
    return 0


if __name__ == "__main__":
    sys.exit(main())

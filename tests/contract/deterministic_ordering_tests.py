import argparse
import os
import random
import sys
from typing import Callable, Iterable, List, Sequence, Tuple, TypeVar


T = TypeVar("T")

REQUIRED_TOKENS = [
    "Entities",
    "Components",
    "Partitions and shards",
    "Domains and topology nodes",
    "Events (tick and sequence)",
    "Cross-shard messages",
    "Packs and providers",
    "Macro events",
    "(phase_id, task_id, sub_index)",
    "Hash map iteration order",
    "Absolute file paths",
]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def semver_tuple(value: str) -> Tuple[int, int, int]:
    parts = (value or "").split(".")
    nums: List[int] = []
    for part in parts[:3]:
        try:
            nums.append(int(part))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


def canonical_pack_key(pack: dict) -> Tuple[int, int, int, str, str, str]:
    major, minor, patch = semver_tuple(pack.get("pack_version", "0.0.0"))
    return (-major, -minor, -patch,
            pack.get("pack_id", ""),
            pack.get("provider_id", ""),
            pack.get("manifest_relpath", ""))


def assert_invariant(
    items: Sequence[T],
    key_fn: Callable[[T], Tuple],
    seeds: Iterable[int],
    label: str,
) -> None:
    canonical = tuple(sorted(items, key=key_fn))
    for seed in seeds:
        shuffled = list(items)
        rng = random.Random(seed)
        rng.shuffle(shuffled)
        candidate = tuple(sorted(shuffled, key=key_fn))
        if candidate != canonical:
            raise AssertionError("ordering invariance failed for {} with seed {}".format(label, seed))


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic ordering invariance tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    ordering_doc = os.path.join(repo_root, "docs", "arch", "DETERMINISTIC_ORDERING_POLICY.md")
    if not os.path.isfile(ordering_doc):
        print("missing ordering policy doc: {}".format(ordering_doc))
        return 1

    text = read_text(ordering_doc)
    missing = [token for token in REQUIRED_TOKENS if token not in text]
    if missing:
        for token in missing:
            print("ordering policy missing token: {}".format(token))
        return 1

    seeds = (0, 1, 7, 19, 42, 99)

    # Entities: (shard_id, topology_node_id)
    entities = [
        {"shard_id": "shard.b", "topology_node_id": "topo.002"},
        {"shard_id": "shard.a", "topology_node_id": "topo.010"},
        {"shard_id": "shard.a", "topology_node_id": "topo.002"},
        {"shard_id": "shard.c", "topology_node_id": "topo.001"},
    ]
    assert_invariant(entities, lambda e: (e["shard_id"], e["topology_node_id"]), seeds, "entities")

    # Components: (component_schema_id, shard_id, topology_node_id)
    components = [
        {"component_schema_id": "dominium.schema.field", "shard_id": "shard.b", "topology_node_id": "topo.002"},
        {"component_schema_id": "dominium.schema.domain", "shard_id": "shard.a", "topology_node_id": "topo.010"},
        {"component_schema_id": "dominium.schema.domain", "shard_id": "shard.a", "topology_node_id": "topo.002"},
        {"component_schema_id": "dominium.schema.domain", "shard_id": "shard.c", "topology_node_id": "topo.001"},
    ]
    assert_invariant(
        components,
        lambda c: (c["component_schema_id"], c["shard_id"], c["topology_node_id"]),
        seeds,
        "components",
    )

    # Events: (act_tick, event_seq, event_id)
    events = [
        {"act_tick": 5, "event_seq": 2, "event_id": "evt.b"},
        {"act_tick": 5, "event_seq": 1, "event_id": "evt.c"},
        {"act_tick": 4, "event_seq": 9, "event_id": "evt.a"},
        {"act_tick": 5, "event_seq": 1, "event_id": "evt.a"},
    ]
    assert_invariant(events, lambda e: (e["act_tick"], e["event_seq"], e["event_id"]), seeds, "events")

    # Cross-shard messages: (delivery_tick, causal_key, origin_shard_id, message_id, sequence)
    messages = [
        {"delivery_tick": 10, "causal_key": "c2", "origin_shard_id": "s2", "message_id": "m9", "sequence": 1},
        {"delivery_tick": 10, "causal_key": "c1", "origin_shard_id": "s3", "message_id": "m1", "sequence": 2},
        {"delivery_tick": 9, "causal_key": "c9", "origin_shard_id": "s1", "message_id": "m7", "sequence": 0},
        {"delivery_tick": 10, "causal_key": "c1", "origin_shard_id": "s3", "message_id": "m1", "sequence": 1},
    ]
    assert_invariant(
        messages,
        lambda m: (m["delivery_tick"], m["causal_key"], m["origin_shard_id"], m["message_id"], m["sequence"]),
        seeds,
        "cross_shard_messages",
    )

    # Packs/providers: descending semver, then stable identifiers.
    packs = [
        {"pack_version": "1.0.0", "pack_id": "org.example.a", "provider_id": "org.example", "manifest_relpath": "packs/a"},
        {"pack_version": "2.0.0", "pack_id": "org.example.b", "provider_id": "org.example", "manifest_relpath": "packs/b"},
        {"pack_version": "2.0.0", "pack_id": "org.example.a", "provider_id": "org.example", "manifest_relpath": "packs/a"},
        {"pack_version": "2.1.0", "pack_id": "org.example.c", "provider_id": "org.example", "manifest_relpath": "packs/c"},
    ]
    assert_invariant(packs, canonical_pack_key, seeds, "packs")

    # Macro events: (macro_tick, macro_phase, macro_event_id, domain_id)
    macro_events = [
        {"macro_tick": 100, "macro_phase": 2, "macro_event_id": "macro.b", "domain_id": "dom.a"},
        {"macro_tick": 100, "macro_phase": 1, "macro_event_id": "macro.c", "domain_id": "dom.b"},
        {"macro_tick": 99, "macro_phase": 9, "macro_event_id": "macro.a", "domain_id": "dom.c"},
        {"macro_tick": 100, "macro_phase": 1, "macro_event_id": "macro.a", "domain_id": "dom.a"},
    ]
    assert_invariant(
        macro_events,
        lambda m: (m["macro_tick"], m["macro_phase"], m["macro_event_id"], m["domain_id"]),
        seeds,
        "macro_events",
    )

    print("Deterministic ordering invariance OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

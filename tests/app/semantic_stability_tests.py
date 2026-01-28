import argparse
import json
import os
import sys


EXPECTED_ENTRIES = [
    {
        "id": "field.pack_manifest.pack_id",
        "kind": "field",
        "definition": "Reverse-DNS stable identifier for a pack. Identity is immutable and never reused.",
    },
    {
        "id": "field.pack_manifest.pack_version",
        "kind": "field",
        "definition": "Semver for pack content. Major bumps denote breaking changes; meaning never shifts.",
    },
    {
        "id": "field.pack_manifest.pack_format_version",
        "kind": "field",
        "definition": "Integer manifest format version that defines parsing and required keys.",
    },
    {
        "id": "field.pack_manifest.requires_engine",
        "kind": "field",
        "definition": "Engine version range required to load the pack; refusal if unmet.",
    },
    {
        "id": "field.pack_manifest.provides",
        "kind": "field",
        "definition": "Declared capabilities provided by this pack.",
    },
    {
        "id": "field.pack_manifest.depends",
        "kind": "field",
        "definition": "Capabilities required by this pack; never pack IDs or file paths.",
    },
    {
        "id": "field.pack_manifest.extensions",
        "kind": "field",
        "definition": "Opaque extension map that must be preserved across loads and saves.",
    },
    {
        "id": "capability.meaning",
        "kind": "capability",
        "definition": "An auditable, namespaced permission to perform an action or access an interface.",
    },
    {
        "id": "authority.semantics",
        "kind": "authority",
        "definition": "Authority gates actions only; it never gates visibility.",
    },
    {
        "id": "refusal.code.meaning",
        "kind": "refusal",
        "definition": "A refusal code is a stable integer and token that explains why an action was refused.",
    },
    {
        "id": "chunk_type.save",
        "kind": "chunk_type",
        "definition": "Chunk type identifies the semantic payload of a save/replay chunk.",
    },
    {
        "id": "process.io.meaning",
        "kind": "process",
        "definition": "Process IO meaning is the semantic contract of inputs and outputs.",
    },
    {
        "id": "policy.no_reuse_identifiers",
        "kind": "policy",
        "definition": "Identifiers once released must never be reused with new meaning.",
    },
    {
        "id": "policy.no_silent_reinterpretation",
        "kind": "policy",
        "definition": "Old data cannot be reinterpreted without explicit versioned transform or refusal.",
    },
]


REQUIRED_SECTIONS = [
    "Immutable Semantics",
    "Mutable Aspects",
    "Allowed Evolution Mechanisms",
    "Explicit Prohibitions",
    "Semantic Anchor Registry",
]

REQUIRED_PROHIBITIONS = [
    "Reusing identifiers with new meaning",
    "Silent reinterpretation of old data",
]


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def entry_key(entry):
    return (entry.get("id"), entry.get("kind"), entry.get("definition"))


def main():
    parser = argparse.ArgumentParser(description="Semantic stability lock checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    policy_path = os.path.join(repo_root, "docs", "architecture", "SEMANTIC_STABILITY_POLICY.md")
    lock_path = os.path.join(repo_root, "docs", "architecture", "SEMANTIC_STABILITY_LOCK.json")
    anti_path = os.path.join(repo_root, "docs", "architecture", "ANTI_ENTROPY_RULES.md")
    review_path = os.path.join(repo_root, "docs", "architecture", "ARCH_CHANGE_PROCESS.md")

    if not os.path.isfile(policy_path):
        print("missing policy doc: {}".format(policy_path))
        return 1
    if not os.path.isfile(lock_path):
        print("missing semantic lock: {}".format(lock_path))
        return 1
    if not os.path.isfile(anti_path):
        print("missing anti-entropy rules: {}".format(anti_path))
        return 1
    if not os.path.isfile(review_path):
        print("missing arch change process: {}".format(review_path))
        return 1

    policy_text = read_text(policy_path)
    for section in REQUIRED_SECTIONS:
        if section not in policy_text:
            print("missing section in policy: {}".format(section))
            return 1
    for item in REQUIRED_PROHIBITIONS:
        if item not in policy_text:
            print("missing prohibition in policy: {}".format(item))
            return 1

    anti_text = read_text(anti_path)
    if "future prompts" not in anti_text:
        print("anti-entropy rules missing future prompt requirement")
        return 1
    review_text = read_text(review_path)
    if "ANTI_ENTROPY_RULES" not in review_text and "ENTROPY0" not in review_text:
        print("anti-entropy rules not referenced in review checklist")
        return 1

    lock_data = load_json(lock_path)
    if lock_data.get("lock_id") != "dominium.semantic_stability_lock":
        print("lock_id mismatch")
        return 1
    if lock_data.get("lock_version") != 1:
        print("lock_version mismatch")
        return 1

    entries = lock_data.get("entries", [])
    if len(entries) != len(EXPECTED_ENTRIES):
        print("entry count mismatch")
        return 1

    expected_map = {entry_key(e): e for e in EXPECTED_ENTRIES}
    seen = set()
    for entry in entries:
        key = entry_key(entry)
        if key not in expected_map:
            print("unexpected or modified entry: {}".format(entry.get("id")))
            return 1
        if entry.get("id") in seen:
            print("duplicate entry id: {}".format(entry.get("id")))
            return 1
        seen.add(entry.get("id"))
        entry_id = entry.get("id", "")
        if "." not in entry_id:
            print("entry id not namespaced: {}".format(entry_id))
            return 1

    if len(seen) != len(EXPECTED_ENTRIES):
        print("missing entries in lock file")
        return 1

    print("Semantic stability lock OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

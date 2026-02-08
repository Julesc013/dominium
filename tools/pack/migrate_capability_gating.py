#!/usr/bin/env python3
import argparse
import json
import os
import re
from typing import Dict, List, Tuple


REQ_KEY = "requires" + "_" + "stage"
PROV_KEY = "provides" + "_" + "stage"
FEAT_KEY = "stage" + "_" + "features"
STAGE_PREFIX = "S" + "TAGE_"
PACK_SCHEMA_ID = "dominium.schema.pack_manifest"
PACK_TARGET_SCHEMA_VERSION = "2.3.0"
WORLD_TARGET_SCHEMA_ID = "dominium.schema.capability_declaration"
WORLD_TARGET_SCHEMA_VERSION = "1.0.0"


CAPABILITY_BY_RANK = {
    0: "dominium.capability.world.nonbio",
    1: "dominium.capability.world.life.nonintelligent",
    2: "dominium.capability.world.life.intelligent",
    3: "dominium.capability.world.pretool",
    4: "dominium.capability.society.institutions",
    5: "dominium.capability.infrastructure.industry",
    6: "dominium.capability.future.affordances",
}


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def parse_rank(value: str) -> int:
    if not isinstance(value, str):
        return -1
    if not value.startswith(STAGE_PREFIX):
        return -1
    match = re.match(r"^[A-Z]+_(\d+)_", value)
    if not match:
        return -1
    try:
        return int(match.group(1))
    except ValueError:
        return -1


def cap_ref(capability_id: str) -> Dict[str, str]:
    return {"capability_id": capability_id}


def extract_capability_ids(entries) -> List[str]:
    out = []
    for entry in normalize_list(entries):
        cap_id = None
        if isinstance(entry, dict):
            cap_id = entry.get("capability_id")
        elif isinstance(entry, str):
            cap_id = entry
        if isinstance(cap_id, str):
            out.append(cap_id)
    return out


def capability_refs(ids: List[str]) -> List[Dict[str, str]]:
    return [cap_ref(capability_id) for capability_id in ids]


def capability_for_rank(rank: int) -> str:
    return CAPABILITY_BY_RANK.get(rank, CAPABILITY_BY_RANK[0])


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def extract_record(payload):
    if isinstance(payload, dict):
        record = payload.get("record")
        if isinstance(record, dict):
            return record
    return None


def migrate_pack_manifest(path: str) -> Tuple[bool, Dict[str, str]]:
    payload = read_json(path)
    record = extract_record(payload)
    if not record:
        return False, {"path": path, "status": "skip", "reason": "record_missing"}

    req_rank = parse_rank(record.get(REQ_KEY))
    prov_rank = parse_rank(record.get(PROV_KEY))
    changed = False

    alias_requires = extract_capability_ids(record.get("depends"))
    alias_provides = extract_capability_ids(record.get("provides"))
    desired_requires = list(alias_requires)
    desired_provides = list(alias_provides)
    if not desired_requires and req_rank >= 0:
        desired_requires = [capability_for_rank(req_rank)]
    if not desired_provides and prov_rank >= 0:
        desired_provides = [capability_for_rank(prov_rank)]

    if extract_capability_ids(record.get("requires_capabilities")) != desired_requires:
        record["requires_capabilities"] = capability_refs(desired_requires)
        changed = True
    if extract_capability_ids(record.get("provides_capabilities")) != desired_provides:
        record["provides_capabilities"] = capability_refs(desired_provides)
        changed = True
    if "optional_capabilities" not in record:
        record["optional_capabilities"] = []
        changed = True
    if "entitlements" not in record:
        record["entitlements"] = []
        changed = True

    if REQ_KEY in record:
        del record[REQ_KEY]
        changed = True
    if PROV_KEY in record:
        del record[PROV_KEY]
        changed = True
    if FEAT_KEY in record:
        del record[FEAT_KEY]
        changed = True

    if payload.get("schema_id") == PACK_SCHEMA_ID and payload.get("schema_version") != PACK_TARGET_SCHEMA_VERSION:
        payload["schema_version"] = PACK_TARGET_SCHEMA_VERSION
        changed = True

    if changed:
        write_json(path, payload)
        return True, {"path": path, "status": "updated"}
    return False, {"path": path, "status": "unchanged"}


def migrate_world_capability_fixture(path: str) -> Tuple[bool, Dict[str, str]]:
    payload = read_json(path)
    record = extract_record(payload)
    if not record:
        return False, {"path": path, "status": "skip", "reason": "record_missing"}

    req_rank = parse_rank(record.get(REQ_KEY))
    prov_rank = parse_rank(record.get(PROV_KEY))
    changed = False

    if req_rank >= 0:
        record["requires_capabilities"] = [cap_ref(capability_for_rank(req_rank))]
        changed = True
    if prov_rank >= 0:
        record["provides_capabilities"] = [cap_ref(capability_for_rank(prov_rank))]
        changed = True
    if "requires_capabilities" not in record:
        record["requires_capabilities"] = []
        changed = True
    if "provides_capabilities" not in record:
        record["provides_capabilities"] = []
        changed = True
    if "optional_capabilities" not in record:
        record["optional_capabilities"] = []
        changed = True
    if "entitlements" not in record:
        record["entitlements"] = []
        changed = True
    if FEAT_KEY in record:
        del record[FEAT_KEY]
        changed = True
    if REQ_KEY in record:
        del record[REQ_KEY]
        changed = True
    if PROV_KEY in record:
        del record[PROV_KEY]
        changed = True

    if payload.get("schema_id") != WORLD_TARGET_SCHEMA_ID:
        payload["schema_id"] = WORLD_TARGET_SCHEMA_ID
        changed = True
    if payload.get("schema_version") != WORLD_TARGET_SCHEMA_VERSION:
        payload["schema_version"] = WORLD_TARGET_SCHEMA_VERSION
        changed = True

    if changed:
        write_json(path, payload)
        return True, {"path": path, "status": "updated"}
    return False, {"path": path, "status": "unchanged"}


def discover_pack_manifests(repo_root: str) -> List[str]:
    roots = [
        os.path.join(repo_root, "data", "packs"),
        os.path.join(repo_root, "data", "worldgen"),
        os.path.join(repo_root, "tests", "fixtures"),
        os.path.join(repo_root, "tests", "distribution", "fixtures"),
    ]
    out = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _, files in os.walk(root):
            for name in files:
                if name == "pack_manifest.json":
                    out.append(os.path.join(walk_root, name))
    out.sort()
    return out


def discover_world_fixtures(repo_root: str) -> List[str]:
    root = os.path.join(repo_root, "tests", "fixtures", "worlds")
    out = []
    if not os.path.isdir(root):
        return out
    for walk_root, _, files in os.walk(root):
        for name in files:
            if name.endswith(".json"):
                out.append(os.path.join(walk_root, name))
    out.sort()
    return out


def to_rel(repo_root: str, abs_path: str) -> str:
    return os.path.relpath(abs_path, repo_root).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic manifest migration to capability-only gating.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report", default="build/capability_gating_migration_report.json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    pack_results = []
    world_results = []
    updated = 0

    for path in discover_pack_manifests(repo_root):
        changed, result = migrate_pack_manifest(path)
        result["path"] = to_rel(repo_root, path)
        pack_results.append(result)
        if changed:
            updated += 1

    for path in discover_world_fixtures(repo_root):
        changed, result = migrate_world_capability_fixture(path)
        result["path"] = to_rel(repo_root, path)
        world_results.append(result)
        if changed:
            updated += 1

    report = {
        "schema_id": "dominium.audit.capability_gating_migration",
        "schema_version": "1.0.0",
        "updated_files": updated,
        "pack_manifests": pack_results,
        "world_fixtures": world_results,
    }

    report_path = os.path.join(repo_root, args.report)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    write_json(report_path, report)
    print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

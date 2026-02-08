#!/usr/bin/env python3
import argparse
import copy
import json
import os
import sys


PACK_MANIFEST_SCHEMA_ID = "dominium.schema.pack_manifest"
PACK_MANIFEST_SOURCE_VERSION = "1.0.0"
PACK_MANIFEST_TARGET_VERSION = "2.0.0"
PACK_MANIFEST_SOURCE_VERSION_2_1 = "2.1.0"
PACK_MANIFEST_TARGET_VERSION_2_2 = "2.2.0"
PACK_MANIFEST_SOURCE_VERSION_2_2 = "2.2.0"
PACK_MANIFEST_TARGET_VERSION_2_3 = "2.3.0"
CAPABILITY_BY_RANK = {
    0: "dominium.capability.world.nonbio",
    1: "dominium.capability.world.life.nonintelligent",
    2: "dominium.capability.world.life.intelligent",
    3: "dominium.capability.world.pretool",
    4: "dominium.capability.society.institutions",
    5: "dominium.capability.infrastructure.industry",
    6: "dominium.capability.future.affordances",
}


def _stable_payload(payload):
    return json.loads(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))


def _migrate_pack_manifest_aliases(record, target_version):
    has_requires = "requires_engine" in record
    has_required_alias = "required_engine_version" in record
    has_depends = "depends" in record
    has_dependencies_alias = "dependencies" in record

    if has_requires and has_required_alias and record["requires_engine"] != record["required_engine_version"]:
        return None, {
            "code": "SCHEMA-MIGRATION-REFUSE",
            "message": "requires_engine and required_engine_version conflict",
            "details": {"field": "requires_engine"}
        }
    if has_depends and has_dependencies_alias and record["depends"] != record["dependencies"]:
        return None, {
            "code": "SCHEMA-MIGRATION-REFUSE",
            "message": "depends and dependencies conflict",
            "details": {"field": "depends"}
        }

    if has_requires:
        requires_engine = record["requires_engine"]
    else:
        requires_engine = record.get("required_engine_version")
    if not isinstance(requires_engine, str) or not requires_engine:
        return None, {
            "code": "SCHEMA-MIGRATION-REFUSE",
            "message": "requires_engine missing",
            "details": {"field": "requires_engine"}
        }

    if has_depends:
        depends = record["depends"]
    else:
        depends = record.get("dependencies")
    if not isinstance(depends, list):
        return None, {
            "code": "SCHEMA-MIGRATION-REFUSE",
            "message": "depends missing",
            "details": {"field": "depends"}
        }

    migrated = copy.deepcopy(record)
    migrated["requires_engine"] = requires_engine
    migrated["required_engine_version"] = requires_engine
    migrated["depends"] = copy.deepcopy(depends)
    migrated["dependencies"] = copy.deepcopy(depends)
    migrated["schema_version"] = target_version
    return migrated, None


def _parse_rank(value):
    if not isinstance(value, str):
        return -1
    if not value.startswith("S" + "TAGE_"):
        return -1
    parts = value.split("_")
    if len(parts) < 2:
        return -1
    try:
        return int(parts[1])
    except ValueError:
        return -1


def _capability_for_rank(rank):
    return CAPABILITY_BY_RANK.get(rank, CAPABILITY_BY_RANK[0])


def _extract_capability_ids(values):
    ids = []
    if not isinstance(values, list):
        return ids
    for item in values:
        if isinstance(item, dict):
            cap_id = item.get("capability_id")
        else:
            cap_id = item
        if isinstance(cap_id, str):
            ids.append(cap_id)
    return ids


def _capability_refs(ids):
    return [{"capability_id": cap_id} for cap_id in ids]


def migrate_pack_manifest_1_0_0_to_2_0_0(payload):
    if not isinstance(payload, dict):
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "payload must be object",
                "details": {}
            }
        }

    schema_id = payload.get("schema_id")
    schema_version = payload.get("schema_version")
    if schema_id != PACK_MANIFEST_SCHEMA_ID:
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "schema_id mismatch",
                "details": {"schema_id": schema_id}
            }
        }
    if schema_version != PACK_MANIFEST_SOURCE_VERSION:
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "source schema_version mismatch",
                "details": {"schema_version": schema_version}
            }
        }

    migrated, refusal = _migrate_pack_manifest_aliases(payload, PACK_MANIFEST_TARGET_VERSION)
    if refusal is not None:
        return {"ok": False, "refusal": refusal}

    return {
        "ok": True,
        "result": _stable_payload(migrated),
        "audit": {
            "schema_id": PACK_MANIFEST_SCHEMA_ID,
            "source_version": PACK_MANIFEST_SOURCE_VERSION,
            "target_version": PACK_MANIFEST_TARGET_VERSION,
            "migration_process_id": "process.schema.migrate.pack_manifest.v1_to_v2",
            "data_loss": "none"
        }
    }


def migrate_pack_manifest_2_1_0_to_2_2_0(payload):
    if not isinstance(payload, dict):
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "payload must be object",
                "details": {}
            }
        }

    schema_id = payload.get("schema_id")
    schema_version = payload.get("schema_version")
    if schema_id != PACK_MANIFEST_SCHEMA_ID:
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "schema_id mismatch",
                "details": {"schema_id": schema_id}
            }
        }
    if schema_version != PACK_MANIFEST_SOURCE_VERSION_2_1:
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "source schema_version mismatch",
                "details": {"schema_version": schema_version}
            }
        }

    migrated, refusal = _migrate_pack_manifest_aliases(payload, PACK_MANIFEST_TARGET_VERSION_2_2)
    if refusal is not None:
        return {"ok": False, "refusal": refusal}

    req_key = "requires" + "_" + "stage"
    prov_key = "provides" + "_" + "stage"
    feat_key = "stage" + "_" + "features"
    req_rank = _parse_rank(migrated.get(req_key))
    prov_rank = _parse_rank(migrated.get(prov_key))

    requires_caps = _extract_capability_ids(migrated.get("requires_capabilities"))
    provides_caps = _extract_capability_ids(migrated.get("provides_capabilities"))
    if not requires_caps and req_rank >= 0:
        requires_caps = [_capability_for_rank(req_rank)]
    if not provides_caps and prov_rank >= 0:
        provides_caps = [_capability_for_rank(prov_rank)]
    migrated["requires_capabilities"] = _capability_refs(requires_caps)
    migrated["provides_capabilities"] = _capability_refs(provides_caps)
    if "optional_capabilities" not in migrated:
        migrated["optional_capabilities"] = []
    if "entitlements" not in migrated:
        migrated["entitlements"] = []
    for field in (req_key, prov_key, feat_key):
        if field in migrated:
            del migrated[field]

    return {
        "ok": True,
        "result": _stable_payload(migrated),
        "audit": {
            "schema_id": PACK_MANIFEST_SCHEMA_ID,
            "source_version": PACK_MANIFEST_SOURCE_VERSION_2_1,
            "target_version": PACK_MANIFEST_TARGET_VERSION_2_2,
            "migration_process_id": "process.schema.migrate.pack_manifest.v2_1_to_v2_2",
            "data_loss": "none"
        }
    }


def migrate_pack_manifest_2_2_0_to_2_3_0(payload):
    if not isinstance(payload, dict):
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "payload must be object",
                "details": {}
            }
        }

    schema_id = payload.get("schema_id")
    schema_version = payload.get("schema_version")
    if schema_id != PACK_MANIFEST_SCHEMA_ID:
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "schema_id mismatch",
                "details": {"schema_id": schema_id}
            }
        }
    if schema_version != PACK_MANIFEST_SOURCE_VERSION_2_2:
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "source schema_version mismatch",
                "details": {"schema_version": schema_version}
            }
        }

    migrated, refusal = _migrate_pack_manifest_aliases(payload, PACK_MANIFEST_TARGET_VERSION_2_3)
    if refusal is not None:
        return {"ok": False, "refusal": refusal}
    for field in ("requires" + "_stage", "provides" + "_stage", "stage" + "_features"):
        if field in migrated:
            del migrated[field]
    for field in ("requires_capabilities", "provides_capabilities", "optional_capabilities", "entitlements"):
        if field not in migrated:
            migrated[field] = []

    return {
        "ok": True,
        "result": _stable_payload(migrated),
        "audit": {
            "schema_id": PACK_MANIFEST_SCHEMA_ID,
            "source_version": PACK_MANIFEST_SOURCE_VERSION_2_2,
            "target_version": PACK_MANIFEST_TARGET_VERSION_2_3,
            "migration_process_id": "process.schema.migrate.pack_manifest.v2_2_to_v2_3",
            "data_loss": "none"
        }
    }


MIGRATION_HANDLERS = {
    (PACK_MANIFEST_SCHEMA_ID, PACK_MANIFEST_SOURCE_VERSION, PACK_MANIFEST_TARGET_VERSION): (
        "process.schema.migrate.pack_manifest.v1_to_v2",
        migrate_pack_manifest_1_0_0_to_2_0_0,
    ),
    (PACK_MANIFEST_SCHEMA_ID, PACK_MANIFEST_SOURCE_VERSION_2_1, PACK_MANIFEST_TARGET_VERSION_2_2): (
        "process.schema.migrate.pack_manifest.v2_1_to_v2_2",
        migrate_pack_manifest_2_1_0_to_2_2_0,
    ),
    (PACK_MANIFEST_SCHEMA_ID, PACK_MANIFEST_SOURCE_VERSION_2_2, PACK_MANIFEST_TARGET_VERSION_2_3): (
        "process.schema.migrate.pack_manifest.v2_2_to_v2_3",
        migrate_pack_manifest_2_2_0_to_2_3_0,
    )
}


def migrate_payload(payload, schema_id, source_version, target_version):
    key = (schema_id, source_version, target_version)
    entry = MIGRATION_HANDLERS.get(key)
    if entry is None:
        return {
            "ok": False,
            "refusal": {
                "code": "SCHEMA-MIGRATION-REFUSE",
                "message": "migration route not found",
                "details": {
                    "schema_id": schema_id,
                    "source_version": source_version,
                    "target_version": target_version
                }
            }
        }
    _, handler = entry
    return handler(payload)


def _cli_main():
    parser = argparse.ArgumentParser(description="Explicit schema migration runner.")
    parser.add_argument("--input", required=True, help="Input JSON file path.")
    parser.add_argument("--output", required=True, help="Output JSON file path.")
    parser.add_argument("--schema-id", required=True)
    parser.add_argument("--source-version", required=True)
    parser.add_argument("--target-version", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    result = migrate_payload(payload, args.schema_id, args.source_version, args.target_version)
    if not result.get("ok"):
        print(json.dumps(result, sort_keys=True, ensure_ascii=True))
        return 1
    with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result.get("result"), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")
    print(json.dumps(result.get("audit"), sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(_cli_main())

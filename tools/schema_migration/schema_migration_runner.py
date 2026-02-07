#!/usr/bin/env python3
import argparse
import copy
import json
import os
import sys


PACK_MANIFEST_SCHEMA_ID = "dominium.schema.pack_manifest"
PACK_MANIFEST_SOURCE_VERSION = "1.0.0"
PACK_MANIFEST_TARGET_VERSION = "2.0.0"


def _stable_payload(payload):
    return json.loads(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))


def _migrate_pack_manifest_aliases(record):
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
    migrated["schema_version"] = PACK_MANIFEST_TARGET_VERSION
    return migrated, None


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

    migrated, refusal = _migrate_pack_manifest_aliases(payload)
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


MIGRATION_HANDLERS = {
    (PACK_MANIFEST_SCHEMA_ID, PACK_MANIFEST_SOURCE_VERSION, PACK_MANIFEST_TARGET_VERSION): (
        "process.schema.migrate.pack_manifest.v1_to_v2",
        migrate_pack_manifest_1_0_0_to_2_0_0,
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

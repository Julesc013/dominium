import argparse
import hashlib
import importlib.util
import json
import os
import sys


MIGRATION_REGISTRY_PATH = os.path.join("schema", "SCHEMA_MIGRATION_REGISTRY.json")
PROCESS_REGISTRY_PATH = os.path.join("data", "registries", "process_registry.json")
MIGRATION_RUNNER_PATH = os.path.join("tools", "schema_migration", "schema_migration_runner.py")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _digest(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_runner(repo_root):
    path = os.path.join(repo_root, MIGRATION_RUNNER_PATH)
    spec = importlib.util.spec_from_file_location("schema_migration_runner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pack_manifest_v1_fixture():
    return {
        "schema_id": "dominium.schema.pack_manifest",
        "schema_version": "1.0.0",
        "pack_id": "org.dominium.example.pack",
        "pack_version": "1.0.0",
        "pack_format_version": 1,
        "required_engine_version": "0.0.0",
        "dependencies": [{"capability_id": "cap.example.alpha"}],
        "provides": [{"capability_id": "cap.example.beta"}],
        "extensions": {"org.dominium.note": {"v": 1}},
        "unknown_legacy_field": {"preserve": True}
    }


def _build_fixture_for_route(schema_id, source_version, target_version):
    if schema_id == "dominium.schema.pack_manifest" and source_version == "1.0.0" and target_version == "2.0.0":
        return _pack_manifest_v1_fixture()
    return None


def main():
    parser = argparse.ArgumentParser(description="Schema migration contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []
    registry = _load_json(os.path.join(repo_root, MIGRATION_REGISTRY_PATH))
    process_registry = _load_json(os.path.join(repo_root, PROCESS_REGISTRY_PATH))
    runner = _load_runner(repo_root)

    process_ids = set()
    for entry in process_registry.get("records", []):
        if isinstance(entry, dict):
            process_id = entry.get("process_id")
            if isinstance(process_id, str):
                process_ids.add(process_id)

    migrations = registry.get("migrations", [])
    if not isinstance(migrations, list) or not migrations:
        violations.append("missing migrations in {}".format(MIGRATION_REGISTRY_PATH))
        migrations = []

    for migration in migrations:
        if not isinstance(migration, dict):
            violations.append("invalid migration entry in {}".format(MIGRATION_REGISTRY_PATH))
            continue
        schema_id = migration.get("schema_id")
        source_version = migration.get("source_version")
        target_version = migration.get("target_version")
        process_id = migration.get("migration_process_id")
        if process_id not in process_ids:
            violations.append("migration process not registered: {}".format(process_id))
            continue

        fixture = _build_fixture_for_route(schema_id, source_version, target_version)
        if fixture is None:
            violations.append("missing fixture for migration route {} {} -> {}".format(
                schema_id, source_version, target_version
            ))
            continue

        result_a = runner.migrate_payload(fixture, schema_id, source_version, target_version)
        result_b = runner.migrate_payload(fixture, schema_id, source_version, target_version)
        if not result_a.get("ok"):
            violations.append("migration refused unexpectedly for {} {} -> {}".format(
                schema_id, source_version, target_version
            ))
            continue
        if _digest(result_a) != _digest(result_b):
            violations.append("non-deterministic migration output for {} {} -> {}".format(
                schema_id, source_version, target_version
            ))
            continue

        migrated = result_a.get("result", {})
        if migrated.get("schema_id") != schema_id:
            violations.append("schema_id changed unexpectedly for {}".format(schema_id))
        if migrated.get("schema_version") != target_version:
            violations.append("target schema_version mismatch for {}".format(schema_id))
        if "unknown_legacy_field" not in migrated:
            violations.append("unknown field lost in migration for {}".format(schema_id))
        if migrated.get("required_engine_version") != migrated.get("requires_engine"):
            violations.append("engine requirement alias mismatch after migration for {}".format(schema_id))
        if migrated.get("dependencies") != migrated.get("depends"):
            violations.append("dependency alias mismatch after migration for {}".format(schema_id))

        bad = dict(fixture)
        bad["requires_engine"] = "9.9.9"
        refusal = runner.migrate_payload(bad, schema_id, source_version, target_version)
        if refusal.get("ok"):
            violations.append("conflict input did not refuse for {}".format(schema_id))

    if violations:
        for violation in sorted(set(violations)):
            print(violation)
        return 1

    print("Schema migration tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

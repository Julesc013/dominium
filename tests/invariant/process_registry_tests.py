import argparse
import json
import os
import sys

from invariant_utils import is_override_active


PROCESS_SCHEMA_ID = "dominium.schema.process"
REGISTRY_SCHEMA_ID = "dominium.schema.process_registry"
REGISTRY_PATH = os.path.join("data", "registries", "process_registry.json")
FIXTURE_PATHS = (
    os.path.join("tests", "contract", "terrain_fixtures.json"),
)


def load_json(path, violations, label):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        violations.append("{}: unable to read {}: {}".format(label, path, exc))
        return None


def iter_json_files(root):
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith(".json"):
                continue
            if "process" not in name.lower():
                continue
            yield os.path.join(dirpath, name)


def collect_process_defs(repo_root, violations):
    defs = {}
    packs_root = os.path.join(repo_root, "data", "packs")
    if not os.path.isdir(packs_root):
        violations.append("missing packs directory: data/packs")
        return defs

    for path in iter_json_files(packs_root):
        data = load_json(path, violations, "process-defs")
        if not isinstance(data, dict):
            continue
        schema_id = data.get("schema_id")
        if not schema_id and isinstance(data.get("record"), dict):
            schema_id = data["record"].get("schema_id")
        if schema_id != PROCESS_SCHEMA_ID:
            continue
        records = data.get("records")
        if records is None and isinstance(data.get("record"), dict):
            records = data["record"].get("records")
        if not isinstance(records, list):
            violations.append("process-defs: invalid records list in {}".format(path))
            continue
        rel_path = os.path.relpath(path, repo_root).replace("\\", "/")
        parts = rel_path.split("/")
        pack_id = parts[2] if len(parts) > 2 and parts[0] == "data" and parts[1] == "packs" else ""
        for record in records:
            if not isinstance(record, dict):
                violations.append("process-defs: invalid record in {}".format(rel_path))
                continue
            process_id = record.get("process_id")
            if not process_id:
                violations.append("process-defs: missing process_id in {}".format(rel_path))
                continue
            if process_id in defs:
                violations.append("process-defs: duplicate process_id {} in {}".format(process_id, rel_path))
                continue
            defs[process_id] = {
                "record": record,
                "pack_id": pack_id,
                "path": rel_path,
            }
    return defs


def collect_fixture_process_ids(repo_root, violations):
    ids = set()
    for rel_path in FIXTURE_PATHS:
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            continue
        data = load_json(path, violations, "process-fixtures")
        if data is None:
            continue
        collect_process_ids(data, ids)
    return ids


def collect_process_ids(node, ids):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "process_id" and isinstance(value, str):
                ids.add(value)
            else:
                collect_process_ids(value, ids)
    elif isinstance(node, list):
        for item in node:
            collect_process_ids(item, ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Process registry contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-PROCESS-REGISTRY"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    registry_path = os.path.join(repo_root, REGISTRY_PATH)
    if not os.path.isfile(registry_path):
        violations.append("missing process registry: {}".format(REGISTRY_PATH))
        registry = None
    else:
        registry = load_json(registry_path, violations, "process-registry")

    registry_entries = {}
    registry_ids = []
    if isinstance(registry, dict):
        if registry.get("schema_id") != REGISTRY_SCHEMA_ID:
            violations.append("process-registry: schema_id mismatch in {}".format(REGISTRY_PATH))
        records = registry.get("records")
        if not isinstance(records, list):
            violations.append("process-registry: records must be a list in {}".format(REGISTRY_PATH))
        else:
            for entry in records:
                if not isinstance(entry, dict):
                    violations.append("process-registry: invalid entry in {}".format(REGISTRY_PATH))
                    continue
                process_id = entry.get("process_id")
                if not process_id:
                    violations.append("process-registry: missing process_id entry")
                    continue
                if process_id in registry_entries:
                    violations.append("process-registry: duplicate process_id {}".format(process_id))
                    continue
                registry_entries[process_id] = entry
                registry_ids.append(process_id)

            for process_id, entry in registry_entries.items():
                notes = entry.get("determinism_notes") or []
                if not isinstance(notes, list) or not notes:
                    violations.append("process-registry: missing determinism_notes for {}".format(process_id))

    process_defs = collect_process_defs(repo_root, violations)
    fixture_ids = collect_fixture_process_ids(repo_root, violations)

    for process_id in fixture_ids:
        if process_id not in registry_entries:
            violations.append("process-registry: fixture process_id missing from registry: {}".format(process_id))

    for process_id, info in process_defs.items():
        entry = registry_entries.get(process_id)
        if not entry:
            violations.append("process-registry: missing registry entry for {}".format(process_id))
            continue
        pack_id = info.get("pack_id")
        rel_path = info.get("path", "")
        record = info.get("record", {})
        ext = entry.get("extensions") if isinstance(entry.get("extensions"), dict) else {}
        source_pack = ext.get("source_pack")
        if pack_id and source_pack != pack_id:
            violations.append("process-registry: source_pack mismatch for {} ({} != {})".format(
                process_id, source_pack, pack_id
            ))
        if rel_path and rel_path not in (entry.get("description") or ""):
            violations.append("process-registry: description missing source path for {}".format(process_id))

        required_authority = record.get("required_authority_tags") or []
        required_law = entry.get("required_law_checks") or []
        missing_law = [tag for tag in required_authority if tag not in required_law]
        if missing_law:
            violations.append("process-registry: required_law_checks missing {} for {}".format(
                ", ".join(missing_law), process_id
            ))

        failure_tags = record.get("failure_mode_tags") or []
        failure_modes = entry.get("failure_modes") or []
        missing_failures = [tag for tag in failure_tags if tag not in failure_modes]
        if missing_failures:
            violations.append("process-registry: failure_modes missing {} for {}".format(
                ", ".join(missing_failures), process_id
            ))

        not_defined = (record.get("extensions") or {}).get("not_defined") or []
        if "no_truth_mutation" in not_defined:
            if entry.get("affected_fields") or entry.get("affected_assemblies"):
                violations.append("process-registry: no_truth_mutation requires empty affected scope for {}".format(
                    process_id
                ))

    for process_id, entry in registry_entries.items():
        ext = entry.get("extensions") if isinstance(entry.get("extensions"), dict) else {}
        if ext.get("source_pack") and process_id not in process_defs:
            violations.append("process-registry: stale registry entry without source pack definition: {}".format(
                process_id
            ))

    if violations:
        for violation in sorted(set(violations)):
            print(violation)
        return 1

    print("Process registry contract tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

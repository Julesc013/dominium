import argparse
import os
import sys
from typing import Dict, List, Optional, Set, Tuple


FAB_SCHEMA_FILES = [
    "schema/material.schema",
    "schema/substance.schema",
    "schema/interface.schema",
    "schema/part.schema",
    "schema/assembly.schema",
    "schema/process_family.schema",
    "schema/instrument.schema",
    "schema/standard.schema",
    "schema/quality.schema",
    "schema/batch_lot.schema",
    "schema/hazard.schema",
]

ALLOWLIST_REFS = {
    "constraint_ref",
    "failure_model_ref",
    "mitigation_ref",
    "node_ref",
    "process_io_ref",
    "provenance_ref",
}


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_records(text: str) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    records: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
    current_record: Optional[str] = None
    current_section: Optional[str] = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("record "):
            current_record = line.split()[1]
            records[current_record] = {"required": [], "optional": []}
            current_section = None
            continue
        if line == "required:":
            current_section = "required"
            continue
        if line == "optional:":
            current_section = "optional"
            continue
        if line.startswith("- ") and current_record and current_section:
            item = line[2:]
            if ":" not in item:
                continue
            field, type_name = [part.strip() for part in item.split(":", 1)]
            records[current_record][current_section].append((field, type_name))
    return records


def extract_ref_types(type_name: str) -> List[str]:
    type_name = type_name.strip()
    if type_name.startswith("[") and type_name.endswith("]"):
        type_name = type_name[1:-1].strip()
    if type_name.endswith("_ref"):
        return [type_name]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-schema reference integrity tests (FAB).")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations: List[str] = []
    for rel_path in FAB_SCHEMA_FILES:
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            violations.append("missing schema file: {}".format(rel_path))
            continue
        text = read_text(path)
        records = parse_records(text)
        ref_types: Set[str] = set()
        for record in records.values():
            for _field, type_name in record.get("required", []) + record.get("optional", []):
                for ref in extract_ref_types(type_name):
                    ref_types.add(ref)

        for ref_type in sorted(ref_types):
            if ref_type in ALLOWLIST_REFS:
                continue
            base = ref_type[: -len("_ref")]
            schema_path = os.path.join(repo_root, "schema", "{}.schema".format(base))
            if not os.path.isfile(schema_path):
                violations.append(
                    "missing referenced schema for {} in {} (expected {})".format(
                        ref_type, rel_path, "schema/{}.schema".format(base)
                    )
                )

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Schema reference integrity tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

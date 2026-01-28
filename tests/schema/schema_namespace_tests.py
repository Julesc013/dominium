import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


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

SCHEMA_ID_RE = re.compile(r"^\s*schema_id\s*:\s*(\S+)")
REVERSE_DNS_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9][a-z0-9_-]*)+$")


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_schema_id(text: str) -> Optional[str]:
    for line in text.splitlines():
        match = SCHEMA_ID_RE.match(line)
        if match:
            return match.group(1)
    return None


def parse_records(text: str) -> Tuple[Dict[str, Dict[str, List[Tuple[str, str]]]], Optional[str]]:
    records: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
    root_record: Optional[str] = None
    in_required_shape = False
    current_record: Optional[str] = None
    current_section: Optional[str] = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("REQUIRED SHAPE:"):
            in_required_shape = True
            continue
        if line.startswith("record "):
            current_record = line.split()[1]
            records[current_record] = {"required": [], "optional": []}
            current_section = None
            if in_required_shape and root_record is None:
                root_record = current_record
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

    return records, root_record


def main() -> int:
    parser = argparse.ArgumentParser(description="Schema namespace validation tests (FAB).")
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
        schema_id = parse_schema_id(text)
        if not schema_id:
            violations.append("missing schema_id in {}".format(rel_path))
            continue
        if not schema_id.isascii():
            violations.append("schema_id not ascii in {}: {}".format(rel_path, schema_id))
        if schema_id.lower() != schema_id:
            violations.append("schema_id not lowercase in {}: {}".format(rel_path, schema_id))
        if not REVERSE_DNS_RE.match(schema_id):
            violations.append("schema_id not reverse-dns in {}: {}".format(rel_path, schema_id))

        records, root_record = parse_records(text)
        if not root_record:
            violations.append("missing root record in {}".format(rel_path))
            continue
        required_fields = records.get(root_record, {}).get("required", [])
        has_id_field = any(type_name.strip() == "id" for _field, type_name in required_fields)
        if not has_id_field:
            violations.append("root record missing id field in {}".format(rel_path))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Schema namespace tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

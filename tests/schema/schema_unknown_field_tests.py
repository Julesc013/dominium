import argparse
import json
import os
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


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


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


def build_value(type_name: str, records: Dict[str, Dict[str, List[Tuple[str, str]]]], stack: List[str]) -> object:
    type_name = type_name.strip()
    if type_name.startswith("[") and type_name.endswith("]"):
        inner = type_name[1:-1].strip()
        return [build_value(inner, records, stack)]
    if type_name == "id":
        return "org.example.id"
    if type_name == "tag":
        return "org.example.tag"
    if type_name == "map":
        return {}
    if type_name == "number":
        return 1
    if type_name in records:
        return build_record(type_name, records, stack)
    return "org.example.value"


def build_record(name: str, records: Dict[str, Dict[str, List[Tuple[str, str]]]], stack: List[str]) -> Dict[str, object]:
    if name in stack:
        return {}
    stack.append(name)
    record = {}
    for field, type_name in records.get(name, {}).get("required", []):
        record[field] = build_value(type_name, records, stack)
    stack.pop()
    return record


def round_trip(obj: object) -> object:
    encoded = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return json.loads(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description="Unknown field preservation tests (FAB).")
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
        records, root_record = parse_records(text)
        if not root_record:
            violations.append("missing root record in {}".format(rel_path))
            continue
        obj = build_record(root_record, records, [])
        obj["unknown_top"] = {"note": "preserve"}
        if "extensions" not in obj:
            obj["extensions"] = {}
        obj["extensions"]["unknown.ext"] = {"note": "preserve"}
        round_obj = round_trip(obj)
        if "unknown_top" not in round_obj:
            violations.append("unknown top-level field dropped in {}".format(rel_path))
        if "extensions" not in round_obj or "unknown.ext" not in round_obj.get("extensions", {}):
            violations.append("unknown extensions field dropped in {}".format(rel_path))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Unknown field preservation tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

SCHEMA_VERSION_RE = re.compile(r"^\s*schema_version\s*:\s*(\d+\.\d+\.\d+)")

REQUIRED_PHRASES = [
    "No field removal or renaming without a MAJOR version bump.",
    "unknown fields MUST be preserved",
    "Identifiers are stable and MUST NOT be reused with new meaning.",
]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_schema_version(text: str) -> Optional[str]:
    for line in text.splitlines():
        match = SCHEMA_VERSION_RE.match(line)
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
    parser = argparse.ArgumentParser(description="Schema version immutability tests (FAB).")
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
        version = parse_schema_version(text)
        if not version:
            violations.append("missing schema_version in {}".format(rel_path))
        elif version == "0.0.0":
            violations.append("schema_version must not be 0.0.0 in {}".format(rel_path))

        for phrase in REQUIRED_PHRASES:
            if phrase not in text:
                violations.append("missing immutability phrase in {}: {}".format(rel_path, phrase))

        records, root_record = parse_records(text)
        if not root_record:
            violations.append("missing root record in {}".format(rel_path))
            continue
        required_fields = records.get(root_record, {}).get("required", [])
        has_extensions = any(field == "extensions" and type_name == "map" for field, type_name in required_fields)
        if not has_extensions:
            violations.append("missing extensions map in {}".format(rel_path))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Schema version immutability tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

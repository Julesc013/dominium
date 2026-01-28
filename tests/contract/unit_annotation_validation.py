import argparse
import os
import re
import sys
from typing import Dict, Iterable, List, Sequence, Tuple


UNIT_ID_RE = re.compile(r"\bunit\.[a-z0-9][a-z0-9_.-]*\b")

REQUIRED_DOC_TOKENS = [
    "Authoritative logic MUST NOT use floating point arithmetic.",
    "Presentation layers may use floating point only for display.",
    "## Tolerance annotations",
]

REQUIRED_SCHEMA_UNIT_TOKENS = [
    ("schema/process.schema", "unit: tag"),
]


def repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_units_block(text: str) -> List[Tuple[str, str, str, str]]:
    start = text.find("```units")
    if start == -1:
        return []
    start = text.find("\n", start)
    end = text.find("```", start + 1)
    if end == -1:
        return []
    rows: List[Tuple[str, str, str, str]] = []
    for raw_line in text[start:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 4:
            continue
        rows.append((parts[0], parts[1], parts[2], parts[3]))
    return rows


def iter_text_files(root: str) -> Iterable[str]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.endswith((".md", ".schema", ".json", ".yaml", ".yml", ".txt")):
                yield os.path.join(dirpath, name)


def validate_units_table(rows: Sequence[Tuple[str, str, str, str]], violations: List[str]) -> Dict[str, Tuple[str, str, str, str]]:
    unit_map: Dict[str, Tuple[str, str, str, str]] = {}
    for unit_id, dimension, base_unit, scale in rows:
        if unit_id in unit_map:
            violations.append("duplicate unit id: {}".format(unit_id))
        unit_map[unit_id] = (unit_id, dimension, base_unit, scale)
        if "." not in unit_id or not unit_id.startswith("unit."):
            violations.append("unit id not namespaced: {}".format(unit_id))
        if "." not in base_unit or not base_unit.startswith("unit."):
            violations.append("base unit not namespaced: {}".format(base_unit))
        try:
            scale_val = int(scale)
        except ValueError:
            violations.append("scale not integer for unit {}".format(unit_id))
            continue
        if scale_val <= 0:
            violations.append("scale must be positive for unit {}".format(unit_id))
    for _unit_id, _dimension, base_unit, _scale in rows:
        if base_unit not in unit_map:
            violations.append("base unit missing from table: {}".format(base_unit))
    return unit_map


def main() -> int:
    parser = argparse.ArgumentParser(description="Unit annotations and numeric policy checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    unit_doc = os.path.join(repo_root, "docs", "architecture", "UNIT_SYSTEM_POLICY.md")

    if not os.path.isfile(unit_doc):
        print("missing unit system policy doc: {}".format(unit_doc))
        return 1

    violations: List[str] = []
    unit_text = read_text(unit_doc)

    for token in REQUIRED_DOC_TOKENS:
        if token not in unit_text:
            violations.append("unit doc missing token: {}".format(token))

    rows = parse_units_block(unit_text)
    if not rows:
        violations.append("missing units block in docs/architecture/UNIT_SYSTEM_POLICY.md")
        unit_map: Dict[str, Tuple[str, str, str, str]] = {}
    else:
        unit_map = validate_units_table(rows, violations)

    # Required schema unit annotations.
    for rel_path, token in REQUIRED_SCHEMA_UNIT_TOKENS:
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            violations.append("missing schema file: {}".format(rel_path))
            continue
        schema_text = read_text(path)
        if token not in schema_text:
            violations.append("{} missing required token: {}".format(rel_path, token))

    # Any declared unit identifiers must exist in the canonical table.
    declared_units = set(unit_map.keys())
    referenced_units = set()
    for root in (os.path.join(repo_root, "docs", "architecture"), os.path.join(repo_root, "schema")):
        if not os.path.isdir(root):
            continue
        for path in iter_text_files(root):
            text = read_text(path)
            for match in UNIT_ID_RE.findall(text):
                referenced_units.add(match)
    unknown_units = sorted(referenced_units - declared_units)
    for unit_id in unknown_units:
        violations.append("unit referenced but not declared: {}".format(unit_id))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Unit annotation validation OK. units={}".format(len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

import argparse
import os
import re
import sys
from typing import Iterable, List, Optional, Sequence, Tuple


SCHEMA_ID_RE = re.compile(r"^\s*schema_id\s*:\s*(\S+)")
REVERSE_DNS_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9][a-z0-9_-]*)+$")

REQUIRED_ID_CLASS_TOKENS = [
    "capability IDs",
    "process_family IDs",
    "field IDs",
    "material IDs",
    "part IDs",
    "assembly IDs",
    "standard IDs",
    "refusal codes",
    "save chunk IDs",
    "schema IDs",
]

REQUIRED_RESERVED_NAMESPACE_TOKENS = [
    "domino.*",
    "dominium.*",
    "dominium.game.*",
    "dominium.tools.*",
    "org.<provider>.*",
    "dominium.ext.*",
    "dominium.future.*",
]


def repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def iter_schema_files(schema_root: str) -> Iterable[str]:
    for dirpath, _dirnames, filenames in os.walk(schema_root):
        for name in filenames:
            if name.endswith(".schema"):
                yield os.path.join(dirpath, name)


def first_schema_id(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                match = SCHEMA_ID_RE.match(line)
                if match:
                    return match.group(1)
    except OSError:
        return None
    return None


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


def validate_reverse_dns(ids: Sequence[Tuple[str, str]], violations: List[str]) -> None:
    for identifier, source in ids:
        if not identifier.isascii():
            violations.append("non-ascii identifier in {}: {}".format(source, identifier))
            continue
        lowered = identifier.lower()
        if identifier != lowered:
            violations.append("identifier must be lowercase in {}: {}".format(source, identifier))
        if not REVERSE_DNS_RE.match(lowered):
            violations.append("identifier is not reverse-dns shaped in {}: {}".format(source, identifier))


def main() -> int:
    parser = argparse.ArgumentParser(description="Namespace and identifier policy checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    schema_root = os.path.join(repo_root, "schema")
    id_rules_doc = os.path.join(repo_root, "docs", "architecture", "ID_AND_NAMESPACE_RULES.md")
    unit_doc = os.path.join(repo_root, "docs", "architecture", "UNIT_SYSTEM_POLICY.md")

    if not os.path.isdir(schema_root):
        print("missing schema directory: {}".format(schema_root))
        return 1
    if not os.path.isfile(id_rules_doc):
        print("missing id and namespace rules: {}".format(id_rules_doc))
        return 1
    if not os.path.isfile(unit_doc):
        print("missing unit system policy: {}".format(unit_doc))
        return 1

    violations: List[str] = []

    # Validate schema IDs.
    schema_ids: List[Tuple[str, str]] = []
    for path in iter_schema_files(schema_root):
        schema_id = first_schema_id(path)
        if not schema_id:
            violations.append("missing schema_id in {}".format(repo_rel(repo_root, path)))
            continue
        schema_ids.append((schema_id, repo_rel(repo_root, path)))
    validate_reverse_dns(schema_ids, violations)

    # Validate unit IDs.
    unit_rows = parse_units_block(read_text(unit_doc))
    if not unit_rows:
        violations.append("missing units block in docs/architecture/UNIT_SYSTEM_POLICY.md")
    else:
        unit_ids = [(row[0], "docs/architecture/UNIT_SYSTEM_POLICY.md") for row in unit_rows]
        base_ids = [(row[2], "docs/architecture/UNIT_SYSTEM_POLICY.md") for row in unit_rows]
        validate_reverse_dns(unit_ids, violations)
        validate_reverse_dns(base_ids, violations)

    # Validate policy doc contains required ID classes and reserved namespaces.
    id_rules_text = read_text(id_rules_doc)
    for token in REQUIRED_ID_CLASS_TOKENS:
        if token not in id_rules_text:
            violations.append("missing id class token in ID_AND_NAMESPACE_RULES.md: {}".format(token))
    for token in REQUIRED_RESERVED_NAMESPACE_TOKENS:
        if token not in id_rules_text:
            violations.append(
                "missing reserved namespace token in ID_AND_NAMESPACE_RULES.md: {}".format(token)
            )

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print(
        "Namespace validation OK. schema_ids={} units={}".format(
            len(schema_ids), len(unit_rows)
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

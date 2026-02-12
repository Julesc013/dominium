import argparse
import json
import os
import sys

from invariant_utils import is_override_active


SCHEMA_REL = os.path.join("schema", "governance", "glossary.schema")
REGISTRY_REL = os.path.join("data", "registries", "glossary.json")
DOC_REL = os.path.join("docs", "architecture", "TERMINOLOGY_GLOSSARY.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: glossary registry/doc consistency.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-GLOSSARY-TERM-CANON"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    schema_path = os.path.join(repo_root, SCHEMA_REL)
    registry_path = os.path.join(repo_root, REGISTRY_REL)
    doc_path = os.path.join(repo_root, DOC_REL)
    for rel, path in ((SCHEMA_REL, schema_path), (REGISTRY_REL, registry_path), (DOC_REL, doc_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    try:
        payload = json.load(open(registry_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        print("{}: invalid json {}".format(invariant_id, REGISTRY_REL.replace("\\", "/")))
        return 1

    terms = ((payload.get("record") or {}).get("terms") or [])
    if not isinstance(terms, list) or not terms:
        print("{}: glossary terms missing/empty".format(invariant_id))
        return 1
    term_ids = []
    display_names = []
    for row in terms:
        if not isinstance(row, dict):
            print("{}: non-object term entry".format(invariant_id))
            return 1
        term_id = str(row.get("term_id", "")).strip()
        display_name = str(row.get("display_name", "")).strip()
        if not term_id or not display_name:
            print("{}: term missing id or display name".format(invariant_id))
            return 1
        term_ids.append(term_id)
        display_names.append(display_name)

    if len(set(term_ids)) != len(term_ids):
        print("{}: duplicate term_id in glossary".format(invariant_id))
        return 1

    doc_text = open(doc_path, "r", encoding="utf-8").read()
    for name in sorted(set(display_names)):
        if name not in doc_text:
            print("{}: glossary doc missing display_name {}".format(invariant_id, name))
            return 1

    print("glossary consistency invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

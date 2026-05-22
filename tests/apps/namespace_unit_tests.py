import argparse
import os
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_unit_block(text):
    start = text.find("```units")
    if start == -1:
        return []
    start = text.find("\n", start)
    end = text.find("```", start + 1)
    if end == -1:
        return []
    block = text[start:end].splitlines()
    rows = []
    for line in block:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            continue
        unit_id = parts[0]
        dimension = parts[1]
        base_unit = parts[2]
        scale = parts[3]
        rows.append((unit_id, dimension, base_unit, scale))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Namespace + unit consistency tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    unit_doc = os.path.join(repo_root, "docs", "architecture", "UNIT_SYSTEM_POLICY.md")
    if not os.path.isfile(unit_doc):
        print("missing unit system policy doc")
        return 1

    text = read_text(unit_doc)
    rows = parse_unit_block(text)
    if not rows:
        print("missing units block")
        return 1

    unit_ids = []
    for unit_id, _dimension, base_unit, scale in rows:
        unit_ids.append(unit_id)
        if "." not in unit_id or not unit_id.startswith("unit."):
            print("unit id not namespaced: {}".format(unit_id))
            return 1
        if "." not in base_unit or not base_unit.startswith("unit."):
            print("base unit not namespaced: {}".format(base_unit))
            return 1
        try:
            scale_val = int(scale)
        except ValueError:
            print("scale not integer for unit {}".format(unit_id))
            return 1
        if scale_val <= 0:
            print("scale must be positive for unit {}".format(unit_id))
            return 1

    # Namespace collision detection
    if len(unit_ids) != len(set(unit_ids)):
        print("duplicate unit ids detected")
        return 1

    # Base units must be declared in the table.
    unit_id_set = set(unit_ids)
    for _unit_id, _dimension, base_unit, _scale in rows:
        if base_unit not in unit_id_set:
            print("base unit missing from table: {}".format(base_unit))
            return 1

    print("Namespace and unit checks OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

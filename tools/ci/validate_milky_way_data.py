#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
MAX_LIST = 256


def load_json(path, errors):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        errors.append(f"{path}: failed to parse json: {exc}")
        return None


def require_keys(obj, keys, path, errors):
    for key in keys:
        if key not in obj:
            errors.append(f"{path}: missing required field '{key}'")


def check_version(meta, path, errors):
    schema_version = meta.get("schema_version")
    if not schema_version or not VERSION_RE.match(schema_version):
        errors.append(f"{path}: invalid schema_version '{schema_version}'")
    stub = meta.get("migration_stub")
    if not isinstance(stub, dict):
        errors.append(f"{path}: missing migration_stub")
        return
    require_keys(stub, ["from_version", "to_version", "status"], path, errors)


def check_list(name, value, path, errors):
    if not isinstance(value, list):
        errors.append(f"{path}: field '{name}' must be a list")
        return
    if len(value) > MAX_LIST:
        errors.append(f"{path}: field '{name}' exceeds max size {MAX_LIST}")


def detect_cycles(parent_map):
    visited = {}

    def visit(node):
        state = visited.get(node, 0)
        if state == 1:
            return True
        if state == 2:
            return False
        visited[node] = 1
        parent = parent_map.get(node)
        if parent:
            if visit(parent):
                return True
        visited[node] = 2
        return False

    for node in parent_map:
        if visit(node):
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    mw_root = os.path.join(repo_root, "data", "world", "milky_way")
    errors = []

    galaxy_path = os.path.join(mw_root, "milky_way.galaxy.json")
    arms_path = os.path.join(mw_root, "milky_way.arms.json")
    regions_path = os.path.join(mw_root, "milky_way.regions.json")
    anchors_path = os.path.join(mw_root, "milky_way.anchors.json")
    rules_path = os.path.join(mw_root, "milky_way.procedural_rules.json")
    readme_path = os.path.join(mw_root, "README.md")

    for path in [galaxy_path, arms_path, regions_path, anchors_path, rules_path, readme_path]:
        if not os.path.exists(path):
            errors.append(f"{path}: missing required file")

    if errors:
        for err in errors:
            print(err)
        return 1

    galaxy_doc = load_json(galaxy_path, errors)
    arms_doc = load_json(arms_path, errors)
    regions_doc = load_json(regions_path, errors)
    anchors_doc = load_json(anchors_path, errors)
    rules_doc = load_json(rules_path, errors)

    if errors:
        for err in errors:
            print(err)
        return 1

    for doc, path in [
        (galaxy_doc, galaxy_path),
        (arms_doc, arms_path),
        (regions_doc, regions_path),
        (anchors_doc, anchors_path),
        (rules_doc, rules_path)
    ]:
        check_version(doc, path, errors)

    galaxy_rec = galaxy_doc.get("record", {})
    require_keys(galaxy_rec, [
        "galaxy_id",
        "universe_ref",
        "name",
        "coordinate_frame_ref",
        "scale_domain_ref",
        "system_ids",
        "morphology_tags",
        "provenance_ref",
        "data_source_refs"
    ], galaxy_path, errors)
    check_list("system_ids", galaxy_rec.get("system_ids", []), galaxy_path, errors)
    check_list("morphology_tags", galaxy_rec.get("morphology_tags", []), galaxy_path, errors)
    check_list("data_source_refs", galaxy_rec.get("data_source_refs", []), galaxy_path, errors)

    arms_rec = arms_doc.get("record", {})
    arm_records = arms_rec.get("arm_records", [])
    check_list("arm_records", arm_records, arms_path, errors)
    arm_ids = set()
    for arm in arm_records:
        require_keys(arm, [
            "arm_id",
            "name",
            "geometry_model_id",
            "geometry_tags",
            "density_class",
            "star_formation_class",
            "arm_region_ref"
        ], arms_path, errors)
        arm_id = arm.get("arm_id")
        if arm_id in arm_ids:
            errors.append(f"{arms_path}: duplicate arm_id '{arm_id}'")
        arm_ids.add(arm_id)
        check_list("geometry_tags", arm.get("geometry_tags", []), arms_path, errors)

    regions_rec = regions_doc.get("record", {})
    region_records = regions_rec.get("region_records", [])
    check_list("region_records", region_records, regions_path, errors)
    region_ids = set()
    parent_map = {}
    for region in region_records:
        require_keys(region, [
            "region_id",
            "name",
            "boundary_ref",
            "parent_region_ref",
            "region_type",
            "region_tags",
            "density_class",
            "age_class",
            "hazard_tags",
            "provenance_ref"
        ], regions_path, errors)
        region_id = region.get("region_id")
        if region_id in region_ids:
            errors.append(f"{regions_path}: duplicate region_id '{region_id}'")
        region_ids.add(region_id)
        parent_map[region_id] = region.get("parent_region_ref")
        check_list("region_tags", region.get("region_tags", []), regions_path, errors)
        check_list("hazard_tags", region.get("hazard_tags", []), regions_path, errors)
    if detect_cycles(parent_map):
        errors.append("region hierarchy contains cycles")

    for arm in arm_records:
        region_ref = arm.get("arm_region_ref")
        if region_ref and region_ref not in region_ids:
            errors.append(f"{arms_path}: arm '{arm.get('arm_id')}' references unknown region '{region_ref}'")

    anchors_rec = anchors_doc.get("record", {})
    anchor_records = anchors_rec.get("anchor_records", [])
    check_list("anchor_records", anchor_records, anchors_path, errors)
    anchor_ids = set()
    sol_found = False
    for anchor in anchor_records:
        require_keys(anchor, [
            "system_id",
            "name",
            "region_ref",
            "arm_ref",
            "position_tags",
            "star_class_tags",
            "hazard_tags",
            "system_ref",
            "anchor_tags"
        ], anchors_path, errors)
        system_id = anchor.get("system_id")
        if system_id in anchor_ids:
            errors.append(f"{anchors_path}: duplicate system_id '{system_id}'")
        anchor_ids.add(system_id)
        if system_id == "sol_system":
            sol_found = True
        region_ref = anchor.get("region_ref")
        if region_ref not in region_ids:
            errors.append(f"{anchors_path}: anchor '{system_id}' references unknown region '{region_ref}'")
        arm_ref = anchor.get("arm_ref")
        if arm_ref is not None and arm_ref not in arm_ids:
            errors.append(f"{anchors_path}: anchor '{system_id}' references unknown arm '{arm_ref}'")
        check_list("position_tags", anchor.get("position_tags", []), anchors_path, errors)
        check_list("star_class_tags", anchor.get("star_class_tags", []), anchors_path, errors)
        check_list("hazard_tags", anchor.get("hazard_tags", []), anchors_path, errors)
        check_list("anchor_tags", anchor.get("anchor_tags", []), anchors_path, errors)
    if not sol_found:
        errors.append(f"{anchors_path}: missing Sol anchor 'sol_system'")

    rules_rec = rules_doc.get("record", {})
    require_keys(rules_rec, ["seed", "rule_sets"], rules_path, errors)
    rule_sets = rules_rec.get("rule_sets", [])
    check_list("rule_sets", rule_sets, rules_path, errors)
    order_keys = []
    rule_ids = set()
    for rule in rule_sets:
        require_keys(rule, [
            "rule_id",
            "order_key",
            "applies_to",
            "target_ref",
            "density_class",
            "metallicity_class",
            "age_class",
            "hazard_class",
            "spawn_rate_class"
        ], rules_path, errors)
        rule_id = rule.get("rule_id")
        if rule_id in rule_ids:
            errors.append(f"{rules_path}: duplicate rule_id '{rule_id}'")
        rule_ids.add(rule_id)
        order_key = rule.get("order_key")
        if not isinstance(order_key, int):
            errors.append(f"{rules_path}: rule '{rule_id}' order_key must be int")
        else:
            order_keys.append(order_key)
        applies_to = rule.get("applies_to")
        target = rule.get("target_ref")
        if applies_to == "region" and target not in region_ids:
            errors.append(f"{rules_path}: rule '{rule_id}' references unknown region '{target}'")
        if applies_to == "arm" and target not in arm_ids:
            errors.append(f"{rules_path}: rule '{rule_id}' references unknown arm '{target}'")
    if order_keys and order_keys != sorted(order_keys):
        errors.append(f"{rules_path}: rule_sets must be ordered by order_key")

    if errors:
        for err in errors:
            print(err)
        return 1

    print("Milky Way data validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

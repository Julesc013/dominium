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


def rail_phase_at(rail, act):
    period = rail.get("period_act", 0)
    if period <= 0:
        return None
    phase = rail.get("phase_offset_act", 0)
    return (act + phase) % period


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    sol_root = os.path.join(repo_root, "data", "world", "sol")
    errors = []

    system_path = os.path.join(sol_root, "sol.system.json")
    orbits_path = os.path.join(sol_root, "sol.orbits.json")
    surfaces_path = os.path.join(sol_root, "sol.surfaces.json")

    system_doc = load_json(system_path, errors)
    orbits_doc = load_json(orbits_path, errors)
    surfaces_doc = load_json(surfaces_path, errors)

    if errors:
        for err in errors:
            print(err)
        return 1

    check_version(system_doc, system_path, errors)
    check_version(orbits_doc, orbits_path, errors)
    check_version(surfaces_doc, surfaces_path, errors)

    system_rec = system_doc.get("record", {})
    require_keys(system_rec, [
        "system_id",
        "galaxy_ref",
        "name",
        "coordinate_frame_ref",
        "scale_domain_ref",
        "star_ids",
        "planet_ids",
        "belt_ids",
        "orbital_rail_ids",
        "provenance_ref",
        "data_source_refs"
    ], system_path, errors)

    for field in ["star_ids", "planet_ids", "belt_ids", "orbital_rail_ids", "data_source_refs"]:
        check_list(field, system_rec.get(field, []), system_path, errors)

    orbits_rec = orbits_doc.get("record", {})
    require_keys(orbits_rec, ["rail_records"], orbits_path, errors)
    rail_records = orbits_rec.get("rail_records", [])
    check_list("rail_records", rail_records, orbits_path, errors)

    rail_ids = set()
    for rail in rail_records:
        require_keys(rail, [
            "rail_id",
            "system_ref",
            "parent_body_ref",
            "child_body_ref",
            "rail_model_id",
            "rail_frame_ref",
            "period_act",
            "phase_offset_act",
            "inclination_mdeg",
            "ascending_node_mdeg",
            "drift_schedule_ref"
        ], orbits_path, errors)
        rail_id = rail.get("rail_id")
        if rail_id:
            rail_ids.add(rail_id)
        period = rail.get("period_act", 0)
        if not isinstance(period, int) or period <= 0:
            errors.append(f"{orbits_path}: rail '{rail_id}' invalid period_act")
        sample_acts = [0, 1, max(0, period // 2)]
        for act in sample_acts:
            phase_a = rail_phase_at(rail, act)
            phase_b = rail_phase_at(rail, act)
            if phase_a is None or phase_a != phase_b:
                errors.append(f"{orbits_path}: rail '{rail_id}' non-deterministic phase")

    surfaces_rec = surfaces_doc.get("record", {})
    require_keys(surfaces_rec, ["surface_records", "region_records"], surfaces_path, errors)
    surface_records = surfaces_rec.get("surface_records", [])
    region_records = surfaces_rec.get("region_records", [])
    check_list("surface_records", surface_records, surfaces_path, errors)
    check_list("region_records", region_records, surfaces_path, errors)

    surface_ids = set()
    for surface in surface_records:
        require_keys(surface, [
            "surface_id",
            "body_ref",
            "surface_type",
            "coordinate_frame_ref",
            "heightmap_ref",
            "climate_map_ref",
            "biome_tags",
            "region_ids",
            "provenance_ref"
        ], surfaces_path, errors)
        surface_id = surface.get("surface_id")
        if surface_id:
            surface_ids.add(surface_id)
        check_list("biome_tags", surface.get("biome_tags", []), surfaces_path, errors)
        check_list("region_ids", surface.get("region_ids", []), surfaces_path, errors)

    region_ids = set()
    for region in region_records:
        require_keys(region, [
            "region_id",
            "surface_ref",
            "volume_ref",
            "boundary_ref",
            "region_type",
            "parent_region_ref",
            "layer_id",
            "region_tags",
            "provenance_ref"
        ], surfaces_path, errors)
        region_id = region.get("region_id")
        if region_id:
            region_ids.add(region_id)
        check_list("region_tags", region.get("region_tags", []), surfaces_path, errors)

    bodies_root = os.path.join(sol_root, "sol.bodies")
    moons_root = os.path.join(sol_root, "sol.moons")
    belts_root = os.path.join(sol_root, "sol.belts")

    def gather_files(root_dir):
        if not os.path.isdir(root_dir):
            return []
        return sorted([
            os.path.join(root_dir, name)
            for name in os.listdir(root_dir)
            if name.endswith(".json")
        ])

    body_files = gather_files(bodies_root)
    moon_files = gather_files(moons_root)
    belt_files = gather_files(belts_root)

    if len(body_files) < 9:
        errors.append(f"{bodies_root}: expected at least 9 body files")
    if len(moon_files) < 9:
        errors.append(f"{moons_root}: expected at least 9 moon files")
    if len(belt_files) < 3:
        errors.append(f"{belts_root}: expected at least 3 belt files")

    body_ids = set()
    parent_map = {}

    def check_body(path):
        doc = load_json(path, errors)
        if not doc:
            return
        check_version(doc, path, errors)
        rec = doc.get("record", {})
        require_keys(rec, [
            "body_id",
            "system_ref",
            "parent_body_ref",
            "body_type",
            "name",
            "radius_m",
            "mass_class",
            "surface_refs",
            "volume_refs",
            "orbital_rail_ref",
            "scale_domain_ref",
            "provenance_ref",
            "data_source_refs",
            "body_tags"
        ], path, errors)
        body_id = rec.get("body_id")
        if body_id:
            body_ids.add(body_id)
        parent_map[body_id] = rec.get("parent_body_ref")
        check_list("surface_refs", rec.get("surface_refs", []), path, errors)
        check_list("volume_refs", rec.get("volume_refs", []), path, errors)
        check_list("data_source_refs", rec.get("data_source_refs", []), path, errors)
        check_list("body_tags", rec.get("body_tags", []), path, errors)
        radius = rec.get("radius_m")
        if not isinstance(radius, int) or radius < 0:
            errors.append(f"{path}: invalid radius_m")
        orbital = rec.get("orbital_rail_ref")
        if orbital is not None and orbital not in rail_ids:
            errors.append(f"{path}: orbital_rail_ref '{orbital}' not found")
        for surface_ref in rec.get("surface_refs", []):
            if surface_ref not in surface_ids:
                errors.append(f"{path}: surface_ref '{surface_ref}' not found")

    for path in body_files + moon_files + belt_files:
        check_body(path)

    system_body_ids = set(system_rec.get("star_ids", []) +
                          system_rec.get("planet_ids", []) +
                          system_rec.get("belt_ids", []))
    missing_ids = [bid for bid in system_body_ids if bid not in body_ids]
    if missing_ids:
        errors.append(f"{system_path}: missing body records for {missing_ids}")

    required_surfaces = [
        "earth_land_surface",
        "earth_ocean_surface",
        "mars_surface",
        "moon_nearside_surface",
        "moon_farside_surface"
    ]
    for sid in required_surfaces:
        if sid not in surface_ids:
            errors.append(f"{surfaces_path}: missing required surface '{sid}'")

    required_regions = [
        "earth_polar_north_region",
        "earth_polar_south_region"
    ]
    for rid in required_regions:
        if rid not in region_ids:
            errors.append(f"{surfaces_path}: missing required region '{rid}'")

    if errors:
        for err in errors:
            print(err)
        return 1

    print("Sol data validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

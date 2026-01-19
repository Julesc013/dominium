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
    earth_root = os.path.join(repo_root, "data", "world", "sol", "earth")
    errors = []

    required_files = [
        os.path.join(earth_root, "earth.body.json"),
        os.path.join(earth_root, "earth.orbits.json"),
        os.path.join(earth_root, "earth.surfaces", "land.surface.json"),
        os.path.join(earth_root, "earth.surfaces", "ocean.surface.json"),
        os.path.join(earth_root, "earth.surfaces", "atmosphere.volume.json"),
        os.path.join(earth_root, "earth.surfaces", "subsurface.volume.json"),
        os.path.join(earth_root, "earth.regions", "continents.json"),
        os.path.join(earth_root, "earth.regions", "oceans.json"),
        os.path.join(earth_root, "earth.regions", "polar_regions.json"),
        os.path.join(earth_root, "earth.regions", "tectonic_plates.json"),
        os.path.join(earth_root, "earth.climate", "climate_zones.json"),
        os.path.join(earth_root, "earth.climate", "biome_tags.json"),
        os.path.join(earth_root, "earth.imports", "README.md"),
        os.path.join(earth_root, "README.md")
    ]

    for path in required_files:
        if not os.path.exists(path):
            errors.append(f"{path}: missing required file")

    if errors:
        for err in errors:
            print(err)
        return 1

    body_doc = load_json(os.path.join(earth_root, "earth.body.json"), errors)
    orbits_doc = load_json(os.path.join(earth_root, "earth.orbits.json"), errors)
    land_doc = load_json(os.path.join(earth_root, "earth.surfaces", "land.surface.json"), errors)
    ocean_doc = load_json(os.path.join(earth_root, "earth.surfaces", "ocean.surface.json"), errors)
    atm_doc = load_json(os.path.join(earth_root, "earth.surfaces", "atmosphere.volume.json"), errors)
    sub_doc = load_json(os.path.join(earth_root, "earth.surfaces", "subsurface.volume.json"), errors)
    continents_doc = load_json(os.path.join(earth_root, "earth.regions", "continents.json"), errors)
    oceans_doc = load_json(os.path.join(earth_root, "earth.regions", "oceans.json"), errors)
    polar_doc = load_json(os.path.join(earth_root, "earth.regions", "polar_regions.json"), errors)
    plates_doc = load_json(os.path.join(earth_root, "earth.regions", "tectonic_plates.json"), errors)
    climate_doc = load_json(os.path.join(earth_root, "earth.climate", "climate_zones.json"), errors)
    biome_doc = load_json(os.path.join(earth_root, "earth.climate", "biome_tags.json"), errors)

    if errors:
        for err in errors:
            print(err)
        return 1

    for doc, path in [
        (body_doc, "earth.body.json"),
        (orbits_doc, "earth.orbits.json"),
        (land_doc, "earth.surfaces/land.surface.json"),
        (ocean_doc, "earth.surfaces/ocean.surface.json"),
        (atm_doc, "earth.surfaces/atmosphere.volume.json"),
        (sub_doc, "earth.surfaces/subsurface.volume.json"),
        (continents_doc, "earth.regions/continents.json"),
        (oceans_doc, "earth.regions/oceans.json"),
        (polar_doc, "earth.regions/polar_regions.json"),
        (plates_doc, "earth.regions/tectonic_plates.json"),
        (climate_doc, "earth.climate/climate_zones.json"),
        (biome_doc, "earth.climate/biome_tags.json")
    ]:
        check_version(doc, path, errors)

    body_rec = body_doc.get("record", {})
    require_keys(body_rec, [
        "body_id",
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
    ], "earth.body.json", errors)
    check_list("surface_refs", body_rec.get("surface_refs", []), "earth.body.json", errors)
    check_list("volume_refs", body_rec.get("volume_refs", []), "earth.body.json", errors)
    check_list("data_source_refs", body_rec.get("data_source_refs", []), "earth.body.json", errors)
    check_list("body_tags", body_rec.get("body_tags", []), "earth.body.json", errors)
    if "supported_scale_domains" in body_rec:
        check_list("supported_scale_domains", body_rec.get("supported_scale_domains", []),
                   "earth.body.json", errors)

    orbits_rec = orbits_doc.get("record", {})
    require_keys(orbits_rec, ["rail_records"], "earth.orbits.json", errors)
    check_list("rail_records", orbits_rec.get("rail_records", []), "earth.orbits.json", errors)

    surface_docs = [land_doc, ocean_doc]
    volume_docs = [atm_doc, sub_doc]
    region_docs = [continents_doc, oceans_doc, polar_doc, plates_doc]

    surface_ids = set()
    volume_ids = set()
    region_ids = set()
    parent_map = {}
    surface_biomes = set()

    for doc, path in [
        (land_doc, "earth.surfaces/land.surface.json"),
        (ocean_doc, "earth.surfaces/ocean.surface.json")
    ]:
        rec = doc.get("record", {})
        surface_records = rec.get("surface_records", [])
        check_list("surface_records", surface_records, path, errors)
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
            ], path, errors)
            surface_id = surface.get("surface_id")
            if surface_id:
                surface_ids.add(surface_id)
            check_list("biome_tags", surface.get("biome_tags", []), path, errors)
            check_list("region_ids", surface.get("region_ids", []), path, errors)
            for tag in surface.get("biome_tags", []):
                surface_biomes.add(tag)

    for doc, path in [
        (atm_doc, "earth.surfaces/atmosphere.volume.json"),
        (sub_doc, "earth.surfaces/subsurface.volume.json")
    ]:
        rec = doc.get("record", {})
        volume_records = rec.get("volume_records", [])
        check_list("volume_records", volume_records, path, errors)
        for volume in volume_records:
            require_keys(volume, [
                "volume_id",
                "body_ref",
                "volume_type",
                "coordinate_frame_ref",
                "bounds_ref",
                "region_ids",
                "provenance_ref"
            ], path, errors)
            volume_id = volume.get("volume_id")
            if volume_id:
                volume_ids.add(volume_id)
            check_list("region_ids", volume.get("region_ids", []), path, errors)

    for doc, path in [
        (continents_doc, "earth.regions/continents.json"),
        (oceans_doc, "earth.regions/oceans.json"),
        (polar_doc, "earth.regions/polar_regions.json"),
        (plates_doc, "earth.regions/tectonic_plates.json"),
        (atm_doc, "earth.surfaces/atmosphere.volume.json"),
        (sub_doc, "earth.surfaces/subsurface.volume.json")
    ]:
        rec = doc.get("record", {})
        region_records = rec.get("region_records", [])
        check_list("region_records", region_records, path, errors)
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
            ], path, errors)
            region_id = region.get("region_id")
            if region_id:
                region_ids.add(region_id)
            parent_map[region_id] = region.get("parent_region_ref")
            surface_ref = region.get("surface_ref")
            volume_ref = region.get("volume_ref")
            if (surface_ref and volume_ref) or (not surface_ref and not volume_ref):
                errors.append(f"{path}: region '{region_id}' must reference exactly one of surface_ref or volume_ref")
            if surface_ref and surface_ref not in surface_ids:
                errors.append(f"{path}: region '{region_id}' references unknown surface '{surface_ref}'")
            if volume_ref and volume_ref not in volume_ids:
                errors.append(f"{path}: region '{region_id}' references unknown volume '{volume_ref}'")
            check_list("region_tags", region.get("region_tags", []), path, errors)

    if detect_cycles(parent_map):
        errors.append("region hierarchy contains cycles")

    for doc, path in [
        (land_doc, "earth.surfaces/land.surface.json"),
        (ocean_doc, "earth.surfaces/ocean.surface.json")
    ]:
        rec = doc.get("record", {})
        for surface in rec.get("surface_records", []):
            for region_id in surface.get("region_ids", []):
                if region_id not in region_ids:
                    errors.append(f"{path}: surface '{surface.get('surface_id')}' references unknown region '{region_id}'")

    climate_rec = climate_doc.get("record", {})
    climate_tags = climate_rec.get("valid_climate_tags", [])
    check_list("valid_climate_tags", climate_tags, "earth.climate/climate_zones.json", errors)
    zones = climate_rec.get("climate_zone_records", [])
    check_list("climate_zone_records", zones, "earth.climate/climate_zones.json", errors)
    for zone in zones:
        require_keys(zone, ["zone_id", "tag", "region_refs", "provenance_ref"],
                     "earth.climate/climate_zones.json", errors)
        tag = zone.get("tag")
        if tag not in climate_tags:
            errors.append(f"earth.climate/climate_zones.json: zone '{zone.get('zone_id')}' has invalid tag '{tag}'")
        check_list("region_refs", zone.get("region_refs", []), "earth.climate/climate_zones.json", errors)

    biome_rec = biome_doc.get("record", {})
    biome_tags = biome_rec.get("valid_biome_tags", [])
    check_list("valid_biome_tags", biome_tags, "earth.climate/biome_tags.json", errors)
    biome_records = biome_rec.get("biome_tag_records", [])
    check_list("biome_tag_records", biome_records, "earth.climate/biome_tags.json", errors)
    for biome in biome_records:
        require_keys(biome, ["tag_id", "category", "provenance_ref"],
                     "earth.climate/biome_tags.json", errors)
        if biome.get("tag_id") not in biome_tags:
            errors.append(f"earth.climate/biome_tags.json: tag '{biome.get('tag_id')}' not in valid list")

    for tag in surface_biomes:
        if tag not in biome_tags:
            errors.append(f"surface biome tag '{tag}' not in earth.climate valid_biome_tags")

    if errors:
        for err in errors:
            print(err)
        return 1

    print("Earth data validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

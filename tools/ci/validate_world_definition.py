#!/usr/bin/env python3
import argparse
import copy
import json
import sys
from pathlib import Path


def _import_lib(repo_root):
    sys.path.insert(0, str(repo_root / "tools" / "worldgen_offline"))
    import world_definition_lib as wdlib
    return wdlib


def _check(condition, message, errors):
    if not condition:
        errors.append(message)


def _generate_builtin(wdlib, template_id, seed=0):
    result = wdlib.run_template(template_id, {"seed.primary": seed})
    if not result.get("ok"):
        return None, result.get("refusal")
    return result.get("world_definition"), None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    wdlib = _import_lib(repo_root)
    errors = []

    # Schema round-trip + unknown field preservation
    empty_worlddef, refusal = _generate_builtin(wdlib, "builtin.empty_universe", seed=0)
    _check(empty_worlddef is not None, f"builtin.empty_universe refused: {refusal}", errors)
    if empty_worlddef:
        expected = {
            "schema_id": wdlib.SCHEMA_ID,
            "schema_version": wdlib.SCHEMA_VERSION,
            "worlddef_id": "builtin.empty_universe.seed.0",
            "topology": {
                "root_node_ref": {"node_id": "universe.root"},
                "nodes": [
                    {
                        "node_id": "universe.root",
                        "trait_tags": ["topology.universe"],
                        "coord_frame_ref": {"frame_id": "frame.universe.root"},
                    }
                ],
                "edges": [],
            },
            "initial_fields": [],
            "policy_sets": {
                "movement_policies": [],
                "authority_policies": [],
                "mode_policies": [],
                "debug_policies": [],
                "playtest_policies": [],
            },
            "spawn_spec": {
                "spawn_node_ref": {"node_id": "universe.root"},
                "coordinate_frame_ref": {"frame_id": "frame.universe.root"},
                "position": {"value": {"x": 0, "y": 0, "z": 0}},
                "orientation": {"value": {"yaw": 0, "pitch": 0, "roll": 0}},
            },
            "provenance": {
                "template_id": "builtin.empty_universe",
                "template_version": "1.0.0",
                "generator_source": "built_in",
                "seed": {"primary": 0},
                "template_params": {"seed.primary": 0},
            },
            "extensions": {},
        }
        hash_expected = wdlib.worlddef_hash(expected)
        hash_empty = wdlib.worlddef_hash(empty_worlddef)
        _check(hash_empty == hash_expected, "deterministic hash mismatch for empty universe", errors)

        round_trip = wdlib.round_trip_json(empty_worlddef)
        _check(round_trip == empty_worlddef, "schema round-trip mismatch for empty universe", errors)

        unknown = copy.deepcopy(empty_worlddef)
        unknown["unknown.top"] = {"note": "preserve"}
        unknown["extensions"]["unknown.ext"] = {"v": 1}
        unknown["topology"]["extensions"] = {"unknown.topology": True}
        round_trip_unknown = wdlib.round_trip_json(unknown)
        _check("unknown.top" in round_trip_unknown, "unknown top-level field not preserved", errors)
        _check("unknown.ext" in round_trip_unknown.get("extensions", {}),
               "unknown extension field not preserved", errors)
        _check("unknown.topology" in round_trip_unknown.get("topology", {}).get("extensions", {}),
               "unknown nested extension not preserved", errors)

    # Built-in template determinism
    for template_id in sorted(wdlib.BUILTIN_TEMPLATES.keys()):
        world_a, refusal_a = _generate_builtin(wdlib, template_id, seed=42)
        world_b, refusal_b = _generate_builtin(wdlib, template_id, seed=42)
        _check(world_a is not None, f"{template_id} refused: {refusal_a}", errors)
        _check(world_b is not None, f"{template_id} refused: {refusal_b}", errors)
        if world_a and world_b:
            hash_a = wdlib.worlddef_hash(world_a)
            hash_b = wdlib.worlddef_hash(world_b)
            _check(hash_a == hash_b, f"{template_id} non-deterministic output", errors)

    # Zero-pack world creation works
    for template_id in sorted(wdlib.BUILTIN_TEMPLATES.keys()):
        worlddef, _ = _generate_builtin(wdlib, template_id, seed=1)
        if not worlddef:
            continue
        pack_refs = worlddef.get("pack_refs")
        _check(pack_refs is None or pack_refs == [],
               f"{template_id} unexpectedly requires packs", errors)

    # Refusal semantics: invalid world definition
    invalid_result = wdlib.validate_world_definition({})
    _check(not invalid_result.get("ok"), "invalid worlddef unexpectedly ok", errors)
    _check(invalid_result.get("refusal", {}).get("code") == wdlib.REFUSAL_INVALID,
           "invalid worlddef refusal code mismatch", errors)

    # Refusal semantics: unsupported schema version
    if empty_worlddef:
        bad_version = copy.deepcopy(empty_worlddef)
        bad_version["schema_version"] = 99
        result = wdlib.validate_world_definition(bad_version)
        _check(not result.get("ok"), "unsupported schema version accepted", errors)
        _check(result.get("refusal", {}).get("code") == wdlib.REFUSAL_SCHEMA,
               "unsupported schema refusal code mismatch", errors)

    # Refusal semantics: missing required capabilities
    if empty_worlddef:
        cap_world = copy.deepcopy(empty_worlddef)
        cap_world["capability_expectations"] = [{"capability_id": "cap.world.create"}]
        result = wdlib.validate_world_definition(cap_world, available_capabilities=[])
        _check(not result.get("ok"), "missing capability accepted", errors)
        _check(result.get("refusal", {}).get("code") == wdlib.REFUSAL_CAPABILITY,
               "missing capability refusal code mismatch", errors)

    # Refusal semantics: template refusal
    refused = wdlib.run_template("builtin.empty_universe", {"seed.primary": -1})
    _check(not refused.get("ok"), "template refusal not triggered", errors)
    _check(refused.get("refusal", {}).get("code") == wdlib.REFUSAL_TEMPLATE,
           "template refusal code mismatch", errors)

    # Built-in vs pack template equivalence (if pack exists)
    packs_root = repo_root / "data" / "packs"
    if packs_root.exists():
        manifest_paths = sorted(packs_root.rglob("pack_manifest.json"))
    else:
        manifest_paths = []
    for manifest_path in manifest_paths:
        try:
            with manifest_path.open("r", encoding="utf-8") as handle:
                manifest_doc = json.load(handle)
        except Exception:
            errors.append(f"{manifest_path}: failed to read pack_manifest.json")
            continue
        record = manifest_doc.get("record", manifest_doc)
        provides = record.get("provides", [])
        has_registry = False
        for cap in provides:
            if isinstance(cap, dict) and cap.get("capability_id") == "world.template.registry":
                has_registry = True
                break
        if not has_registry:
            continue
        templates_path = manifest_path.parent / "world_templates.json"
        if not templates_path.exists():
            errors.append(f"{templates_path}: missing world_templates.json for template registry pack")
            continue
        try:
            with templates_path.open("r", encoding="utf-8") as handle:
                templates_doc = json.load(handle)
        except Exception:
            errors.append(f"{templates_path}: failed to read world_templates.json")
            continue
        for record in templates_doc.get("records", []):
            builtin_equiv = record.get("builtin_equivalent")
            if not builtin_equiv:
                continue
            eq_hash = record.get("equivalence_hash")
            if not eq_hash:
                errors.append(f"{templates_path}: missing equivalence_hash for {builtin_equiv}")
                continue
            seed = record.get("equivalence_seed", 0)
            builtin_worlddef, refusal = _generate_builtin(wdlib, builtin_equiv, seed=seed)
            _check(builtin_worlddef is not None, f"builtin template missing: {refusal}", errors)
            if builtin_worlddef:
                built_hash = wdlib.worlddef_hash(builtin_worlddef, strip_extensions=True)
                _check(eq_hash == built_hash,
                       f"{templates_path}: equivalence hash mismatch for {builtin_equiv}", errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("WorldDefinition validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

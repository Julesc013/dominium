import argparse
import json
import os
import sys


DOC_TOKENS = {
    "docs/architecture/TERRAIN_TRUTH_MODEL.md": [
        "Terrain truth is NOT meshes.",
        "Signed Distance Field",
        "phi(x) < 0",
        "phi(x) = 0",
        "phi(x) > 0",
        "Meshes are view-only caches",
        "Process outputs",
    ],
    "docs/architecture/TERRAIN_FIELDS.md": [
        "terrain.phi",
        "terrain.material_primary",
        "terrain.support_capacity",
        "env.temperature",
        "env.moisture",
        "terrain.roughness",
        "travel.cost",
        "unit.length.meter",
        "unit.pressure.pascal",
        "unit.temperature.kelvin",
        "unit.dimensionless.ratio",
    ],
    "docs/architecture/TERRAIN_PROVIDER_CHAIN.md": [
        "Procedural base provider",
        "Anchor provider",
        "Simulation provider",
        "Player edit overlay provider",
        "Tool/editor workspace overlay provider",
        "Cache provider",
    ],
    "docs/architecture/TERRAIN_OVERLAYS.md": [
        "delta_phi",
        "delta_material",
        "delta_field",
        "cut",
        "fill",
        "smooth",
    ],
    "docs/architecture/STRUCTURAL_STABILITY_MODEL.md": [
        "stress exceeds",
        "support_capacity",
        "Process",
    ],
    "docs/architecture/DECAY_EROSION_REGEN.md": [
        "No per-tick global erosion",
        "scheduled macro events",
        "deterministic",
    ],
    "docs/architecture/TERRAIN_COORDINATES.md": [
        "hierarchical",
        "no floating point",
        "fixed-point",
    ],
    "docs/architecture/TERRAIN_MACRO_CAPSULE.md": [
        "RNG cursor",
        "sufficient statistics",
        "provenance",
    ],
}

SCHEMA_TOKENS = {
    "schema/terrain.field.schema": [
        "terrain.phi",
        "terrain.material_primary",
        "terrain.support_capacity",
        "env.temperature",
        "env.moisture",
        "terrain.roughness",
        "travel.cost",
        "unit_annotations",
        "maturity",
        "extensions",
    ],
    "schema/terrain.provider.schema": [
        "terrain_provider_chain",
        "provider_id",
        "provider_type",
        "capability_id",
        "unit_annotations",
        "maturity",
        "extensions",
    ],
    "schema/terrain.overlay.schema": [
        "terrain_overlay",
        "overlay_id",
        "overlay_type",
        "delta_phi",
        "delta_material",
        "delta_field",
        "process_id",
        "operation",
        "unit_annotations",
        "maturity",
        "extensions",
    ],
    "schema/terrain.macro_capsule.schema": [
        "terrain_macro_capsule",
        "capsule_id",
        "rng_cursor",
        "unit_annotations",
        "maturity",
        "extensions",
    ],
}

FORBIDDEN_SCHEMA_TOKENS = ("mesh", "planet", "station")

REQUIRED_FIELDS = [
    "terrain.phi",
    "terrain.material_primary",
    "terrain.support_capacity",
    "env.temperature",
    "env.moisture",
    "terrain.roughness",
    "travel.cost",
]

PROVIDER_ORDER = [
    "provider.procedural.base",
    "provider.anchor",
    "provider.simulation",
    "provider.overlay.player",
    "provider.overlay.tool",
    "provider.cache",
]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def require_tokens(path: str, tokens, violations, label=None):
    text = read_text(path)
    missing = [token for token in tokens if token not in text]
    if missing:
        violations.append("{} missing tokens: {}".format(label or path, ", ".join(missing)))


def require_no_forbidden_tokens(path: str, tokens, violations, label=None):
    text = read_text(path).lower()
    hits = [token for token in tokens if token in text]
    if hits:
        violations.append("{} contains forbidden tokens: {}".format(label or path, ", ".join(hits)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Terrain contract guard (TERRAIN0).")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []

    for rel_path, tokens in DOC_TOKENS.items():
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            violations.append("missing doc: {}".format(rel_path))
            continue
        require_tokens(path, tokens, violations, rel_path)

    for rel_path, tokens in SCHEMA_TOKENS.items():
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            violations.append("missing schema: {}".format(rel_path))
            continue
        require_tokens(path, tokens, violations, rel_path)
        require_no_forbidden_tokens(path, FORBIDDEN_SCHEMA_TOKENS, violations, rel_path)

    fixture_path = os.path.join(repo_root, "tests", "contract", "terrain_fixtures.json")
    if not os.path.isfile(fixture_path):
        violations.append("missing terrain fixtures: tests/contract/terrain_fixtures.json")
    else:
        with open(fixture_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if data.get("truth_field") != "terrain.phi":
            violations.append("terrain fixtures truth_field must be terrain.phi")

        field_stack = data.get("terrain_field_stack", {})
        required_ids = field_stack.get("required_field_ids", [])
        for field_id in REQUIRED_FIELDS:
            if field_id not in required_ids:
                violations.append("terrain fixtures missing required_field_id: {}".format(field_id))

        providers = data.get("provider_chain", {}).get("providers", [])
        ordered = sorted(providers, key=lambda item: item.get("stage_order", 0))
        provider_types = [item.get("provider_type") for item in ordered]
        if provider_types != PROVIDER_ORDER:
            violations.append("provider chain order mismatch: {}".format(provider_types))
        base_provider = None
        for provider in providers:
            if provider.get("provider_type") == "provider.procedural.base":
                base_provider = provider
                break
        if not base_provider:
            violations.append("fixtures missing procedural base provider")
        else:
            payload = base_provider.get("payload", {})
            if payload.get("shape") != "sphere":
                violations.append("base provider payload must define sphere SDF")

        overlays = data.get("overlays", [])
        operations = {item.get("operation") for item in overlays}
        if "cut" not in operations or "fill" not in operations:
            violations.append("fixtures must include cut and fill overlays")
        collapse = [item for item in overlays if item.get("payload", {}).get("purpose") == "collapse"]
        if not collapse:
            violations.append("fixtures must include collapse overlay payload")
        for overlay in overlays:
            for key in ("process_id", "event_id", "tick_index", "rng_stream"):
                if not overlay.get(key):
                    violations.append("overlay missing {}: {}".format(key, overlay.get("overlay_id")))

        macro_capsule = data.get("macro_capsule", {})
        rng_cursor = macro_capsule.get("rng_cursor", {})
        if not rng_cursor.get("stream") or rng_cursor.get("cursor") is None:
            violations.append("macro_capsule missing rng_cursor stream/cursor")

        fixture_text = json.dumps(data).lower()
        for token in FORBIDDEN_SCHEMA_TOKENS + ("mesh",):
            if token in fixture_text:
                violations.append("fixtures contain forbidden token: {}".format(token))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Terrain contract tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

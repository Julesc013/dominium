import argparse
import json
import sys
from pathlib import Path

from _common import (
    collect_records,
    ensure_cache_path,
    find_pack_manifests,
    load_json,
    parse_pack_paths,
    repo_root,
    write_json,
)


def collect_capabilities(manifests):
    capability_map = {}
    for path in manifests:
        manifest = load_json(path)
        record = manifest.get("record", {})
        pack_id = record.get("pack_id", "pack.unknown")
        for cap in record.get("provides", []):
            cap_id = cap.get("capability_id")
            if not cap_id:
                continue
            capability_map.setdefault(cap_id, []).append(pack_id)
    return capability_map


def collect_refinement_conflicts(plan_records):
    seen = {}
    conflicts = []
    for plan in plan_records:
        plan_id = plan.get("plan_id")
        for layer in plan.get("layers", []):
            precedence = layer.get("precedence_tag", "precedence.unspecified")
            scope = layer.get("domain_scope", {})
            scope_key = (
                scope.get("domain_id", "domain.any"),
                scope.get("volume_id", "volume.any"),
            )
            for field in layer.get("field_refs", []):
                field_id = field.get("field_id", "field.unknown")
                key = (field_id, scope_key, precedence)
                existing = seen.get(key)
                entry = {
                    "plan_id": plan_id,
                    "layer_id": layer.get("layer_id"),
                    "field_id": field_id,
                    "precedence_tag": precedence,
                    "domain_id": scope_key[0],
                    "volume_id": scope_key[1],
                }
                if existing:
                    conflicts.append({"first": existing, "second": entry})
                else:
                    seen[key] = entry
    return conflicts


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline pack diff and override visualizer.")
    parser.add_argument("--packs", action="append", help="Pack root or pack directory.")
    parser.add_argument("--output", help="Optional JSON report path under build/cache/assets.")
    args = parser.parse_args()

    roots = parse_pack_paths(args)
    manifests = find_pack_manifests(roots)
    if not manifests:
        print("No pack manifests found.", file=sys.stderr)
        return 2

    capability_map = collect_capabilities(manifests)
    capability_conflicts = {
        cap: providers for cap, providers in capability_map.items() if len(providers) > 1
    }

    plan_records = collect_records(roots, "refinement_plans.json")
    precedence_rules = []
    for plan in plan_records:
        for rule in plan.get("precedence_rules", []):
            precedence_rules.append(
                {
                    "plan_id": plan.get("plan_id"),
                    "higher_tag": rule.get("higher_tag"),
                    "lower_tag": rule.get("lower_tag"),
                }
            )

    conflicts = collect_refinement_conflicts(plan_records)

    report = {
        "tool_id": "dominium.tool.pack_diff_visualizer",
        "tool_version": "1.0.0",
        "capability_providers": capability_map,
        "capability_conflicts": capability_conflicts,
        "precedence_rules": precedence_rules,
        "refinement_conflicts": conflicts,
        "notes": [
            "Capability conflicts are informational unless precedence is explicit.",
            "Refinement conflicts indicate same field and precedence in same scope.",
        ],
    }

    if args.output:
        root = repo_root()
        output_path = ensure_cache_path(Path(args.output), root)
        write_json(output_path, report)
        print(f"Wrote pack report: {output_path}")
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

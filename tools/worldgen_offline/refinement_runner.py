import argparse
import sys
from pathlib import Path

from _common import (
    collect_records,
    compute_hash,
    ensure_cache_path,
    find_pack_manifests,
    load_json,
    parse_pack_paths,
    repo_root,
    write_json,
)


def build_request(args, plan_record):
    field_ids = []
    if args.fields:
        field_ids = [field.strip() for field in args.fields.split(",") if field.strip()]
    else:
        for layer in plan_record.get("layers", []):
            for field in layer.get("field_refs", []):
                field_id = field.get("field_id")
                if field_id and field_id not in field_ids:
                    field_ids.append(field_id)

    scope = plan_record.get("plan_domain_scope", {})
    request = {
        "target": {
            "node_id": args.target_node or scope.get("node_id", "node.unspecified"),
            "domain_id": args.domain_id or scope.get("domain_id", "domain.unspecified"),
            "volume_id": args.volume_id or scope.get("volume_id", "volume.unspecified"),
        },
        "resolution_band": {
            "lod_min_tag": args.lod_min or "lod.any",
            "lod_max_tag": args.lod_max or "lod.any",
        },
        "field_set": field_ids,
        "mode": args.mode,
        "budget": {
            "cost_units_max": args.budget_cost,
            "memory_units_max": args.budget_memory,
            "time_units_max": args.budget_time,
        },
        "authority_token": args.authority_token or "authority.unspecified",
        "seed_namespace": args.seed_namespace or "seed.unspecified",
        "required_capabilities": args.required_capability or [],
        "dependencies": args.dependency or [],
        "failure_semantics": args.failure_semantics,
    }
    return request


def build_validation_targets(model_records, plan_record):
    targets = []
    model_lookup = {model["model_id"]: model for model in model_records if "model_id" in model}
    for layer in plan_record.get("layers", []):
        for ref in layer.get("model_refs", []):
            model_id = ref.get("model_id")
            model = model_lookup.get(model_id)
            if not model:
                continue
            for target in model.get("validation_targets", []):
                targets.append(
                    {
                        "model_id": model_id,
                        "target_id": target.get("target_id"),
                        "schema_id": target.get("schema_id"),
                        "target_tags": target.get("target_tags", []),
                    }
                )
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline refinement runner (metadata only).")
    parser.add_argument("--plan-id", required=True, help="Refinement plan id to execute.")
    parser.add_argument("--packs", action="append", help="Pack root or pack directory.")
    parser.add_argument("--mode", choices=["objective", "subjective"], default="objective")
    parser.add_argument("--lod-min", dest="lod_min")
    parser.add_argument("--lod-max", dest="lod_max")
    parser.add_argument("--fields", help="Comma-separated field ids.")
    parser.add_argument("--target-node", dest="target_node")
    parser.add_argument("--domain-id")
    parser.add_argument("--volume-id")
    parser.add_argument("--seed-namespace")
    parser.add_argument("--authority-token", dest="authority_token")
    parser.add_argument("--required-capability", action="append")
    parser.add_argument("--dependency", action="append")
    parser.add_argument("--budget-cost", type=int)
    parser.add_argument("--budget-memory", type=int)
    parser.add_argument("--budget-time", type=int)
    parser.add_argument(
        "--failure-semantics",
        default="degrade_or_freeze",
        choices=["degrade_or_freeze", "degrade", "freeze", "deny"],
    )
    parser.add_argument("--run-id")
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    roots = parse_pack_paths(args)
    plan_records = collect_records(roots, "refinement_plans.json")
    plan_record = next((p for p in plan_records if p.get("plan_id") == args.plan_id), None)
    if not plan_record:
        print(f"Plan not found: {args.plan_id}", file=sys.stderr)
        return 2

    model_records = collect_records(roots, "worldgen_models.json")
    request = build_request(args, plan_record)
    validation_targets = build_validation_targets(model_records, plan_record)

    manifest_paths = find_pack_manifests(roots)
    pack_ids = []
    for manifest_path in manifest_paths:
        manifest = load_json(manifest_path)
        pack_id = manifest.get("record", {}).get("pack_id")
        if pack_id:
            pack_ids.append(pack_id)

    payload = {
        "tool_id": "dominium.tool.refinement_runner",
        "tool_version": "1.0.0",
        "request": request,
        "plan_summary": {
            "plan_id": plan_record.get("plan_id"),
            "plan_tags": plan_record.get("plan_tags", []),
            "layer_ids": [layer.get("layer_id") for layer in plan_record.get("layers", [])],
            "precedence_rules": plan_record.get("precedence_rules", []),
            "source": plan_record.get("_source"),
        },
        "validation": {
            "targets": validation_targets,
            "determinism_expected": True,
        },
        "provenance": {
            "provenance_id": f"prov.tool.refinement_runner.{args.plan_id}",
            "input_packs": sorted(set(pack_ids)),
        },
        "extensions": {
            "not_defined": [
                "no_simulation_outputs",
                "no_objective_state_mutation",
            ]
        },
    }

    run_id = args.run_id or compute_hash(payload)
    root = repo_root()
    output_dir = Path(args.output_dir) if args.output_dir else root / "build" / "cache" / "assets" / "refinement_runs"
    output_path = ensure_cache_path(output_dir / f"refinement_run_{run_id}.json", root)
    write_json(output_path, payload)
    print(f"Wrote refinement metadata: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

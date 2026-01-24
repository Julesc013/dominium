import argparse
import sys
from pathlib import Path

from _common import (
    collect_records,
    compute_hash,
    ensure_cache_path,
    parse_pack_paths,
    repo_root,
    write_json,
)


def filter_by_tag(records, key, tags):
    if not tags:
        return records
    filtered = []
    for record in records:
        value = record.get(key)
        if value in tags:
            filtered.append(record)
    return filtered


def filter_by_visibility(records, visibility):
    if not visibility:
        return records
    filtered = []
    for record in records:
        access = record.get("access_control", {})
        if access.get("visibility") == visibility:
            filtered.append(record)
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline epistemic simulator (metadata only).")
    parser.add_argument("--packs", action="append", help="Pack root or pack directory.")
    parser.add_argument("--knowledge-tag", action="append", help="Filter by knowledge domain tag.")
    parser.add_argument("--measurement-tag", action="append", help="Filter by measurement domain tag.")
    parser.add_argument("--visibility", help="Filter measurements by access visibility.")
    parser.add_argument("--mode", choices=["objective", "subjective"], default="subjective")
    parser.add_argument("--run-id")
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    roots = parse_pack_paths(args)
    knowledge_records = collect_records(roots, "knowledge_artifacts.json")
    measurement_records = collect_records(roots, "measurement_artifacts.json")

    knowledge_records = filter_by_tag(knowledge_records, "knowledge_domain_tag", args.knowledge_tag or [])
    measurement_records = filter_by_tag(measurement_records, "measurement_domain_tag", args.measurement_tag or [])
    measurement_records = filter_by_visibility(measurement_records, args.visibility)

    payload = {
        "tool_id": "dominium.tool.epistemic_simulator",
        "tool_version": "1.0.0",
        "request": {
            "mode": args.mode,
            "knowledge_tags": args.knowledge_tag or [],
            "measurement_tags": args.measurement_tag or [],
            "visibility": args.visibility or "unspecified",
        },
        "selected_knowledge": [record.get("knowledge_artifact_id") for record in knowledge_records],
        "selected_measurements": [
            record.get("measurement_artifact_id") for record in measurement_records
        ],
        "subjective_snapshot": {
            "mode": args.mode,
            "notes": "No objective truth modification.",
        },
        "extensions": {
            "not_defined": [
                "no_objective_state_mutation"
            ]
        },
    }

    run_id = args.run_id or compute_hash(payload)
    root = repo_root()
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else root / "build" / "cache" / "assets" / "epistemic_runs"
    )
    output_path = ensure_cache_path(output_dir / f"epistemic_run_{run_id}.json", root)
    write_json(output_path, payload)
    print(f"Wrote epistemic metadata: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Explain deterministic GEO-9 property provenance for an object/property path."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.geo import explain_property_origin  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _default_merge_result() -> dict:
    property_history = [
        {
            "layer_id": "base.worldgen",
            "layer_kind": "base",
            "source_ref": "base.worldgen",
            "pack_hash": "",
            "pack_id": "",
            "operation": "base",
            "value": "Procedural Earth",
            "previous_value": None,
        },
        {
            "layer_id": "save.patch",
            "layer_kind": "save",
            "source_ref": "save.patch",
            "pack_hash": "",
            "pack_id": "",
            "operation": "set",
            "value": "New Earth",
            "previous_value": "Procedural Earth",
        },
    ]
    merge_result = {
        "overlay_manifest_hash": canonical_sha256({"fixture": "overlay_manifest"}),
        "property_patch_hash_chain": canonical_sha256({"fixture": "property_patch_chain"}),
        "overlay_merge_result_hash_chain": canonical_sha256({"fixture": "overlay_merge_result_chain"}),
        "overlay_conflict_artifact_hash_chain": canonical_sha256({"fixture": "overlay_conflict_chain"}),
        "overlay_conflict_policy_id": "overlay.conflict.last_wins",
        "overlay_conflict_mode": "last_wins",
        "property_origin_index": {
            "object.earth": {
                "display_name": property_history,
            }
        },
        "overlay_conflict_index": {
            "object.earth": {
                "display_name": [],
            }
        },
    }
    return merge_result


def explain_property_origin_report(
    *,
    object_id: str,
    property_path: str,
    merge_result: Mapping[str, object] | None = None,
) -> dict:
    resolved_merge = dict(merge_result or _default_merge_result())
    report = explain_property_origin(
        merge_result=resolved_merge,
        object_id=object_id,
        property_path=property_path,
    )
    if str(report.get("result", "")) != "complete":
        return dict(report)
    out = {
        "result": "complete",
        "explain_contract_id": "explain.property_origin",
        "overlay_conflict_contract_id": "explain.overlay_conflict",
        "report": dict(report),
        "merge_result_hash": canonical_sha256(
            {
                "overlay_manifest_hash": str(resolved_merge.get("overlay_manifest_hash", "")).strip(),
                "property_patch_hash_chain": str(resolved_merge.get("property_patch_hash_chain", "")).strip(),
                "overlay_merge_result_hash_chain": str(resolved_merge.get("overlay_merge_result_hash_chain", "")).strip(),
                "overlay_conflict_artifact_hash_chain": str(
                    resolved_merge.get("overlay_conflict_artifact_hash_chain", "")
                ).strip(),
            }
        ),
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Explain GEO-9 property provenance.")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--property-path", required=True)
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = explain_property_origin_report(
        object_id=str(args.object_id).strip(),
        property_path=str(args.property_path).strip(),
    )
    output_path = str(args.output_path or "").strip()
    if output_path:
        abs_path = os.path.normpath(os.path.abspath(output_path))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

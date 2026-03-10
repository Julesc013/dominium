#!/usr/bin/env python3
"""Verify GEO-9 overlay merge replay determinism."""

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

from src.geo import overlay_conflict_policy_registry_hash, overlay_policy_registry_hash, overlay_proof_surface  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.testx.tests.geo9_testlib import (  # noqa: E402
    merge_state_overlay,
    run_overlay_save_patch_process,
    seed_overlay_state,
)


def verify_overlay_merge_replay(
    *,
    state_payload: Mapping[str, object],
    property_patches: object,
    merge_result: Mapping[str, object],
) -> dict:
    surface = overlay_proof_surface(
        overlay_manifest=state_payload.get("overlay_manifest"),
        property_patches=property_patches,
        effective_object_views=(dict(merge_result or {})).get("effective_object_views"),
        overlay_conflict_artifacts=(dict(merge_result or {})).get("overlay_conflict_artifacts"),
    )
    recorded = {
        "overlay_manifest_hash": str((dict(merge_result or {})).get("overlay_manifest_hash", "")).strip().lower()
        or str(state_payload.get("overlay_manifest_hash", "")).strip().lower(),
        "property_patch_hash_chain": str((dict(merge_result or {})).get("property_patch_hash_chain", "")).strip().lower()
        or str(state_payload.get("property_patch_hash_chain", "")).strip().lower(),
        "overlay_merge_result_hash_chain": str((dict(merge_result or {})).get("overlay_merge_result_hash_chain", "")).strip().lower(),
        "overlay_conflict_artifact_hash_chain": str(
            (dict(merge_result or {})).get("overlay_conflict_artifact_hash_chain", "")
        ).strip().lower(),
    }
    observed = {
        "overlay_policy_registry_hash": overlay_policy_registry_hash().strip().lower(),
        "overlay_conflict_policy_registry_hash": overlay_conflict_policy_registry_hash().strip().lower(),
        "overlay_manifest_hash": str(surface.get("overlay_manifest_hash", "")).strip().lower(),
        "property_patch_hash_chain": str(surface.get("property_patch_hash_chain", "")).strip().lower(),
        "overlay_merge_result_hash_chain": str(surface.get("overlay_merge_result_hash_chain", "")).strip().lower(),
        "overlay_conflict_artifact_hash_chain": str(surface.get("overlay_conflict_artifact_hash_chain", "")).strip().lower(),
    }
    violations = []
    for key in (
        "overlay_manifest_hash",
        "property_patch_hash_chain",
        "overlay_merge_result_hash_chain",
        "overlay_conflict_artifact_hash_chain",
    ):
        recorded_value = str(recorded.get(key, "")).strip().lower()
        observed_value = str(observed.get(key, "")).strip().lower()
        if recorded_value and observed_value and recorded_value != observed_value:
            violations.append("recorded {} does not match observed replay hash".format(key))
    report = {
        "result": "violation" if violations else "complete",
        "recorded": recorded,
        "observed": observed,
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _run_once() -> dict:
    state = seed_overlay_state(include_mods=True)
    process_result = run_overlay_save_patch_process(state=state, value="New Earth")
    merged = merge_state_overlay(state=state, include_mods=True)
    merge_result = dict(merged.get("merge_result") or {})
    report = verify_overlay_merge_replay(
        state_payload=state,
        property_patches=merged.get("property_patches"),
        merge_result=merge_result,
    )
    return {
        "process_result": dict(process_result),
        "merge_result": merge_result,
        "replay_report": dict(report),
        "overlay_manifest_hash": str(merge_result.get("overlay_manifest_hash", "")).strip(),
        "property_patch_hash_chain": str(merge_result.get("property_patch_hash_chain", "")).strip(),
        "overlay_merge_result_hash_chain": str(merge_result.get("overlay_merge_result_hash_chain", "")).strip(),
        "overlay_conflict_artifact_hash_chain": str(merge_result.get("overlay_conflict_artifact_hash_chain", "")).strip(),
        "run_hash": canonical_sha256(
            {
                "process_result": dict(process_result),
                "merge_result": merge_result,
                "replay_report": dict(report),
            }
        ),
    }


def verify_overlay_merge_fixture() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    replay_report = dict(first.get("replay_report") or {})
    report = {
        "result": "complete" if stable and str(replay_report.get("result", "")) == "complete" else "violation",
        "replay_report": replay_report,
        "overlay_manifest_hash": str(first.get("overlay_manifest_hash", "")),
        "property_patch_hash_chain": str(first.get("property_patch_hash_chain", "")),
        "overlay_merge_result_hash_chain": str(first.get("overlay_merge_result_hash_chain", "")),
        "overlay_conflict_artifact_hash_chain": str(first.get("overlay_conflict_artifact_hash_chain", "")),
        "run_hash": str(first.get("run_hash", "")),
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-9 overlay merge replay determinism.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_overlay_merge_fixture()
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

#!/usr/bin/env python3
"""PerformX deterministic performance envelope runner."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(THIS_DIR, "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

DEV_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "scripts", "dev"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from benchmark_runner import run_envelopes
from cache import build_cache_key, load_cache, write_cache
from canonicalize import canonical_sha256, canonicalize_json_payload
from envelope_validator import (
    absolute_path,
    load_registry,
    profile_index,
    select_envelopes,
    validate_envelope_registry,
    validate_profile_registry,
)
from hardware_profile import capture_hardware_profile, select_profile
from regression_detector import detect_regressions
from env_tools_lib import canonical_workspace_id, canonicalize_env_for_workspace, detect_repo_root


ENVELOPE_REGISTRY_REL = os.path.join("data", "registries", "performance_envelopes.json")
PROFILE_REGISTRY_REL = os.path.join("data", "registries", "performance_profiles.json")
OUTPUT_ROOT_REL = os.path.join("docs", "audit", "performance")
RESULTS_REL = "PERFORMX_RESULTS.json"
REGRESSIONS_REL = "PERFORMX_REGRESSIONS.json"
RUN_META_REL = "RUN_META.json"
BASELINE_REL = "PERFORMX_BASELINE.json"


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return detect_repo_root(os.getcwd(), __file__)


def _relpath(path: str, repo_root: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def _read_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_canonical_json(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    canonical_payload = canonicalize_json_payload(payload)
    _write_json(path, canonical_payload)
    return canonical_payload


def _load_inputs(
    repo_root: str,
    envelope_registry_rel: str,
    profile_registry_rel: str,
) -> Tuple[Dict[str, Any] | None, Dict[str, Any] | None, List[str]]:
    errors: List[str] = []
    envelope_payload, envelope_errors = load_registry(
        absolute_path(repo_root, envelope_registry_rel),
        "refuse.performance_envelope_registry_missing",
    )
    profile_payload, profile_errors = load_registry(
        absolute_path(repo_root, profile_registry_rel),
        "refuse.performance_profile_registry_missing",
    )
    errors.extend(envelope_errors)
    errors.extend(profile_errors)

    if envelope_payload is not None:
        errors.extend(validate_envelope_registry(envelope_payload))
    if profile_payload is not None:
        errors.extend(validate_profile_registry(profile_payload))
    return envelope_payload, profile_payload, sorted(set(errors))


def _selected_envelopes(envelope_payload: Dict[str, Any], selected_ids: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    selected, missing = select_envelopes(envelope_payload, selected_ids)
    return selected, sorted(set(missing))


def _result_payload(
    profile: Dict[str, Any],
    normalization_factor: float,
    results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "artifact_class": "CANONICAL",
        "schema_id": "dominium.schema.governance.performance_result",
        "schema_version": "1.0.0",
        "record": {
            "result_set_id": "performx.results",
            "profile_id": str(profile.get("profile_id", "profile.default")).strip() or "profile.default",
            "normalization_factor": float(normalization_factor),
            "results": results,
            "extensions": {},
        },
    }


def _load_baseline(path: str) -> Dict[str, Any] | None:
    if not os.path.isfile(path):
        return None
    return _read_json(path)


def _run_repox(repo_root: str) -> int:
    repox = os.path.join(repo_root, "scripts", "ci", "check_repox_rules.py")
    result = subprocess.run(
        [sys.executable, repox, "--repo-root", repo_root],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    return int(result.returncode)


def _baseline_payload(
    results_payload: Dict[str, Any],
    identity_payload: Dict[str, Any],
    justification_rel: str,
) -> Dict[str, Any]:
    record = results_payload.get("record", {}) if isinstance(results_payload.get("record"), dict) else {}
    return {
        "artifact_class": "CANONICAL",
        "schema_id": "dominium.schema.governance.performance_result",
        "schema_version": "1.0.0",
        "record": {
            "baseline_id": "performx.baseline",
            "identity_fingerprint_sha256": canonical_sha256(identity_payload),
            "source_results_sha256": canonical_sha256(results_payload),
            "justification_path": justification_rel,
            "results": record.get("results", []),
            "extensions": {},
        },
    }


def _run(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    start = time.time()

    ws_id = canonical_workspace_id(repo_root, env=os.environ)
    env, ws_dirs = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=ws_id)
    output_root = absolute_path(repo_root, args.output_root)
    baseline_path = absolute_path(repo_root, args.baseline_path)

    envelope_payload, profile_payload, errors = _load_inputs(
        repo_root,
        args.envelope_registry,
        args.profile_registry,
    )
    if errors or envelope_payload is None or profile_payload is None:
        print(json.dumps({"result": "refused", "refusal_codes": sorted(set(errors))}, indent=2, sort_keys=True))
        return 2

    selected_ids = sorted(set(args.envelope or []))
    selected, missing = _selected_envelopes(envelope_payload, selected_ids)
    if missing:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.unknown_envelope", "missing": missing}, indent=2, sort_keys=True))
        return 2
    if not selected:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.no_envelopes_selected"}, indent=2, sort_keys=True))
        return 2

    hardware = capture_hardware_profile()
    profile = select_profile(profile_payload, hardware)
    factor = float(profile.get("normalization_factor", 1.0) or 1.0)
    seed = int(args.seed)

    cache_context = {
        "schema_version": "1.0.0",
        "selected_envelopes": [str(item.get("envelope_id", "")).strip() for item in selected],
        "profile_id": str(profile.get("profile_id", "")),
        "normalization_factor": factor,
        "seed": seed,
        "envelope_registry_version": str(envelope_payload.get("record", {}).get("registry_version", "")),
    }
    cache_key = build_cache_key(cache_context)
    workspace_id = str(ws_dirs.get("workspace_id", ""))
    cache_hit = False
    if args.cache_mode == "auto":
        cached = load_cache(repo_root, cache_key, workspace_id=workspace_id)
        if isinstance(cached, dict) and isinstance(cached.get("results"), list):
            results_rows = cached["results"]
            cache_hit = True
        else:
            results_rows = run_envelopes(selected, normalization_factor=factor, seed=seed)
            write_cache(repo_root, cache_key, {"results": results_rows}, workspace_id=workspace_id)
    else:
        results_rows = run_envelopes(selected, normalization_factor=factor, seed=seed)

    result_payload = _result_payload(profile, factor, results_rows)
    envelope_index = {str(row.get("envelope_id", "")).strip(): row for row in selected}
    baseline_payload = _load_baseline(baseline_path)
    regression_payload = detect_regressions(results_rows, envelope_index, baseline_payload)

    results_path = os.path.join(output_root, RESULTS_REL)
    regressions_path = os.path.join(output_root, REGRESSIONS_REL)
    run_meta_path = os.path.join(output_root, RUN_META_REL)
    canonical_results = _write_canonical_json(results_path, result_payload)
    canonical_regressions = _write_canonical_json(regressions_path, regression_payload)

    run_meta_payload = {
        "artifact_class": "RUN_META",
        "status": "DERIVED",
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_ms": int((time.time() - start) * 1000.0),
        "workspace_id": str(ws_dirs.get("workspace_id", "")),
        "cache_key": cache_key,
        "cache_hit": bool(cache_hit),
        "hardware_profile": hardware,
        "result_hash": canonical_sha256(canonical_results),
        "regression_hash": canonical_sha256(canonical_regressions),
    }
    _write_json(run_meta_path, run_meta_payload)

    critical_failures = int(
        canonical_regressions.get("record", {}).get("summary", {}).get("critical_failures", 0)
    )
    response = {
        "result": "complete",
        "workspace_id": str(ws_dirs.get("workspace_id", "")),
        "results": _relpath(results_path, repo_root),
        "regressions": _relpath(regressions_path, repo_root),
        "run_meta": _relpath(run_meta_path, repo_root),
        "critical_failures": critical_failures,
    }
    print(json.dumps(response, indent=2, sort_keys=True))

    if critical_failures > 0 and args.fail_on_critical:
        return 2
    return 0


def _baseline_update(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    if not args.update:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.baseline_update_not_requested"}, indent=2, sort_keys=True))
        return 2
    results_path = absolute_path(repo_root, args.results_path)
    baseline_path = absolute_path(repo_root, args.baseline_path)
    justification_path = absolute_path(repo_root, args.justification)
    identity_path = absolute_path(repo_root, os.path.join("docs", "audit", "identity_fingerprint.json"))

    if not os.path.isfile(justification_path):
        print(json.dumps({"result": "refused", "refusal_code": "refuse.justification_missing"}, indent=2, sort_keys=True))
        return 2
    results_payload = _read_json(results_path)
    if results_payload is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.results_missing"}, indent=2, sort_keys=True))
        return 2
    identity_payload = _read_json(identity_path)
    if identity_payload is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.identity_fingerprint_missing"}, indent=2, sort_keys=True))
        return 2

    if _run_repox(repo_root) != 0:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.repox_not_green_for_baseline_update"}, indent=2, sort_keys=True))
        return 2

    baseline_payload = _baseline_payload(
        results_payload=results_payload,
        identity_payload=identity_payload,
        justification_rel=_relpath(justification_path, repo_root),
    )
    canonical_baseline = _write_canonical_json(baseline_path, baseline_payload)

    print(
        json.dumps(
            {
                "result": "baseline_updated",
                "baseline": _relpath(baseline_path, repo_root),
                "baseline_hash": canonical_sha256(canonical_baseline),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PerformX deterministic performance envelopes.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run PerformX envelopes and write artifacts.")
    run.add_argument("--repo-root", default="")
    run.add_argument("--envelope", action="append", default=[])
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--cache-mode", choices=("auto", "off"), default="auto")
    run.add_argument("--fail-on-critical", action="store_true", default=True)
    run.add_argument("--output-root", default=OUTPUT_ROOT_REL)
    run.add_argument("--baseline-path", default=os.path.join(OUTPUT_ROOT_REL, BASELINE_REL))
    run.add_argument("--envelope-registry", default=ENVELOPE_REGISTRY_REL)
    run.add_argument("--profile-registry", default=PROFILE_REGISTRY_REL)
    run.set_defaults(func=_run)

    baseline = sub.add_parser("baseline", help="Baseline management.")
    baseline.add_argument("--repo-root", default="")
    baseline.add_argument("--update", action="store_true")
    baseline.add_argument("--results-path", default=os.path.join(OUTPUT_ROOT_REL, RESULTS_REL))
    baseline.add_argument("--baseline-path", default=os.path.join(OUTPUT_ROOT_REL, BASELINE_REL))
    baseline.add_argument("--justification", default="")
    baseline.set_defaults(func=_baseline_update)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

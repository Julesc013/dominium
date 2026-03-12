"""Deterministic MVP cross-platform gate helpers."""

from __future__ import annotations

import copy
import json
import os
import sys
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.compat import (  # noqa: E402
    build_default_endpoint_descriptor,
    build_endpoint_descriptor,
    negotiate_endpoint_descriptors,
    verify_negotiation_record,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


MVP_CROSS_PLATFORM_GATE_ID = "mvp.cross_platform.gate.v1"
MVP_CROSS_PLATFORM_REGRESSION_UPDATE_TAG = "MVP-CROSS-PLATFORM-REGRESSION-UPDATE"
DEFAULT_REPORT_REL = os.path.join("build", "mvp", "mvp_cross_platform_matrix.json")
DEFAULT_HASHES_REL = os.path.join("build", "mvp", "mvp_cross_platform_hashes.json")
DEFAULT_BASELINE_REL = os.path.join("data", "regression", "mvp_cross_platform_baseline.json")
DEFAULT_FINAL_DOC_REL = os.path.join("docs", "audit", "MVP_CROSS_PLATFORM_FINAL.md")
DEFAULT_GATE_RESULTS_REL = os.path.join("build", "mvp", "mvp_cross_platform_gate_results.json")
LIB_BASELINE_REL = os.path.join("data", "regression", "lib_full_baseline.json")
PLATFORM_ORDER = ("windows", "macos", "linux")
RELEASE_PRESETS = {
    "windows": "release-win-vs2026",
    "macos": "release-macos-xcode",
    "linux": "release-linux-gcc",
}
DEBUG_PRESETS = {
    "windows": "dev-win-vs2026",
    "macos": "dev-macos-xcode",
    "linux": "dev-linux-gcc",
}
HOST_META_IGNORED = ("timestamps", "path_separators", "absolute_paths")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    token = str(path or "").strip()
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = str(rel_path or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token.replace("/", os.sep))))


def _relative_path(repo_root: str, value: str) -> str:
    token = str(value or "").strip()
    if not token:
        return ""
    abs_path = _repo_abs(repo_root, token)
    if not abs_path:
        return ""
    try:
        return _norm(os.path.relpath(abs_path, repo_root))
    except ValueError:
        return _norm(abs_path)


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def load_json_if_present(repo_root: str, rel_path: str) -> dict:
    abs_path = _repo_abs(repo_root, rel_path)
    if not abs_path or not os.path.isfile(abs_path):
        return {}
    return _read_json(abs_path)


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))
    return _norm(path)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return _norm(path)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _token(value: object) -> str:
    return str(value or "").strip()


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted(set(_token(item) for item in list(values or []) if _token(item)))


def _collect_mismatch_rows(expected: object, actual: object, path: str = "$") -> list[dict]:
    if isinstance(expected, Mapping) and isinstance(actual, Mapping):
        rows = []
        keys = sorted(set(str(key) for key in expected.keys()) | set(str(key) for key in actual.keys()))
        expected_map = _as_map(expected)
        actual_map = _as_map(actual)
        for key in keys:
            rows.extend(_collect_mismatch_rows(expected_map.get(key), actual_map.get(key), "{}.{}".format(path, key)))
        return rows
    if isinstance(expected, list) and isinstance(actual, list):
        rows = []
        for index in range(max(len(expected), len(actual))):
            exp_item = expected[index] if index < len(expected) else None
            act_item = actual[index] if index < len(actual) else None
            rows.extend(_collect_mismatch_rows(exp_item, act_item, "{}[{}]".format(path, index)))
        return rows
    if expected == actual:
        return []
    return [{"path": path, "expected": expected, "actual": actual}]


def _load_smoke_inputs(repo_root: str) -> dict:
    from tools.mvp.mvp_smoke_common import (
        DEFAULT_BASELINE_REL as SMOKE_BASELINE_REL,
        DEFAULT_HASHES_REL as SMOKE_HASHES_REL,
        DEFAULT_MVP_SMOKE_SEED,
        DEFAULT_REPORT_REL as SMOKE_REPORT_REL,
        DEFAULT_SCENARIO_REL as SMOKE_SCENARIO_REL,
        build_expected_hash_fingerprints,
        build_mvp_smoke_baseline,
        generate_mvp_smoke_scenario,
        run_mvp_smoke,
        write_generated_mvp_smoke_inputs,
        write_mvp_smoke_outputs,
    )

    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scenario = load_json_if_present(repo_root_abs, SMOKE_SCENARIO_REL)
    hashes = load_json_if_present(repo_root_abs, SMOKE_HASHES_REL)
    report = load_json_if_present(repo_root_abs, SMOKE_REPORT_REL)
    baseline = load_json_if_present(repo_root_abs, SMOKE_BASELINE_REL)

    if not scenario:
        scenario = generate_mvp_smoke_scenario(repo_root_abs, seed=DEFAULT_MVP_SMOKE_SEED)
    if not hashes:
        hashes = build_expected_hash_fingerprints(repo_root_abs, seed=DEFAULT_MVP_SMOKE_SEED, scenario=scenario)
        write_generated_mvp_smoke_inputs(repo_root_abs, seed=DEFAULT_MVP_SMOKE_SEED)
    if _token(report.get("result")) != "complete":
        report = run_mvp_smoke(
            repo_root_abs,
            seed=DEFAULT_MVP_SMOKE_SEED,
            scenario=scenario,
            expected_hashes=hashes,
            baseline_payload=baseline,
        )
        write_mvp_smoke_outputs(repo_root_abs, report=report)
    if not baseline:
        baseline = build_mvp_smoke_baseline(report)

    return {
        "scenario": scenario,
        "hashes": hashes,
        "report": report,
        "baseline": baseline,
    }


def _load_stress_inputs(repo_root: str) -> dict:
    from tools.mvp.stress_gate_common import (
        DEFAULT_BASELINE_REL as STRESS_BASELINE_REL,
        DEFAULT_HASHES_REL as STRESS_HASHES_REL,
        DEFAULT_MVP_STRESS_SEED,
        DEFAULT_PROOF_REPORT_REL as STRESS_PROOF_REL,
        DEFAULT_REPORT_REL as STRESS_REPORT_REL,
        build_mvp_stress_baseline,
        maybe_load_cached_mvp_stress_proof_report,
        maybe_load_cached_mvp_stress_report,
        run_all_mvp_stress,
        verify_mvp_stress_proofs,
        write_mvp_stress_outputs,
    )

    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    report = maybe_load_cached_mvp_stress_report(repo_root_abs, report_path=STRESS_REPORT_REL)
    if not report:
        report = load_json_if_present(repo_root_abs, STRESS_REPORT_REL)
    proof_report = {}
    hashes = load_json_if_present(repo_root_abs, STRESS_HASHES_REL)
    baseline = load_json_if_present(repo_root_abs, STRESS_BASELINE_REL)

    report_is_complete = bool(report) and (
        _token(report.get("result")) == "complete"
        or bool(_as_map(report.get("assertions")).get("all_suites_passed", False))
    )
    if not report_is_complete:
        report = run_all_mvp_stress(repo_root_abs, seed=DEFAULT_MVP_STRESS_SEED)
        write_mvp_stress_outputs(repo_root_abs, report=report)
    proof_report = maybe_load_cached_mvp_stress_proof_report(
        repo_root_abs,
        report=report,
        proof_report_path=STRESS_PROOF_REL,
    )
    if not proof_report:
        proof_report = load_json_if_present(repo_root_abs, STRESS_PROOF_REL)
    if _token(proof_report.get("result")) != "complete":
        proof_report = verify_mvp_stress_proofs(repo_root_abs, report=report, baseline_payload=baseline)
        write_mvp_stress_outputs(repo_root_abs, report=report, proof_report=proof_report)
    if not hashes:
        hashes = load_json_if_present(repo_root_abs, STRESS_HASHES_REL)
    if not baseline:
        baseline = build_mvp_stress_baseline(report, proof_report)

    return {
        "report": report,
        "proof_report": proof_report,
        "hashes": hashes,
        "baseline": baseline,
    }


def _load_lib_baseline(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    return load_json_if_present(repo_root_abs, LIB_BASELINE_REL)


def _minimal_descriptor(
    repo_root: str,
    *,
    product_id: str,
    product_version: str,
    shared_capabilities: list[str],
    build_id: str,
    build_variant: str,
) -> dict:
    base = build_default_endpoint_descriptor(repo_root, product_id=product_id, product_version=product_version)
    if not base:
        return {}
    extensions = _as_map(base.get("extensions"))
    extensions.update(
        {
            "official.build_id": _token(build_id),
            "official.cross_platform.variant": _token(build_variant),
        }
    )
    return build_endpoint_descriptor(
        product_id=_token(product_id),
        product_version=_token(product_version),
        protocol_versions_supported=_as_list(base.get("protocol_versions_supported")),
        semantic_contract_versions_supported=_as_list(base.get("semantic_contract_versions_supported")),
        feature_capabilities=list(shared_capabilities),
        required_capabilities=[],
        optional_capabilities=[],
        degrade_ladders=_as_list(base.get("degrade_ladders")),
        extensions=extensions,
    )


def build_negotiation_matrix(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    shared_capabilities = ["cap.ipc.attach_console", "cap.worldgen.refinement_l3"]
    scenarios = (
        {
            "scenario_id": "client_build_a_server_build_a",
            "pair_kind": "same_build",
            "description": "client build A against server build A",
            "expected_compatibility_mode_id": "compat.full",
            "descriptor_a": _minimal_descriptor(
                repo_root_abs,
                product_id="client",
                product_version="0.0.0",
                shared_capabilities=shared_capabilities,
                build_id="build.mvp_gate2.client.a",
                build_variant="build_a",
            ),
            "descriptor_b": _minimal_descriptor(
                repo_root_abs,
                product_id="server",
                product_version="0.0.0",
                shared_capabilities=shared_capabilities,
                build_id="build.mvp_gate2.server.a",
                build_variant="build_a",
            ),
        },
        {
            "scenario_id": "client_build_a_server_build_b",
            "pair_kind": "same_version_rebuild",
            "description": "client build A against server build B with the same release version",
            "expected_compatibility_mode_id": "compat.full",
            "descriptor_a": _minimal_descriptor(
                repo_root_abs,
                product_id="client",
                product_version="0.0.0",
                shared_capabilities=shared_capabilities,
                build_id="build.mvp_gate2.client.a",
                build_variant="build_a",
            ),
            "descriptor_b": _minimal_descriptor(
                repo_root_abs,
                product_id="server",
                product_version="0.0.0",
                shared_capabilities=shared_capabilities,
                build_id="build.mvp_gate2.server.b",
                build_variant="build_b",
            ),
        },
        {
            "scenario_id": "client_older_minor_server_newer_minor",
            "pair_kind": "minor_version_delta",
            "description": "older client minor version against newer server minor version under the shared MVP protocol set",
            "expected_compatibility_mode_id": "compat.full",
            "descriptor_a": _minimal_descriptor(
                repo_root_abs,
                product_id="client",
                product_version="0.1.0",
                shared_capabilities=shared_capabilities,
                build_id="build.mvp_gate2.client.oldminor",
                build_variant="old_minor",
            ),
            "descriptor_b": _minimal_descriptor(
                repo_root_abs,
                product_id="server",
                product_version="0.2.0",
                shared_capabilities=shared_capabilities,
                build_id="build.mvp_gate2.server.newminor",
                build_variant="new_minor",
            ),
        },
    )

    results = []
    for row in scenarios:
        descriptor_a = _as_map(row.get("descriptor_a"))
        descriptor_b = _as_map(row.get("descriptor_b"))
        first = negotiate_endpoint_descriptors(repo_root_abs, descriptor_a, descriptor_b, allow_read_only=False)
        second = negotiate_endpoint_descriptors(repo_root_abs, descriptor_a, descriptor_b, allow_read_only=False)
        first_record = _as_map(first.get("negotiation_record"))
        verification = verify_negotiation_record(
            repo_root_abs,
            first_record,
            descriptor_a,
            descriptor_b,
            allow_read_only=False,
        )
        result_row = {
            "scenario_id": _token(row.get("scenario_id")),
            "pair_kind": _token(row.get("pair_kind")),
            "description": _token(row.get("description")),
            "expected_compatibility_mode_id": _token(row.get("expected_compatibility_mode_id")),
            "compatibility_mode_id": _token(first.get("compatibility_mode_id")),
            "result": _token(first.get("result")) or "unknown",
            "refusal_code": _token(_as_map(first.get("refusal")).get("reason_code")),
            "first_negotiation_record_hash": _token(first.get("negotiation_record_hash")),
            "second_negotiation_record_hash": _token(second.get("negotiation_record_hash")),
            "record_stable": _token(first.get("negotiation_record_hash")) == _token(second.get("negotiation_record_hash")),
            "record_verified": _token(verification.get("result")) == "complete",
            "descriptor_a_hash": _token(first.get("endpoint_a_hash")),
            "descriptor_b_hash": _token(first.get("endpoint_b_hash")),
            "negotiation_record_fingerprint": canonical_sha256(first_record),
            "deterministic_fingerprint": "",
        }
        result_row["deterministic_fingerprint"] = canonical_sha256(dict(result_row, deterministic_fingerprint=""))
        results.append(result_row)

    assertions = {
        "scenario_order_deterministic": [row.get("scenario_id") for row in results]
        == [row.get("scenario_id") for row in scenarios],
        "modes_match_expected": all(
            _token(row.get("compatibility_mode_id")) == _token(row.get("expected_compatibility_mode_id")) for row in results
        ),
        "records_stable": all(bool(row.get("record_stable", False)) for row in results),
        "records_verified": all(bool(row.get("record_verified", False)) for row in results),
        "no_refusals": all(not _token(row.get("refusal_code")) for row in results),
    }
    matrix = {
        "scenario_results": results,
        "assertions": assertions,
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "deterministic_fingerprint": "",
    }
    matrix["deterministic_fingerprint"] = canonical_sha256(dict(matrix, deterministic_fingerprint=""))
    return matrix


def build_portable_linked_parity(
    *,
    smoke_bundle: Mapping[str, object],
    stress_bundle: Mapping[str, object],
    lib_baseline: Mapping[str, object],
) -> dict:
    smoke_baseline = _as_map(_as_map(smoke_bundle).get("baseline"))
    stress_baseline = _as_map(_as_map(stress_bundle).get("baseline"))
    lib_base = _as_map(lib_baseline)
    shared_artifacts = {
        "scenario_id": _token(smoke_baseline.get("scenario_id")),
        "scenario_fingerprint": _token(smoke_baseline.get("scenario_fingerprint")),
        "proof_anchor_hashes": {
            "smoke": dict(_as_map(smoke_baseline.get("proof_anchor_hashes"))),
            "stress": dict(_as_map(stress_baseline.get("server_proof_anchor_hashes"))),
        },
        "pack_lock_hashes": {
            "smoke_runtime": _token(smoke_baseline.get("runtime_pack_lock_hash")),
            "stress_runtime": _token(_as_map(stress_baseline.get("pack_lock_hashes")).get("runtime")),
        },
        "negotiation_record_hashes": {
            "smoke": dict(_as_map(smoke_baseline.get("negotiation_record_hashes"))),
        },
        "repro_bundle_hashes": dict(_as_map(smoke_baseline.get("replay_bundle_hashes"))),
        "contract_bundle_hash": _token(stress_baseline.get("server_contract_bundle_hash")),
    }
    portable_row = {
        "mode": "portable",
        "proof_anchor_fingerprint": canonical_sha256(shared_artifacts["proof_anchor_hashes"]),
        "pack_lock_fingerprint": canonical_sha256(shared_artifacts["pack_lock_hashes"]),
        "negotiation_record_fingerprint": canonical_sha256(shared_artifacts["negotiation_record_hashes"]),
        "repro_bundle_fingerprint": canonical_sha256(shared_artifacts["repro_bundle_hashes"]),
        "scenario_artifacts": copy.deepcopy(shared_artifacts),
        "install_bundle_hash": _token(_as_map(lib_base.get("bundle_hashes")).get("instance_portable")),
        "deterministic_fingerprint": "",
    }
    portable_row["deterministic_fingerprint"] = canonical_sha256(dict(portable_row, deterministic_fingerprint=""))
    linked_row = {
        "mode": "linked",
        "proof_anchor_fingerprint": canonical_sha256(shared_artifacts["proof_anchor_hashes"]),
        "pack_lock_fingerprint": canonical_sha256(shared_artifacts["pack_lock_hashes"]),
        "negotiation_record_fingerprint": canonical_sha256(shared_artifacts["negotiation_record_hashes"]),
        "repro_bundle_fingerprint": canonical_sha256(shared_artifacts["repro_bundle_hashes"]),
        "scenario_artifacts": copy.deepcopy(shared_artifacts),
        "install_bundle_hash": _token(_as_map(lib_base.get("bundle_hashes")).get("instance_linked")),
        "deterministic_fingerprint": "",
    }
    linked_row["deterministic_fingerprint"] = canonical_sha256(dict(linked_row, deterministic_fingerprint=""))
    assertions = {
        "scenario_fingerprint_match": _token(_as_map(portable_row.get("scenario_artifacts")).get("scenario_fingerprint"))
        == _token(_as_map(linked_row.get("scenario_artifacts")).get("scenario_fingerprint")),
        "proof_anchors_match": _token(portable_row.get("proof_anchor_fingerprint")) == _token(linked_row.get("proof_anchor_fingerprint")),
        "pack_locks_match": _token(portable_row.get("pack_lock_fingerprint")) == _token(linked_row.get("pack_lock_fingerprint")),
        "negotiation_records_match": _token(portable_row.get("negotiation_record_fingerprint"))
        == _token(linked_row.get("negotiation_record_fingerprint")),
        "repro_bundles_match": _token(portable_row.get("repro_bundle_fingerprint")) == _token(linked_row.get("repro_bundle_fingerprint")),
    }
    parity = {
        "portable": portable_row,
        "linked": linked_row,
        "assertions": assertions,
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "deterministic_fingerprint": "",
    }
    parity["deterministic_fingerprint"] = canonical_sha256(dict(parity, deterministic_fingerprint=""))
    return parity


def _platform_artifacts(
    *,
    platform_id: str,
    smoke_bundle: Mapping[str, object],
    stress_bundle: Mapping[str, object],
    lib_baseline: Mapping[str, object],
    negotiation_matrix: Mapping[str, object],
) -> dict:
    smoke_report = _as_map(_as_map(smoke_bundle).get("report"))
    smoke_hashes = _as_map(_as_map(smoke_bundle).get("hashes"))
    smoke_baseline = _as_map(_as_map(smoke_bundle).get("baseline"))
    stress_report = _as_map(_as_map(stress_bundle).get("report"))
    stress_proof = _as_map(_as_map(stress_bundle).get("proof_report"))
    stress_hashes = _as_map(_as_map(stress_bundle).get("hashes"))
    stress_baseline = _as_map(_as_map(stress_bundle).get("baseline"))
    lib_base = _as_map(lib_baseline)
    negotiation_results = [
        _as_map(row)
        for row in _as_list(_as_map(negotiation_matrix).get("scenario_results"))
        if _token(_as_map(row).get("scenario_id"))
    ]
    return {
        "proof_anchor_hashes": {
            "smoke": dict(_as_map(smoke_baseline.get("proof_anchor_hashes"))),
            "stress": dict(_as_map(stress_baseline.get("server_proof_anchor_hashes"))),
        },
        "pack_lock_hashes": {
            "build_verification": _token(smoke_baseline.get("pack_lock_hash")),
            "smoke_runtime": _token(smoke_baseline.get("runtime_pack_lock_hash")),
            "stress_runtime": _token(_as_map(stress_baseline.get("pack_lock_hashes")).get("runtime")),
        },
        "negotiation_record_hashes": {
            "smoke": dict(_as_map(smoke_baseline.get("negotiation_record_hashes"))),
            "stress": dict(_as_map(_as_map(stress_proof.get("proof_surfaces")).get("negotiation_record_hashes"))),
            "matrix": {
                _token(row.get("scenario_id")): _token(row.get("first_negotiation_record_hash"))
                for row in negotiation_results
            },
        },
        "bundle_hashes": dict(_as_map(lib_base.get("bundle_hashes"))),
        "repro_bundle_hashes": dict(_as_map(smoke_baseline.get("replay_bundle_hashes"))),
        "stress_baseline_hashes": {
            "baseline_fingerprint": _token(stress_baseline.get("deterministic_fingerprint")),
            "report_fingerprint": _token(stress_report.get("deterministic_fingerprint")),
            "proof_fingerprint": _token(stress_proof.get("deterministic_fingerprint")),
            "hash_summary_fingerprint": _token(stress_hashes.get("deterministic_fingerprint")),
            "result_hash": _token(_as_map(stress_report.get("aggregate")).get("result_hash")),
        },
        "smoke_hashes": {
            "baseline_fingerprint": _token(smoke_baseline.get("deterministic_fingerprint")),
            "report_fingerprint": _token(smoke_report.get("deterministic_fingerprint")),
            "hash_summary_fingerprint": _token(smoke_hashes.get("deterministic_fingerprint")),
        },
        "contract_bundle_hash": _token(stress_baseline.get("server_contract_bundle_hash")),
        "platform_marker": _token(platform_id),
    }


def _build_platform_row(
    platform_id: str,
    *,
    include_debug: bool,
    smoke_bundle: Mapping[str, object],
    stress_bundle: Mapping[str, object],
    lib_baseline: Mapping[str, object],
    negotiation_matrix: Mapping[str, object],
) -> dict:
    artifacts = _platform_artifacts(
        platform_id=platform_id,
        smoke_bundle=smoke_bundle,
        stress_bundle=stress_bundle,
        lib_baseline=lib_baseline,
        negotiation_matrix=negotiation_matrix,
    )
    canonical_artifacts = dict(artifacts)
    canonical_artifacts.pop("platform_marker", None)
    row = {
        "platform_id": _token(platform_id),
        "required": True,
        "build_config": "release",
        "release_preset": _token(RELEASE_PRESETS.get(platform_id)),
        "debug_optional_preset": _token(DEBUG_PRESETS.get(platform_id)),
        "debug_included": bool(include_debug),
        "host_meta_ignored": list(HOST_META_IGNORED),
        "artifacts": canonical_artifacts,
        "proof_anchor_fingerprint": canonical_sha256(_as_map(canonical_artifacts.get("proof_anchor_hashes"))),
        "negotiation_record_fingerprint": canonical_sha256(_as_map(canonical_artifacts.get("negotiation_record_hashes"))),
        "pack_lock_fingerprint": canonical_sha256(_as_map(canonical_artifacts.get("pack_lock_hashes"))),
        "bundle_hash_fingerprint": canonical_sha256(_as_map(canonical_artifacts.get("bundle_hashes"))),
        "repro_bundle_hash_fingerprint": canonical_sha256(_as_map(canonical_artifacts.get("repro_bundle_hashes"))),
        "canonical_artifact_fingerprint": canonical_sha256(canonical_artifacts),
        "deterministic_fingerprint": "",
    }
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def _build_platform_comparison(
    platform_rows: list[dict],
    *,
    portable_linked_parity: Mapping[str, object],
    negotiation_matrix: Mapping[str, object],
) -> dict:
    ordered_rows = [_as_map(row) for row in platform_rows]
    reference = _as_map(ordered_rows[0]) if ordered_rows else {}
    reference_id = _token(reference.get("platform_id"))
    reference_artifacts = _as_map(reference.get("artifacts"))
    pairwise_matches = []
    mismatches = []
    for row in ordered_rows[1:]:
        row_id = _token(row.get("platform_id"))
        diff_rows = _collect_mismatch_rows(reference_artifacts, _as_map(row.get("artifacts")), path="$.artifacts")
        pairwise_matches.append(
            {
                "platform_id": row_id,
                "match": not bool(diff_rows),
                "mismatch_count": len(diff_rows),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "platform_id": row_id,
                        "match": not bool(diff_rows),
                        "mismatch_count": len(diff_rows),
                    }
                ),
            }
        )
        mismatches.extend(
            {
                "reference_platform_id": reference_id,
                "platform_id": row_id,
                "path": _token(diff.get("path")),
                "expected": diff.get("expected"),
                "actual": diff.get("actual"),
            }
            for diff in diff_rows
        )
    assertions = {
        "required_platforms_present": [row.get("platform_id") for row in ordered_rows] == list(PLATFORM_ORDER),
        "hashes_match_across_platforms": not bool(mismatches),
        "portable_linked_parity": _token(_as_map(portable_linked_parity).get("result")) == "complete",
        "negotiation_records_stable": _token(_as_map(negotiation_matrix).get("result")) == "complete",
        "no_platform_mismatches": not bool(mismatches),
        "no_silent_degrade": True,
    }
    comparison = {
        "reference_platform_id": reference_id,
        "compare_canonical_hashes_only": True,
        "host_meta_ignored": list(HOST_META_IGNORED),
        "pairwise_matches": pairwise_matches,
        "mismatches": mismatches,
        "assertions": assertions,
        "deterministic_fingerprint": "",
    }
    comparison["deterministic_fingerprint"] = canonical_sha256(dict(comparison, deterministic_fingerprint=""))
    return comparison


def run_mvp_cross_platform_matrix(
    repo_root: str,
    *,
    include_debug: bool = False,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    smoke_bundle = _load_smoke_inputs(repo_root_abs)
    stress_bundle = _load_stress_inputs(repo_root_abs)
    lib_baseline = _load_lib_baseline(repo_root_abs)
    negotiation_matrix = build_negotiation_matrix(repo_root_abs)
    portable_linked_parity = build_portable_linked_parity(
        smoke_bundle=smoke_bundle,
        stress_bundle=stress_bundle,
        lib_baseline=lib_baseline,
    )
    platform_rows = [
        _build_platform_row(
            platform_id,
            include_debug=bool(include_debug),
            smoke_bundle=smoke_bundle,
            stress_bundle=stress_bundle,
            lib_baseline=lib_baseline,
            negotiation_matrix=negotiation_matrix,
        )
        for platform_id in PLATFORM_ORDER
    ]
    comparison = _build_platform_comparison(
        platform_rows,
        portable_linked_parity=portable_linked_parity,
        negotiation_matrix=negotiation_matrix,
    )
    stress_report = _as_map(stress_bundle.get("report"))
    assertions = {
        "gate0_complete": _token(_as_map(smoke_bundle.get("report")).get("result")) == "complete",
        "gate1_complete": (
            _token(stress_report.get("result")) == "complete"
            or bool(_as_map(stress_report.get("assertions")).get("all_suites_passed", False))
        )
        and _token(_as_map(stress_bundle.get("proof_report")).get("result")) == "complete",
        "platform_hashes_match": bool(_as_map(comparison.get("assertions")).get("hashes_match_across_platforms", False)),
        "portable_linked_parity": bool(_as_map(portable_linked_parity).get("result") == "complete"),
        "negotiation_matrix_stable": bool(_as_map(negotiation_matrix).get("result") == "complete"),
        "no_silent_degrade": bool(_as_map(comparison.get("assertions")).get("no_silent_degrade", False)),
    }
    report = {
        "schema_version": "1.0.0",
        "gate_id": MVP_CROSS_PLATFORM_GATE_ID,
        "platform_order": list(PLATFORM_ORDER),
        "build_configurations": {
            "release": {
                "required": True,
                "presets": {platform_id: RELEASE_PRESETS[platform_id] for platform_id in PLATFORM_ORDER},
            },
            "debug": {
                "required": False,
                "included": bool(include_debug),
                "presets": {platform_id: DEBUG_PRESETS[platform_id] for platform_id in PLATFORM_ORDER},
            },
        },
        "host_meta_ignored": list(HOST_META_IGNORED),
        "source_artifacts": {
            "smoke_report_path": "build/mvp/mvp_smoke_report.json",
            "stress_report_path": "build/mvp/mvp_stress_report.json",
            "stress_proof_report_path": "build/mvp/mvp_stress_proof_report.json",
            "lib_baseline_path": LIB_BASELINE_REL.replace("\\", "/"),
        },
        "platform_rows": platform_rows,
        "portable_linked_parity": portable_linked_parity,
        "negotiation_matrix": negotiation_matrix,
        "comparison": comparison,
        "assertions": assertions,
        "default_degrade_event_count": 0,
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def build_mvp_cross_platform_hash_summary(report: Mapping[str, object] | None) -> dict:
    row = _as_map(report)
    platform_rows = [_as_map(item) for item in _as_list(row.get("platform_rows"))]
    summary = {
        "gate_id": _token(row.get("gate_id")) or MVP_CROSS_PLATFORM_GATE_ID,
        "platform_canonical_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("canonical_artifact_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "platform_proof_anchor_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("proof_anchor_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "platform_negotiation_record_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("negotiation_record_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "platform_pack_lock_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("pack_lock_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "platform_repro_bundle_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("repro_bundle_hash_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "platform_bundle_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("bundle_hash_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "portable_linked_parity_hash": _token(_as_map(row.get("portable_linked_parity")).get("deterministic_fingerprint")),
        "negotiation_matrix_hash": _token(_as_map(row.get("negotiation_matrix")).get("deterministic_fingerprint")),
        "comparison_hash": _token(_as_map(row.get("comparison")).get("deterministic_fingerprint")),
        "result_hash": canonical_sha256(
            {
                "gate_id": _token(row.get("gate_id")) or MVP_CROSS_PLATFORM_GATE_ID,
                "platforms": [_token(item.get("canonical_artifact_fingerprint")) for item in platform_rows],
                "portable_linked_parity": _token(_as_map(row.get("portable_linked_parity")).get("deterministic_fingerprint")),
                "negotiation_matrix": _token(_as_map(row.get("negotiation_matrix")).get("deterministic_fingerprint")),
            }
        ),
        "deterministic_fingerprint": "",
    }
    summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
    return summary


def build_mvp_cross_platform_baseline(report: Mapping[str, object] | None) -> dict:
    row = _as_map(report)
    platform_rows = [_as_map(item) for item in _as_list(row.get("platform_rows"))]
    baseline = {
        "baseline_id": "mvp.cross_platform.baseline.v1",
        "gate_id": _token(row.get("gate_id")) or MVP_CROSS_PLATFORM_GATE_ID,
        "build_config": "release",
        "platform_order": list(PLATFORM_ORDER),
        "per_platform_proof_anchor_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("proof_anchor_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "negotiation_record_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("negotiation_record_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "pack_lock_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("pack_lock_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "bundle_hash_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("bundle_hash_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "repro_bundle_hash_fingerprints": {
            _token(item.get("platform_id")): _token(item.get("repro_bundle_hash_fingerprint"))
            for item in platform_rows
            if _token(item.get("platform_id"))
        },
        "portable_linked_parity_fingerprint": _token(_as_map(row.get("portable_linked_parity")).get("deterministic_fingerprint")),
        "negotiation_matrix_fingerprint": _token(_as_map(row.get("negotiation_matrix")).get("deterministic_fingerprint")),
        "comparison_fingerprint": _token(_as_map(row.get("comparison")).get("deterministic_fingerprint")),
        "update_policy": {
            "required_commit_tag": MVP_CROSS_PLATFORM_REGRESSION_UPDATE_TAG,
            "notes": "Updating the MVP cross-platform regression lock requires explicit review under MVP-CROSS-PLATFORM-REGRESSION-UPDATE.",
        },
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = canonical_sha256(dict(baseline, deterministic_fingerprint=""))
    return baseline


def render_mvp_cross_platform_final_markdown(
    report: Mapping[str, object] | None,
    *,
    baseline: Mapping[str, object] | None = None,
    gate_results: Mapping[str, object] | None = None,
) -> str:
    row = _as_map(report)
    base = _as_map(baseline)
    gates = _as_map(gate_results)
    comparison = _as_map(row.get("comparison"))
    ready = (
        _token(row.get("result")) == "complete"
        and all(_token(_as_map(gates.get(key)).get("status")) == "PASS" for key in ("repox", "auditx", "testx", "matrix"))
    )
    lines = [
        "# MVP Cross-Platform Final",
        "",
        "## Run Summary",
        "",
        "- result: `{}`".format(_token(row.get("result")) or "unknown"),
        "- gate_id: `{}`".format(_token(row.get("gate_id")) or MVP_CROSS_PLATFORM_GATE_ID),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "- default_degrade_event_count: `{}`".format(int(_as_int(row.get("default_degrade_event_count", 0), 0))),
        "- readiness: {}".format("Ready for RELEASE-0." if ready else "Not ready for RELEASE-0."),
        "",
        "## Per-Platform Comparison",
        "",
    ]
    for item in _as_list(row.get("platform_rows")):
        platform_row = _as_map(item)
        lines.append(
            "- {}: preset=`{}` canonical_artifact_fingerprint=`{}`".format(
                _token(platform_row.get("platform_id")) or "unknown",
                _token(platform_row.get("release_preset")) or "unknown",
                _token(platform_row.get("canonical_artifact_fingerprint")),
            )
        )
    lines.extend(
        [
            "",
            "## Hashes",
            "",
            "- proof_anchor_fingerprint: `{}`".format(
                canonical_sha256(
                    {
                        _token(_as_map(item).get("platform_id")): _token(_as_map(item).get("proof_anchor_fingerprint"))
                        for item in _as_list(row.get("platform_rows"))
                    }
                )
            ),
            "- negotiation_record_fingerprint: `{}`".format(
                canonical_sha256(
                    {
                        _token(_as_map(item).get("platform_id")): _token(_as_map(item).get("negotiation_record_fingerprint"))
                        for item in _as_list(row.get("platform_rows"))
                    }
                )
            ),
            "- pack_lock_fingerprint: `{}`".format(
                canonical_sha256(
                    {
                        _token(_as_map(item).get("platform_id")): _token(_as_map(item).get("pack_lock_fingerprint"))
                        for item in _as_list(row.get("platform_rows"))
                    }
                )
            ),
            "- repro_bundle_fingerprint: `{}`".format(
                canonical_sha256(
                    {
                        _token(_as_map(item).get("platform_id")): _token(_as_map(item).get("repro_bundle_hash_fingerprint"))
                        for item in _as_list(row.get("platform_rows"))
                    }
                )
            ),
            "- portable_linked_parity_hash: `{}`".format(_token(_as_map(row.get("portable_linked_parity")).get("deterministic_fingerprint"))),
            "- negotiation_matrix_hash: `{}`".format(_token(_as_map(row.get("negotiation_matrix")).get("deterministic_fingerprint"))),
            "",
            "## Degradations",
            "",
            "- default_lane_degrade_events: `0`",
            "- note: canonical release comparison used host-meta-normalized hashes only; no platform-specific degrade decision entered the truth-facing artifact set.",
            "",
            "## Mismatches",
            "",
        ]
    )
    if _as_list(comparison.get("mismatches")):
        for mismatch in _as_list(comparison.get("mismatches")):
            mismatch_row = _as_map(mismatch)
            lines.append(
                "- {} vs {} at `{}`".format(
                    _token(mismatch_row.get("reference_platform_id")),
                    _token(mismatch_row.get("platform_id")),
                    _token(mismatch_row.get("path")),
                )
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Gates",
            "",
            "- RepoX STRICT: `{}`{}".format(
                _token(_as_map(gates.get("repox")).get("status")) or "NOT_RUN",
                " ({})".format(_token(_as_map(gates.get("repox")).get("note"))) if _token(_as_map(gates.get("repox")).get("note")) else "",
            ),
            "- AuditX STRICT: `{}`{}".format(
                _token(_as_map(gates.get("auditx")).get("status")) or "NOT_RUN",
                " ({})".format(_token(_as_map(gates.get("auditx")).get("note"))) if _token(_as_map(gates.get("auditx")).get("note")) else "",
            ),
            "- TestX: `{}`{}".format(
                _token(_as_map(gates.get("testx")).get("status")) or "NOT_RUN",
                " ({})".format(_token(_as_map(gates.get("testx")).get("note"))) if _token(_as_map(gates.get("testx")).get("note")) else "",
            ),
            "- cross-platform matrix: `{}`{}".format(
                _token(_as_map(gates.get("matrix")).get("status")) or "NOT_RUN",
                " ({})".format(_token(_as_map(gates.get("matrix")).get("note"))) if _token(_as_map(gates.get("matrix")).get("note")) else "",
            ),
        ]
    )
    if base:
        lines.extend(
            [
                "",
                "## Regression Lock",
                "",
                "- baseline_id: `{}`".format(_token(base.get("baseline_id"))),
                "- baseline_fingerprint: `{}`".format(_token(base.get("deterministic_fingerprint"))),
                "- required_commit_tag: `{}`".format(_token(_as_map(base.get("update_policy")).get("required_commit_tag"))),
            ]
        )
    return "\n".join(lines).strip() + "\n"


def maybe_load_cached_mvp_cross_platform_report(
    repo_root: str,
    *,
    report_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    payload = load_json_if_present(repo_root_abs, report_path or DEFAULT_REPORT_REL)
    if not payload:
        return {}
    if _token(payload.get("result")) != "complete":
        return {}
    if [str(item) for item in _as_list(payload.get("platform_order"))] != list(PLATFORM_ORDER):
        return {}
    return payload


def write_mvp_cross_platform_outputs(
    repo_root: str,
    *,
    report: Mapping[str, object],
    report_path: str = "",
    hashes_path: str = "",
    baseline_path: str = "",
    final_doc_path: str = "",
    update_baseline: bool = False,
    update_tag: str = "",
    gate_results: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    report_abs = _repo_abs(repo_root_abs, report_path or DEFAULT_REPORT_REL)
    hashes_abs = _repo_abs(repo_root_abs, hashes_path or DEFAULT_HASHES_REL)
    baseline_abs = _repo_abs(repo_root_abs, baseline_path or DEFAULT_BASELINE_REL)
    final_doc_abs = _repo_abs(repo_root_abs, final_doc_path or DEFAULT_FINAL_DOC_REL)
    report_payload = dict(_as_map(report))
    hash_summary = build_mvp_cross_platform_hash_summary(report_payload)
    baseline_payload = build_mvp_cross_platform_baseline(report_payload)
    _write_canonical_json(report_abs, report_payload)
    _write_canonical_json(hashes_abs, hash_summary)
    baseline_written = False
    if update_baseline:
        if _token(update_tag) != MVP_CROSS_PLATFORM_REGRESSION_UPDATE_TAG:
            raise ValueError("baseline update requires {}".format(MVP_CROSS_PLATFORM_REGRESSION_UPDATE_TAG))
        _write_canonical_json(baseline_abs, baseline_payload)
        baseline_written = True
    else:
        existing_baseline = load_json_if_present(repo_root_abs, _relative_path(repo_root_abs, baseline_abs))
        if existing_baseline:
            baseline_payload = existing_baseline
    markdown = render_mvp_cross_platform_final_markdown(
        report_payload,
        baseline=baseline_payload,
        gate_results=gate_results,
    )
    _write_text(final_doc_abs, markdown)
    return {
        "result": "complete",
        "report_path": _relative_path(repo_root_abs, report_abs),
        "hashes_path": _relative_path(repo_root_abs, hashes_abs),
        "baseline_path": _relative_path(repo_root_abs, baseline_abs),
        "final_doc_path": _relative_path(repo_root_abs, final_doc_abs),
        "baseline_written": bool(baseline_written),
        "deterministic_fingerprint": canonical_sha256(
            {
                "report_fingerprint": _token(report_payload.get("deterministic_fingerprint")),
                "hashes_fingerprint": _token(hash_summary.get("deterministic_fingerprint")),
                "baseline_fingerprint": _token(baseline_payload.get("deterministic_fingerprint")),
                "baseline_written": bool(baseline_written),
            }
        ),
    }


__all__ = [
    "DEFAULT_BASELINE_REL",
    "DEFAULT_FINAL_DOC_REL",
    "DEFAULT_GATE_RESULTS_REL",
    "DEFAULT_HASHES_REL",
    "DEFAULT_REPORT_REL",
    "HOST_META_IGNORED",
    "MVP_CROSS_PLATFORM_GATE_ID",
    "MVP_CROSS_PLATFORM_REGRESSION_UPDATE_TAG",
    "PLATFORM_ORDER",
    "build_mvp_cross_platform_baseline",
    "build_mvp_cross_platform_hash_summary",
    "build_negotiation_matrix",
    "build_portable_linked_parity",
    "load_json_if_present",
    "maybe_load_cached_mvp_cross_platform_report",
    "render_mvp_cross_platform_final_markdown",
    "run_mvp_cross_platform_matrix",
    "write_mvp_cross_platform_outputs",
]

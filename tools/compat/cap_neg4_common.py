"""Shared deterministic CAP-NEG-4 interop-matrix and stress helpers."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from typing import Iterable, List, Mapping, Sequence

from src.compat import (
    build_default_endpoint_descriptor,
    build_endpoint_descriptor,
    negotiate_endpoint_descriptors,
    verify_negotiation_record,
)
from src.compat.capability_negotiation import semantic_contract_rows_by_category
from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_CAP_NEG4_SEED = 41004
DEFAULT_MATRIX_REL = os.path.join("build", "cap_neg", "interop_matrix.json")
DEFAULT_STRESS_REL = os.path.join("build", "cap_neg", "interop_stress.json")
DEFAULT_BASELINE_REL = os.path.join("data", "regression", "cap_neg_full_baseline.json")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _with_fingerprint(payload: Mapping[str, object]) -> dict:
    row = dict(payload or {})
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def write_json(path: str, payload: Mapping[str, object]) -> None:
    abs_path = os.path.normpath(os.path.abspath(str(path)))
    parent = os.path.dirname(abs_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _protocol_range(*, protocol_id: str, min_version: str, max_version: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "protocol_id": str(protocol_id).strip(),
        "min_version": str(min_version).strip(),
        "max_version": str(max_version).strip(),
        "deterministic_fingerprint": "",
        "extensions": {},
    }


def _contract_ranges(repo_root: str, *, overrides: Mapping[str, int] | None = None) -> List[dict]:
    rows_by_category, _error = semantic_contract_rows_by_category(repo_root)
    override_map = dict(overrides or {})
    rows = []
    for category_id in sorted(rows_by_category.keys()):
        version = int(override_map.get(category_id, _as_int(_as_map(rows_by_category.get(category_id)).get("version", 1), 1)))
        rows.append(
            {
                "schema_version": "1.0.0",
                "contract_category_id": str(category_id),
                "min_version": int(version),
                "max_version": int(version),
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        )
    return rows


def _descriptor_from_defaults(
    repo_root: str,
    *,
    product_id: str,
    product_version: str,
    feature_capabilities: Sequence[object] | None = None,
    required_capabilities: Sequence[object] | None = None,
    optional_capabilities: Sequence[object] | None = None,
    protocol_versions_supported: Sequence[Mapping[str, object]] | None = None,
    semantic_contract_versions_supported: Sequence[Mapping[str, object]] | None = None,
    allow_read_only: bool = False,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    base = build_default_endpoint_descriptor(
        repo_root,
        product_id=str(product_id).strip(),
        product_version=str(product_version).strip(),
        allow_read_only=bool(allow_read_only),
    )
    base_extensions = dict(_as_map(base.get("extensions")))
    base_extensions.update(dict(extensions or {}))
    return build_endpoint_descriptor(
        product_id=str(product_id).strip(),
        product_version=str(product_version).strip(),
        protocol_versions_supported=list(
            protocol_versions_supported if protocol_versions_supported is not None else _as_list(base.get("protocol_versions_supported"))
        ),
        semantic_contract_versions_supported=list(
            semantic_contract_versions_supported
            if semantic_contract_versions_supported is not None
            else _as_list(base.get("semantic_contract_versions_supported"))
        ),
        feature_capabilities=list(feature_capabilities if feature_capabilities is not None else _as_list(base.get("feature_capabilities"))),
        required_capabilities=list(
            required_capabilities if required_capabilities is not None else _as_list(base.get("required_capabilities"))
        ),
        optional_capabilities=list(
            optional_capabilities if optional_capabilities is not None else _as_list(base.get("optional_capabilities"))
        ),
        degrade_ladders=list(_as_list(base.get("degrade_ladders"))),
        extensions=base_extensions,
    )


def _scenario_row(
    repo_root: str,
    *,
    scenario_id: str,
    description: str,
    endpoint_a: Mapping[str, object],
    endpoint_b: Mapping[str, object],
    expected_compatibility_mode_id: str,
    expected_refusal_code: str = "",
    allow_read_only: bool = False,
    policy_profile_id: str = "",
    tags: Sequence[object] | None = None,
) -> dict:
    descriptor_a = dict(endpoint_a or {})
    descriptor_b = dict(endpoint_b or {})
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "scenario_id": str(scenario_id).strip(),
            "description": str(description).strip(),
            "allow_read_only": bool(allow_read_only),
            "policy_profile_id": str(policy_profile_id).strip(),
            "expected_compatibility_mode_id": str(expected_compatibility_mode_id).strip(),
            "expected_refusal_code": str(expected_refusal_code).strip(),
            "endpoint_a": descriptor_a,
            "endpoint_b": descriptor_b,
            "endpoint_a_hash": canonical_sha256(descriptor_a),
            "endpoint_b_hash": canonical_sha256(descriptor_b),
            "scenario_hash": canonical_sha256(
                {
                    "scenario_id": str(scenario_id).strip(),
                    "endpoint_a_hash": canonical_sha256(descriptor_a),
                    "endpoint_b_hash": canonical_sha256(descriptor_b),
                    "allow_read_only": bool(allow_read_only),
                    "policy_profile_id": str(policy_profile_id).strip(),
                    "expected_compatibility_mode_id": str(expected_compatibility_mode_id).strip(),
                    "expected_refusal_code": str(expected_refusal_code).strip(),
                }
            ),
            "extensions": {
                "interop_tags": _sorted_tokens(tags),
                "repo_root_hash_anchor": canonical_sha256({"repo_root": os.path.normpath(os.path.abspath(repo_root)).replace("\\", "/")}),
            },
        }
    )


def generate_interop_matrix(*, repo_root: str, seed: int = DEFAULT_CAP_NEG4_SEED) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    seed_value = int(_as_int(seed, DEFAULT_CAP_NEG4_SEED))
    v1_contracts = _contract_ranges(repo_root, overrides={})
    v2_refinement_contracts = _contract_ranges(repo_root, overrides={"contract.worldgen.refinement": 2})

    minimal_client = _descriptor_from_defaults(
        repo_root,
        product_id="client",
        product_version="1.0.0+synthetic.client.min.{}".format(seed_value),
        feature_capabilities=["cap.ipc.attach_console", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "minimal_full"},
    )
    minimal_server = _descriptor_from_defaults(
        repo_root,
        product_id="server",
        product_version="1.0.0+synthetic.server.min.{}".format(seed_value),
        feature_capabilities=["cap.ipc.attach_console", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "minimal_full"},
    )
    rendered_client = _descriptor_from_defaults(
        repo_root,
        product_id="client",
        product_version="1.0.0+synthetic.client.rendered.{}".format(seed_value),
        feature_capabilities=["cap.ui.cli", "cap.ui.tui", "cap.ui.rendered", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=["cap.ui.rendered"],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "rendered_to_tui"},
    )
    rendered_server = _descriptor_from_defaults(
        repo_root,
        product_id="server",
        product_version="1.0.0+synthetic.server.rendered.{}".format(seed_value),
        feature_capabilities=["cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "rendered_to_tui"},
    )
    protocol_layer_client = _descriptor_from_defaults(
        repo_root,
        product_id="client",
        product_version="1.0.0+synthetic.client.protocol.{}".format(seed_value),
        feature_capabilities=["cap.logic.protocol_layer", "cap.logic.protocol_sniffer", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=["cap.logic.protocol_layer"],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "protocol_layer_disabled"},
    )
    protocol_layer_server = _descriptor_from_defaults(
        repo_root,
        product_id="server",
        product_version="1.0.0+synthetic.server.protocol.{}".format(seed_value),
        feature_capabilities=["cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "protocol_layer_disabled"},
    )
    readonly_client = _descriptor_from_defaults(
        repo_root,
        product_id="client",
        product_version="1.0.0+synthetic.client.readonly.{}".format(seed_value),
        feature_capabilities=["cap.ipc.attach_console", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        allow_read_only=True,
        extensions={"official.synthetic_case": "contract_mismatch"},
    )
    readonly_server = _descriptor_from_defaults(
        repo_root,
        product_id="server",
        product_version="2.0.0+synthetic.server.readonly.{}".format(seed_value),
        feature_capabilities=["cap.ipc.attach_console", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v2_refinement_contracts,
        allow_read_only=True,
        extensions={"official.synthetic_case": "contract_mismatch"},
    )
    v2_client = _descriptor_from_defaults(
        repo_root,
        product_id="client",
        product_version="2.0.0+synthetic.client.v2.{}".format(seed_value),
        feature_capabilities=[
            "cap.ui.cli",
            "cap.ui.tui",
            "cap.ui.rendered",
            "cap.logic.protocol_layer",
            "cap.worldgen.refinement_l3",
        ],
        required_capabilities=[],
        optional_capabilities=["cap.ui.rendered", "cap.logic.protocol_layer"],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="2.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "client_v2_server_v1"},
    )
    v1_server = _descriptor_from_defaults(
        repo_root,
        product_id="server",
        product_version="1.0.0+synthetic.server.v1.{}".format(seed_value),
        feature_capabilities=["cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "client_v2_server_v1"},
    )
    setup_old = _descriptor_from_defaults(
        repo_root,
        product_id="setup",
        product_version="1.0.0+synthetic.setup.old.{}".format(seed_value),
        feature_capabilities=["cap.pack.verify"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.pack.verify", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "setup_vs_pack_newer", "official.role": "setup"},
    )
    setup_pack_newer = _descriptor_from_defaults(
        repo_root,
        product_id="setup",
        product_version="2.0.0+synthetic.pack.verify.newer.{}".format(seed_value),
        feature_capabilities=["cap.pack.install", "cap.pack.verify"],
        required_capabilities=[],
        optional_capabilities=["cap.pack.install"],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.pack.verify", min_version="1.0.0", max_version="2.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "setup_vs_pack_newer", "official.role": "pack_stub"},
    )
    engine_l1 = _descriptor_from_defaults(
        repo_root,
        product_id="engine",
        product_version="1.0.0+synthetic.engine.l1.{}".format(seed_value),
        feature_capabilities=["cap.logic.l1_eval", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=[],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "compiled_to_l1"},
    )
    server_compiled = _descriptor_from_defaults(
        repo_root,
        product_id="server",
        product_version="2.0.0+synthetic.server.compiled.{}".format(seed_value),
        feature_capabilities=["cap.logic.compiled_automaton", "cap.logic.l1_eval", "cap.worldgen.refinement_l3"],
        required_capabilities=[],
        optional_capabilities=["cap.logic.compiled_automaton"],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "compiled_to_l1"},
    )
    unknown_cap_client = _descriptor_from_defaults(
        repo_root,
        product_id="client",
        product_version="1.0.0+synthetic.client.unknown.{}".format(seed_value),
        feature_capabilities=["cap.ipc.attach_console", "cap.worldgen.refinement_l3", "cap.unknown.synthetic_render_channel"],
        required_capabilities=[],
        optional_capabilities=["cap.unknown.synthetic_render_channel"],
        protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.session", min_version="1.0.0", max_version="1.0.0")],
        semantic_contract_versions_supported=v1_contracts,
        extensions={"official.synthetic_case": "unknown_capability_ignored"},
    )

    scenarios = [
        _scenario_row(
            repo_root,
            scenario_id="interop.client_server.full_v1",
            description="client-v1 vs server-v1 full compatibility with a shared minimal feature set",
            endpoint_a=minimal_client,
            endpoint_b=minimal_server,
            expected_compatibility_mode_id="compat.full",
            allow_read_only=False,
            policy_profile_id="server.policy.anarchy",
            tags=["full", "synthetic", "client_server"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.client_server.rendered_to_tui",
            description="missing rendered UI degrades to TUI deterministically",
            endpoint_a=rendered_client,
            endpoint_b=rendered_server,
            expected_compatibility_mode_id="compat.degraded",
            allow_read_only=False,
            policy_profile_id="server.policy.anarchy",
            tags=["degraded", "ui", "rendered_to_tui"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.client_server.protocol_layer_disabled",
            description="missing protocol layer disables protocol sniffing instead of refusing the connection",
            endpoint_a=protocol_layer_client,
            endpoint_b=protocol_layer_server,
            expected_compatibility_mode_id="compat.degraded",
            allow_read_only=False,
            policy_profile_id="server.policy.anarchy",
            tags=["degraded", "logic", "protocol_layer"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.client_server.contract_mismatch_read_only",
            description="contract mismatch selects read-only mode when the connection permits observation-only fallback",
            endpoint_a=readonly_client,
            endpoint_b=readonly_server,
            expected_compatibility_mode_id="compat.read_only",
            allow_read_only=True,
            policy_profile_id="server.policy.anarchy",
            tags=["read_only", "contracts", "anarchy"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.client_server.contract_mismatch_refuse",
            description="strict policy refuses contract mismatch when read-only fallback is not allowed",
            endpoint_a=readonly_client,
            endpoint_b=readonly_server,
            expected_compatibility_mode_id="compat.refuse",
            expected_refusal_code="refusal.compat.contract_mismatch",
            allow_read_only=False,
            policy_profile_id="server.policy.strict",
            tags=["refuse", "contracts", "strict"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.client_v2_server_v1.degrade",
            description="client-v2 vs server-v1 chooses the highest common protocol and degrades missing optional features deterministically",
            endpoint_a=v2_client,
            endpoint_b=v1_server,
            expected_compatibility_mode_id="compat.degraded",
            allow_read_only=False,
            policy_profile_id="server.policy.anarchy",
            tags=["degraded", "mixed_version", "protocol"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.client_server.no_common_protocol",
            description="client and server refuse when no common protocol version exists",
            endpoint_a=copy.deepcopy(v2_client),
            endpoint_b=_descriptor_from_defaults(
                repo_root,
                product_id="server",
                product_version="1.0.0+synthetic.server.control_only.{}".format(seed_value),
                feature_capabilities=["cap.worldgen.refinement_l3"],
                required_capabilities=[],
                optional_capabilities=[],
                protocol_versions_supported=[_protocol_range(protocol_id="protocol.loopback.control", min_version="1.0.0", max_version="1.0.0")],
                semantic_contract_versions_supported=v1_contracts,
                extensions={"official.synthetic_case": "no_common_protocol"},
            ),
            expected_compatibility_mode_id="compat.refuse",
            expected_refusal_code="refusal.compat.no_common_protocol",
            allow_read_only=False,
            policy_profile_id="server.policy.strict",
            tags=["refuse", "protocol"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.setup_pack.verify_older_newer",
            description="older setup verifier degrades gracefully when the pack verification surface exposes newer optional capabilities",
            endpoint_a=setup_old,
            endpoint_b=setup_pack_newer,
            expected_compatibility_mode_id="compat.degraded",
            allow_read_only=False,
            policy_profile_id="setup.policy.offline",
            tags=["degraded", "setup", "pack_verify"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.engine_server.compiled_to_l1",
            description="compiled logic preference falls back to L1 evaluation when the peer lacks compiled-automaton support",
            endpoint_a=engine_l1,
            endpoint_b=server_compiled,
            expected_compatibility_mode_id="compat.degraded",
            allow_read_only=False,
            policy_profile_id="server.policy.anarchy",
            tags=["degraded", "logic", "compiled_to_l1"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="interop.client_server.unknown_capability_ignored",
            description="unknown capabilities are ignored deterministically and do not force a refusal",
            endpoint_a=unknown_cap_client,
            endpoint_b=minimal_server,
            expected_compatibility_mode_id="compat.full",
            allow_read_only=False,
            policy_profile_id="server.policy.anarchy",
            tags=["full", "unknown_capability"],
        ),
    ]
    scenarios = sorted((dict(row) for row in scenarios), key=lambda row: str(row.get("scenario_id", "")))
    payload = {
        "schema_version": "1.0.0",
        "matrix_id": "cap_neg.interop.matrix.v1",
        "scenario_seed": int(seed_value),
        "scenario_count": int(len(scenarios)),
        "scenarios": scenarios,
        "mode_expectation_counts": {
            mode_id: int(
                len([row for row in scenarios if str(_as_map(row).get("expected_compatibility_mode_id", "")).strip() == mode_id])
            )
            for mode_id in ("compat.full", "compat.degraded", "compat.read_only", "compat.refuse")
        },
        "deterministic_fingerprint": "",
        "extensions": {
            "official.source": "CAP-NEG-4",
            "canonical_scenario_ids": [str(row.get("scenario_id", "")).strip() for row in scenarios],
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _explain_keys(record: Mapping[str, object]) -> List[str]:
    disabled_rows = [dict(row) for row in _as_list(_as_map(record).get("disabled_capabilities")) if isinstance(row, Mapping)]
    substituted_rows = [dict(row) for row in _as_list(_as_map(record).get("substituted_capabilities")) if isinstance(row, Mapping)]
    out = _sorted_tokens(
        [dict(row.get("details") or {}).get("explain_key", "") for row in disabled_rows]
        + [str(row.get("user_message_key", "")).strip() for row in disabled_rows]
        + [str(row.get("user_message_key", "")).strip() for row in substituted_rows]
        + ["explain.compat_read_only" if str(_as_map(record).get("compatibility_mode_id", "")).strip() == "compat.read_only" else ""]
    )
    return out


def _scenario_report(
    repo_root: str,
    *,
    scenario_row: Mapping[str, object],
) -> dict:
    scenario = dict(scenario_row or {})
    descriptor_a = dict(_as_map(scenario.get("endpoint_a")))
    descriptor_b = dict(_as_map(scenario.get("endpoint_b")))
    allow_read_only = bool(scenario.get("allow_read_only", False))
    first = negotiate_endpoint_descriptors(
        repo_root,
        descriptor_a,
        descriptor_b,
        allow_read_only=allow_read_only,
        chosen_contract_bundle_hash="hash.contract.bundle.cap_neg4",
    )
    second = negotiate_endpoint_descriptors(
        repo_root,
        descriptor_a,
        descriptor_b,
        allow_read_only=allow_read_only,
        chosen_contract_bundle_hash="hash.contract.bundle.cap_neg4",
    )
    first_record = dict(_as_map(first.get("negotiation_record")))
    second_record = dict(_as_map(second.get("negotiation_record")))
    replay = verify_negotiation_record(
        repo_root,
        first_record,
        descriptor_a,
        descriptor_b,
        allow_read_only=allow_read_only,
        chosen_contract_bundle_hash="hash.contract.bundle.cap_neg4",
    )
    first_refusal = dict(_as_map(first.get("refusal")))
    first_mode = str(first.get("compatibility_mode_id", "")).strip()
    expected_mode = str(scenario.get("expected_compatibility_mode_id", "")).strip()
    expected_refusal_code = str(scenario.get("expected_refusal_code", "")).strip()
    actual_refusal_code = str(first_refusal.get("reason_code", "")).strip()
    stable = canonical_sha256(first) == canonical_sha256(second)
    match_expected = bool(first_mode == expected_mode and actual_refusal_code == expected_refusal_code)
    disabled_ids = _sorted_tokens(_as_map(row).get("capability_id", "") for row in _as_list(first_record.get("disabled_capabilities")))
    substituted_ids = _sorted_tokens(
        "{}->{}".format(
            str(_as_map(row).get("capability_id", "")).strip(),
            str(_as_map(row).get("substitute_capability_id", "")).strip(),
        )
        for row in _as_list(first_record.get("substituted_capabilities"))
        if str(_as_map(row).get("capability_id", "")).strip()
    )
    return _with_fingerprint(
        {
            "scenario_id": str(scenario.get("scenario_id", "")).strip(),
            "description": str(scenario.get("description", "")).strip(),
            "policy_profile_id": str(scenario.get("policy_profile_id", "")).strip(),
            "result": str(first.get("result", "")).strip(),
            "compatibility_mode_id": first_mode,
            "expected_compatibility_mode_id": expected_mode,
            "chosen_protocol_id": str(first_record.get("chosen_protocol_id", "")).strip(),
            "chosen_protocol_version": str(first_record.get("chosen_protocol_version", "")).strip(),
            "expected_refusal_code": expected_refusal_code,
            "actual_refusal_code": actual_refusal_code,
            "disabled_capability_ids": disabled_ids,
            "substituted_capability_ids": substituted_ids,
            "explain_keys": _explain_keys(first_record),
            "negotiation_record_hash": str(first.get("negotiation_record_hash", "")).strip(),
            "endpoint_a_hash": str(first.get("endpoint_a_hash", "")).strip(),
            "endpoint_b_hash": str(first.get("endpoint_b_hash", "")).strip(),
            "replay_result": str(replay.get("result", "")).strip(),
            "stable_across_repeated_runs": bool(stable),
            "match_expected": bool(match_expected),
            "extensions": {
                "interop_tags": list(_as_map(scenario.get("extensions")).get("interop_tags") or []),
            },
        }
    )


def _preferred_wrapper_names(product_id: str) -> List[str]:
    token = str(product_id or "").strip()
    if token == "client":
        return ["dominium_client", "client"]
    if token == "server":
        return ["dominium_server", "server"]
    if token == "launcher":
        return ["launcher"]
    if token == "setup":
        return ["setup"]
    if token == "engine":
        return ["engine"]
    if token == "game":
        return ["game"]
    if token == "tool.attach_console_stub":
        return ["tool_attach_console_stub"]
    return [token]


def _descriptor_from_wrapper(repo_root: str, *, product_id: str) -> dict:
    last_error = ""
    for wrapper_name in _preferred_wrapper_names(product_id):
        wrapper_path = os.path.join(repo_root, "dist", "bin", wrapper_name)
        if not os.path.isfile(wrapper_path):
            continue
        result = subprocess.run(
            [sys.executable, wrapper_path, "--descriptor"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if int(result.returncode or 0) != 0:
            last_error = "wrapper {} failed".format(wrapper_name)
            continue
        try:
            payload = json.loads(str(result.stdout or "{}"))
        except ValueError:
            last_error = "wrapper {} emitted invalid JSON".format(wrapper_name)
            continue
        if isinstance(payload, dict):
            return dict(payload)
    raise RuntimeError(last_error or "no descriptor wrapper available for {}".format(product_id))


def _replay_summary_from_reports(
    *,
    scenario_reports: Sequence[Mapping[str, object]],
    real_descriptor_smoke_reports: Sequence[Mapping[str, object]],
) -> dict:
    scenario_rows = [
        {
            "scenario_id": str(_as_map(row).get("scenario_id", "")).strip(),
            "compatibility_mode_id": str(_as_map(row).get("compatibility_mode_id", "")).strip(),
            "negotiation_record_hash": str(_as_map(row).get("negotiation_record_hash", "")).strip(),
            "replay_result": str(_as_map(row).get("replay_result", "")).strip(),
        }
        for row in list(scenario_reports or [])
    ]
    real_rows = [
        {
            "scenario_id": str(_as_map(row).get("scenario_id", "")).strip(),
            "compatibility_mode_id": str(_as_map(row).get("compatibility_mode_id", "")).strip(),
            "negotiation_record_hash": str(_as_map(row).get("negotiation_record_hash", "")).strip(),
            "replay_result": str(_as_map(row).get("replay_result", "")).strip(),
        }
        for row in list(real_descriptor_smoke_reports or [])
    ]
    payload = {
        "result": "complete"
        if all(
            str(_as_map(row).get("replay_result", "")).strip() == "complete"
            for row in list(scenario_reports or []) + list(real_descriptor_smoke_reports or [])
        )
        else "refused",
        "scenario_record_hashes": sorted(
            scenario_rows,
            key=lambda row: (str(row.get("scenario_id", "")), str(row.get("negotiation_record_hash", ""))),
        ),
        "real_descriptor_record_hashes": sorted(
            real_rows,
            key=lambda row: (str(row.get("scenario_id", "")), str(row.get("negotiation_record_hash", ""))),
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _real_descriptor_scenarios(repo_root: str, *, seed: int) -> List[dict]:
    actual_client = _descriptor_from_wrapper(repo_root, product_id="client")
    actual_server = _descriptor_from_wrapper(repo_root, product_id="server")
    actual_launcher = _descriptor_from_wrapper(repo_root, product_id="launcher")
    actual_setup = _descriptor_from_wrapper(repo_root, product_id="setup")
    matrix_payload = generate_interop_matrix(repo_root=repo_root, seed=seed)
    setup_pack_stub = {}
    for row in _as_list(matrix_payload.get("scenarios")):
        row_map = _as_map(row)
        if str(row_map.get("scenario_id", "")).strip() == "interop.setup_pack.verify_older_newer":
            setup_pack_stub = dict(_as_map(row_map.get("endpoint_b")))
            break
    if not setup_pack_stub:
        raise RuntimeError("CAP-NEG-4 setup pack stub scenario missing from generated matrix")
    return [
        _scenario_row(
            repo_root,
            scenario_id="real.client_server.current_build",
            description="current built client and server descriptors negotiate through the live emitted endpoint descriptors",
            endpoint_a=actual_client,
            endpoint_b=actual_server,
            expected_compatibility_mode_id="compat.degraded",
            allow_read_only=False,
            policy_profile_id="server.policy.private.default",
            tags=["real_descriptor", "client_server"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="real.launcher_client.current_build",
            description="current built launcher and client descriptors refuse when there is no shared protocol",
            endpoint_a=actual_launcher,
            endpoint_b=actual_client,
            expected_compatibility_mode_id="compat.refuse",
            expected_refusal_code="refusal.compat.no_common_protocol",
            allow_read_only=False,
            policy_profile_id="launcher.policy.local",
            tags=["real_descriptor", "launcher_client"],
        ),
        _scenario_row(
            repo_root,
            scenario_id="real.setup_pack_stub.current_build",
            description="current built setup descriptor remains fully compatible with the newer pack-verification stub",
            endpoint_a=actual_setup,
            endpoint_b=setup_pack_stub,
            expected_compatibility_mode_id="compat.full",
            allow_read_only=False,
            policy_profile_id="setup.policy.offline",
            tags=["real_descriptor", "setup_pack"],
        ),
    ]


def run_interop_stress(
    *,
    repo_root: str,
    matrix: Mapping[str, object] | None = None,
    seed: int = DEFAULT_CAP_NEG4_SEED,
) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    matrix_payload = dict(matrix or generate_interop_matrix(repo_root=repo_root, seed=int(seed)))
    scenario_rows = [dict(row) for row in _as_list(matrix_payload.get("scenarios")) if isinstance(row, Mapping)]
    reports = [_scenario_report(repo_root, scenario_row=row) for row in scenario_rows]
    real_descriptor_reports = [_scenario_report(repo_root, scenario_row=row) for row in _real_descriptor_scenarios(repo_root, seed=int(seed))]
    mode_counts = {
        mode_id: int(len([row for row in reports if str(row.get("compatibility_mode_id", "")).strip() == mode_id]))
        for mode_id in ("compat.full", "compat.degraded", "compat.read_only", "compat.refuse")
    }
    refusal_counts: dict[str, int] = {}
    disabled_counts: dict[str, int] = {}
    for row in reports:
        refusal_code = str(row.get("actual_refusal_code", "")).strip()
        if refusal_code:
            refusal_counts[refusal_code] = int(refusal_counts.get(refusal_code, 0)) + 1
        for capability_id in _as_list(row.get("disabled_capability_ids")):
            token = str(capability_id).strip()
            if token:
                disabled_counts[token] = int(disabled_counts.get(token, 0)) + 1
    refusal_rows = [
        {"refusal_code": key, "count": int(refusal_counts[key])} for key in sorted(refusal_counts.keys())
    ]
    disabled_rows = [
        {"capability_id": key, "count": int(disabled_counts[key])}
        for key in sorted(disabled_counts.keys(), key=lambda token: (-disabled_counts[token], token))
    ]
    explain_rows = [
        {
            "scenario_id": str(row.get("scenario_id", "")).strip(),
            "compatibility_mode_id": str(row.get("compatibility_mode_id", "")).strip(),
            "actual_refusal_code": str(row.get("actual_refusal_code", "")).strip(),
            "explain_keys": list(row.get("explain_keys") or []),
        }
        for row in reports
        if str(row.get("compatibility_mode_id", "")).strip() != "compat.full"
    ]
    assertions = {
        "matrix_rows_present": bool(reports),
        "deterministic_outcomes": all(bool(row.get("stable_across_repeated_runs", False)) for row in reports),
        "expected_modes_match": all(bool(row.get("match_expected", False)) for row in reports),
        "replay_matches": all(str(row.get("replay_result", "")).strip() == "complete" for row in reports),
        "real_descriptor_smoke_matches": all(bool(row.get("match_expected", False)) for row in real_descriptor_reports),
        "real_descriptor_smoke_replay_matches": all(
            str(row.get("replay_result", "")).strip() == "complete" for row in real_descriptor_reports
        ),
    }
    replay_summary = _replay_summary_from_reports(
        scenario_reports=reports,
        real_descriptor_smoke_reports=real_descriptor_reports,
    )
    report = {
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "matrix_id": str(matrix_payload.get("matrix_id", "")).strip(),
        "matrix_fingerprint": str(matrix_payload.get("deterministic_fingerprint", "")).strip(),
        "scenario_seed": int(_as_int(matrix_payload.get("scenario_seed", seed), seed)),
        "scenario_count": int(len(reports)),
        "mode_counts": mode_counts,
        "refusal_counts": refusal_rows,
        "disabled_capability_frequency": disabled_rows,
        "explain_rows": explain_rows,
        "scenario_reports": reports,
        "real_descriptor_smoke_reports": real_descriptor_reports,
        "replay_summary": replay_summary,
        "assertions": assertions,
        "deterministic_fingerprint": "",
        "extensions": {
            "official.source": "CAP-NEG-4",
        },
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_interop_stress_replay(
    *,
    repo_root: str,
    matrix: Mapping[str, object] | None = None,
    seed: int = DEFAULT_CAP_NEG4_SEED,
) -> dict:
    report = run_interop_stress(repo_root=repo_root, matrix=matrix, seed=seed)
    replay = dict(_as_map(report.get("replay_summary")))
    return {
        "result": str(replay.get("result", "")).strip() or "refused",
        "stress_report_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "replay_summary": replay,
        "deterministic_fingerprint": canonical_sha256(
            {
                "stress_report_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
                "replay_summary": replay,
            }
        ),
    }


def build_cap_neg_full_baseline(
    *,
    repo_root: str,
    matrix: Mapping[str, object] | None = None,
    stress_report: Mapping[str, object] | None = None,
    seed: int = DEFAULT_CAP_NEG4_SEED,
) -> dict:
    matrix_payload = dict(matrix or generate_interop_matrix(repo_root=repo_root, seed=seed))
    report = dict(stress_report or run_interop_stress(repo_root=repo_root, matrix=matrix_payload, seed=seed))
    scenario_rows = []
    for row in list(report.get("scenario_reports") or []):
        row_map = _as_map(row)
        scenario_rows.append(
            {
                "scenario_id": str(row_map.get("scenario_id", "")).strip(),
                "compatibility_mode_id": str(row_map.get("compatibility_mode_id", "")).strip(),
                "chosen_protocol_id": str(row_map.get("chosen_protocol_id", "")).strip(),
                "chosen_protocol_version": str(row_map.get("chosen_protocol_version", "")).strip(),
                "refusal_code": str(row_map.get("actual_refusal_code", "")).strip(),
                "disabled_capability_ids": _sorted_tokens(row_map.get("disabled_capability_ids")),
                "substituted_capability_ids": _sorted_tokens(row_map.get("substituted_capability_ids")),
                "negotiation_record_hash": str(row_map.get("negotiation_record_hash", "")).strip(),
            }
        )
    real_rows = []
    for row in list(report.get("real_descriptor_smoke_reports") or []):
        row_map = _as_map(row)
        real_rows.append(
            {
                "scenario_id": str(row_map.get("scenario_id", "")).strip(),
                "compatibility_mode_id": str(row_map.get("compatibility_mode_id", "")).strip(),
                "chosen_protocol_id": str(row_map.get("chosen_protocol_id", "")).strip(),
                "chosen_protocol_version": str(row_map.get("chosen_protocol_version", "")).strip(),
                "refusal_code": str(row_map.get("actual_refusal_code", "")).strip(),
                "disabled_capability_ids": _sorted_tokens(row_map.get("disabled_capability_ids")),
                "substituted_capability_ids": _sorted_tokens(row_map.get("substituted_capability_ids")),
            }
        )
    replay_summary = _as_map(report.get("replay_summary"))
    stable_replay_summary = {
        "result": str(replay_summary.get("result", "")).strip(),
        "scenario_rows": sorted(
            [
                {
                    "scenario_id": str(_as_map(row).get("scenario_id", "")).strip(),
                    "compatibility_mode_id": str(_as_map(row).get("compatibility_mode_id", "")).strip(),
                    "replay_result": str(_as_map(row).get("replay_result", "")).strip(),
                }
                for row in list(replay_summary.get("scenario_record_hashes") or [])
            ],
            key=lambda row: str(row.get("scenario_id", "")),
        ),
        "real_descriptor_rows": sorted(
            [
                {
                    "scenario_id": str(_as_map(row).get("scenario_id", "")).strip(),
                    "compatibility_mode_id": str(_as_map(row).get("compatibility_mode_id", "")).strip(),
                    "replay_result": str(_as_map(row).get("replay_result", "")).strip(),
                }
                for row in list(replay_summary.get("real_descriptor_record_hashes") or [])
            ],
            key=lambda row: str(row.get("scenario_id", "")),
        ),
    }
    stable_stress_summary = {
        "mode_counts": dict(_as_map(report.get("mode_counts"))),
        "refusal_counts": [dict(row) for row in list(report.get("refusal_counts") or []) if isinstance(row, Mapping)],
        "disabled_capability_frequency": [
            dict(row) for row in list(report.get("disabled_capability_frequency") or []) if isinstance(row, Mapping)
        ],
        "canonical_scenarios": sorted(
            scenario_rows,
            key=lambda row: (str(row.get("scenario_id", "")), str(row.get("negotiation_record_hash", ""))),
        ),
        "real_descriptor_smoke": sorted(
            real_rows,
            key=lambda row: str(row.get("scenario_id", "")),
        ),
        "replay_summary": stable_replay_summary,
    }
    baseline = {
        "baseline_id": "cap.neg.full.baseline.v1",
        "schema_version": "1.0.0",
        "description": "Deterministic CAP-NEG-4 regression lock for mixed-version negotiation, degrade ladders, read-only fallback, and refusal surfaces.",
        "scenario_seed": int(_as_int(seed, DEFAULT_CAP_NEG4_SEED)),
        "matrix_fingerprint": str(matrix_payload.get("deterministic_fingerprint", "")).strip(),
        "stress_report_fingerprint": canonical_sha256(stable_stress_summary),
        "replay_summary_fingerprint": canonical_sha256(stable_replay_summary),
        "mode_counts": dict(_as_map(report.get("mode_counts"))),
        "refusal_counts": [dict(row) for row in list(report.get("refusal_counts") or []) if isinstance(row, Mapping)],
        "disabled_capability_frequency": [
            dict(row) for row in list(report.get("disabled_capability_frequency") or []) if isinstance(row, Mapping)
        ],
        "canonical_scenarios": sorted(
            scenario_rows,
            key=lambda row: (str(row.get("scenario_id", "")), str(row.get("negotiation_record_hash", ""))),
        ),
        "real_descriptor_smoke": sorted(
            real_rows,
            key=lambda row: str(row.get("scenario_id", "")),
        ),
        "update_policy": {
            "required_commit_tag": "CAP-NEG-REGRESSION-UPDATE",
            "notes": "Baseline updates require rerunning CAP-NEG-4 matrix, stress, and replay verification under explicit CAP-NEG-REGRESSION-UPDATE review.",
        },
        "extensions": {
            "generated_from": {
                "matrix_path": DEFAULT_MATRIX_REL.replace("\\", "/"),
                "stress_report_path": DEFAULT_STRESS_REL.replace("\\", "/"),
            },
            "lock_scope": "capability_negotiation_envelope",
        },
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = canonical_sha256(dict(baseline, deterministic_fingerprint=""))
    return baseline


__all__ = [
    "DEFAULT_BASELINE_REL",
    "DEFAULT_CAP_NEG4_SEED",
    "DEFAULT_MATRIX_REL",
    "DEFAULT_STRESS_REL",
    "build_cap_neg_full_baseline",
    "generate_interop_matrix",
    "run_interop_stress",
    "verify_interop_stress_replay",
    "write_json",
]

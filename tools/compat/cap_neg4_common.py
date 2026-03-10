"""Shared deterministic CAP-NEG-4 interop-matrix helpers."""

from __future__ import annotations

import copy
import json
import os
from typing import Iterable, List, Mapping, Sequence

from src.compat import build_default_endpoint_descriptor, build_endpoint_descriptor
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


__all__ = [
    "DEFAULT_BASELINE_REL",
    "DEFAULT_CAP_NEG4_SEED",
    "DEFAULT_MATRIX_REL",
    "DEFAULT_STRESS_REL",
    "generate_interop_matrix",
    "write_json",
]

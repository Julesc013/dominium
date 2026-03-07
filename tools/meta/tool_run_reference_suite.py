#!/usr/bin/env python3
"""Run META-REF0 runtime-vs-reference equivalence checks for selected evaluators."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable, Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.meta.reference import evaluate_reference_suite, reference_evaluator_rows_by_id  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


REGISTRY_REL = "data/registries/reference_evaluator_registry.json"
MISMATCH_REL_TEMPLATE = "docs/audit/REFERENCE_MISMATCH_{seed}.md"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be object"
    return dict(payload), ""


def _load_registry(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload, err = _read_json(abs_path)
    return {} if err else payload


def _stable_tokens(values: Iterable[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _fixture_state(seed: int, tick_start: int, tick_end: int) -> dict:
    tick_a = int(max(0, _as_int(tick_start, 0)))
    tick_b = int(max(tick_a, _as_int(tick_end, tick_a)))
    model_payload = {"nodes": [{"node_id": "node.input", "op": "input"}], "seed": int(seed)}
    payload_hash = canonical_sha256(model_payload)
    source_hash = canonical_sha256({"source_kind": "model_set", "seed": int(seed)})
    proof_hash = canonical_sha256(
        {
            "source_hash": source_hash,
            "compiled_payload_hash": payload_hash,
            "proof_kind": "exact",
            "verification_procedure_id": "verify.exact_structural",
            "error_bound_policy_id": None,
        }
    )
    entries = []
    for index in range(6):
        tick_value = int(tick_a + (index % 3))
        input_energy = int(100 + ((seed + index) % 11))
        output_energy = int(90 + ((seed + index) % 11))
        entries.append(
            {
                "schema_version": "1.0.0",
                "entry_id": "ledger.energy.ref.{}".format(index),
                "tick": tick_value,
                "transformation_id": "transform.ref.energy",
                "source_id": "source.ref.{}".format(index % 2),
                "input_values": {"quantity.energy_total": input_energy},
                "output_values": {"quantity.energy_total": output_energy},
                "energy_total_delta": int(output_energy - input_energy),
            }
        )
    return {
        "energy_ledger_entries": entries,
        "model_rows": [
            {
                "schema_version": "1.0.0",
                "model_id": "model.ref.alpha",
                "model_type_id": "model_type.ref.stub",
                "cache_policy_id": "cache.none",
                "supported_tiers": ["macro"],
                "input_signature": [{"input_kind": "derived", "input_id": "input.alpha", "selector": None}],
                "output_signature": [{"output_kind": "derived_quantity", "output_id": "quantity.ref.alpha"}],
                "cost_units": 4,
                "uses_rng_stream": False,
                "rng_stream_name": "",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "model_id": "model.ref.beta",
                "model_type_id": "model_type.ref.stub",
                "cache_policy_id": "cache.none",
                "supported_tiers": ["macro"],
                "input_signature": [{"input_kind": "derived", "input_id": "input.beta", "selector": None}],
                "output_signature": [{"output_kind": "derived_quantity", "output_id": "quantity.ref.beta"}],
                "cost_units": 5,
                "uses_rng_stream": False,
                "rng_stream_name": "",
                "extensions": {},
            },
        ],
        "model_binding_rows": [
            {
                "binding_id": "binding.ref.alpha",
                "model_id": "model.ref.alpha",
                "target_kind": "custom",
                "target_id": "target.ref.alpha",
                "tier": "macro",
                "parameters": {},
                "enabled": True,
                "extensions": {},
            },
            {
                "binding_id": "binding.ref.beta",
                "model_id": "model.ref.beta",
                "target_kind": "custom",
                "target_id": "target.ref.beta",
                "tier": "macro",
                "parameters": {},
                "enabled": True,
                "extensions": {},
            },
        ],
        "model_type_rows": {
            "model_type.ref.stub": {"model_type_id": "model_type.ref.stub"},
        },
        "cache_policy_rows": {"cache.none": {"cache_policy_id": "cache.none", "mode": "none", "ttl_ticks": None}},
        "max_cost_units": 9,
        "far_target_ids": [],
        "far_tick_stride": 4,
        "system_rows": [
            {
                "system_id": "system.ref.alpha",
                "boundary_invariant_ids": ["invariant.ref.mass", "invariant.ref.energy"],
                "extensions": {
                    "boundary_invariant_template_ids": ["inv.ref.mass_energy"],
                    "safety_pattern_ids": ["safety.ref.fail_safe"],
                    "emits_pollutants": False,
                },
            }
        ],
        "system_boundary_invariant_rows": [
            {
                "invariant_id": "invariant.ref.mass",
                "invariant_kind": "mass",
                "tolerance_policy_id": "tol.default",
                "boundary_flux_allowed": True,
                "ledger_transform_required": False,
            },
            {
                "invariant_id": "invariant.ref.energy",
                "invariant_kind": "energy",
                "tolerance_policy_id": "tol.default",
                "boundary_flux_allowed": True,
                "ledger_transform_required": True,
            },
        ],
        "boundary_invariant_template_registry_payload": {
            "record": {
                "boundary_invariant_templates": [
                    {
                        "boundary_invariant_template_id": "inv.ref.mass_energy",
                        "required_invariants": ["invariant.ref.mass", "invariant.ref.energy"],
                        "required_safety_pattern_ids": ["safety.ref.fail_safe"],
                    }
                ]
            }
        },
        "tolerance_policy_registry_payload": {
            "record": {"tolerance_policies": [{"tolerance_policy_id": "tol.default"}]}
        },
        "safety_pattern_registry_payload": {
            "record": {"safety_patterns": [{"pattern_id": "safety.ref.fail_safe"}]}
        },
        "compiled_model_rows": [
            {
                "compiled_model_id": "compiled_model.ref.alpha",
                "source_kind": "model_set",
                "source_hash": source_hash,
                "compiled_type_id": "compiled.reduced_graph",
                "compiled_payload_ref": {"payload": model_payload, "payload_hash": payload_hash},
                "input_signature_ref": "signature.input.ref.alpha",
                "output_signature_ref": "signature.output.ref.alpha",
                "validity_domain_ref": "validity_domain.ref.alpha",
                "equivalence_proof_ref": "proof.ref.alpha",
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "equivalence_proof_rows": [
            {
                "proof_id": "proof.ref.alpha",
                "proof_kind": "exact",
                "verification_procedure_id": "verify.exact_structural",
                "error_bound_policy_id": None,
                "proof_hash": proof_hash,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "current_tick": int(tick_b),
    }


def _active_evaluators(registry_payload: Mapping[str, object]) -> list[str]:
    by_id = reference_evaluator_rows_by_id(registry_payload)
    active = []
    for evaluator_id in sorted(by_id.keys()):
        row = dict(by_id.get(evaluator_id) or {})
        status = str(_as_map(row.get("extensions")).get("status", "active")).strip().lower() or "active"
        if status == "active":
            active.append(evaluator_id)
    return active


def _write_mismatch_report(repo_root: str, seed: int, report: Mapping[str, object]) -> str:
    rel_path = MISMATCH_REL_TEMPLATE.format(seed=int(max(0, _as_int(seed, 0))))
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    lines = []
    lines.append("# Reference Mismatch Report")
    lines.append("")
    lines.append("- seed: `{}`".format(int(max(0, _as_int(seed, 0)))))
    lines.append("- tick_range: `{}`".format(json.dumps(_as_map(report.get("tick_range")), sort_keys=True)))
    lines.append("- mismatch_count: `{}`".format(len(list(report.get("mismatches") or []))))
    lines.append("")
    lines.append("## Mismatches")
    lines.append("")
    for row in list(report.get("mismatches") or []):
        if not isinstance(row, Mapping):
            continue
        lines.append("- evaluator_id: `{}`".format(str(row.get("evaluator_id", "")).strip()))
        lines.append("  run_id: `{}`".format(str(row.get("run_id", "")).strip()))
        lines.append("  summary: `{}`".format(str(row.get("discrepancy_summary", "")).strip()))
    lines.append("")

    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    return rel_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic META-REF0 runtime/reference equivalence suite.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--state-path", default="", help="optional JSON state payload path")
    parser.add_argument("--seed", type=int, default=1107)
    parser.add_argument("--tick-start", type=int, default=0)
    parser.add_argument("--tick-end", type=int, default=3)
    parser.add_argument("--current-tick", type=int, default=-1)
    parser.add_argument("--evaluators", default="", help="comma-separated evaluator ids")
    parser.add_argument("--out-path", default="", help="optional JSON report output path")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    registry_payload = _load_registry(repo_root, REGISTRY_REL)

    state_source = "fixture"
    state_payload = {}
    state_path = str(args.state_path or "").strip()
    if state_path:
        abs_state_path = os.path.normpath(os.path.abspath(os.path.join(repo_root, state_path))) if not os.path.isabs(state_path) else os.path.normpath(os.path.abspath(state_path))
        state_payload, state_err = _read_json(abs_state_path)
        if state_err:
            print(json.dumps({"result": "error", "reason_code": "refusal.reference.invalid_state_path", "details": state_err}, indent=2, sort_keys=True))
            return 2
        state_source = os.path.relpath(abs_state_path, repo_root).replace("\\", "/")
    else:
        state_payload = _fixture_state(seed=int(args.seed), tick_start=int(args.tick_start), tick_end=int(args.tick_end))

    evaluator_arg = [token.strip() for token in str(args.evaluators or "").split(",") if token.strip()]
    evaluator_ids = _stable_tokens(evaluator_arg if evaluator_arg else _active_evaluators(registry_payload))
    if not evaluator_ids:
        print(json.dumps({"result": "error", "reason_code": "refusal.reference.no_evaluators"}, indent=2, sort_keys=True))
        return 2

    current_tick = int(args.current_tick)
    if current_tick < 0:
        current_tick = int(max(0, _as_int(state_payload.get("current_tick", args.tick_end), args.tick_end)))
    suite = evaluate_reference_suite(
        evaluator_ids=evaluator_ids,
        state_payload=state_payload,
        current_tick=int(current_tick),
        seed=int(args.seed),
        tick_start=int(args.tick_start),
        tick_end=int(args.tick_end),
        configs_by_evaluator_id={},
    )

    report = {
        "result": str(suite.get("result", "")).strip(),
        "seed": int(args.seed),
        "tick_range": {"start": int(args.tick_start), "end": int(args.tick_end)},
        "current_tick": int(current_tick),
        "evaluator_ids": evaluator_ids,
        "state_source": state_source,
        "reference_run_record_rows": list(suite.get("reference_run_record_rows") or []),
        "mismatches": list(suite.get("mismatches") or []),
        "deterministic_fingerprint": "",
        "mismatch_report_path": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))

    if list(report.get("mismatches") or []):
        report["mismatch_report_path"] = _write_mismatch_report(repo_root, int(args.seed), report)

    out_path = str(args.out_path or "").strip()
    if out_path:
        abs_out = os.path.normpath(os.path.abspath(os.path.join(repo_root, out_path))) if not os.path.isabs(out_path) else os.path.normpath(os.path.abspath(out_path))
        os.makedirs(os.path.dirname(abs_out), exist_ok=True)
        with open(abs_out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

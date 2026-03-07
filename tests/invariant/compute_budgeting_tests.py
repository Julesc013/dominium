import argparse
import hashlib
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.meta.compile import build_compiled_model_row, build_validity_domain_row, compiled_model_execute
from src.meta.compute import evaluate_compute_budget_tick


def _canonical_hash(payload) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _load_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _profile_payload(*, instruction_budget: int, memory_budget: int, eval_cap: int, power_coupling_enabled: bool, profile_id: str = "compute.default", degrade_policy_id: str = "degrade.default_order") -> dict:
    return {
        "record": {
            "compute_budget_profiles": [
                {
                    "schema_version": "1.0.0",
                    "compute_profile_id": str(profile_id),
                    "instruction_budget_per_tick": int(instruction_budget),
                    "memory_budget_total": int(memory_budget),
                    "evaluation_cap_per_tick": int(eval_cap),
                    "degrade_policy_id": str(degrade_policy_id),
                    "power_coupling_enabled": bool(power_coupling_enabled),
                    "extensions": {"source": "test"},
                }
            ]
        }
    }


def _policy_payload(*, policy_id: str = "degrade.default_order", tick_bucket_stride: int = 2, allow_representation_degrade: bool = True, fail_safe_on_critical_overrun: bool = False) -> dict:
    return {
        "record": {
            "compute_degrade_policies": [
                {
                    "schema_version": "1.0.0",
                    "degrade_policy_id": str(policy_id),
                    "order": [
                        "reduce_frequency",
                        "degrade_representation",
                        "cap_evaluations",
                        "refuse_noncritical",
                        "shutdown_if_required",
                    ],
                    "tick_bucket_stride": int(max(1, tick_bucket_stride)),
                    "allow_representation_degrade": bool(allow_representation_degrade),
                    "fail_safe_on_critical_overrun": bool(fail_safe_on_critical_overrun),
                    "extensions": {"source": "test"},
                }
            ]
        }
    }


def case_budget_allocation_deterministic() -> int:
    owners = [
        {"owner_kind": "controller", "owner_id": "owner.alpha", "instruction_units": 32, "memory_units": 8, "priority": 10, "critical": True},
        {"owner_kind": "controller", "owner_id": "owner.beta", "instruction_units": 16, "memory_units": 4, "priority": 20, "critical": False},
        {"owner_kind": "process", "owner_id": "owner.gamma", "instruction_units": 8, "memory_units": 2, "priority": 30, "critical": False},
    ]
    profile_registry = _profile_payload(
        instruction_budget=128,
        memory_budget=2048,
        eval_cap=16,
        power_coupling_enabled=False,
    )
    policy_registry = _policy_payload(policy_id="degrade.default_order")
    first = evaluate_compute_budget_tick(
        current_tick=12,
        owner_rows=owners,
        compute_runtime_state={},
        compute_budget_profile_registry_payload=profile_registry,
        compute_degrade_policy_registry_payload=policy_registry,
        compute_budget_profile_id="compute.default",
    )
    second = evaluate_compute_budget_tick(
        current_tick=12,
        owner_rows=owners,
        compute_runtime_state={},
        compute_budget_profile_registry_payload=profile_registry,
        compute_degrade_policy_registry_payload=policy_registry,
        compute_budget_profile_id="compute.default",
    )
    if _canonical_hash(first) != _canonical_hash(second):
        print("budget allocation is not deterministic")
        return 1
    if first.get("compute_consumption_hash_chain") != second.get("compute_consumption_hash_chain"):
        print("compute consumption hash chain mismatch")
        return 1
    print("test_budget_allocation_deterministic=ok")
    return 0


def case_throttle_order_deterministic() -> int:
    owners = [
        {"owner_kind": "controller", "owner_id": "owner.zeta", "instruction_units": 36, "memory_units": 1, "priority": 5, "critical": False},
        {"owner_kind": "controller", "owner_id": "owner.alpha", "instruction_units": 36, "memory_units": 1, "priority": 5, "critical": False},
        {"owner_kind": "controller", "owner_id": "owner.delta", "instruction_units": 36, "memory_units": 1, "priority": 5, "critical": False},
    ]
    profile_registry = _profile_payload(
        instruction_budget=48,
        memory_budget=128,
        eval_cap=4,
        power_coupling_enabled=False,
    )
    policy_registry = _policy_payload(policy_id="degrade.default_order", tick_bucket_stride=2, allow_representation_degrade=True)
    first = evaluate_compute_budget_tick(
        current_tick=22,
        owner_rows=owners,
        compute_runtime_state={},
        compute_budget_profile_registry_payload=profile_registry,
        compute_degrade_policy_registry_payload=policy_registry,
        compute_budget_profile_id="compute.default",
    )
    second = evaluate_compute_budget_tick(
        current_tick=22,
        owner_rows=list(reversed(owners)),
        compute_runtime_state={},
        compute_budget_profile_registry_payload=profile_registry,
        compute_degrade_policy_registry_payload=policy_registry,
        compute_budget_profile_id="compute.default",
    )
    first_rows = [
        (str(row.get("decision_log_row", {}).get("owner_id", "")), str(row.get("action_taken", "")))
        for row in list(first.get("decision_rows") or [])
    ]
    second_rows = [
        (str(row.get("decision_log_row", {}).get("owner_id", "")), str(row.get("action_taken", "")))
        for row in list(second.get("decision_rows") or [])
    ]
    if first_rows != second_rows:
        print("throttle order changed with owner input order")
        return 1
    if first_rows != sorted(first_rows, key=lambda item: item[0]):
        print("owner decisions are not in stable owner_id order under same priority")
        return 1
    if all(action == "none" for _, action in first_rows):
        print("expected at least one throttled/degraded/deferred action under constrained budget")
        return 1
    print("test_throttle_order_deterministic=ok")
    return 0


def case_consumption_records_logged() -> int:
    owners = [
        {"owner_kind": "controller", "owner_id": "owner.one", "instruction_units": 12, "memory_units": 1, "priority": 1, "critical": False},
        {"owner_kind": "process", "owner_id": "owner.two", "instruction_units": 12, "memory_units": 1, "priority": 2, "critical": False},
    ]
    result = evaluate_compute_budget_tick(
        current_tick=7,
        owner_rows=owners,
        compute_runtime_state={},
        compute_budget_profile_registry_payload=_profile_payload(
            instruction_budget=24,
            memory_budget=64,
            eval_cap=8,
            power_coupling_enabled=False,
        ),
        compute_degrade_policy_registry_payload=_policy_payload(),
        compute_budget_profile_id="compute.default",
    )
    rows = list(result.get("compute_consumption_record_rows") or [])
    if len(rows) != 2:
        print("expected 2 consumption records, got {}".format(len(rows)))
        return 1
    for row in rows:
        if not str(row.get("record_id", "")).strip():
            print("missing record_id")
            return 1
        if not str(row.get("deterministic_fingerprint", "")).strip():
            print("missing deterministic_fingerprint")
            return 1
        if int(row.get("tick", -1)) != 7:
            print("unexpected tick in consumption record")
            return 1
    print("test_consumption_records_logged=ok")
    return 0


def case_power_coupling_ledgered_when_enabled() -> int:
    model_row = build_compiled_model_row(
        compiled_model_id="compiled_model.test_compute",
        source_kind="model_set",
        source_hash="source.hash.1",
        compiled_type_id="compiled.reduced_graph",
        compiled_payload_ref={
            "payload_hash": "payload.hash.1",
            "payload": {
                "optimization_summary": {"source_node_count": 3, "reduced_node_count": 2},
                "constant_bindings": {"const.a": 1},
            },
        },
        input_signature_ref="sig.input.test",
        output_signature_ref="sig.output.test",
        validity_domain_ref="validity.test_compute",
        equivalence_proof_ref="proof.test_compute",
        deterministic_fingerprint="",
        extensions={},
    )
    validity_row = build_validity_domain_row(
        domain_id="validity.test_compute",
        input_ranges={"x": {"min": 0, "max": 10}},
        deterministic_fingerprint="",
        extensions={},
    )
    result = compiled_model_execute(
        compiled_model_id="compiled_model.test_compute",
        inputs={"x": 3},
        compiled_model_rows=[model_row],
        validity_domain_rows=[validity_row],
        state_vector_definition_rows=[],
        state_vector_snapshot_rows=[],
        current_tick=9,
        compute_runtime_state={},
        compute_budget_profile_registry_payload=_profile_payload(
            instruction_budget=1024,
            memory_budget=4096,
            eval_cap=32,
            power_coupling_enabled=True,
            profile_id="compute.rank_strict",
            degrade_policy_id="degrade.strict_shutdown",
        ),
        compute_degrade_policy_registry_payload=_policy_payload(
            policy_id="degrade.strict_shutdown",
            allow_representation_degrade=False,
            fail_safe_on_critical_overrun=True,
        ),
        compute_budget_profile_id="compute.rank_strict",
        owner_priority=10,
    )
    if str(result.get("result", "")).strip() != "complete":
        print("compiled model execution failed")
        return 1
    transform = dict(result.get("compute_energy_transform_row") or {})
    if str(transform.get("transformation_id", "")).strip() != "transform.electrical_to_thermal":
        print("missing compute electrical->thermal transform")
        return 1
    input_energy = int(((transform.get("input_values") or {}).get("quantity.energy.electrical", 0) or 0))
    output_energy = int(((transform.get("output_values") or {}).get("quantity.energy.thermal", 0) or 0))
    if input_energy <= 0 or output_energy <= 0 or input_energy != output_energy:
        print("invalid compute power coupling transform values")
        return 1
    print("test_power_coupling_ledgered_when_enabled=ok")
    return 0


def case_cross_platform_compute_hash_match(repo_root: str) -> int:
    profile_registry = _load_json(os.path.join(repo_root, "data", "registries", "compute_budget_profile_registry.json"))
    degrade_registry = _load_json(os.path.join(repo_root, "data", "registries", "compute_degrade_policy_registry.json"))
    if not profile_registry or not degrade_registry:
        print("failed to load compute registries")
        return 1
    result = evaluate_compute_budget_tick(
        current_tick=30,
        owner_rows=[
            {"owner_kind": "controller", "owner_id": "owner.hash.a", "instruction_units": 20, "memory_units": 2, "priority": 10},
            {"owner_kind": "controller", "owner_id": "owner.hash.b", "instruction_units": 30, "memory_units": 2, "priority": 20},
        ],
        compute_runtime_state={},
        compute_budget_profile_registry_payload=profile_registry,
        compute_degrade_policy_registry_payload=degrade_registry,
        compute_budget_profile_id="compute.default",
    )
    first = _canonical_hash(result)
    second = _canonical_hash(json.loads(json.dumps(result)))
    if first != second:
        print("cross-platform canonical hash mismatch for compute result")
        return 1
    print("test_cross_platform_compute_hash_match=ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="META-COMPUTE0 deterministic compute budget tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--case",
        required=True,
        choices=(
            "budget_allocation_deterministic",
            "throttle_order_deterministic",
            "consumption_records_logged",
            "power_coupling_ledgered_when_enabled",
            "cross_platform_compute_hash_match",
        ),
    )
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "budget_allocation_deterministic":
        return case_budget_allocation_deterministic()
    if args.case == "throttle_order_deterministic":
        return case_throttle_order_deterministic()
    if args.case == "consumption_records_logged":
        return case_consumption_records_logged()
    if args.case == "power_coupling_ledgered_when_enabled":
        return case_power_coupling_ledgered_when_enabled()
    return case_cross_platform_compute_hash_match(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())

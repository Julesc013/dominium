"""FAST test: SYS-4 nested template toposort is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_nested_templates_toposort_deterministic"
TEST_TAGS = ["fast", "system", "sys4", "template"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.system import resolve_nested_template_order

    payload = {
        "system_templates": [
            {
                "template_id": "template.root",
                "version": "1.0.0",
                "description": "root",
                "required_domains": [],
                "assembly_graph_spec_ref": "ag.root",
                "interface_signature_template_id": "interface.engine_basic",
                "boundary_invariant_template_ids": ["inv.mass_energy_basic"],
                "macro_model_set_id": "macro.engine_stub",
                "tier_contract_id": "tier.system.default",
                "safety_pattern_instance_templates": [],
                "spec_bindings": [],
                "nested_template_refs": ["template.child_a", "template.child_b"],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
            {
                "template_id": "template.child_a",
                "version": "1.0.0",
                "description": "child a",
                "required_domains": [],
                "assembly_graph_spec_ref": "ag.child_a",
                "interface_signature_template_id": "interface.engine_basic",
                "boundary_invariant_template_ids": ["inv.mass_energy_basic"],
                "macro_model_set_id": "macro.engine_stub",
                "tier_contract_id": "tier.system.default",
                "safety_pattern_instance_templates": [],
                "spec_bindings": [],
                "nested_template_refs": ["template.leaf"],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
            {
                "template_id": "template.child_b",
                "version": "1.0.0",
                "description": "child b",
                "required_domains": [],
                "assembly_graph_spec_ref": "ag.child_b",
                "interface_signature_template_id": "interface.engine_basic",
                "boundary_invariant_template_ids": ["inv.mass_energy_basic"],
                "macro_model_set_id": "macro.engine_stub",
                "tier_contract_id": "tier.system.default",
                "safety_pattern_instance_templates": [],
                "spec_bindings": [],
                "nested_template_refs": ["template.leaf"],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
            {
                "template_id": "template.leaf",
                "version": "1.0.0",
                "description": "leaf",
                "required_domains": [],
                "assembly_graph_spec_ref": "ag.leaf",
                "interface_signature_template_id": "interface.engine_basic",
                "boundary_invariant_template_ids": ["inv.mass_energy_basic"],
                "macro_model_set_id": "macro.engine_stub",
                "tier_contract_id": "tier.system.default",
                "safety_pattern_instance_templates": [],
                "spec_bindings": [],
                "nested_template_refs": [],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
        ]
    }
    order_a = resolve_nested_template_order(
        template_id="template.root",
        system_template_registry_payload=payload,
    )
    order_b = resolve_nested_template_order(
        template_id="template.root",
        system_template_registry_payload=payload,
    )
    if list(order_a) != list(order_b):
        return {"status": "fail", "message": "nested template toposort order changed across equivalent runs"}
    if list(order_a) != ["template.leaf", "template.child_a", "template.child_b", "template.root"]:
        return {"status": "fail", "message": "nested template toposort order did not match deterministic expectation"}
    return {"status": "pass", "message": "nested template toposort is deterministic"}


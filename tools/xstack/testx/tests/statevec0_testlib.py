"""Shared STATEVEC-0 TestX fixtures/helpers."""

from __future__ import annotations

import copy


def state_vector_definition_rows(owner_id: str = "system.system.engine.alpha") -> list[dict]:
    owner_token = str(owner_id or "").strip() or "system.system.engine.alpha"
    return [
        {
            "schema_version": "1.0.0",
            "owner_id": owner_token,
            "version": "1.0.0",
            "state_fields": [
                {"field_id": "captured_tick", "path": "captured_tick", "field_kind": "u64", "default": 0},
                {"field_id": "assembly_rows", "path": "assembly_rows", "field_kind": "list", "default": []},
                {"field_id": "root_assembly_id", "path": "root_assembly_id", "field_kind": "id", "default": ""},
            ],
            "deterministic_fingerprint": "",
            "extensions": {"source": "statevec0.test"},
        }
    ]


def source_state_payload() -> dict:
    return {
        "captured_tick": 7,
        "assembly_rows": [
            {"assembly_id": "assembly.alpha", "assembly_type_id": "assembly.engine.root"},
            {"assembly_id": "assembly.beta", "assembly_type_id": "assembly.generator"},
        ],
        "root_assembly_id": "assembly.alpha",
    }


def cloned_sys0_state() -> dict:
    from tools.xstack.testx.tests.sys0_testlib import cloned_state

    return copy.deepcopy(cloned_state())

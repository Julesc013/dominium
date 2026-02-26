"""Shared RS-2 conservation ledger helpers for TestX."""

from __future__ import annotations

import copy


_CONTRACT_SETS = [
    {
        "contract_set_id": "contracts.default.realistic",
        "quantities": [
            {
                "quantity_id": "quantity.mass_energy_total",
                "mode": "enforce_strict",
                "tolerance": 0,
                "allowed_exception_types": ["exception.numeric_error_budget"],
            },
            {
                "quantity_id": "quantity.charge_total",
                "mode": "enforce_strict",
                "tolerance": 0,
                "allowed_exception_types": ["exception.numeric_error_budget"],
            },
            {
                "quantity_id": "quantity.entropy_metric",
                "mode": "track_only",
                "tolerance": 0,
                "allowed_exception_types": ["exception.numeric_error_budget"],
            },
        ],
    },
    {
        "contract_set_id": "contracts.magic_relaxed",
        "quantities": [
            {
                "quantity_id": "quantity.mass_energy_total",
                "mode": "allow_with_ledger",
                "tolerance": 0,
                "allowed_exception_types": [
                    "exception.creation_annihilation",
                    "exception.field_exchange",
                    "exception.meta_law_override",
                    "exception.numeric_error_budget",
                ],
            },
            {
                "quantity_id": "quantity.charge_total",
                "mode": "track_only",
                "tolerance": 0,
                "allowed_exception_types": ["exception.numeric_error_budget"],
            },
            {
                "quantity_id": "quantity.entropy_metric",
                "mode": "track_only",
                "tolerance": 0,
                "allowed_exception_types": ["exception.numeric_error_budget"],
            },
        ],
    },
    {
        "contract_set_id": "contracts.null",
        "quantities": [
            {
                "quantity_id": "quantity.mass_energy_total",
                "mode": "ignore",
                "tolerance": 0,
                "allowed_exception_types": [],
            },
            {
                "quantity_id": "quantity.charge_total",
                "mode": "ignore",
                "tolerance": 0,
                "allowed_exception_types": [],
            },
            {
                "quantity_id": "quantity.entropy_metric",
                "mode": "track_only",
                "tolerance": 0,
                "allowed_exception_types": ["exception.numeric_error_budget"],
            },
            {
                "quantity_id": "quantity.ledger_balance",
                "mode": "track_only",
                "tolerance": 0,
                "allowed_exception_types": ["exception.numeric_error_budget"],
            },
        ],
    },
]

_QUANTITIES = [
    {"quantity_id": "quantity.mass_energy_total"},
    {"quantity_id": "quantity.mass"},
    {"quantity_id": "quantity.energy"},
    {"quantity_id": "quantity.charge_total"},
    {"quantity_id": "quantity.ledger_balance"},
    {"quantity_id": "quantity.entropy_metric"},
]

_EXCEPTION_TYPES = [
    {"exception_type_id": "exception.boundary_flux"},
    {"exception_type_id": "exception.field_exchange"},
    {"exception_type_id": "exception.creation_annihilation"},
    {"exception_type_id": "exception.coordinate_gauge"},
    {"exception_type_id": "exception.numeric_error_budget"},
    {"exception_type_id": "exception.meta_law_override"},
]


def build_policy_context(contract_set_id: str, physics_profile_id: str = "") -> dict:
    profile_id = str(physics_profile_id).strip() or "physics.test.{}".format(str(contract_set_id).replace(".", "_"))
    return {
        "active_shard_id": "shard.0",
        "pack_lock_hash": "pack_lock_hash.testx.rs2",
        "physics_profile_id": profile_id,
        "universe_physics_profile_registry": {
            "physics_profiles": [
                {
                    "physics_profile_id": profile_id,
                    "conservation_contract_set_id": str(contract_set_id),
                    "allowed_exception_types": [],
                }
            ]
        },
        "conservation_contract_set_registry": {
            "contract_sets": copy.deepcopy(_CONTRACT_SETS),
        },
        "quantity_registry": {
            "quantities": copy.deepcopy(_QUANTITIES),
        },
        "exception_type_registry": {
            "exception_types": copy.deepcopy(_EXCEPTION_TYPES),
        },
    }

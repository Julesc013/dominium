# Invariant Registry

This registry indexes invariants referenced by code comments and CI checks.
It complements (does not replace) `docs/arch/INVARIANTS.md`.

## Rules
- IDs are stable and never reused.
- Each invariant maps to an authoritative spec and enforcement location.
- New invariants must be added here and to the relevant spec.

## Core Entries (Initial)

| ID | Description | Source | Enforcement |
| --- | --- | --- | --- |
| CODEHYGIENE-CAT-A | Architectural enums are closed-world; no CUSTOM/OTHER. | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_forbidden_enums.py |
| CODEHYGIENE-CAT-B | Open-world taxonomies are registry IDs (data-driven). | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_switch_on_taxonomy.py |
| CODEHYGIENE-CAT-C | Magic numbers forbidden outside constants/data. | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_magic_numbers.py |
| CODEHYGIENE-CAT-D | Derived data is deterministic and non-authoritative. | docs/arch/CODE_DATA_BOUNDARY.md | scripts/ci/check_hygiene_scan.py |
| CTRL-NONINTERFERENCE | Control layers never alter authoritative outcomes. | docs/arch/NON_INTERFERENCE.md | tests/control/interference |
| CTRL-NO-SECRETS | No secrets in engine or game. | docs/arch/CONTROL_LAYERS.md | tests/control/audit |
| AUTH3-AUTH-001 | Authority gates actions only, never visibility. | docs/arch/AUTHORITY_AND_ENTITLEMENTS.md | tests/authority |
| AUTH3-ENT-002 | Entitlements gate authority issuance only. | docs/arch/DISTRIBUTION_AND_STOREFRONTS.md | tests/entitlement |
| AUTH3-DEMO-003 | Demo is an authority profile, not a build. | docs/arch/DEMO_AND_TOURIST_MODEL.md | tests/demo |
| AUTH3-TOURIST-004 | Tourists never mutate authoritative state. | docs/arch/DEMO_AND_TOURIST_MODEL.md | tests/tourist |
| AUTH3-SERVICE-005 | Services affect access only. | docs/arch/SERVICES_AND_PRODUCTS.md | tests/services |
| AUTH3-PIRACY-006 | Piracy contained by authority, not DRM. | docs/arch/PIRACY_CONTAINMENT.md | tests/piracy_containment |
| AUTH3-UPGRADE-007 | Authority upgrades/downgrades do not mutate state. | docs/arch/UPGRADE_AND_CONVERSION.md | tests/authority |
| AUTH3-SAVE-008 | Saves are tagged by authority scope. | docs/arch/UPGRADE_AND_CONVERSION.md | tests/authority |
| SCALE0-PROJECTION-001 | Scaling is a semantics-preserving projection. | docs/arch/SCALING_MODEL.md | tests/app/scale0_contract_tests.py |
| SCALE0-CONSERVE-002 | Conservation across collapse/expand is exact. | docs/arch/INVARIANTS_AND_TOLERANCES.md | tests/app/scale0_contract_tests.py |
| SCALE0-COMMIT-003 | Collapse/expand only at commit boundaries. | docs/arch/COLLAPSE_EXPAND_CONTRACT.md | tests/app/scale0_contract_tests.py |
| SCALE0-DETERMINISM-004 | Macro time ordering and scaling are deterministic. | docs/arch/MACRO_TIME_MODEL.md | tests/app/scale0_contract_tests.py |
| SCALE0-TOLERANCE-005 | Sufficient statistics within declared tolerances. | docs/arch/INVARIANTS_AND_TOLERANCES.md | tests/app/scale0_contract_tests.py |
| SCALE0-INTEREST-006 | Interest drives activation; no view-based scaling. | docs/arch/INTEREST_MODEL.md | tests/app/scale0_contract_tests.py |
| SCALE0-NO-EXNIHILO-007 | Expansion cannot create ex nihilo state. | docs/arch/COLLAPSE_EXPAND_CONTRACT.md | tests/app/scale0_contract_tests.py |
| SCALE0-REPLAY-008 | Replay equivalence across collapse/expand. | docs/arch/MACRO_TIME_MODEL.md | tests/app/scale0_contract_tests.py |
| SCALE3-BUDGET-009 | Scaling work is budget-gated and policy-controlled. | docs/arch/BUDGET_POLICY.md | tests/app/scale3_budget_tests.py |
| SCALE3-ADMISSION-010 | Budget refusal/defer is explicit and non-mutating. | docs/arch/BUDGET_POLICY.md | tests/app/scale3_budget_tests.py |
| SCALE3-CONSTCOST-011 | Per-commit cost is bounded by active fidelity only. | docs/arch/CONSTANT_COST_GUARANTEE.md | tests/app/scale3_budget_tests.py |

## Notes
- Full invariant list lives in `docs/arch/INVARIANTS.md`.
- Update this registry when adding enforcement checks or new invariant IDs.

Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Invariant Registry





This registry indexes invariants referenced by code comments and CI checks.


It complements (does not replace) `docs/architecture/INVARIANTS.md`.





## Rules


- IDs are stable and never reused.


- Each invariant maps to an authoritative spec and enforcement location.


- New invariants must be added here and to the relevant spec.





## Core Entries (Initial)





| ID | Description | Source | Enforcement |


| --- | --- | --- | --- |


| CODEHYGIENE-CAT-A | Architectural enums are closed-world; no CUSTOM/OTHER. | docs/architecture/CODE_DATA_BOUNDARY.md | scripts/ci/check_forbidden_enums.py |


| CODEHYGIENE-CAT-B | Open-world taxonomies are registry IDs (data-driven). | docs/architecture/CODE_DATA_BOUNDARY.md | scripts/ci/check_switch_on_taxonomy.py |


| CODEHYGIENE-CAT-C | Magic numbers forbidden outside constants/data. | docs/architecture/CODE_DATA_BOUNDARY.md | scripts/ci/check_magic_numbers.py |


| CODEHYGIENE-CAT-D | Derived data is deterministic and non-authoritative. | docs/architecture/CODE_DATA_BOUNDARY.md | scripts/ci/check_hygiene_scan.py |


| CTRL-NONINTERFERENCE | Control layers never alter authoritative outcomes. | docs/architecture/NON_INTERFERENCE.md | tests/control/interference |


| CTRL-NO-SECRETS | No secrets in engine or game. | docs/architecture/CONTROL_LAYERS.md | tests/control/audit |


| AUTH3-AUTH-001 | Authority gates actions only, never visibility. | docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md | tests/authority |


| AUTH3-ENT-002 | Entitlements gate authority issuance only. | docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md | tests/entitlement |


| AUTH3-DEMO-003 | Demo is an authority profile, not a build. | docs/architecture/DEMO_AND_TOURIST_MODEL.md | tests/demo |


| AUTH3-TOURIST-004 | Tourists never mutate authoritative state. | docs/architecture/DEMO_AND_TOURIST_MODEL.md | tests/tourist |


| AUTH3-SERVICE-005 | Services affect access only. | docs/architecture/SERVICES_AND_PRODUCTS.md | tests/services |


| AUTH3-PIRACY-006 | Piracy contained by authority, not DRM. | docs/architecture/PIRACY_CONTAINMENT.md | tests/piracy_containment |


| AUTH3-UPGRADE-007 | Authority upgrades/downgrades do not mutate state. | docs/architecture/UPGRADE_AND_CONVERSION.md | tests/authority |


| AUTH3-SAVE-008 | Saves are tagged by authority scope. | docs/architecture/UPGRADE_AND_CONVERSION.md | tests/authority |


| SCALE0-PROJECTION-001 | Scaling is a semantics-preserving projection. | docs/architecture/SCALING_MODEL.md | tests/app/scale0_contract_tests.py |


| SCALE0-CONSERVE-002 | Conservation across collapse/expand is exact. | docs/architecture/INVARIANTS_AND_TOLERANCES.md | tests/app/scale0_contract_tests.py |


| SCALE0-COMMIT-003 | Collapse/expand only at commit boundaries. | docs/architecture/COLLAPSE_EXPAND_CONTRACT.md | tests/app/scale0_contract_tests.py |


| SCALE0-DETERMINISM-004 | Macro time ordering and scaling are deterministic. | docs/architecture/MACRO_TIME_MODEL.md | tests/app/scale0_contract_tests.py |


| SCALE0-TOLERANCE-005 | Sufficient statistics within declared tolerances. | docs/architecture/INVARIANTS_AND_TOLERANCES.md | tests/app/scale0_contract_tests.py |


| SCALE0-INTEREST-006 | Interest drives activation; no view-based scaling. | docs/architecture/INTEREST_MODEL.md | tests/app/scale0_contract_tests.py |


| SCALE0-NO-EXNIHILO-007 | Expansion cannot create ex nihilo state. | docs/architecture/COLLAPSE_EXPAND_CONTRACT.md | tests/app/scale0_contract_tests.py |


| SCALE0-REPLAY-008 | Replay equivalence across collapse/expand. | docs/architecture/MACRO_TIME_MODEL.md | tests/app/scale0_contract_tests.py |
| SCALE3-BUDGET-009 | Scaling work is budget-gated and policy-controlled. | docs/architecture/BUDGET_POLICY.md | tests/app/scale3_budget_tests.py |
| SCALE3-ADMISSION-010 | Budget refusal/defer is explicit and non-mutating. | docs/architecture/BUDGET_POLICY.md | tests/app/scale3_budget_tests.py |
| SCALE3-CONSTCOST-011 | Per-commit cost is bounded by active fidelity only. | docs/architecture/CONSTANT_COST_GUARANTEE.md | tests/app/scale3_budget_tests.py |
| TERRAIN0-TRUTH-001 | Terrain truth is SDF fields; meshes are non-authoritative. | docs/architecture/TERRAIN_TRUTH_MODEL.md | tests/contract/terrain_contract_tests.py |
| TERRAIN0-PROC-002 | Terrain overlays are process-only and provenance-tagged. | docs/architecture/TERRAIN_OVERLAYS.md | tests/contract/terrain_contract_tests.py |
| TERRAIN0-NOSPECIAL-003 | Terrain bodies are generic; no planet/station special casing. | docs/architecture/TERRAIN_TRUTH_MODEL.md | tests/contract/terrain_contract_tests.py |
| TERRAIN0-DECAY-004 | No per-tick global erosion; decay is event-driven. | docs/architecture/DECAY_EROSION_REGEN.md | tests/contract/terrain_contract_tests.py |
| TERRAIN0-PHI-005 | Terrain collision/truth queries reference phi/SDF. | docs/architecture/TERRAIN_TRUTH_MODEL.md | tests/invariant/terrain_authority_invariant.py |
| MMO0-UNIVERSE-012 | The universe is logically single under distribution. | docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md | tests/app/mmo0_distributed_contract_tests.py |
| MMO0-OWNERSHIP-013 | Domain ownership is exclusive and commit-boundary only. | docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md | tests/app/mmo0_distributed_contract_tests.py |


| MMO0-ID-014 | Global identifiers are deterministic and collision-free. | docs/architecture/GLOBAL_ID_MODEL.md | tests/app/mmo0_distributed_contract_tests.py |


| MMO0-LOG-015 | Cross-shard interaction uses ordered, append-only logs. | docs/architecture/CROSS_SHARD_LOG.md | tests/app/mmo0_distributed_contract_tests.py |


| MMO0-TIME-016 | Distributed time and ordering preserve outcomes. | docs/architecture/DISTRIBUTED_TIME_MODEL.md | tests/app/mmo0_distributed_contract_tests.py |


| MMO0-RESYNC-017 | Join/resync is deterministic and capability-safe. | docs/architecture/JOIN_RESYNC_CONTRACT.md | tests/app/mmo0_distributed_contract_tests.py |


| MMO0-COMPAT-018 | Singleplayer and multiplayer semantics are unified. | docs/architecture/MMO_COMPATIBILITY.md | tests/app/mmo0_distributed_contract_tests.py |





| INV-CANON-INDEX | Canon index exists and is complete. | docs/architecture/CANON_INDEX.md | scripts/ci/check_repox_rules.py |
| INV-DOC-STATUS-HEADER | Docs require canonical status headers. | docs/architecture/CANON_INDEX.md | scripts/ci/check_repox_rules.py |
| INV-CANON-NO-HIST-REF | Canonical docs must not reference historical docs. | docs/architecture/CANON_INDEX.md | scripts/ci/check_repox_rules.py |
| INV-CANON-CODE-REF | Code references canonical docs only. | docs/architecture/CANON_INDEX.md | scripts/ci/check_repox_rules.py |
| INV-CANON-NO-SUPERSEDED | Canonical docs must not be superseded. | docs/architecture/CANON_INDEX.md | scripts/ci/check_repox_rules.py |
| INV-SCHEMA-VERSION-BUMP | Schema changes require schema_version update. | docs/architecture/SCHEMA_VERSIONING.md | scripts/ci/check_repox_rules.py |
| INV-REPORT-CANON | Canon compliance report emitted. | docs/architecture/CANON_INDEX.md | scripts/ci/compliance_report.py |

## Notes


- Full invariant list lives in `docs/architecture/INVARIANTS.md`.


- Update this registry when adding enforcement checks or new invariant IDs.

Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CHEM-1 Combustion & Fuel Chains Baseline

Date: 2026-03-05  
Scope: CHEM-1 phases 7-10 completion (proof/replay, enforcement, tests, final baseline report)

## Invariants and Contracts Upheld
- `docs/canon/constitution_v1.md` (A1 determinism, A2 process-only mutation, A6 provenance)
- `docs/canon/glossary_v1.md` canonical terminology
- `INV-ENERGY-TRANSFORM-REGISTERED`
- `INV-COMBUSTION-THROUGH-REACTION-ENGINE`
- `INV-NO-DIRECT-FUEL-DECREMENT`
- `INV-DERIVED-ONLY-COMPACTABLE`
- `INV-AFFORDANCE-DECLARED`

## Contract / Schema Impact
- No schema version bumps in this phase.
- Registry compatibility extended (non-breaking):
  - `data/registries/provenance_classification_registry.json` backfilled with CHEM-1 artifact classifications.
  - `data/meta/real_world_affordance_matrix.json` now declares CHEM series coverage.

## Energy Coupling Summary
- Combustion execution remains in `process.fire_tick`.
- Chemical-to-thermal conversion is ledgered via `transform.chemical_to_thermal`.
- Ledger conservation for combustion path is now explicit in runtime output mapping:
  - transformed chemical basis recorded as `quantity.energy_thermal`
  - dissipation still surfaced as `quantity.heat_loss`
- Optional chemical-to-electrical hook remains via `transform.chemical_to_electrical` when generator binding is declared.

## Efficiency Model
- Runtime keeps model-driven efficiency (`efficiency_permille`) from temperature, entropy, and mixture ratio inputs.
- Combustion event rows expose:
  - `chemical_energy_in`
  - `thermal_energy_out`
  - `electrical_energy_out`
  - `irreversibility_loss`
  - `efficiency_permille`

## Emission Handling
- Emissions are deterministic and logged through:
  - `combustion_emission_rows`
  - `pollutant_species_pool_rows`
  - `artifact.record.combustion_emission` RECORD artifacts
- POLL hook remains data-ready without requiring POLL solver activation.

## Explosion / Impulse Hook
- Explosive profile (`reaction.explosive_stub`) emits deterministic impulse rows:
  - `combustion_impulse_rows`
  - `impulse_hash_chain`
- Hook remains process-disciplined and references `process.apply_impulse` pathway.

## Proof / Replay Coverage
- Proof chains active:
  - `combustion_hash_chain`
  - `emission_hash_chain`
  - `impulse_hash_chain`
- Replay tool:
  - `python tools/chem/tool_replay_combustion_window.py --state-path build/chem/combustion_state.json --expected-state-path build/chem/combustion_state_expected.json`
  - Result: `complete`

## TestX Coverage Added
- `test_combustion_mass_conserved`
- `test_chemical_to_thermal_transform`
- `test_entropy_increment_on_burn`
- `test_emission_logged`
- `test_explosion_impulse_deterministic`
- `test_cross_platform_hash_match`

Run:
- `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_combustion_mass_conserved,test_chemical_to_thermal_transform,test_entropy_increment_on_burn,test_emission_logged,test_explosion_impulse_deterministic,test_cross_platform_hash_match`
- Result: `pass` (6/6)

## Gate Results (Current Repository Baseline)
- RepoX STRICT:
  - Command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: `pass` (17 warn findings; 0 fail/refusal).
  - Note: in-flight runs previously refused on `INV-WORKTREE-HYGIENE`; final committed baseline is clean.
- AuditX STRICT:
  - Command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - Result: `fail`
  - Promoted blockers: 7 (`E179_INLINE_RESPONSE_CURVE_SMELL`) in pre-existing non-CHEM modules.
- TestX STRICT (CHEM-1 subset): `pass`
- Combustion replay harness: `pass`
- Strict build check:
  - Command: `python -m py_compile tools/xstack/sessionx/process_runtime.py tools/xstack/testx/tests/chem_testlib.py tools/xstack/testx/tests/test_combustion_mass_conserved.py tools/xstack/testx/tests/test_chemical_to_thermal_transform.py tools/xstack/testx/tests/test_entropy_increment_on_burn.py tools/xstack/testx/tests/test_emission_logged.py tools/xstack/testx/tests/test_explosion_impulse_deterministic.py tools/xstack/testx/tests/test_cross_platform_hash_match.py`
  - Result: `pass`

## Topology Map
- Regenerated:
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/TOPOLOGY_MAP.md`
- Deterministic fingerprint: `86c35d6bb2f2ae27f7d69121e828950bf83229cf3d02982c8156b193ae01e373`

## Readiness for CHEM-2
- Ready on combustion substrate:
  - deterministic reaction/event/proof path established
  - energy ledger path explicit and replayable
  - emissions and impulse hooks available
- Remaining global blockers before full STRICT-green baseline:
  - existing repository-wide `E179` promotions outside CHEM scope
  - clean-worktree requirement at gate runtime

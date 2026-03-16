Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Energy Ledger Baseline

Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-3 completion baseline for deterministic energy accounting.

## 1) Canonical Transformations

Registered baseline transformations in `data/registries/energy_transformation_registry.json`:

- `transform.kinetic_to_thermal`
- `transform.electrical_to_thermal`
- `transform.chemical_to_thermal`
- `transform.potential_to_kinetic`
- `transform.external_irradiance`
- `transform.impulse_to_kinetic` (auxiliary boundary-transform hook)

## 2) Conservation Rules

- Non-boundary transforms are evaluated with deterministic energy-balance checks.
- Enforcing profiles (`phys.realistic.default`, `phys.realistic.rank_strict`) reject non-conserving non-boundary transforms.
- Boundary pathways must emit explicit `boundary_flux_event` rows and deterministic hash-chain updates.
- Violations route through `exception_event` emission (`conservation_violation`) instead of silent mutation.

## 3) Integration Summary

PHYS-3 runtime integration points:

- `process.apply_force` / `process.apply_impulse` / model-applied force: kinetic delta ledger integration.
- `process.elec.network_tick`: electrical dissipation mapped to `transform.electrical_to_thermal`.
- `process.fire_tick`: combustion heat mapped to `transform.chemical_to_thermal`.
- deterministic state surfaces:
  - `energy_ledger_entries`
  - `boundary_flux_events`
  - `energy_ledger_hash_chain`
  - `boundary_flux_hash_chain`

Proof/replay surfaces updated:

- control proof bundle includes `energy_ledger_hash_chain` and `boundary_flux_hash_chain`.
- net policy/shard payload surfaces mirror both chains for replay verification.

## 4) Enforcement Readiness

RepoX invariants added:

- `INV-ENERGY-TRANSFORM-REGISTERED`
- `INV-NO-DIRECT-ENERGY-MUTATION`

AuditX analyzers added:

- `E212_DIRECT_ENERGY_WRITE_SMELL` (`DirectEnergyWriteSmell`)
- `E213_MISSING_LEDGER_ENTRY_SMELL` (`MissingLedgerEntrySmell`)

Tool added:

- `tools/physics/tool_verify_energy_conservation`

## 5) Regression Baseline Status

PHYS-3 TestX additions:

- `test_energy_transformation_registered`
- `test_energy_conservation_enforced`
- `test_boundary_flux_logged`
- `test_cross_domain_energy_consistency`
- `test_replay_energy_hash_match`

## 6) Readiness for PHYS-4

PHYS-3 establishes:

- explicit deterministic transform registry governance,
- process-only energy mutation pathways,
- boundary flux logging and proof-chain hooks,
- replay-stable energy hash anchors.

This baseline is ready for PHYS-4 entropy/irreversibility layering without introducing ad hoc energy mutation paths.

## 7) Gate Execution Snapshot

Executed during PHYS-3 closeout (2026-03-04, local workspace):

- RepoX STRICT: `pass` (warnings present; no blocking refusals).
- AuditX STRICT: `fail` due existing promoted `E179_INLINE_RESPONSE_CURVE_SMELL` findings outside PHYS-3 scope.
- TestX PHYS-3 subset: `pass` for all five added PHYS-3 tests.
- TestX full STRICT: `fail` due broad pre-existing non-PHYS3 failures and refusals (for example session/create and unrelated subsystem suites).
- strict gate wrapper (`scripts/dev/gate.py strict`): `fail` on pre-existing structural/canon/doc-header/tool-hash constraints unrelated to PHYS-3 deltas.
- topology map: regenerated (`docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md`).

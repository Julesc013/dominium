Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Universe Contract Enforcement Baseline

## Pinned Versions
- Default v0.0.0 universes pin the full semantic contract `*.v1` family from `data/registries/semantic_contract_registry.json`.
- `UniverseIdentity` now carries:
  - `universe_contract_bundle_ref`
  - `universe_contract_bundle_hash`
- `SessionSpec` now carries:
  - `contract_bundle_hash`
  - `semantic_contract_registry_hash`

## Refusal Codes
- `refusal.contract.missing_bundle`
  - Used when identity/session artifacts do not carry the required contract pins or the sidecar file is missing.
- `refusal.contract.mismatch`
  - Used when pinned hashes do not match, the bundle fails registry validation, or replay sees a registry-hash mismatch.

## Proof Integration
- Boot and replay proof surfaces now include:
  - `semantic_contract_registry_hash`
  - `contract_bundle_hash`
  - `semantic_contract_proof_bundle`

## Confirmation
- No worldgen, logic, GEO, PHYS, TEMP, or runtime simulation algorithms were changed.
- The integration only pins and enforces semantic contract metadata on universe/session boot paths.

## Next Step
- Ready for `COMPAT-SEM-2` extension-discipline work with explicit migration tooling surfaces.

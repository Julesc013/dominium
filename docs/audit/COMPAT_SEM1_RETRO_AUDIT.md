Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# COMPAT-SEM-1 Retro Audit

## Scope
- UniverseIdentity creation/storage path
- SessionSpec creation/storage path
- Session boot and headless replay validation points
- Minimum integration points for semantic contract bundle pinning

## Findings
- `tools/xstack/sessionx/creator.py` already built and wrote `universe_contract_bundle.json` but did not pin its ref/hash into `UniverseIdentity`.
- `tools/xstack/sessionx/creator.py` did not write `contract_bundle_hash` into `SessionSpec`.
- `tools/xstack/sessionx/runner.py` and `tools/xstack/sessionx/script_runner.py` validated `UniverseIdentity.identity_hash` but did not enforce semantic contract sidecar presence or hash match.
- `tools/xstack/sessionx/common.py` hashed the full UniverseIdentity body except `identity_hash`, so new contract-bundle metadata had to be excluded explicitly to preserve identity-derived object IDs.
- Existing CompatX semantic helpers in `tools/compatx/core/semantic_contract_validator.py` were sufficient to avoid a large refactor; only a narrow bridge module was needed under `src/universe/`.

## Integration Decision
- Keep `universe_contract_bundle.json` as the canonical sidecar.
- Store `universe_contract_bundle_ref` and `universe_contract_bundle_hash` inside `UniverseIdentity`.
- Store `contract_bundle_hash` and `semantic_contract_registry_hash` in `SessionSpec`.
- Enforce presence and hash equality during load/replay with explicit refusal codes instead of silent repair.

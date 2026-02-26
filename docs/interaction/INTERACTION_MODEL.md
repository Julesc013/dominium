# Interaction Model

## Scope
- Interaction is a deterministic selection of `process_id`/intent for a perceived target.
- Affordances are derived from `PerceivedModel`, `LawProfile`, `AuthorityContext`, and UI metadata registries.
- UI and renderer are presentation layers and do not mutate TruthModel.

## Derivation Inputs
- `PerceivedModel`: visible target semantics and channels only.
- `LawProfile`: allowed/forbidden process set.
- `AuthorityContext`: entitlements and privilege gates.
- `interaction_action_registry`: display/payload/preview metadata only.

## Execution Contract
- Client creates deterministic intent/envelope payloads.
- Server/shard remains authoritative for validation and process execution.
- Outcomes are observed through updated `PerceivedModel`; no direct truth writes from UI.

## Ordering and Determinism
- Affordance list ordering: `(display_name_key, process_id, affordance_id)`.
- Stable `affordance_id`: `H(target_semantic_id, process_id)`.
- Parameter serialization and envelope construction must be canonical and deterministic.

## Preview Contract
- Preview is derived and best-effort.
- Preview modes:
  - `none`
  - `cheap` (Perceived-only summary)
  - `expensive` (inspection-cache backed; budget-gated)
- Preview never grants new epistemic channels and never mutates truth.

## Anti-cheat Notes
- Interaction spam and unauthorized action attempts are policy-detected.
- Ranked/private detail exposure is profile-driven; refusal reason codes remain stable.

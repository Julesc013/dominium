# SPEC_REFINEMENT_SEEDS (EXIST1)

Schema ID: REFINEMENT_SEEDS
Schema Version: 1.0.0
Status: binding.
Scope: deterministic seed sources for refinement and collapse.

## Purpose
Define deterministic seed material used to expand macro state into micro state
without nondeterministic RNG.

## Seed Sources (Canonical)
- world_seed
- epoch_id
- subject_id
- provenance_hash
- law_context_hash
- contract_id
- optional seed_commitment_hash (player-visible verification)

## Seed Composition Rules
- Concatenate sources in a fixed, documented order.
- Hash using the canonical engine hash for deterministic identity.
- No RNG without explicit seeded streams.

## Commitments
If seed commitments are exposed to players or tools:
- The commitment hash must be derived from the same seed material.
- Commitments are immutable once published.

## References
- `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
- `schema/existence/SPEC_COLLAPSE_CONTRACTS.md`

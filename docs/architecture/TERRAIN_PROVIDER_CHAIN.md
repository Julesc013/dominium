Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Terrain Provider Chain (TERRAIN0)

Status: binding.
Scope: provider chain composition for terrain fields.

## Provider model
Providers are deterministic field sources that may be stacked and composed.
They MUST be capability-registered, namespaced, and auditable.

Providers MUST:
- be composable and orderable.
- preserve determinism and replayability.
- be budget/interest bounded.
- emit provenance and support refusals.
- respect capability scope boundaries (game.* authoritative; client.ui.* presentational).

## Canonical provider resolution order
1) Procedural base provider
2) Anchor provider (real/artist data)
3) Simulation provider (slow, event-driven)
4) Player edit overlay provider
5) Tool/editor workspace overlay provider
6) Cache provider (disposable)

Resolution order is authoritative. Later providers override earlier providers
for the same field and region. Cache providers never override authoritative
providers; they are view-only and disposable.

## Deterministic composition
- Provider ordering is stable and deterministic.
- Ties are resolved by provider_id ordering.
- Composition uses deterministic operators per field type.

## See also
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
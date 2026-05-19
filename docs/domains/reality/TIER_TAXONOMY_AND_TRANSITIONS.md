Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Tier Taxonomy And Transitions

## Purpose
Define canonical fidelity tiers and deterministic, contract-checked transition rules for collapse/expand/refine/degrade operations.

## A) Tier Taxonomy
Canonical ordered tiers:
- `tier.macro`: global stocks/flows/distributions.
- `tier.meso`: subsystem/network/graph aggregates.
- `tier.micro`: explicit local assemblies/fields inside active interest zones.
- `tier.render`: presentation-only approximation tier; non-authoritative.

## B) Domain Tier Declarations
Each domain declares:
- supported tiers
- allowed tier transitions
- required invariant checks at boundaries
- tolerance envelopes and exception contract hooks

A domain must not transition through undeclared tier paths.

## C) Transition Types
- `collapse`: finer -> coarser (`micro->meso`, `micro->macro`, `meso->macro` when declared)
- `expand`: coarser -> finer (`macro->meso`, `macro->micro`, `meso->micro` when declared)
- `refine`: coarser -> finer within same tier family
- `degrade`: finer -> coarser within same tier family

## D) Constitutional Guarantees
Transition execution must satisfy all of the following:
- Deterministic selection and ordering from canonical state + policy inputs only.
- Conservation compatibility with RS-2: preserve within tolerance or emit allowed exception entries.
- Epistemic compatibility with ED-4: refinement must not create unauthorized information channels.
- Contract-bound refusals: strict invariant failures return deterministic refusal codes.

No wall-clock input may participate in transition decisions.

## E) Transition Artifacts
Every transition boundary operation emits deterministic transition artifacts.

Canonical `transition_event` fields:
- `event_id`
- `tick`
- `shard_id`
- `region_id`
- `domain_id`
- `solver_id` (optional)
- `from_tier`
- `to_tier`
- `reason` (`interest|budget|user_request|server_policy`)
- `invariant_checks` (list of check results)
- `ledger_hash`
- `deterministic_fingerprint`
- `extensions`

These artifacts are auditable and replay-stable.

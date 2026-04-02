Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ-2, Σ-3, Σ-4, Σ-5
Canonical Source: `AGENTS.md`
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/agents/AGENT_MIRROR_POLICY.md`

# Dominium Claude Mirror

This file is a derived mirror for Claude-style repository instruction entry points.
`AGENTS.md` remains the single canonical governance source.
If this file disagrees with `AGENTS.md` or any scope-specific canonical repo artifact, follow the canonical repo artifact and treat this file as stale.

## Canonical Reading Order

Read these first for substantive work:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. task-relevant canonical planning, semantic, runtime, schema, and policy artifacts
5. this mirror and other derived mirrors

Chat summaries do not override repo artifacts.

## Current Repo State

This mirror reflects the live post-early-`Φ` checkpoint:

- `Λ-0` through `Λ-6` complete
- `Σ-0` canonical governance complete
- `Φ-0` runtime kernel doctrine complete
- `Φ-1` component doctrine complete
- `Φ-2` runtime service doctrine complete
- current execution position: `post-Λ / post-Σ-0 / post-C-Σ0ΦA1 / post-Φ-2 / pre-Σ-1`

This is a derived continuity note grounded in committed repo artifacts, not a competing canon.

## Post-Φ Runtime Terms

Use these distinctions precisely:

- kernel hosts lawful deterministic execution; it does not define semantic ontology
- components are bounded runtime-facing functional units
- services are bounded coordinated runtime-facing mediation or hosting structures layered downstream of kernel and component law

Do not use stale pre-`Φ` vocabulary that collapses kernel, components, and services into one undifferentiated runtime blob.

## Ownership And Anti-Reinvention Cautions

Carry these cautions forward:

- `field/` vs `fields/` is not a free equivalence
- `schema/` vs `schemas/` is not a free equivalence
- `packs/` vs `data/packs/` is not a free equivalence
- projected or generated roots are not promoted to canonical authority for convenience
- thin `runtime/` naming does not make that root canonical

Extend from live repo embodiment rather than inventing a clean-room replacement layout.

## Working Boundaries

- planning-only prompts do not authorize implementation work
- mirrors do not create new law
- runtime convenience may not redefine semantic law, bridge law, or governance law
- products and UI may not redefine kernel, component, or service semantics
- review ownership-sensitive bindings before using overlapping roots

## Validation Floor

At minimum:

- verify prompt-required artifacts exist
- parse touched JSON when relevant
- check prose and machine-readable outputs for consistency
- run `git diff --check`
- report run and unrun checks honestly

For mirror precedence, maintenance, and conflict handling, use `docs/agents/AGENT_MIRROR_POLICY.md`.

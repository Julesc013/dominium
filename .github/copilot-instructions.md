Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ-2, Σ-3, Σ-4, Σ-5
Canonical Source: `AGENTS.md`
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/agents/AGENT_MIRROR_POLICY.md`

# Dominium Copilot Mirror

This file is a derived instruction mirror for GitHub Copilot-style repository entry surfaces.
It is not canonical governance.
If this file conflicts with `AGENTS.md` or any task-relevant canonical repo artifact, the canonical repo artifact wins and this mirror must be updated.

## Authority Order

Use this precedence:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. scope-specific canonical planning, semantic, runtime, schema, and policy artifacts relevant to the task
5. this derived mirror and other generated mirror surfaces
6. chat summaries or remembered transcript claims

## Current Execution Context

This mirror reflects the current post-early-`Φ` state:

- semantic constitution complete through `Λ-6`
- canonical governance established in `Σ-0`
- early runtime doctrine established through `Φ-0`, `Φ-1`, and `Φ-2`
- current execution position: `post-Λ / post-Σ-0 / post-C-Σ0ΦA1 / post-Φ-2 / pre-Σ-1`

This continuity note is derived from the current checkpoint lineage and early `Φ` doctrine.
It does not create a second governance canon.

## Runtime Vocabulary

Use the post-`Φ-2` runtime distinctions accurately:

- kernel: constitutional host for lawful deterministic runtime execution; it does not define semantic truth
- component: bounded runtime-facing functional unit with explicit identity and boundary
- service: bounded coordinated runtime-facing mediation or hosting structure that composes, coordinates, routes through, or exposes component behavior

Do not collapse these terms into one generic "engine", "service", "module", or "plugin" abstraction.

## Ownership Cautions

Do not normalize these splits for convenience:

- `fields/` is canonical semantic field substrate; `field/` is transitional
- `schema/` is canonical semantic contract law; `schemas/` is a projection or advisory mirror
- `packs/` and `data/packs/` have scoped ownership and are not interchangeable
- thin `runtime/` naming does not imply canonical authority
- generated roots under `build/`, `artifacts/`, `.xstack_cache/`, and `run_meta/` are evidence only

## Working Rules

- repo artifacts outrank chat memory
- extend over replace unless stronger doctrine or explicit human direction says otherwise
- planning-only prompts do not authorize runtime or refactor work
- runtime work may not redefine semantic doctrine, governance law, or ownership review outcomes
- products, UI, or convenience layers may not redefine kernel, component, or service law
- use `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md` before binding to overlapping roots

## Minimum Validation

Before claiming success:

- verify required artifacts exist
- parse touched JSON where relevant
- check prose and machine-readable mirrors for alignment when both are produced
- run `git diff --check`
- report what was run and what was not run

For full mirror-law details, use `docs/agents/AGENT_MIRROR_POLICY.md`.

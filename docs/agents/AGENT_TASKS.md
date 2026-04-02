Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ-2, Σ-3
Replacement Target: later `Σ-2` task-intent bridge and `Σ-3` task catalog should refine this guide without competing with `AGENTS.md`
Binding Sources: `AGENTS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`

# Agent Task Classes

## 1. Purpose

This file is a high-level human-readable guide to the main work classes recognized by `AGENTS.md`.

It is not the canonical governance source.
It is a derived companion that helps humans and agents understand:

- what each task class usually touches
- whether the class is normally planning-only or implementation-heavy
- what review posture usually applies
- what anti-reinvention expectations normally matter

Later `Σ-2` may refine this into a stronger task-intent bridge. Later `Σ-3` may freeze a machine-facing task catalog. Until then, `AGENTS.md` remains canonical.

## 2. Task Class Guide

| Work Class | Typical Surfaces | Default Posture | Typical Review Expectation | Anti-Reinvention Constraint |
| --- | --- | --- | --- | --- |
| `planning` | `docs/planning/**`, `data/planning/**`, checkpoint docs, dependency graphs, prompt inventories | planning-only | review if sequence, authority, or gates change | do not replace existing continuity artifacts with chat-only summaries |
| `doctrine_spec` | `specs/**`, `docs/contracts/**`, semantic constitutions, contract docs | planning-only unless prompt says otherwise | review if doctrine scope is foundational or cross-series | extend live doctrine stacks rather than inventing parallel theory |
| `governance` | `AGENTS.md`, `.agentignore`, `docs/agents/**`, future task and safety docs | planning-only | review if authority, safety, or ownership posture changes | strengthen the existing governance baseline rather than spawning a new one |
| `semantic_domain` | `specs/reality/**`, `data/reality/**`, domain roots, semantic registries | planning-first, sometimes implementation-adjacent later | review when bridge law, ownership, or foundational semantics move | formalize live semantic roots instead of clean-room replacement |
| `runtime_platform` | `engine/**`, `game/**`, `app/**`, `compat/**`, `control/**`, `core/**`, `net/**`, `process/**`, `server/runtime/**`, `server/persistence/**` | implementation-heavy | review for boundary freezes, missing foundations, or ownership-sensitive bindings | extract from the distributed substrate; do not crown convenience roots silently |
| `release_control_plane` | `release/**`, `repo/**`, `updates/**`, `data/architecture/**`, `data/registries/**`, `tools/xstack/**`, trust and publication surfaces | implementation-adjacent doctrine and tooling | review for public policy, licensing, trust, and provenance meaning | consolidate the live release/control-plane backbone instead of replacing it |
| `packaging_checkpointing` | `tmp/**`, reports, manifests, bundle scripts, curated archives | packaging-only | usually low review unless packaging touches policy or canon | prioritize planning value over bulk completeness |
| `validation_audit` | tests, schema parsers, proofs, reports, consistency checks, audit registries | mixed | review if findings imply doctrine drift or hidden risk | do not let generated evidence outrank canonical artifacts |
| `refactor_convergence` | merge-later families, root normalization, structural cleanup | implementation-heavy and review-sensitive | explicit human review is normal | respect `EXTEND_NOT_REPLACE_LEDGER` and ownership review before converging anything |

## 3. Planning-Dominant Classes

The following classes are usually planning-only unless a prompt explicitly says otherwise:

- `planning`
- `doctrine_spec`
- `governance`
- most early `semantic_domain`
- most early `release_control_plane`
- `packaging_checkpointing`

Planning-only means:

- no opportunistic runtime edits
- no structural cleanup just because a better layout is obvious
- no implementation claims without implementation work
- no hidden migration from prose into code

## 4. Implementation-Heavy Classes

The following classes often carry real code or structural impact:

- `runtime_platform`
- implementation-facing `semantic_domain`
- implementation-facing `release_control_plane`
- `refactor_convergence`

Implementation-heavy work still inherits the same governance floor:

- read canon and current planning state first
- respect ownership-sensitive roots
- preserve determinism, Process mutation law, and truth/perceived/render separation
- keep pack, schema, and release contracts explicit

## 5. Typical Review Triggers

Escalate or slow down when work:

- touches canon or glossary meaning
- changes authority order or governance posture
- binds to `field/` vs `fields/`, `schema/` vs `schemas/`, or `packs/` vs `data/packs/`
- changes release, licensing, trust, or public-policy meaning
- crosses from planning-only into implementation-heavy scope
- enters deep `Φ`, `Υ` policy, or `Ζ` live-ops territory

## 6. Practical Rule

If the task class is unclear:

1. treat the task as narrower than it sounds
2. read the ownership and gate artifacts again
3. prefer extension over replacement
4. avoid implementation work unless the prompt clearly asks for it
5. keep `AGENTS.md` as the canonical source

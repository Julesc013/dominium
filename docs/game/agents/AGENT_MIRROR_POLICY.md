Status: CANONICAL
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ-2, Σ-3, Σ-4, Σ-5
Replacement Target: later Σ prompts may refine mirror generation and use, but they must not create a competing governance canon
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`

# Agent Mirror Policy

## 1. Purpose and Scope

This document defines the mirror-generation and mirror-maintenance law for Dominium.
It exists because multiple agent ecosystems look for repository entry instructions in different places, but the project must still keep one canonical governance source.

Mirrors solve a projection problem:

- they provide concise entry instructions for vendor or tool ecosystems
- they project current canonical governance and runtime vocabulary into the surfaces those ecosystems actually read
- they reduce friction without creating a second governance universe

Mirrors do not solve:

- canonical governance authorship
- natural-language task intent mapping
- XStack task catalog definition
- MCP interface exposure
- final hardened safety policy

Those remain later `Σ` work.

## 2. Canonical vs Derived Rule

`AGENTS.md` remains the single canonical governance source.
Mirrors are derived projections.
They are subordinate to canonical repo artifacts and may never outrank them.

When instruction surfaces disagree, use this order:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. scope-specific canonical planning, semantic, runtime, schema, contract, release, and policy artifacts named by the active task
5. this mirror policy and other scope-specific canonical mirror-governance artifacts
6. derived mirror files such as `.github/copilot-instructions.md` and `CLAUDE.md`
7. chat summaries, remembered transcript claims, and uncommitted notes

If a mirror and canonical governance disagree, canonical governance wins and the mirror must be updated or removed.

## 3. Mirror Families

The allowed mirror families at this stage are:

- root ecosystem mirrors
  - examples: `.github/copilot-instructions.md`, `CLAUDE.md`
  - purpose: provide concise vendor-facing repository entry instructions
- path-specific ecosystem mirrors
  - examples: `.github/instructions/*.instructions.md`
  - purpose: capture real path-local differences only when those differences are stable and justified
- bounded agent profile mirrors
  - examples: `.claude/agents/*.md`
  - purpose: define tightly-scoped derived profiles only when the repo has a justified need for them

Current `Σ-1` decision:

- enable root ecosystem mirrors now
- defer path-specific GitHub instruction files
- defer `.claude/agents/` profiles

Those deferrals are intentional.
The current repo state does not justify path-scoped shadow instructions or privileged sub-agent profiles yet, and creating them now would increase drift risk before `Σ-2`, `Σ-4`, and `Σ-5`.

## 4. Precedence and Conflict Handling

Mirror conflict handling is mandatory:

- canonical artifacts always win
- mirrors never resolve doctrine disputes by themselves
- mirrors must reference the canonical sources they summarize
- mirrors must be regenerated or edited when canonical governance or the scoped canonical runtime vocabulary changes
- stale mirrors are a maintenance bug, not a new authority source

If path-specific instruction files are created later:

- they may narrow emphasis for their path
- they may not contradict root mirrors
- they may not contradict `AGENTS.md`
- they may not silently create path-local exceptions to canon

If a path needs a real exception, the exception must first be added to canonical governance or a task-specific canonical artifact.

## 5. Content Constraints

Mirrors may contain:

- concise authority reminders
- concise current execution-context notes
- ownership-sensitive caution summaries
- post-`Φ-2` runtime vocabulary reminders
- minimum validation reminders
- explicit links back to canonical governance and scoped canonical doctrine

Mirrors must not contain:

- new governance law
- vendor-specific doctrine that contradicts canon
- hidden exceptions to ownership review
- replacement task taxonomies
- new semantic, runtime, or release policy invented for one ecosystem only

Deep doctrinal detail belongs in canonical artifacts, not mirrors.

## 6. Ownership and Anti-Reinvention Caution

Mirrors must carry forward the current ownership-sensitive cautions.
They must not silently normalize:

- `field/` versus `fields/`
- `schema/` versus `schemas/`
- `packs/` versus `data/packs/`
- canonical versus generated or mirrored roots
- thin directory-name prominence into architectural authority

Mirrors must also preserve the extend-over-replace posture.
They exist to project current law into entry surfaces, not to restart governance from scratch for each tool.

## 7. Runtime Vocabulary Alignment

Mirrors created after early `Φ` must use the current runtime vocabulary accurately.
At minimum, they must preserve these distinctions:

- kernel: constitutional host for lawful deterministic runtime execution
- component: bounded runtime-facing functional unit
- service: bounded coordinated runtime-facing mediation or hosting structure

Mirrors must not:

- collapse kernel, component, and service into a single generic runtime term
- revert to stale pre-`Φ` wording
- let product, UI, or tool convenience redefine runtime-layer meaning

## 8. Lifecycle and Maintenance

Create or update mirrors when:

- a supported ecosystem uses a recognized repository instruction entry point
- canonical governance changes in a way the mirror summarizes
- ownership cautions or runtime vocabulary change
- checkpoint continuity shifts enough that a mirror would become misleading

Defer or remove mirrors when:

- the repo does not yet have a justified use case for them
- the mirror would mainly duplicate canonical governance without adding entry-surface value
- the mirror would create path-local or vendor-local drift risk

Later `Σ` prompts refine this layer as follows:

- `Σ-2` refines task-intent and natural-language mapping
- `Σ-3` aligns mirror language with the XStack task catalog
- `Σ-4` aligns mirror language with MCP exposure surfaces
- `Σ-5` hardens safety policy expectations

## 9. Anti-Patterns and Forbidden Shapes

The following mirror shapes are forbidden:

- a mirror becoming shadow canon
- vendor-specific instructions that contradict repo law
- path-specific mirrors silently overriding canonical doctrine
- mirrors that hide ownership cautions for convenience
- mirrors that bake in stale runtime or checkpoint vocabulary
- mirrors that imply generated surfaces are canonical because they are easy to consume
- mirrors that create hidden privileged agent classes without explicit canonical basis

## 10. Stability and Evolution

This artifact is a provisional but canonical mirror-governance policy.
It is stable enough for `Σ-1` and the next `Σ` prompts to consume, but it must evolve only through explicit updates to canonical artifacts rather than silent drift inside vendor mirrors.

The immediate downstream consumers are:

- `Σ-2`
- `Σ-3`
- `Σ-4`
- `Σ-5`

Those prompts may refine generation, structure, and safety expectations, but they must not replace `AGENTS.md` as the canonical governance source.

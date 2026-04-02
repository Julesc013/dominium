Status: CANONICAL
Last Reviewed: 2026-04-02
Supersedes: prior `AGENTS.md` v1.0.0 legacy control contract
Superseded By: none
Stability: stable
Future Series: Σ-1, Σ-2, Σ-3, Σ-4, Σ-5, Φ, Υ, Ζ
Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`

# Dominium Agent Governance

## 1. Purpose And Scope

`AGENTS.md` is the single canonical governance source for how humans, GPT/Codex agents, Claude-style agents, Copilot-style agents, MCP-mediated tools, and future execution prompts are allowed to operate in this repository.

It governs:

- authority precedence for repo-grounded work
- current program-state orientation for post-`Λ` execution
- core operating rules and non-negotiable execution constraints
- high-level work classes
- validation and reporting expectations
- review-gated and ownership-sensitive areas

It does not yet define:

- generated mirrors or vendor-specific instruction surfaces
- the natural-language task bridge
- the XStack task catalog
- MCP exposure contracts
- the final hardened agent safety policy

Those later surfaces must inherit from this file instead of inventing a parallel governance canon.

## 2. Authority Model

When repo artifacts, mirrors, generated outputs, and chat memory differ, use the following rule:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. scope-specific canonical planning, semantic, schema, contract, release, and policy artifacts named by the active task
5. operational registries, projections, mirrors, manifests, and generated evidence with intact provenance
6. chat summaries, remembered transcript claims, and uncommitted planning notes

The governing consequences are:

- repo artifacts outrank chat memory
- canon and glossary outrank all lower-level prose
- mirrors are derived, not canonical
- generated outputs are evidence only unless a stronger source explicitly promotes them
- if repo artifacts conflict materially, resolve the conflict with `docs/planning/AUTHORITY_ORDER.md` and `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md` rather than by convenience
- chat summaries may orient work, but they may not override repo truth

## 3. Current Program State

The current committed execution position is:

- `Ω`, `Ξ`, and `Π` complete
- `P-0` through `P-4` complete
- `0-0` planning hardening complete
- `Λ-0` through `Λ-6` complete
- current checkpoint: `post-Λ / pre-Σ-A`
- current executable prompt: `Σ-0`
- current execution block: `Σ-A`

Governance work must therefore consume the completed `Λ` doctrine rather than invent a new semantic baseline.

Continuity note:

- some older planning artifacts still retain pre-`Σ` or earlier `Σ` ordering text
- for governance execution, treat the active executable prompt and this file as the canonical post-`Λ` governance baseline until downstream planning mirrors are refreshed
- do not silently rewrite broader planning artifacts just to erase that drift unless a prompt explicitly targets them

## 4. Core Operating Rules

All humans and agents operating in this repo must follow these rules:

- extend over replace unless stronger doctrine or explicit human direction says otherwise
- do not introduce silent semantic drift
- do not bypass authority ordering, gate logic, or review checkpoints
- do not infer canon from convenience, shared code, or generated output shape
- do not replace repo truth with chat summaries or remembered intent
- do not silently rebind work to projected, generated, transitional, or quarantined roots
- planning-only prompts do not authorize runtime, refactor, or implementation work
- implementation-facing prompts do not authorize doctrine rewrites unless they explicitly target doctrine

## 5. Constitutional Execution Floor

The following inherited rules remain non-negotiable:

### 5.1 No mode flags; profiles only

- do not add or preserve hardcoded runtime mode branches
- express behavior composition through profiles, bundles, law surfaces, and explicit constraints

### 5.2 Process-only mutation

- authoritative truth mutation must occur through lawful deterministic Process execution
- UI, render, operator, tooling, or convenience layers must not mutate truth directly

### 5.3 Truth / Perceived / Render separation

- truth is authoritative
- perception and observation are filtered views
- rendering is presentation only
- later governance and tool work must not collapse those layers

### 5.4 Pack-driven integration

- optional content and capabilities must remain pack- and registry-driven
- missing packs require explicit refusal or degradation rather than hidden fallback magic

### 5.5 Determinism discipline

- use named RNG streams for authoritative randomness
- preserve thread-count invariance, deterministic ordering, and deterministic reductions
- preserve replay-hash equivalence for canonical partitions where applicable

### 5.6 Contract and compatibility discipline

- respect explicit schema identity, version, stability, migration, and refusal obligations
- do not perform silent migrations or compatibility reinterpretation
- update contract-facing docs when behavior or compatibility meaning changes

## 6. Required Doctrine Inputs Before Acting

Before substantive work, agents must consult the relevant authoritative repo artifacts for the task. At minimum, the normal doctrine packet is:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/POST_PI_EXECUTION_PLAN.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- the relevant `Λ` semantic constitution artifacts under `specs/reality/` and `data/reality/`
- `data/planning/final_prompt_inventory.json`
- `data/planning/dependency_graph_post_pi.json`

Task-specific additions are mandatory when scope expands:

- schema or compatibility work: `schema/**`, `docs/contracts/**`, compat metadata
- release or control-plane work: `docs/release/**`, `repo/release_policy.toml`, release and update registries
- runtime extraction work: relevant runtime roots plus ownership review and bridge law
- bridge or ownership-sensitive work: `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md` before binding to overlapping roots

## 7. Work Classes

The repository recognizes these high-level work classes:

- `planning`: sequencing, checkpoints, inventories, dependency maps, gates, and continuity work
- `doctrine_spec`: normative constitutional, contract, or specification work
- `governance`: agent, operator, instruction, refusal, and review-surface work
- `semantic_domain`: reality, domain, capability, representation, formalization, or bridge work
- `runtime_platform`: kernel, component, event, service, persistence, sandbox, or platform-boundary work
- `release_control_plane`: release, build, versioning, identity, trust, archive, publication, or control-plane work
- `packaging_checkpointing`: bundle, report, manifest, and checkpoint-curation work
- `validation_audit`: verification, consistency, evidence, audit, and proof work
- `refactor_convergence`: physical convergence, replacement, merge-later, or structure-normalization work

High-level task intent mapping is refined later. This file only defines the canonical class vocabulary and the minimum expectations attached to each class.

## 8. Validation And Reporting Expectations

Before claiming success, agents must:

1. state the relevant invariant documents or IDs being upheld
2. state whether contract or schema impact changed
3. use `FAST` validation at minimum unless the task is docs-only and explicitly exempt from stronger checks
4. verify that the target artifacts required by the prompt exist
5. parse touched JSON or schema artifacts where relevant
6. check internal consistency between prose and machine-readable mirrors when both are produced
7. run `git diff --check`
8. report what was run and what was not run
9. avoid claiming implementation progress on planning-only prompts

Validation strength must increase when task scope increases. A docs-only task does not excuse false claims about unrun runtime or build checks.

## 9. Review-Gated And Protected Areas

Explicit human review is required for work that:

- changes canon doctrine or glossary meaning
- reinterprets authority ordering, intake law, or this governance baseline
- touches replace-classified or do-not-replace surfaces in ways that exceed the prompt
- crosses unresolved or quarantined ownership areas
- changes release, publication, licensing, trust, or public policy meaning
- enters live-ops or `Ζ`-class territory
- alters foundational semantic meaning without an explicit doctrine-update prompt

Protected or caution-heavy zones include:

- `docs/canon/**`
- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `specs/reality/**`
- `schema/**`
- `docs/release/**`
- `release/**`, `repo/**`, `updates/**`, `security/**`
- generated echoes under `build/**`, `artifacts/**`, `.xstack_cache/**`, and `run_meta/**`

Protected does not mean untouchable. It means explicit scope, review awareness, and provenance discipline are required.

## 10. Ownership And Projection Cautions

Agents must not assume the following ownership-sensitive roots are equivalent peers:

- `fields/` is canonical semantic field substrate; `field/` is a transitional compatibility facade
- `schema/` is canonical semantic contract law; `schemas/` is a validator-facing projection or advisory mirror
- `packs/` is canonical in runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/` remains authoritative within authored pack content and declaration scope, but stays transitional and residual-quarantined for any attempted single-root convergence
- `specs/reality/` is canonical over `data/reality/`
- `docs/planning/` is canonical over `data/planning/`

Agents may not:

- silently bind new governance, runtime, task, or bridge work to the wrong side of those splits
- treat projections as semantic owners because they are easier to consume
- collapse residual quarantine into certainty by naming preference

## 11. Relation To Later Σ Work

This file is intentionally canonical but not overloaded.

Later `Σ` prompts refine derived surfaces only:

- `Σ-1` generates governance mirrors from this canonical source
- `Σ-2` formalizes high-level task intent and natural-language mapping
- `Σ-3` freezes the XStack task catalog
- `Σ-4` formalizes MCP and related interface exposure
- `Σ-5` hardens the agent safety policy

No later `Σ` prompt may create a competing governance canon. They must refine or project this layer.

## 12. Commit Discipline

When tracked repository files change:

- make frequent commits at meaningful boundaries
- use explicit, verbose, audit-grade commit messages
- write commit messages that are sufficient to reconstruct a later changelog
- do not invent commits for ignored or untracked checkpoint outputs only

## 13. Forbidden Moves

The following moves are forbidden unless a prompt explicitly authorizes them and the required review conditions are met:

- creating a parallel canonical governance file
- treating mirrors as canonical
- bypassing doctrine to "just get it done"
- replacing repo truth with prompt convenience or chat memory
- refactoring code during planning-only work
- binding runtime, governance, or release work to quarantined roots without review
- silently promoting generated outputs into semantic authority
- silently normalizing ownership drift because two roots look similar

## 14. Task Invocation Template

Use this block when framing future work:

```text
Task:
Goal:
Touched Paths:
Relevant Invariants:
Contracts/Schemas:
Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

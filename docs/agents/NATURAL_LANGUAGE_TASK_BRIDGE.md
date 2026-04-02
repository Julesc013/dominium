Status: CANONICAL
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: C-ΣA1ΦA2, Σ-3, Σ-4, Σ-5, Φ, Υ, Ζ
Replacement Target: later Σ prompts may refine catalogs, MCP exposure, and safety handling, but they must not replace this bridge with raw conversational authority
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/AGENT_TASKS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMA0_PHIA1_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`

# Natural-Language Task Bridge

## 1. Purpose and Scope

This document defines the canonical natural-language task bridge for Dominium.
It exists so freeform human or agent requests can be normalized into stable, lawful task classes instead of becoming the project's real execution contract by tone, convenience, or wording accidents.

The bridge solves three problems:

- conversational wording is often underspecified, overloaded, or misleading
- the same words can mean different things at different checkpoints
- later tooling, catalog, and interface work need stable task vocabulary rather than ad hoc prompt interpretation

This bridge governs:

- how natural-language requests are normalized into bounded task families
- how authority, ownership, and runtime cautions constrain that normalization
- how ambiguous requests are classified conservatively
- how later Σ work should inherit stable task-intent vocabulary

It does not yet define:

- the XStack task catalog
- MCP exposure surfaces
- the final hardened safety policy
- a vendor-specific prompt parser
- an execution engine that decides work without canonical repo doctrine

It is therefore a normalization layer, not a planner, not a policy engine, and not a replacement for canonical governance.

Continuity note:

- older planning artifacts still contain stale Σ ordering where `Σ-2` is safety policy and the natural-language bridge lands later
- the active checkpoint path and the completed `Σ-1` plus early `Φ-A1` artifacts establish this bridge now as the current local execution law
- this document follows that current checkpoint law and does not silently treat older sequencing drift as authoritative for intent normalization

## 2. Core Definition

The natural-language task bridge is the canonical classification layer that maps freeform requests into stable task families, review gates, authority requirements, and caution handling.

It is not:

- a source of new project law
- a freeform parser that treats lexical cues as commands
- a replacement for `AGENTS.md`
- a substitute for scope-specific semantic, runtime, release, or planning doctrine
- the XStack task catalog
- the MCP interface contract

The bridge exists because natural language is too lossy to act as the execution contract by itself.
Words like `runtime`, `package`, `fix`, `bridge`, `update`, `release`, or `service` can point to very different work classes depending on the live checkpoint, the roots touched, the authority surfaces involved, and the doctrine that already exists in-repo.

Later `Σ-3` may turn these families into a governed task catalog.
Later `Σ-4` may expose them through governed interfaces.
Later `Σ-5` may harden refusal and safety behavior around them.
Those later surfaces must consume this bridge rather than replacing it with raw chat phrasing.

## 3. Canonical vs Conversational Distinction

Natural language is not authoritative execution law.
It is an input to classify.

The authoritative order remains:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. scope-specific canonical planning, semantic, runtime, schema, contract, release, and policy artifacts
5. this task bridge and its machine-readable mirror
6. derived mirrors and generated artifacts
7. chat summaries, remembered transcript claims, and informal notes

The bridge therefore requires the following:

- freeform requests must be normalized before execution assumptions are made
- conversational intensity does not change work class by itself
- vendor mirror wording does not outrank canonical governance
- chat history may orient but may not override repo truth
- a request that sounds implementation-heavy may still normalize to planning, doctrine, or review-gated handling

If natural language and canonical repo doctrine disagree, canonical repo doctrine wins and the request must be reclassified or narrowed.

## 4. Task Family Taxonomy

At this stage, Dominium recognizes the following stable task families for natural-language normalization.

| Task Family | Constitutional Role | Default Posture | Typical Surfaces |
| --- | --- | --- | --- |
| `planning_checkpointing` | Sequence, checkpoint, dependency, continuity, and gate work. | planning-only | `docs/planning/**`, `data/planning/**`, checkpoint artifacts |
| `doctrine_specification` | Normative semantic, runtime, contract, governance, or policy specification work. | planning-only unless prompt explicitly targets implementation | `specs/**`, `docs/runtime/**`, `docs/contracts/**`, canonical governance docs |
| `governance_policy` | Governance, mirror, instruction, review, refusal, and operator/agent policy work. | planning-only | `AGENTS.md`, `.agentignore`, `docs/agents/**`, `data/agents/**` |
| `semantic_domain` | Domain, capability, bridge, formalization, representation, and semantic-law work. | planning-first | `specs/reality/**`, `data/reality/**`, semantic roots |
| `runtime_platform` | Kernel, component, service, persistence, replay, sandbox, and runtime-boundary work. | implementation-adjacent or implementation-heavy depending scope | `docs/runtime/**`, `engine/**`, `game/**`, `app/**`, `compat/**`, `control/**`, `core/**`, `net/**`, `process/**`, `server/runtime/**`, `server/persistence/**` |
| `product_app_shell` | Client, server, launcher, setup, tools, appshell, and product-facing shell work. | mixed | `client/**`, `server/**`, `launcher/**`, `setup/**`, `appshell/**`, product UI and command surfaces |
| `release_distribution_control_plane` | Release, publication, identity, trust, archive, update, and control-plane work. | implementation-adjacent doctrine or tooling | `release/**`, `repo/**`, `updates/**`, `security/**`, `docs/release/**` |
| `validation_audit` | Verification, proof, consistency, audit, diagnostics, and evidence work. | mixed | tests, proofs, reports, schema parsers, audit registries |
| `refactor_convergence` | Physical convergence, merge-later execution, replacement, and structural normalization. | implementation-heavy and review-gated | split or duplicated roots, convergence candidates, structural cleanup areas |
| `packaging_bundling` | Checkpoint bundles, reports, manifests, upload packages, and temporary curation artifacts. | packaging-only | `tmp/**`, bundle reports, manifests, support zips |
| `documentation_explanation` | Explanation, walkthrough, summarization, and docs that do not change doctrine meaning. | usually docs-only | explanatory docs, README-like surfaces, answer-oriented text |
| `analysis_inspection` | Investigation, codebase reading, classification, inventorying, and non-mutating inspection work. | read-only by default | repo-wide inspection, inventories, architecture evidence, reports |

These families are stable classification buckets, not yet the final task catalog.

## 5. Intent Normalization Rules

Natural-language requests must be normalized using the following rules.

### 5.1 Lexical Cues Are Suggestive, Not Authoritative

Words such as:

- `runtime`
- `service`
- `component`
- `release`
- `package`
- `fix`
- `bridge`
- `audit`
- `document`
- `refactor`

are only hints.
They do not decide the work class without checking the actual scope, touched roots, checkpoint state, and governing artifacts.

### 5.2 Repo State Constrains Classification

The same wording can normalize differently at different checkpoints.

Examples:

- `define runtime services`
  - before early `Φ-A1`: could be blocked or deferred
  - after `Φ-0` and `Φ-1`: can normalize to `doctrine_specification` plus `runtime_platform`
- `make a task bridge`
  - before `Σ-1`: could be premature
  - after mirrors and early `Φ`: can normalize to `governance_policy` plus `planning_checkpointing`

Checkpoint state is therefore part of classification, not post-processing.

### 5.3 Scope Beats Tone

Requests are normalized by:

1. identifying the affected roots or artifact families
2. identifying whether the request seeks classification, doctrine, implementation, validation, or packaging
3. checking review-gated and ownership-sensitive surfaces
4. checking whether the current checkpoint enables or forbids the work

Urgent or broad wording does not bypass this process.

### 5.4 Compound Requests Must Be Split

If a request contains multiple intents, classify them as:

- one primary task family
- zero or more secondary task families
- zero or more review-gate flags

Example:

- `update the runtime docs and zip a checkpoint`
  - primary: `documentation_explanation`
  - secondary: `packaging_bundling`
  - not a release task by default

### 5.5 Ambiguity Must Be Handled Conservatively

When ambiguity remains:

- prefer the narrower family over the broader one
- prefer planning, analysis, or doctrine over implementation if the prompt does not clearly authorize implementation
- prefer review-gated handling over silent escalation
- prefer explicit checkpoint-local continuity notes over stale older planning drift

### 5.6 Natural Language Does Not Rebind Ownership

If a request refers to a split family casually, the bridge must still preserve ownership review outcomes.

Examples:

- `update schema validators` does not make `schemas/**` canonical contract law
- `use runtime for service work` does not make `runtime/**` canonical runtime authority
- `package packs` does not flatten `packs/**` and `data/packs/**` into one scope

## 6. Distinguishing Nearby Task Classes

Some neighboring task families are easily confused.
The bridge must keep them distinct.

### 6.1 Planning vs Implementation

- planning/checkpointing work sequences, reviews, inventories, gates, and continuity
- implementation changes code, behavior, or runtime structure

If a request asks to `plan`, `review`, `map`, `sequence`, `checkpoint`, or `assess`, default to planning or analysis unless explicit implementation scope is present.

### 6.2 Doctrine/Specification vs Runtime Work

- doctrine/specification freezes normative meaning or boundary law
- runtime/platform work changes or extracts runtime structure, code, or runtime-facing architecture

A request to `define`, `formalize`, or `specify` kernel, component, or service law can still be doctrine/specification even when the subject is runtime.

### 6.3 Runtime Work vs Release/Control-Plane Work

- runtime/platform work concerns kernel, components, services, persistence, replay, lifecycle, and runtime execution boundaries
- release/control-plane work concerns build, publication, updates, trust, archive, release identity, and distribution behavior

The word `service` does not automatically imply control-plane work.
The word `update` does not automatically imply release policy.

### 6.4 Semantic/Domain Work vs Product UX Work

- semantic/domain work changes or freezes reality law, domain contracts, bridges, capability surfaces, or formalization rules
- product/app-shell work changes client, server, launcher, setup, or shell-facing behavior

UI phrasing does not authorize semantic reinterpretation.

### 6.5 Packaging/Checkpointing vs Release Packaging

- packaging/bundling work creates support artifacts such as checkpoint zips, reports, and manifests
- release/distribution/control-plane work creates or governs shipping artifacts, channels, trust, publication, or updater behavior

`Make me a zip` is not a release task by default.
It becomes release/control-plane work only when distribution, publication, channel, installer, artifact identity, or trust semantics are in scope.

### 6.6 Analysis/Inspection vs Code Change

- analysis/inspection is read-only unless the request explicitly escalates to changes
- code change requires explicit implementation or docs-update scope

Requests like `review`, `inspect`, `map`, `audit`, or `find` do not authorize edits by default unless the prompt or repo policy says otherwise.

### 6.7 Refactor/Convergence vs Greenfield Creation

- refactor/convergence changes physical structure, ownership alignment, or root layout
- doctrine/specification may describe future convergence without performing it

Vague requests such as `clean this up`, `normalize the repo`, or `fix the architecture` must not map straight to refactor execution.
They normalize first to `analysis_inspection`, `planning_checkpointing`, or `governance_policy` unless explicit convergence authority exists.

## 7. Runtime Vocabulary Alignment

Natural-language normalization after early `Φ-A1` must preserve the following runtime vocabulary precisely.

| Term | Required Meaning | Forbidden Collapse |
| --- | --- | --- |
| `kernel` | constitutional host for lawful deterministic runtime execution | not a synonym for app, engine root, or generic runtime blob |
| `component` | bounded runtime-facing functional unit with explicit identity and boundary | not a synonym for service, module, or product feature |
| `service` | bounded coordinated runtime-facing mediation or hosting structure | not a synonym for component, control-plane service, or generic orchestrator |
| `module` | implementation, packaging, or discovery surface | not a synonym for component or service meaning |
| `domain` | semantic unit governed by domain contracts | not a runtime grouping abstraction |
| `product` | client, server, launcher, setup, tools, appshell, or other shell surface | not runtime law owner by default |
| `pack/content` | declarative or authored content and capability expansion surface | not a runtime component or service by default |
| `mirror` | derived instruction or registry projection | not canonical governance |
| `canonical artifact` | normative owner of meaning in repo authority order | not automatically the easiest file to consume |
| `projected/generated artifact` | operational mirror, evidence, or generated output | not promoted to authority by convenience |

Requests that flatten these layers must be reclassified or handled conservatively.

## 8. Ownership and Authority Cautions

Natural-language requests must not bypass ownership or authority cautions already frozen in canonical doctrine.

The bridge must preserve all of the following:

- `field/` versus `fields/`
  - `fields/` remains canonical semantic field substrate
  - `field/` remains transitional
- `schema/` versus `schemas/`
  - `schema/` remains canonical semantic contract law
  - `schemas/` remains a projection or advisory mirror
- `packs/` versus `data/packs/`
  - these remain scoped ownership surfaces and are not interchangeable
- canonical versus projected/generated artifacts
  - generated evidence, caches, manifests, and mirrors do not become semantic or governance owners by conversational convenience
- older planning artifacts with stale sequence or numbering
  - stale prompt numbering or ordering does not outrank the current checkpoint law and committed canonical artifacts
- thin `runtime/` naming
  - natural-language `runtime` requests do not automatically bind to the `runtime/` root

If a request would cross these cautions, normalization must set review or clarification pressure rather than silently choosing the easy path.

## 9. Review-Gated Task Classes

Some normalized intents require human review or explicit gate handling even when the wording sounds ordinary.

At minimum, escalate when a request touches:

- canon doctrine or glossary meaning
- authority-order reinterpretation
- ownership-sensitive rebinding
- replace-classified or do-not-replace subsystems
- release, publication, licensing, trust, archive, or public policy meaning
- late `Ζ` or live-ops style work
- broad refactors that cross multiple authority layers
- foundational semantic, kernel, component, or service boundary reinterpretation outside the active doctrine prompt

The bridge does not grant permission to cross those gates.
It only ensures those requests normalize into review-aware handling rather than casual execution.

## 10. Examples of Normalized Intent

The following examples are representative and non-vendor-specific.

| Natural-Language Request | Normalized Primary Family | Secondary Families / Flags | Handling Note |
| --- | --- | --- | --- |
| `Create a checkpoint review for the current post-Φ state.` | `planning_checkpointing` | `documentation_explanation` | checkpoint/gating artifact, not runtime implementation |
| `Formalize a new bridge doctrine between ecology and logistics.` | `semantic_domain` | `doctrine_specification`, possible review gate | must consume domain contracts and cross-domain bridge law |
| `Define the next runtime persistence service boundary.` | `doctrine_specification` | `runtime_platform` | post-`Φ-A1` runtime vocabulary required; not a service implementation by default |
| `Update the Copilot mirror to reflect the new service model.` | `governance_policy` | `documentation_explanation` | mirror work remains derived and subordinate |
| `Make me a tmp zip for this checkpoint.` | `packaging_bundling` | `planning_checkpointing` | support artifact, not release distribution |
| `Freeze release-index rules for update channels.` | `release_distribution_control_plane` | `doctrine_specification`, likely review-aware | release and trust policy scope is in play |
| `Merge schema and schemas and clean up the repo.` | `refactor_convergence` | ownership-sensitive review gate | must not proceed casually; review and ownership law apply |
| `Explain how the kernel, components, and services differ.` | `documentation_explanation` | `analysis_inspection` | explanation only unless change scope is explicit |
| `Inspect whether the current service model contradicts AGENTS.` | `analysis_inspection` | `validation_audit`, `governance_policy` | read-only consistency check first |
| `Ship a zip to users with updated launcher and trust metadata.` | `release_distribution_control_plane` | `product_app_shell`, review gate | distribution, publication, and trust semantics are in scope |

## 11. Anti-Patterns and Forbidden Shapes

The following task-bridge shapes are forbidden:

- raw chat wording becomes de facto project law
- vague `fix the architecture` language maps directly to refactor execution
- `use runtime` silently binds work to the thin `runtime/` root
- packaging or checkpoint wording is silently treated as release distribution work
- mirror or tool wording overrides canonical governance
- natural-language convenience overrides ownership review outcomes
- runtime wording collapses kernel, component, service, module, and product into one generic `system`
- stale planning numbering is treated as more authoritative than the active checkpoint and committed canonical artifacts

## 12. Stability and Evolution

This artifact is a provisional but canonical task-intent bridge.
It is stable enough for immediate checkpoint consumption and for later catalog, interface, and safety refinements, but it must evolve through explicit canonical updates rather than hidden changes in prompt style or mirror wording.

The immediate downstream consumers are:

- checkpoint `C-ΣA1ΦA2`
- `Σ-3`
- `Σ-4`
- `Σ-5`

Those later prompts may refine:

- catalog structure
- interface exposure categories
- refusal and escalation hardening
- tool-facing task surfaces

They must not replace this bridge with raw conversational interpretation.

## 13. Direct Constitutional Answers

1. The natural-language task bridge is the canonical classification layer that maps freeform requests into stable task families, authority requirements, and review-aware handling.
2. Freeform language is not sufficient as the execution contract because wording is ambiguous, checkpoint-sensitive, and too weak to outrank repo doctrine.
3. The stable task families at this stage are planning/checkpointing, doctrine/specification, governance/policy, semantic/domain, runtime/platform, product/app-shell, release/distribution/control-plane, validation/audit, refactor/convergence, packaging/bundling, documentation/explanation, and analysis/inspection.
4. Ambiguous requests are normalized conservatively by checking affected roots, checkpoint state, review gates, ownership cautions, and whether the wording truly authorizes implementation.
5. The ownership and runtime cautions that must survive normalization are the `field/` versus `fields/`, `schema/` versus `schemas/`, and `packs/` versus `data/packs/` splits; canonical versus projected/generated distinctions; stale planning drift; and the requirement to preserve post-`Φ-A1` kernel/component/service vocabulary.
6. This bridge now enables checkpoint `C-ΣA1ΦA2` and later `Σ-3`, `Σ-4`, and `Σ-5`.

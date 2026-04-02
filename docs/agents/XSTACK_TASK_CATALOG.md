Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ-4, Σ-5, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMAA1_PHIA2_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/XSTACK.md`, `docs/xstack/CI_GUARDRAILS.md`

# Dominium XStack Task Catalog

## 1. Purpose and Scope

This document defines the canonical XStack task catalog for Dominium.
It exists because `Σ-2` froze the natural-language task bridge, while `Φ-0` through `Φ-5` froze the deeper runtime vocabulary that later tool surfaces must preserve.
The repository now needs a stable repo-native task surface taxonomy so normalized task families can bind to lawful execution surfaces without letting prompt phrasing, mirror wording, or ad hoc script names become the true interface contract.

The XStack task catalog governs:

- what an XStack task is
- why the catalog exists as a distinct layer after natural-language normalization
- how normalized task families map onto stable repo-native task surfaces
- what output classes each task family may lawfully produce
- which task families are planning-only, implementation-capable, read-only, packaging-only, or review-gated
- what later MCP exposure and safety policy work must consume once the catalog exists

This prompt does not:

- implement MCP exposure
- implement the full safety policy
- turn every script or command into a catalog entry
- redefine semantic doctrine, runtime doctrine, governance doctrine, or release doctrine
- authorize unsafe automation by naming a task family

The task catalog therefore sits:

- downstream of canonical governance, mirror policy, and the natural-language task bridge
- downstream of the completed semantic and runtime doctrine
- upstream of later `Σ-4` MCP exposure and `Σ-5` safety hardening

## 2. Core Definition

In Dominium, an XStack task is a cataloged, repo-native, authority-aware task surface class that binds a normalized task family to:

- bounded authoritative inputs
- allowed output classes
- a default execution posture
- review expectations
- ownership and runtime cautions
- later MCP and safety expectations

An XStack task is distinct from:

- `raw prompt text`
  - prompts are inputs to normalize, not the stable execution contract
- `mirror instructions`
  - mirrors are derived guidance and may not define an independent task universe
- `scripts or commands by themselves`
  - scripts are implementation evidence and possible task realizations, not canon by name alone
- `runtime services`
  - services are runtime structures; tasks are governed operator and agent work surfaces
- `products`
  - client, server, launcher, setup, tools, and appshell are product or shell surfaces, not task families
- `release artifacts`
  - shipping artifacts are outputs or governed surfaces, not the task-catalog layer itself

Stable task surfaces are needed because:

- raw prompts are too lossy and checkpoint-dependent to serve as the true interface
- script names drift over time and often encode implementation detail rather than lawful scope
- mirrors are intentionally derived and subordinate
- runtime, semantic, release, and governance work must remain distinct rather than flattened into generic automation verbs

## 3. Canonical Task-Catalog Role

The XStack task catalog is the stable repo-native execution surface taxonomy for post-`Φ-A2` governance alignment.

Its constitutional role is:

- downstream of `AGENTS.md`
- downstream of the mirror policy
- downstream of the natural-language task bridge
- downstream of semantic and runtime doctrine
- upstream of later MCP exposure categories
- upstream of later safety hardening

The catalog must not become:

- a second governance canon
- a replacement for authority ordering
- a replacement for runtime or semantic doctrine
- a vendor-specific command map
- a hidden script registry that silently outranks the repo

Catalog inclusion means:

- the family is recognized as a stable task surface class
- its inputs, outputs, and cautions are explicit
- later tools may reason about it

Catalog inclusion does not mean:

- it is automatically safe
- it is automatically autonomous
- it is automatically remotely exposed
- it may override ownership review or runtime law

## 4. Task Family Taxonomy

The XStack task catalog preserves the normalized families from the natural-language task bridge, but upgrades them into stable repo-native task surfaces.

The constitutional family set is:

| Task Family | Core Purpose | Default Posture |
| --- | --- | --- |
| `planning_checkpointing` | sequence, checkpoint, dependency, continuity, and gate work | planning-only |
| `doctrine_specification` | normative semantic, runtime, contract, governance, or policy specification work | planning-only |
| `governance_policy` | governance, mirror, instruction, review, refusal, and operator or agent policy work | planning-only |
| `semantic_domain` | domain, capability, bridge, representation, formalization, and semantic-law work | planning-first |
| `runtime_platform` | kernel, component, service, binding, state, lifecycle, persistence-boundary, and runtime-architecture work | implementation-capable |
| `product_app_shell` | client, server, launcher, setup, appshell, and product-shell work | mixed |
| `release_distribution_control_plane` | release, publication, archive, trust, identity, update, and control-plane work | implementation-capable and review-heavy |
| `validation_audit` | validation, proof, diagnostics, audit, and evidence-emission work | read-only or evidence-emitting by default |
| `refactor_convergence` | structural convergence, replacement, merge-later execution, and physical normalization | implementation-capable and review-gated |
| `packaging_bundling` | checkpoint bundles, support packages, bundle manifests, registry compile support, and packaging curation | packaging-only |
| `documentation_explanation` | explanatory docs, walkthroughs, summaries, and non-canonical-meaning text updates | docs-only |
| `analysis_inspection` | investigation, classification, inventorying, and read-only architectural or repo inspection | read-only |

These families are stable surface classes.
They are not a command list and not a commitment that every family is equally automatable.

## 5. Task Surface Structure

Each cataloged task family must be expressible through the same structural fields.

At minimum, every task family defines:

- `purpose`
  - what class of repo work the family exists to support
- `typical authoritative inputs`
  - which canonical artifacts or root families must govern execution
- `allowed output classes`
  - what the family may lawfully produce
- `default execution posture`
  - planning-only, implementation-capable, read-only, packaging-only, or docs-only
- `review expectation`
  - whether human review is usually expected, conditional, or required
- `ownership-sensitive cautions`
  - whether the family commonly touches split-root or canonical-versus-projected hazards
- `runtime-semantic coupling cautions`
  - whether the family must preserve kernel/component/service/binding/state/lifecycle versus domain/product distinctions
- `later MCP eligibility`
  - whether the family is a candidate, limited candidate, or review-gated candidate for later MCP exposure
- `later safety-hardening requirement`
  - what level of later refusal, permission, escalation, or bounded-autonomy hardening it will require
- `prohibited conflations`
  - what the family must not collapse into by convenience

These structural fields stabilize the catalog without overcommitting to a specific execution engine.

## 6. Cataloged Task Families

### 6.1 `planning_checkpointing`

- Purpose: sequence, checkpoint, dependency, gate, continuity, and prompt-state work.
- Typical authoritative inputs: `AGENTS.md`, `docs/planning/**`, `data/planning/**`, active checkpoint reviews, prompt inventories, dependency graphs.
- Allowed output classes: checkpoint docs, dependency maps, plan registries, continuity notes, gate reviews, sequencing summaries.
- Default posture: planning-only.
- Review expectation: review-aware whenever authority ordering, gates, or active sequencing would materially change.
- Ownership cautions: high for planning-doc versus planning-JSON authority and stale numbering drift.
- Runtime-semantic coupling cautions: must not promise runtime, semantic, release, or safety outcomes that doctrine has not yet frozen.
- Later MCP eligibility: bounded candidate only; exposed operations must stay narrow and checkpoint-aware.
- Later safety hardening: medium; must block prompt-driven silent checkpoint advancement.

### 6.2 `doctrine_specification`

- Purpose: freeze or refine normative semantic, runtime, contract, governance, or policy meaning.
- Typical authoritative inputs: canonical doctrine for the scoped layer, `AGENTS.md`, current checkpoint law, relevant semantic or runtime specs.
- Allowed output classes: canonical docs, machine-readable mirrors paired to those docs, doctrine registries, scoped normative reports.
- Default posture: planning-only.
- Review expectation: high whenever foundational meaning, authority, ownership, bridge law, or runtime boundaries are affected.
- Ownership cautions: high across semantic, runtime, and schema surfaces.
- Runtime-semantic coupling cautions: must preserve post-`Φ` vocabulary and may not let products, tools, or scripts redefine layer meaning.
- Later MCP eligibility: review-gated candidate only.
- Later safety hardening: high; doctrine tasks must not become unconstrained rewrite authority.

### 6.3 `governance_policy`

- Purpose: govern agents, mirrors, task surfaces, review expectations, refusal posture, and operator-facing policy layers.
- Typical authoritative inputs: `AGENTS.md`, `.agentignore`, `docs/agents/**`, `data/agents/**`, authority order, mirror policy, task bridge, checkpoints.
- Allowed output classes: governance docs, derived registries, mirror-alignment updates, policy summaries, refusal or escalation posture docs.
- Default posture: planning-only.
- Review expectation: high whenever authority order, review gates, or policy posture change.
- Ownership cautions: high because governance work must preserve split-root cautions rather than simplify them away.
- Runtime-semantic coupling cautions: must preserve the post-`Φ` runtime nouns but must not collapse into runtime implementation design.
- Later MCP eligibility: limited candidate; governance inspection surfaces may later be exposed, but governance mutation surfaces remain tightly gated.
- Later safety hardening: high.

### 6.4 `semantic_domain`

- Purpose: define or refine domains, capability surfaces, bridges, formalization, ladders, and semantic-law relationships.
- Typical authoritative inputs: `specs/reality/**`, semantic ownership review, player desire acceptance map, bridge law, formalization chain, representation ladders.
- Allowed output classes: domain specs, bridge specs, semantic registries, doctrine mirrors, scoped semantic evidence docs.
- Default posture: planning-first.
- Review expectation: high whenever ownership, bridges, capability meaning, or canonical semantic roots are touched.
- Ownership cautions: very high.
- Runtime-semantic coupling cautions: semantic tasks may inform runtime surfaces later but may not let runtime convenience redefine domain law.
- Later MCP eligibility: narrow, review-gated candidate.
- Later safety hardening: high.

### 6.5 `runtime_platform`

- Purpose: define, inspect, or implement bounded runtime surfaces while preserving kernel, component, service, binding, state, lifecycle, and product distinctions.
- Typical authoritative inputs: `docs/runtime/**`, relevant runtime roots, semantic inputs consumed by the runtime layer, checkpoints, ownership review, bridge law.
- Allowed output classes: runtime doctrine docs, runtime registries, bounded runtime code, validation hooks, support manifests, scoped runtime reports.
- Default posture: implementation-capable.
- Review expectation: medium to high depending on whether the task freezes doctrine, changes boundaries, or crosses ownership-sensitive roots.
- Ownership cautions: high for any semantic or packaging adjacency.
- Runtime-semantic coupling cautions: very high; task surfaces must preserve kernel/component/service/binding/state/lifecycle vocabulary and must not imply semantic ownership.
- Later MCP eligibility: selective candidate only.
- Later safety hardening: high.

### 6.6 `product_app_shell`

- Purpose: work on client, server, launcher, setup, appshell, and other product-shell surfaces without turning shell flow into runtime or semantic canon.
- Typical authoritative inputs: product-shell roots, scoped runtime doctrine, semantic doctrine where user-visible behavior reflects domain meaning, governance doctrine where instruction surfaces are involved.
- Allowed output classes: product-shell docs, shell-local code, adapters, session-flow support assets, presentation or control wrappers, bounded product diagnostics.
- Default posture: mixed.
- Review expectation: medium; higher if shell work risks redefining runtime, semantic, or governance meaning.
- Ownership cautions: medium to high depending on proximity to semantic or runtime roots.
- Runtime-semantic coupling cautions: high; products may consume runtime surfaces but may not define kernel, service, or domain meaning by convenience.
- Later MCP eligibility: selective and safety-gated candidate only.
- Later safety hardening: high where remote or autonomous control could be implied.

### 6.7 `release_distribution_control_plane`

- Purpose: govern release, publication, trust, signing, archive, distribution, updater, and control-plane surfaces.
- Typical authoritative inputs: `docs/release/**`, `release/**`, `repo/**`, `updates/**`, `security/**`, trust policy, provenance rules, compatibility doctrine.
- Allowed output classes: release docs, manifests, trust registries, update metadata, archive records, policy reports, controlled release tooling updates.
- Default posture: implementation-capable and review-heavy.
- Review expectation: high.
- Ownership cautions: high for canonical-versus-generated surfaces and pack/content versus packaged distribution scope.
- Runtime-semantic coupling cautions: must not let release/control-plane tasks redefine runtime or semantic truth.
- Later MCP eligibility: generally review-gated and likely limited.
- Later safety hardening: very high.

### 6.8 `validation_audit`

- Purpose: run, curate, or summarize validation, proof, consistency, diagnostics, and audit surfaces.
- Typical authoritative inputs: canonical doctrine, schema contracts, audit registries, CI guard definitions, test registries, validation entrypoints, scoped runtime or semantic artifacts.
- Allowed output classes: reports, audit findings, validation summaries, evidence registries, deterministic logs, refusal evidence, proof bundles.
- Default posture: read-only or evidence-emitting by default.
- Review expectation: conditional; findings are review-relevant when they imply doctrine drift, hidden risk, or authority ambiguity.
- Ownership cautions: medium to high because evidence must not outrank canon.
- Runtime-semantic coupling cautions: must report against post-`Φ` distinctions rather than flattening runtime layers.
- Later MCP eligibility: strong candidate for bounded exposure, especially read-only or report-emitting tasks.
- Later safety hardening: medium to high depending on whether execution or only inspection is exposed.

### 6.9 `refactor_convergence`

- Purpose: execute or plan structural convergence, merge-later family resolution, physical normalization, or replacement-sensitive cleanup.
- Typical authoritative inputs: extend-not-replace ledger, ownership review, authority order, current checkpoints, convergence plans, scoped runtime or semantic doctrine.
- Allowed output classes: convergence plans, reviewed structural changes, merge reports, replacement-safe refactor patches, follow-up inventories.
- Default posture: implementation-capable and review-gated.
- Review expectation: explicit human review is normal.
- Ownership cautions: very high.
- Runtime-semantic coupling cautions: high because convergence can silently erase runtime or semantic distinctions if under-specified.
- Later MCP eligibility: not eligible by default.
- Later safety hardening: very high.

### 6.10 `packaging_bundling`

- Purpose: create or validate checkpoint bundles, support packages, bundle manifests, registry-compile support outputs, and other non-distribution packaging artifacts.
- Typical authoritative inputs: bundle profiles, pack manifests, packaging policy docs, scoped registry compile inputs, checkpoint instructions, packaging support scripts.
- Allowed output classes: support bundles, bundle manifests, bundle validation reports, compiled support registries, checkpoint zips, packaging summaries.
- Default posture: packaging-only.
- Review expectation: usually moderate; higher when packaging touches policy, trust, or ownership-sensitive surfaces.
- Ownership cautions: high for `packs/` versus `data/packs/`, canonical versus generated artifacts, and packaging versus release distribution.
- Runtime-semantic coupling cautions: must not silently flatten pack/content, runtime activation, and release distribution.
- Later MCP eligibility: selective candidate only.
- Later safety hardening: medium to high.

### 6.11 `documentation_explanation`

- Purpose: explain, summarize, walk through, or document repository state without silently rewriting canonical meaning.
- Typical authoritative inputs: canonical docs for the scoped layer, active checkpoints, current registries, validated runtime or semantic artifacts.
- Allowed output classes: explanatory docs, summaries, walkthroughs, inventories, answer-oriented notes, scoped support docs.
- Default posture: docs-only.
- Review expectation: low to medium unless explanatory text risks becoming shadow doctrine.
- Ownership cautions: medium because explanation may accidentally promote projections or stale wording.
- Runtime-semantic coupling cautions: must preserve post-`Φ` vocabulary and avoid flattening runtime layers into generic system language.
- Later MCP eligibility: strong candidate for bounded read or explain surfaces.
- Later safety hardening: medium.

### 6.12 `analysis_inspection`

- Purpose: inspect, classify, inventory, compare, map, or assess repo state without mutating tracked implementation or doctrine by default.
- Typical authoritative inputs: repo artifacts across the scoped layer, checkpoints, inventories, runtime or semantic evidence roots, audit outputs.
- Allowed output classes: analyses, inventories, classifications, evidence summaries, inspection reports, architectural notes.
- Default posture: read-only.
- Review expectation: findings may trigger review, but the task family itself is non-mutating by default.
- Ownership cautions: medium because analysis may still drift if it mistakes mirrors or generated outputs for canon.
- Runtime-semantic coupling cautions: must preserve post-`Φ` distinctions in its reporting vocabulary.
- Later MCP eligibility: strong candidate for bounded read-only exposure.
- Later safety hardening: medium.

## 7. Authority and Ownership Constraints

Task surfaces must remain subordinate to authority order and ownership review.

The governing rules are:

- task surfaces must not bypass canonical governance
- task surfaces must not silently bind to ownership-ambiguous roots
- task surfaces must distinguish canonical versus projected or generated artifacts
- task surfaces must not infer semantic or runtime canon from convenience, script proximity, or path prominence
- task surfaces must preserve the planning-docs-over-planning-JSON rule for checkpoint interpretation
- task surfaces must treat mirrors, vendor instructions, and generated evidence as derived and subordinate

The key ownership cautions remain:

- `field/` versus `fields/`
- `schema/` versus `schemas/`
- `packs/` versus `data/packs/`
- canonical versus projected/generated artifacts
- thin `runtime/` root non-canonicality
- stale planning numbering drift

Cataloging a family does not relax any of those cautions.

## 8. Runtime Vocabulary Alignment

The task catalog must preserve the post-`Φ` runtime vocabulary exactly enough for later tooling and policy to reason over it.

At minimum, cataloged task surfaces must keep these distinctions explicit:

- `kernel`
  - constitutional host for lawful deterministic runtime execution
- `component`
  - bounded runtime-facing functional unit
- `service`
  - bounded coordinated runtime-facing mediation or hosting structure
- `domain-service binding`
  - lawful service-domain attachment grammar
- `state externalization`
  - law governing authoritative versus derived, transient, projected, and continuity-relevant state
- `lifecycle`
  - law governing runtime posture changes without semantic drift
- `domain`
  - semantic unit governed by domain contracts
- `product`
  - client, server, launcher, setup, appshell, or other shell surface
- `pack/content`
  - declarative or authored expansion surface
- `mirror`
  - derived projection rather than canonical owner
- `canonical versus projected/generated artifact`
  - explicit authority distinction rather than convenience choice

Task surfaces must not flatten these layers into generic `system`, `service`, or `runtime` wording.

## 9. Catalogability versus Non-Catalogability

Not all work should become a stable XStack task surface.

Work that should remain non-cataloged or strongly gated includes:

- fundamental canon rewrites
- unresolved ownership rebinding
- release, publication, licensing, trust, or public-policy changes with high risk
- late `Ζ` live-ops work
- broad multi-layer refactors without explicit review
- one-off emergency shell procedures that have not been normalized into stable doctrine
- operations whose safe execution model depends on later MCP or safety-policy constraints that do not yet exist

The catalog therefore defines lawful task families, not a universal permission lattice.

## 10. Relationship to Later MCP Exposure

Later MCP work must consume this task catalog.
It may not invent its own unrelated task universe.

The governing rules are:

- MCP surfaces are downstream of the task catalog
- catalogability does not imply automatic remote or tool exposure
- later MCP work must narrow and gate exposure using the family posture, review expectation, ownership caution, and runtime-coupling caution already defined here
- read-only or evidence-emitting families are generally stronger MCP candidates than review-heavy mutation families

This prompt therefore stops at cataloging.
It does not yet define the MCP surface map.

## 11. Relationship to Later Safety Policy

The task catalog exists before full safety policy hardening.
That is intentional.

The governing rules are:

- task catalog inclusion is not permission for unconstrained autonomous execution
- later `Σ-5` must harden refusal, escalation, autonomy, and permission rules using this catalog
- review-heavy or ownership-sensitive families remain review-heavy or ownership-sensitive even if later tools can invoke them
- catalogability is a classification statement, not a blanket safety approval

## 12. Examples of Cataloged Task Classes

Representative cataloged task classes include:

- create or update a doctrine specification
- produce a planning checkpoint review
- inspect a runtime boundary using post-`Φ` vocabulary
- update a schema-adjacent or registry-adjacent support artifact with validation
- package a checkpoint bundle or validate a bundle profile
- run validation or audit surfaces and emit evidence
- perform runtime-architecture planning grounded in kernel, component, service, binding, state, and lifecycle doctrine
- explain or summarize authoritative repo state without promoting mirrors into canon

These examples stay taxonomy-level.
They do not define tool-implementation detail or final MCP endpoints.

## 13. Anti-Patterns and Forbidden Shapes

The following task-catalog shapes are constitutionally forbidden:

- raw prompt text treated as the true interface
- script names used as hidden canon
- flattening planning and implementation into one generic task
- a catalog entry that silently crosses ownership boundaries
- a catalog entry that treats packaging as release distribution by default
- a catalog entry that encodes stale pre-`Φ` runtime vocabulary
- a catalog entry that implies automatic unsafe autonomy
- mirror-defined task families that compete with canonical governance
- a task surface that silently treats generated or projected artifacts as canonical inputs

## 14. Stability and Evolution

This artifact is `provisional` and canonical.
It freezes the first stable post-`Φ-A2` XStack task-surface taxonomy without claiming that the final interface or safety layers are complete.

The governing evolution rules are:

- `Σ-4` may consume this catalog to build MCP exposure categories
- `Σ-5` may consume this catalog to harden safety policy
- later `Υ` and `Ζ` work may reference these family distinctions where task surfaces intersect release, migration, restart, cutover, packaging, or live-ops support
- updates must remain explicit, reviewable, and consistent with canonical governance, the natural-language task bridge, and completed runtime doctrine

This document therefore answers the mandatory task-catalog questions for the current checkpoint:

- an XStack task is a stable repo-native, authority-aware task surface class rather than a prompt or script name
- a task catalog is needed after the natural-language bridge because normalized families still need bounded repo-native execution surfaces
- task families exist as explicit, review-aware catalog surfaces and are not interchangeable
- some work must remain non-cataloged or strongly gated rather than normalized into routine automation
- ownership and runtime cautions constrain task cataloging just as they constrain planning and runtime doctrine
- this catalog now enables `Σ-4` and `Σ-5` to build later interface and safety layers on top of stable task surfaces instead of inventing them ad hoc

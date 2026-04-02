Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ-5, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMAA1_PHIA2_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/XSTACK.md`, `docs/xstack/CI_GUARDRAILS.md`, `tools/controlx/README.md`

# Dominium MCP Interface Model

## 1. Purpose and Scope

This document defines the canonical MCP interface model for Dominium.
It exists because `Σ-3` froze the XStack task catalog, and the repository now needs a distinct interface-exposure layer that decides which cataloged task surfaces may be presented through tool-mediated interfaces without letting remote accessibility, convenience tooling, or vendor expectations become a shadow governance or shadow authority layer.

The MCP interface model governs:

- what an MCP-facing interface surface is in Dominium
- why MCP exposure is a distinct layer after the task catalog
- what classes of task surfaces may be eligible for tool-mediated exposure
- what classes must remain non-exposed, delayed, or strongly review-gated
- how exposure must preserve governance, ownership, runtime, and semantic boundaries
- what later `Σ-5`, `Υ`, and `Ζ` work may rely on once exposure law is explicit

This prompt does not:

- implement actual MCP servers or endpoints
- define final safety or autonomy policy
- expose every cataloged task automatically
- redefine governance, semantic doctrine, runtime doctrine, or release doctrine
- grant hidden permissions or mutation authority

The MCP interface model therefore sits:

- downstream of canonical governance, mirror policy, natural-language normalization, and the XStack task catalog
- downstream of semantic doctrine and completed runtime doctrine
- upstream of later safety hardening and concrete automation or remote-tooling use

## 2. Core Definition

In Dominium, an MCP-facing interface surface is a bounded, tool-mediated exposure envelope that presents a cataloged task surface to an interface consumer through an explicit exposure class, explicit input and output expectations, explicit review posture, and explicit ownership and runtime cautions.

An MCP-facing interface surface is distinct from:

- `canonical governance`
  - governance defines law; MCP surfaces consume that law
- `mirrors`
  - mirrors may summarize or reference interface behavior later, but they do not define exposure law
- `natural-language normalization`
  - normalization classifies prompts into task families; it does not decide what is exposable
- `task catalog entries`
  - the task catalog defines stable repo-native task surfaces; the MCP layer decides which of those surfaces may be exposed and under what class
- `runtime services`
  - services are runtime structures; MCP surfaces are governed interface envelopes over task surfaces
- `scripts and commands`
  - scripts are implementation evidence or realizations, not exposure law by themselves
- `product UIs`
  - product interfaces may consume MCP surfaces later, but product behavior does not define exposure semantics

The distinct exposure layer is needed because:

- task catalog inclusion is broader than safe or sensible interface exposure
- remote or tool-mediated access increases the risk of bypassing review, ownership caution, or runtime layering by convenience
- scripts and wrappers drift over time and do not encode the full legal boundary by themselves
- later safety policy needs a stable exposure universe rather than ad hoc endpoint assumptions

## 3. Canonical Role in the Stack

The MCP interface layer is a bounded exposure model, not a parallel canon.

Its constitutional position is:

- downstream of `AGENTS.md`
- downstream of the mirror policy
- downstream of the natural-language task bridge
- downstream of the XStack task catalog
- downstream of semantic and runtime doctrine
- upstream of later safety hardening
- upstream of concrete remote and automation integrations

The MCP interface layer must not become:

- a hidden policy engine
- a parallel governance surface
- a replacement task universe
- a shortcut around review, ownership, or runtime law
- a vendor-specific interface canon

Exposure is therefore a governed narrowing step.
It narrows cataloged task surfaces into interface classes without redefining the task catalog or the doctrine that the catalog already consumes.

## 4. Exposure Classes

The exposure-class taxonomy is constitutional and intentionally transport-agnostic.

### 4.1 Read and Inspect Surfaces

These surfaces expose stable read-only inspection of canonical or derived state without mutating tracked doctrine, code, or release artifacts.
Typical examples include inspecting planning state, reading doctrine artifacts, listing bundles, or reporting current runtime boundary state.

### 4.2 Planning and Analysis Surfaces

These surfaces expose classification, proposal, planning, inventory, or analysis behavior.
They may emit candidate artifacts, summaries, or reports, but they do not imply direct review-free mutation of canonical surfaces.

### 4.3 Validation and Audit Surfaces

These surfaces expose deterministic validation, proof, consistency, diagnostics, or audit behavior.
They may emit evidence, findings, refusal payloads, or reports.
They do not automatically promote generated evidence into authority.

### 4.4 Packaging and Checkpoint Surfaces

These surfaces expose bounded support-artifact packaging such as checkpoint bundles, bundle validation, or support-manifest generation.
They remain distinct from release distribution or trust-bearing publication.

### 4.5 Controlled Mutation Surfaces

These surfaces expose bounded mutation-capable task surfaces only where scope, authoritative inputs, auditability, review posture, and runtime or semantic boundaries are already explicit enough to support later hardening.
Controlled mutation is not equivalent to unrestricted mutation.

### 4.6 Strongly Review-Gated Surfaces

These surfaces correspond to task families whose exposure, if any, must remain explicitly review-aware, escalated, proposal-oriented, or delayed until stronger safety rules exist.
Exposure may be limited to request or proposal submission rather than direct mutation.

### 4.7 Non-Exposable or Excluded Surfaces

These surfaces are excluded from current MCP exposure because the required authority, ownership, safety, or continuity model is not yet formalized enough to expose them lawfully.

## 5. Exposure Eligibility Rules

For a task or task family to be MCP-eligible, the following requirements must be satisfiable explicitly:

- a stable cataloged task family already exists
- authoritative inputs are explicit
- ownership-sensitive cautions are known and preserved
- canonical versus projected or generated distinctions remain explicit
- planning-only versus implementation-capable posture is already known
- review expectations are already known
- runtime and semantic boundaries are not flattened
- the exposed action is auditable in principle
- the output class is explicit
- the exposure class is explicit

Eligibility therefore depends on prior doctrine and catalog structure.
MCP exposure may not invent missing clarity later.

## 6. Non-Eligibility and Delayed-Eligibility Rules

Some work classes should not yet be exposed, or should remain delayed or strongly gated, even if related scripts exist in the repo.

The major delayed or non-eligible classes include:

- canon rewrites
- ownership rebinding across protected splits
- broad refactors across multiple authority layers
- release, publication, trust, signing, or archive changes
- late `Ζ` live-ops or distributed-authority classes
- actions whose safety model is not yet formalized
- actions requiring deeper runtime semantics than the currently stabilized runtime doctrine provides
- direct prompt-driven execution wrappers treated as if they were already lawful interface contracts

Script presence does not erase any of those exclusions.

## 7. Authority and Ownership Constraints

MCP surfaces must preserve authority ordering and ownership caution.

The governing rules are:

- MCP surfaces must not bypass authority order
- MCP surfaces must not silently bind to ownership-ambiguous roots
- MCP surfaces must distinguish canonical versus projected or generated artifacts
- remote accessibility does not create authority
- derived mirrors or wrapper docs do not create exposure law
- interface consumers must not infer canonicality from whichever file is easiest to call

The key ownership cautions remain:

- `field/` versus `fields/`
- `schema/` versus `schemas/`
- `packs/` versus `data/packs/`
- canonical versus projected/generated artifacts
- thin `runtime/` root non-canonicality
- stale planning numbering drift

Exposure eligibility must not override any of those constraints.

## 8. Runtime Vocabulary Alignment

The MCP interface layer must preserve the completed post-`Φ` runtime vocabulary exactly enough that later safety policy can reason about interface risk correctly.

At minimum, MCP exposure must keep these distinctions explicit:

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

MCP exposure must not flatten these layers into generic `system`, `service`, or `remote action` language.

## 9. Exposure Semantics versus Autonomy

Exposure does not imply autonomy.
Exposure does not imply permission.
Exposure does not imply review-free mutation.
Exposure does not imply final safety approval.

The governing rules are:

- exposed does not mean autonomous
- exposed does not mean always allowed to mutate
- exposed does not mean safety-approved
- exposed does not mean exempt from review gates
- exposed does not mean the caller can bypass ownership, bridge, runtime, or release constraints

Later `Σ-5` will harden these distinctions further.
This prompt freezes only the interface-law floor needed for that hardening to make sense.

## 10. Relationship to Mirrors

Mirrors may later mention or reference MCP usage patterns.
They do not define exposure law.

The governing rules are:

- mirrors remain derived and subordinate
- vendor or tool expectations must not redefine interface exposure
- mirror wording may describe exposure classes later only by inheriting this canonical layer

MCP exposure is therefore canonical-governance downstream, not mirror-driven.

## 11. Relationship to the Task Catalog

The task catalog defines stable task surfaces.
The MCP layer defines which of those surfaces are eligible for tool-mediated exposure and under what class.

The governing rules are:

- catalogability does not imply exposability
- exposure is a narrower decision than catalog inclusion
- the MCP layer must reuse task-family boundaries rather than invent new generic interface buckets that ignore the catalog
- exposure classes may cut across multiple task families, but must never erase the original family posture, review expectation, or cautions

## 12. Relationship to Runtime Doctrine

MCP exposure may interact with runtime-facing tasks.
It must not imply runtime truth ownership or flatten the runtime stack.

The governing rules are:

- MCP surfaces touching runtime tasks must preserve kernel, component, service, binding, state, and lifecycle distinctions
- no MCP surface may imply that a tool-mediated interface owns semantic truth or runtime authority
- runtime-facing exposure must remain subordinate to semantic doctrine, runtime doctrine, state law, and lifecycle law
- product-facing interface wrappers must not redefine runtime law by remote convenience

## 13. Examples of Exposure Classes

Representative policy-level examples include:

- inspect current planning state
  - read and inspect surface
- inspect a runtime doctrine artifact
  - read and inspect surface
- run a validation or audit-oriented task
  - validation and audit surface
- build a checkpoint bundle or validate a bundle profile
  - packaging and checkpoint surface
- propose a planning artifact update
  - planning and analysis surface
- perform a bounded runtime-support mutation whose task family is already implementation-capable and auditable
  - controlled mutation surface
- request a doctrine rewrite, ownership rebinding, or trust-bearing release change
  - strongly review-gated or non-exposable surface

These examples remain taxonomy-level only.
They do not define concrete endpoint shapes.

## 14. Anti-Patterns and Forbidden Shapes

The following interface shapes are constitutionally forbidden:

- `if it exists in tools, expose it`
- remote interface becomes hidden governance override
- MCP surface treats projected or generated artifacts as canonical
- exposure silently grants unsafe mutation
- MCP layer flattens runtime vocabulary
- vendor or tool assumptions override repo law
- task catalog and MCP exposure collapse into one concept
- exposure eligibility inferred from script names alone
- interface reachability treated as authority

## 15. Stability and Evolution

This artifact is `provisional` and canonical.
It freezes the first stable post-`Σ-3` MCP exposure model without claiming that safety, permissions, or concrete endpoint implementation are complete.

The governing evolution rules are:

- `Σ-5` may consume this model to harden safety policy
- later `Υ` and `Ζ` work may reference stable exposure distinctions where release, migration, cutover, packaging, or live-ops support interacts with interface surfaces
- updates must remain explicit, reviewable, and consistent with canonical governance, the task catalog, and completed runtime doctrine

This document therefore answers the mandatory MCP-interface questions for the current checkpoint:

- an MCP-facing interface surface is a bounded, tool-mediated exposure envelope over a cataloged task surface
- an MCP layer is needed after the task catalog because catalog inclusion is broader than lawful interface exposure
- some task classes are reasonable candidates for read, planning, validation, packaging, or tightly bounded mutation exposure
- other classes must remain non-exposed or strongly gated
- ownership and runtime cautions constrain exposure just as they constrain task cataloging and runtime doctrine
- exposure does not imply autonomy because safety, permission, review, and authority remain separate layers
- this model now enables `Σ-5` to harden safety policy around an explicit exposure universe instead of inventing one ad hoc

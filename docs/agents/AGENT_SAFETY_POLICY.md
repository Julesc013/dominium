Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_SIGMAA1_PHIA2_REVIEW.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/xstack/CI_GUARDRAILS.md`, `tools/controlx/README.md`, `repo/release_policy.toml`, `docs/release/SIGNING_POLICY.md`

# Dominium Agent Safety Policy

## 1. Purpose and Scope

This document defines the canonical agent safety policy for Dominium.
It exists because the repository now has explicit governance, mirror law, natural-language normalization, task-catalog law, MCP interface law, and deeper runtime doctrine, but it still needs a distinct safety layer that decides what kinds of action are actually safe to perform, under what review posture, and under what refusal or escalation rules.

The agent safety policy governs:

- what safe, review-gated, strongly gated, and prohibited action means in Dominium
- how safety policy relates to canonical governance, mirrors, natural-language normalization, task cataloging, MCP exposure, semantic doctrine, runtime doctrine, ownership review, and checkpoint law
- what classes of work are allowed, allowed with validation, allowed with explicit human review, strongly gated, or prohibited
- what escalation and refusal paths apply when authority, ownership, runtime, release, or auditability risk is high
- what later `Υ`, `Ζ`, and future enforcement layers may rely on once safety law is explicit

This prompt does not:

- implement enforcement middleware
- implement MCP servers or endpoints
- implement release, publication, or live-ops automation
- redefine governance, semantic doctrine, runtime doctrine, checkpoint law, or release doctrine
- collapse safety into a single yes-or-no permission bit

The agent safety policy therefore sits:

- downstream of canonical governance, mirror policy, natural-language normalization, the XStack task catalog, and the MCP interface model
- downstream of semantic doctrine and completed runtime doctrine
- upstream of later release/control-plane hardening in `Υ`
- upstream of later live-ops and continuity-sensitive work in `Ζ`
- upstream of any future enforcement or execution layer that needs explicit permission, refusal, or escalation semantics

## 2. Core Definition

In Dominium, an action is safe only when all of the following are true:

- the action is subordinate to canonical governance and scope-specific doctrine
- the authoritative inputs are explicit
- the action does not depend on convenience to choose authority, ownership, or runtime meaning
- the action preserves semantic, ownership, bridge, state, and lifecycle law
- the action has a bounded scope and auditable effect model
- the required validation and review posture are explicit

An action is unsafe when its legality depends on:

- ambiguous or convenience-selected authority
- ownership drift
- hidden mutation of authoritative state or semantic meaning
- implicit permission inferred from task cataloging or exposure
- release, trust, or live-ops behavior without explicit review and doctrine
- insufficient auditability, traceability, or validation

Safety is distinct from:

- `canonical governance`
  - governance defines authority order and baseline operating law
- `mirrors`
  - mirrors are derived projections and may not define permission
- `natural-language classification`
  - classification normalizes intent but does not authorize execution
- `task cataloging`
  - the task catalog stabilizes task families but does not decide safety
- `MCP exposure`
  - exposure defines interface eligibility, not permission or autonomy
- `runtime lifecycle law`
  - lifecycle law governs lawful runtime posture transitions, not whether an actor may trigger them
- `release or publication policy`
  - release policy governs release semantics and trust-bearing surfaces, but safety policy governs whether those classes of work may be autonomously or semi-autonomously acted on at all

The distinct safety layer is necessary because the stack now has:

- classification without permission
- catalogability without safety
- exposure without autonomy
- runtime structure without action authorization

Safety policy is the layer that turns those bounded surfaces into explicit permission, review, escalation, and refusal posture.

## 3. Safety Action Classes

Safety classification is multi-level, not boolean.
The highest live risk dimension sets the floor.
Missing clarity escalates the class; it never relaxes it.

| Action Class | Meaning | Default Posture |
| --- | --- | --- |
| `allowed_bounded` | Safe to perform within explicit scope without extra human review beyond the normal task request, provided no higher-risk dimension is triggered. | bounded, auditable, low-blast-radius |
| `allowed_with_required_validation` | Permitted only if the required validation floor is run and the action stays within explicit scope and authority. | bounded but validation-gated |
| `allowed_with_explicit_human_review` | May proceed only with explicit human review or approval because the action can alter important canonical, runtime, or policy surfaces. | review-gated |
| `strongly_gated_privileged` | Requires explicit human control, privileged review posture, or later series doctrine before execution. Not part of default autonomous or routine tool-mediated scope. | privileged, tightly constrained |
| `prohibited_or_out_of_scope` | Must be refused, deferred, or kept non-automated at the current doctrine level. | not executable under current safety policy |

The classes are ordered.
Later tooling may implement them with finer machinery, but later tooling may not flatten them back into `allowed` and `not allowed`.

## 4. Safety Dimensions

Every proposed action must be evaluated across the following dimensions.
These are constitutional dimensions, not vendor-specific heuristics.

| Safety Dimension | What It Evaluates | Typical Escalation Effect |
| --- | --- | --- |
| `semantic_doctrine_risk` | Whether the action could alter or contradict canonical semantic law, capability meaning, representation law, or formalization law. | escalates to human review or stronger |
| `ownership_risk` | Whether the action touches ownership-sensitive roots, unresolved ownership splits, or canonical-versus-derived authority boundaries. | escalates to review, quarantine, or refusal |
| `runtime_state_lifecycle_risk` | Whether the action could flatten kernel/component/service/binding/state/lifecycle distinctions or trap authoritative state. | escalates to review or strong gate |
| `release_publication_trust_risk` | Whether the action touches release channels, trust roots, signing, publication, archive identity, updater behavior, or external commitments. | escalates to strong gate or prohibition |
| `scope_blast_radius_risk` | Whether the action affects one bounded artifact, one subsystem, multiple authority layers, or broad repo structure. | escalates as scope widens |
| `irreversibility_risk` | Whether the action is difficult to reverse, hard to audit, or likely to outlive a normal local rollback. | escalates to review or refusal |
| `ambiguity_risk` | Whether the request, authority source, execution target, or expected result is materially ambiguous. | downgrades to planning or refusal |
| `projection_confusion_risk` | Whether the action risks treating projected, mirrored, cached, generated, or transitional artifacts as canonical. | escalates to review or refusal |
| `cross_domain_bridge_risk` | Whether the action touches bridge-mediated domain interaction or could create hidden cross-domain coupling. | escalates to review or strong gate |
| `auditability_traceability_risk` | Whether the action can be validated, traced, explained, and reviewed after the fact. | blocks mutation if missing |

These dimensions are cumulative.
An action need only trip one sufficiently serious dimension to escalate.

## 5. Allowed Action Classes

Safe bounded automation exists, but it is narrow and conditional.

### 5.1 `allowed_bounded`

The following classes are generally safe enough for bounded execution when they remain scoped, auditable, and free of higher-risk triggers:

- read-only analysis and inspection
- explanation, summarization, and inventory work
- doctrine, runtime, or planning state explanation that does not mutate canonical meaning
- checkpoint-state inspection and continuity reporting
- mirror or catalog reading that does not redefine governance or safety

Typical examples include:

- inspecting current planning or runtime doctrine state
- summarizing authoritative repo state
- inventorying task-family or exposure-class mappings
- reading and comparing canonical versus derived artifacts without mutating them

### 5.2 `allowed_with_required_validation`

The following classes are generally allowed only when the validation floor is explicit and satisfied:

- planning/checkpoint artifact creation within active law
- deterministic validation and audit execution
- packaging and checkpoint-bundling work that remains distinct from release distribution
- bounded documentation or registry updates outside foundational canon
- small bounded tooling or governance-support changes where authoritative inputs, effects, and validation are explicit

Typical examples include:

- producing checkpoint summaries or registries
- updating paired machine-readable mirrors for already-scoped non-canon governance artifacts
- emitting evidence bundles or validation reports
- building support bundles that do not publish, ship, sign, or advance trust-bearing artifacts

Allowed-with-validation does not permit:

- silent ownership rebinding
- release/publication side effects
- ambiguous canonical root selection
- runtime or semantic boundary changes by convenience

## 6. Review-Gated and Strongly Gated Action Classes

Some work can be lawful only with explicit human review, and some is more tightly constrained still.

### 6.1 `allowed_with_explicit_human_review`

This class covers work that may proceed only when a human explicitly reviews or authorizes it because the work can alter important canonical, governance, runtime, or policy surfaces even when the scope is known.

Typical examples include:

- bounded doctrine or governance policy updates
- bounded runtime-platform mutations that touch shared runtime surfaces
- bounded product-shell changes that could affect runtime or governance interpretation
- scoped semantic work that is already clearly authorized and not trying to rebind ownership or bridge law by convenience
- registry or manifest changes whose meaning affects multiple downstream surfaces

This class is still constrained by validation, authority order, and ownership caution.
Human review does not authorize contradiction of canon.

### 6.2 `strongly_gated_privileged`

This class covers work that is too sensitive for default autonomous or routine tool-mediated execution even when technically exposable.
It requires explicit human control, additional doctrine, or a future series to define the operational safeguards.

Typical examples include:

- changes to canon doctrine or glossary meaning
- ownership rebinding across protected splits
- cross-domain bridge-law changes
- changes affecting authoritative state semantics or lifecycle continuity guarantees
- replace-classified subsystems and broad multi-layer refactors
- release, publication, signing, trust-root, archive, or updater changes
- privileged control-plane or remote-control actions

This class is a hard ceiling for default autonomy.
Technical reachability does not lower it.

## 7. Non-Exposable and Prohibited Action Classes

Some actions must remain prohibited or out of scope under the current policy.
They are refused even if a prompt asks for them plainly or a tool could technically do them.

The prohibited or out-of-scope classes include:

- silent canon rewrites
- bypass of ownership review
- choosing a canonical root by convenience in an ambiguous split
- automatic publication, trust-root changes, or release-channel advancement
- late `Ζ` live-ops behavior without later doctrine
- destructive broad refactors without explicit human control
- actions whose safety depends on infrastructure or guarantees not yet formalized
- runtime convenience that would override bridge law, state law, or lifecycle law
- converting projections, mirrors, caches, or generated outputs into truth or authority by convenience

When the only way to proceed would require one of those shapes, the correct outcome is refusal, deferral, or downgrade to planning-only work.

## 8. Relationship to the Task Catalog and MCP

The safety stack is ordered.

1. natural-language classification
2. XStack task catalog
3. MCP exposure model
4. safety policy
5. future enforcement or execution machinery

The governing consequences are:

- natural-language classification does not imply permission
- task catalog inclusion does not imply permission
- MCP exposure does not imply permission
- MCP exposure does not imply autonomy
- safety policy is the layer that decides what cataloged or exposed tasks are actually safe to run and under what review posture

This means:

- a task can be cataloged but still review-gated
- a task can be MCP-exposed but still disallowed for autonomous mutation
- an interface can be reachable yet still forbidden to perform a sensitive class of action

Exposure and permission must remain distinct.

## 9. Relationship to Runtime Doctrine

Safety policy must preserve the completed post-`Φ` runtime vocabulary and boundary law.
It must not flatten runtime structure into generic `system` or `service` permission language.

At minimum, safety decisions must preserve:

- `kernel`
- `component`
- `service`
- `domain-service binding`
- `state externalization`
- `lifecycle`
- `domain`
- `product`
- `pack/content`
- `mirror`
- `canonical versus projected/generated artifact`

The safety consequences are:

- no action may treat service convenience as semantic ownership
- no action may treat runtime availability as truth existence
- no action may trap authoritative truth in transient or product-local state
- no action may hide cross-domain behavior inside runtime convenience
- no action may suspend, restart, replace, or degrade runtime structures in a way that silently changes ownership, truth, or lifecycle law

Runtime-facing actions are safe only when they remain subordinate to the runtime doctrine and the semantic law it already consumes.

## 10. Ownership and Authority Caution

The following cautions remain binding for safety classification:

- `field/` versus `fields/`
- `schema/` versus `schemas/`
- `packs/` versus `data/packs/`
- canonical versus projected/generated artifacts
- thin `runtime/` root non-canonicality
- older planning numbering drift

No action may use convenience, path adjacency, script habit, or interface exposure to bypass those cautions.

The governing consequences are:

- ambiguous roots escalate rather than auto-resolve
- projections and mirrors may inform work but may not silently become owners
- remote access does not create authority
- mirrors do not define permission
- checkpoint drift does not authorize sequence shortcuts

## 11. Validation Expectations

Safety classification and validation are related but not identical.
Validation does not erase high-risk action classes, but missing validation blocks lower-risk classes from remaining safe.

The baseline policy expectations are:

- verify that required target artifacts exist
- check that authoritative inputs were the ones actually used
- parse touched JSON, schema, or machine-readable artifacts where relevant
- check consistency between normative and machine-readable outputs when both are produced
- run `git diff --check`
- account clearly for what changed
- state what was intentionally not changed
- report what validations were run and what was not run

Higher action classes inherit the same floor and add more review.
Validation is necessary for many actions, but validation alone never converts privileged or prohibited work into routine safe automation.

## 12. Escalation and Review

When risk, ambiguity, or scope exceeds the current class, the action must escalate instead of silently proceeding.

The valid escalation paths are:

- require human review before mutation
- preserve quarantine around ownership-sensitive or unresolved roots
- downgrade the task to planning-only or proposal-only output
- refuse unsafe automation
- defer until later doctrine or checkpoints exist

The governing triggers are:

- high ambiguity
  - downgrade to planning or refuse
- ownership ambiguity
  - preserve quarantine and escalate
- release, publication, trust, or external-commitment impact
  - strongly gate or refuse unattended execution
- missing auditability or unclear side effects
  - refuse mutation until the action model is explicit
- late `Ζ` live-ops style action
  - defer until the later series defines the needed doctrine

Escalation is not failure.
It is the lawful response when the current policy floor is insufficient for unattended or lightly supervised action.

## 13. Anti-Patterns and Forbidden Shapes

The following safety shapes are forbidden:

- `if exposed, then allowed`
- `if cataloged, then safe`
- mirrors define permission
- prompt wording overrides policy
- agent silently chooses the canonical root in an ambiguous split
- runtime refactor disguised as planning or inspection
- packaging treated as release distribution
- publication or trust change treated like a normal bounded task
- projections, caches, or generated outputs promoted to authority by convenience
- runtime convenience used to bypass ownership, bridge, state, or lifecycle law

These are constitutional policy failures, not mere style problems.

## 14. Stability and Evolution

This artifact is a provisional but canonical safety policy.
It is stable enough for later `Υ`, `Ζ`, and future enforcement layers to consume, but it must evolve only through explicit updates that remain subordinate to canonical governance, semantic doctrine, runtime doctrine, checkpoint law, and release doctrine.

Immediate downstream uses include:

- `Υ`
  - release and control-plane work must inherit the release, trust, and publication caution floor defined here
- `Ζ`
  - live-ops, replacement, handoff, and continuity-sensitive operations must inherit the strong-gating and defer-until-doctrine rules defined here
- future enforcement and interface layers
  - must consume this action-class and escalation model rather than inventing new permission semantics

Updates must remain:

- explicit
- auditable
- consistent with upstream doctrine
- non-silent about changed safety posture

## 15. Direct Answers and Enabled Work

The answers this policy freezes are:

- what makes an action safe, review-gated, or prohibited
  - explicit authority, bounded scope, preserved doctrine, preserved ownership, preserved runtime law, sufficient validation, and auditability make an action safe; high-risk doctrine, ownership, state, lifecycle, release, trust, or ambiguity concerns escalate it; contradiction of upstream law makes it prohibited
- why safety is distinct from task classification and MCP exposure
  - classification identifies the task family, cataloging stabilizes the task surface, exposure defines interface eligibility, and safety decides whether execution is actually permitted and under what constraints
- what classes are safe enough for bounded automation now
  - read-only inspection, explanation, bounded planning artifacts, deterministic validation/audit, support packaging, and small bounded non-foundational updates with explicit validation
- what classes must remain human-reviewed or out of scope
  - doctrine and governance mutation, semantic rebinding, bridge-law changes, authoritative state/lifecycle meaning changes, release/trust work, broad refactors, and late live-ops classes
- how ownership, runtime, state, lifecycle, bridge, and release concerns shape safety
  - they set escalation floors and refusal conditions; they are not optional secondary checks
- what later work depends on this policy
  - `Υ`, `Ζ`, and future enforcement or interface layers now have an explicit safety floor for permission, refusal, review, and escalation without inventing a parallel policy universe

Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: post-Φ-B4 checkpoints, Φ-B5, later Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB3_YB_SAFE_REVIEW.md`, `docs/planning/CHECKPOINT_C_YC_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YC.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/RELEASE_OPS_EXECUTION_ENVELOPE.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/MANUAL_REVIEW_GATES.md`, `runtime/process_spawn.py`, `server/app/main_server.c`, `release/update_resolver.py`, `security/trust/trust_verifier.py`, `tools/controlx/core/execution_router.py`, `tools/review/series_execution_strategy_common.py`, `repo/release_policy.toml`, `data/registries/release_channel_registry.json`, `data/registries/target_matrix_registry.json`, `data/registries/trust_root_registry.json`

# Dominium Hotswap Boundaries Doctrine

## A. Purpose And Scope

This doctrine exists because the post-`Υ-C` checkpoint reclassified `Φ-B4 — HOTSWAP_BOUNDARIES-0` from `dangerous` to `ready_with_cautions`, while still recording that hotswap boundary maturity and runtime cutover proof remain active blockers for later `Φ-B5` and `Ζ` work.

It solves a specific problem: Dominium now has explicit law for lifecycle, state externalization, replay, snapshots, isolation, coexistence, release operations, rehearsal, canary and downgrade movement, receipts, and trust continuity. Without one explicit hotswap-boundary doctrine, later work could wrongly treat:

- coexistence as automatic live swappability
- restartless replacement as a tool trick rather than a governed continuity event
- release-control readiness as proof of lawful runtime cutover
- rehearsal or canary success as proof that live swap legality already exists

This artifact governs:

- what hotswap means in Dominium
- what a lawful hotswap boundary must declare and preserve
- what classes of subjects are never hot-swappable, conditionally hot-swappable, or only boundedly swappable
- what continuity, legality, and review constraints remain upstream of any future implementation
- what later checkpoints, `Φ-B5`, and `Ζ` planning must consume rather than reinvent

This artifact does not implement:

- hot-reload or hotswap engines
- rolling restart or live cutover machinery
- distributed handoff or split-authority transfer
- trust-root rotation or live trust updates
- publication automation or release orchestration

Checkpoint relation:

- this is the first risky-tail `Φ` doctrine prompt executed after the post-`Υ-C` checkpoint
- it remains doctrine-level only
- it must preserve the checkpoint caution that implementation maturity is still incomplete

## B. Core Definition

In Dominium, `hotswap` is the live replacement or live handoff of a bounded runtime or control-plane realization across an explicit boundary without collapsing the surrounding authority envelope into an undeclared restart or arbitrary reload.

A `hotswap boundary` is the declared legality envelope that states:

- what subject is being replaced, rebound, or handed off
- what continuity properties must remain preserved
- what lifecycle posture must hold before, during, and after the change
- what state may move, what state must remain externalized, and what state must not be trapped
- what replay, snapshot, isolation, coexistence, release-control, receipt, and trust constraints remain binding

Hotswap is not:

- `restart`: stopping and starting the subject or enclosing host remains a different continuity posture
- `rollback`: restoration or reselection of a prior recorded state is a separate transaction class
- `downgrade`: downward release movement is a release-control decision, not automatically a live runtime swap
- `coexistence`: bounded side-by-side presence does not itself authorize live replacement
- `archive retention`: historical availability does not imply runtime swap legality
- `publication visibility change`: mirror or feed visibility is not live runtime cutover
- `implementation-level hot reload`: a tool-local file watcher or preview loop does not define architectural canon

## C. Why Hotswap Law Is Necessary

Hotswap law is necessary because live replacement changes availability, continuity, authority, and reconstructability assumptions all at once.

Coexistence alone is insufficient. A subject can lawfully coexist with another version and still remain non-swappable because semantic ownership, lifecycle legality, replay continuity, or trust posture would be broken by live replacement.

Rehearsal, canary, and deterministic downgrade doctrine are also insufficient on their own. They improve release and control-plane maturity, but they do not prove that a runtime subject may be replaced in-process, in-place, or restartlessly.

This doctrine therefore freezes one constitutional rule: hotswap is never inferred from convenience, partial runtime experiments, or release-control sophistication. It must be declared and bounded explicitly.

## D. Hotswap Subject Classes

The following high-level subject classes define what may, may not, or may only conditionally be hot-swapped.

### 1. Non-Swappable Semantic And Authority-Bearing Subjects

These subjects are never hot-swappable by convenience:

- semantic truth owners
- authority-bearing domain structures
- bridge-legality owners
- semantic contract meaning owners
- subjects whose replacement would silently reinterpret truth, ownership, or bridge legality

Their default posture is `never hot-swappable`.

### 2. Foundational Continuity Anchors

These subjects remain `restart-required` unless later doctrine and proof say otherwise:

- kernel-adjacent continuity anchors
- foundational runtime hosting structures
- subjects whose live replacement would alter replay, snapshot, or lifecycle interpretation

Their default posture is `restart required`, not lawful hotswap.

### 3. State-Externalized Service-Facing Realizations

These subjects may become `conditionally hot-swappable` only when all of the following remain explicit:

- authoritative truth is externalized rather than trapped in the realization
- lifecycle posture supports a lawful handoff or replacement window
- replay and snapshot interpretation remain intact
- isolation boundaries remain explicit
- coexistence, if used, remains bounded and non-authoritative

Their default posture is `review-gated hotswap`.

### 4. Observation-, Representation-, And Projection-Facing Realizations

Derived renderers, inspection adapters, previews, and similar observation-facing subjects may be `boundedly swappable` only when they:

- own no authoritative truth
- do not redefine semantic meaning
- do not silently become bridge or trust owners
- remain reconstructable through receipts or local evidence where required

Their default posture is `bounded local swap`, not general runtime swappability.

### 5. Bounded Control-Plane Runtime Adjuncts

Certain runtime-adjacent control-plane helpers may be `conditionally or boundedly swappable` only when their swap does not:

- change release truth by convenience
- alter receipt continuity or operator transaction meaning
- smuggle trust posture changes
- hide a runtime authority transfer

Their default posture is `bounded local swap` or `review-gated hotswap`, depending on blast radius.

### 6. Trust-, Revocation-, And Distributed-Authority-Sensitive Subjects

These subjects remain `future-only or prohibited` for hotswap claims in the current doctrine horizon:

- trust-root or verifier-authority transitions with live effect
- revocation propagation subjects whose continuity would alter acceptance semantics in-flight
- split-authority or distributed handoff subjects reserved for later `Φ-B5`

Their default posture is `future-only or prohibited`.

## E. Boundary Classes

Dominium recognizes the following boundary classes.

### 1. No-Swap Boundaries

Use this class when live replacement is unlawful because semantic truth, authority, or bridge legality would be altered by the change.

### 2. Restart-Required Boundaries

Use this class when replacement may eventually be lawful, but only through stop, suspend, retire, or restart semantics rather than live cutover.

### 3. Bounded Local Swap Boundaries

Use this class when a subject may be replaced locally and narrowly without claiming full runtime continuity. This class is limited to bounded, non-truth-owning, non-authority-bearing subjects.

### 4. Review-Gated Hotswap Boundaries

Use this class when a live swap claim may be discussable only if explicit lifecycle, state, replay, snapshot, coexistence, receipt, and trust constraints are satisfied and a human review gate remains active.

### 5. Future-Only Or Prohibited Boundaries

Use this class when the subject depends on unsolved live-cutover, distributed-authority, trust-rotation, or continuity problems that remain outside the current doctrine floor.

## F. Relationship To Semantic Doctrine

Semantic law outranks hotswap law.

Hotswap must not:

- redefine semantic truth
- alter domain ownership
- erase cross-domain bridge legality
- turn projection or representation convenience into semantic authority
- convert a tool-level rebinding trick into lawful semantic replacement

If a subject is semantically authoritative, that subject remains non-swappable unless a stronger later doctrine explicitly changes the legality envelope.

## G. Relationship To State And Lifecycle

State externalization and lifecycle legality remain upstream prerequisites.

Lawful hotswap claims must therefore preserve all of the following:

- authoritative truth is not trapped inside the outgoing realization
- lifecycle posture is explicit before, during, and after the swap
- active, suspended, degraded, quiesced, retiring, or replace-or-handoff-adjacent states remain distinguishable
- swap claims do not bypass lifecycle law by presenting an undeclared restart as a live handoff

Hotswap must not create irreplaceable hidden state. If a subject cannot externalize or lawfully hand off the relevant state, the boundary is not hot-swappable.

## H. Relationship To Replay And Snapshots

Replay intelligibility and snapshot legality are prerequisites, not afterthoughts.

Lawful hotswap claims must preserve:

- reconstructable transition history
- explicit version and boundary identity where realizations change
- replay semantics that remain intelligible after the swap
- snapshot legality across the boundary

Hotswap must not:

- erase the transition from event history
- create non-reconstructable boundaries
- leave snapshots ambiguous about what realization, authority, or lifecycle posture they capture

## I. Relationship To Isolation And Coexistence

Coexistence may be necessary, but it is never sufficient.

Isolation and coexistence constrain hotswap in the following way:

- coexistence can provide bounded side-by-side presence during a handoff horizon
- coexistence does not prove that live replacement is legal
- isolation boundaries may make bounded local swaps discussable, but they do not erase continuity obligations
- hotswap must not collapse isolation law into convenience or blur multiple authorities together

If coexistence introduces hidden shared state, dual writers, or split authority, it invalidates stronger hotswap claims rather than enabling them.

## J. Relationship To Release/Control-Plane Doctrine

Hotswap remains subordinate to release-control doctrine wherever versioned realizations, release identities, or operator actions are involved.

This means:

- release contract profile remains upstream for any version-distinguished live swap claim
- release-index and resolution semantics remain explicit where versioned realizations are selected
- operator transactions remain typed and attributable
- receipt and provenance continuity remain required where operator-controlled swap actions are claimed
- archive and mirror continuity do not create live swap legality
- canary, downgrade, rehearsal, and rollback doctrine may support review, but they do not themselves prove lawful hotswap

Release-control convenience must not be mistaken for runtime cutover legality.

## K. Relationship To Trust And Revocation Continuity

Trust posture may constrain, block, or fully prohibit a hotswap claim.

This doctrine therefore preserves the following:

- trust execution and revocation continuity remain upstream
- mirror visibility or archive presence do not establish trust-safe live swap semantics
- live trust-root or revocation-sensitive transitions remain outside current implementation maturity
- trust-affecting boundaries may remain future-only even when a runtime subject is otherwise technically replaceable

This doctrine does not claim that live trust changes are solved. It only freezes that hotswap claims must respect trust continuity where relevant.

## L. Invalidity And Failure

Hotswap claims must be classifiable. The following invalidity and failure categories are canonical:

- `bounded_lawful`: the boundary is explicit and the continuity envelope is satisfied
- `review_gated`: stronger claims require explicit human review
- `restart_required`: live replacement is not lawful, but non-live replacement may remain legal
- `provisional`: some evidence exists, but continuity proof is incomplete
- `semantic_authority_non_swappable`: semantic ownership or truth would be altered
- `lifecycle_invalid`: lifecycle posture is incompatible with the claim
- `state_entangled`: state is trapped, hidden, or unlawfully intertwined
- `replay_snapshot_incompatible`: reconstructability or continuity would be broken
- `isolation_invalid`: containment or separation is insufficient
- `coexistence_insufficient`: coexistence exists but does not satisfy live replacement requirements
- `release_control_continuity_missing`: operator, receipt, index, or release-profile continuity is incomplete
- `trust_or_revocation_blocked`: trust continuity prevents the live claim
- `future_only_or_policy_prohibited`: the claim depends on later doctrine or remains prohibited

## M. Canonical Vs Derived Distinctions

Canonical truth about hotswap boundaries lives in doctrine, lawful receipts, and later explicitly promoted continuity records.

The following are derived only:

- dashboards
- UIs
- file names
- build labels
- preview hosts
- local reload loops
- operator convenience wrappers

Derived views may expose or summarize swap posture, but they must not redefine what is actually swappable.

## N. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- `fields/` remains canonical over `field/`
- `schema/` remains canonical over `schemas/`
- `packs/` and `data/packs/` are not freely collapsible
- canonical vs projected/generated distinctions remain binding
- the thin `runtime/` root is not automatically canonical over stronger doctrine
- stale numbering or older checkpoint titles do not override active checkpoint law
- repo reality must be extended rather than replaced
- tool-local reload behavior must not be promoted into architecture by convenience

## O. Anti-Patterns / Forbidden Shapes

The following shapes are forbidden:

- coexistence implies hotswap
- canary success implies hotswap readiness
- restart semantics treated as hotswap semantics
- rollback, downgrade, or publication actions treated as interchangeable with hotswap
- tool-local reload tricks treated as architectural truth
- hotswap that bypasses lifecycle, replay, snapshot, isolation, coexistence, release-control, receipt, or trust law
- hotswap that silently changes truth ownership or bridge legality
- distributed split-authority handoff hidden under local replacement language
- doctrine existence treated as proof of implementation maturity

## P. Stability And Evolution

This artifact is `provisional` because the post-`Υ-C` checkpoint only moved hotswap into `ready_with_cautions`, not into proven implementation maturity.

This doctrine now enables:

- the next checkpoint after `Φ-B4`
- later reconsideration of `Φ-B5 — DISTRIBUTED_AUTHORITY_FOUNDATIONS-0`
- clearer `Ζ` blocker reduction around runtime cutover maturity

Later prompts may refine this doctrine only by extending it explicitly. They may not:

- reinterpret coexistence as hotswap
- backfill hot-reload tricks into canonical law
- erase the preserved distinctions among restart, rollback, downgrade, control-plane movement, and live replacement

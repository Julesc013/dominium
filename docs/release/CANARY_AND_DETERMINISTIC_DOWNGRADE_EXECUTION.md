Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-C2, next checkpoint before Φ-B4, risky Φ-B4, risky Φ-B5, future Ζ planning
Replacement Target: later rollout, downgrade, publication, trust, and live-ops operational doctrine may refine procedures and tooling without replacing the canary and deterministic downgrade semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB3_YB_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB3_YB.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/MANUAL_AUTOMATION_PARITY_AND_REHEARSAL.md`, `docs/release/RELEASE_OPS_EXECUTION_ENVELOPE.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `release/update_resolver.py`, `release/component_graph_resolver.py`, `repo/release_policy.toml`, `updates/stable.json`, `updates/beta.json`, `updates/pinned.json`, `updates/README.md`, `data/registries/release_channel_registry.json`, `data/registries/release_resolution_policy_registry.json`, `data/registries/install_profile_registry.json`, `data/registries/target_matrix_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/refusal_code_registry.json`, `data/registries/remediation_playbooks.json`, `tools/controlx/README.md`, `tools/xstack/testx/tests/test_rollback_restores_previous_component_set.py`, `tools/xstack/testx/tests/test_update_plan_excludes_yanked.py`, `tools/xstack/testx/tests/test_yanked_excluded_from_latest.py`

# Canary And Deterministic Downgrade Execution

## A. Purpose And Scope

This doctrine exists to freeze the canonical meaning of canary and deterministic downgrade execution in the post-`Φ-B3`, post-`Υ-B`, and in-`Υ-C` control-plane maturity band selected by `C-ΦB3ΥB_SAFE_REVIEW`.

It solves a specific problem. The repo now has explicit operator transaction law, receipt continuity law, execution-envelope law, and rollback-alignment law, plus real resolver surfaces for deterministic policy selection, yanked-candidate exclusion, rollback transaction logging, channel feeds, target matrices, and install profiles. Without one explicit doctrine, later work could still drift into dangerous folklore:

- "canary" meaning any vague small rollout
- "downgrade" meaning choose an older version by convenience
- staged exposure occurring without exact target or receipt continuity reasoning
- rollback and downgrade being flattened into the same thing
- canary success being misread as hotswap readiness
- tooling wrappers and feeds becoming the real rollout contract by convenience

This document governs:

- what a canary is in Dominium
- what deterministic downgrade execution is in Dominium
- which canary and downgrade classes are lawful, review-gated, bounded, or prohibited
- how canary and downgrade execution remain subordinate to release identity, release contract profile, release-index resolution, receipts, archive continuity, parity and rehearsal law, and runtime doctrine
- what later `Υ-C2`, the next checkpoint, risky `Φ-B4`, risky `Φ-B5`, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- rollout-engine implementation
- downgrade automation
- release-pipeline implementation
- live cutover or hotswap implementation
- distributed authority implementation
- trust-root rotation implementation

This layer sits after `Υ-C0` because rehearsal and rollback-alignment law had to be frozen first. It sits before any honest reconsideration of `Φ-B4` because canary and downgrade discipline must be explicit before the project can reason about more dangerous runtime transitions.

## B. Core Definition

A canary in Dominium is a bounded, intentionally scoped exposure or selection posture for a governed release candidate that preserves exact release identity, compatibility envelope, target scope, receipt continuity, and review posture while limiting blast radius.

Deterministic downgrade execution is a governed downward movement in release selection or component realization where the chosen target and resulting state are reproducible from explicit inputs, explicit policy, explicit target scope, explicit receipts, and explicit refusal rules rather than from operator convenience.

These concepts differ from nearby ideas:

- generic staged rollout may describe informal rollout practice; a Dominium canary is a typed, bounded control-plane posture
- rollback restores a previously recorded managed state through recorded history; downgrade selects an older lawful target under deterministic rules
- yank changes eligibility or visibility posture; it does not itself perform a downgrade
- deprecation changes warning and preference posture; it does not itself move selection
- rollback rehearsal is non-live evidence gathering; canary and downgrade execution remain live or execution-posture-bearing
- archive retention preserves artifacts; it does not define canary scope or downgrade law
- hotswap changes live runtime replacement posture; canary and downgrade execution do not imply that hotswap is solved

Canary and downgrade therefore remain connected to rollback and resolution law, but they are not interchangeable with those concepts.

## C. Why These Doctrines Are Necessary

These doctrines are necessary because Dominium needs explicit semantics for bounded exposure and reversible release movement before any later runtime-sensitive work can be judged honestly.

The repo already shows the underlying ingredients:

- deterministic release-resolution policy ids such as `policy.latest_compatible` and `policy.exact_suite`
- exact target and install-profile registries
- yanked-candidate exclusion and explicit yanked opt-in behavior
- rollback transaction logs carrying `install_plan_hash`, `prior_component_set_hash`, and selected component identifiers
- channel feeds for `stable`, `beta`, and `pinned`

But these ingredients do not by themselves answer:

- what makes a rollout canary-shaped rather than just partial
- what makes a downgrade deterministic rather than improvised
- when bounded exposure remains lawful under compatibility and trust posture
- how partial exposure and reversal remain reconstructable

Later hotswap and distributed authority maturity depend on stronger control-plane staging and reversal discipline first. This doctrine closes that gap without claiming live cutover maturity.

## D. Canary Classes

The following high-level canary classes are recognized:

### D.1 Observation-Only Canary

A bounded posture that surfaces candidate state, readiness, or diagnostics without changing authoritative default selection for the wider population.

This class may support evidence gathering but does not by itself change live selection.

### D.2 Bounded Availability Canary

A bounded posture that changes availability or exposure for a constrained scope while keeping canonical identity, compatibility law, and receipt continuity explicit.

This class governs visibility-shaped movement, not arbitrary ad hoc exposure.

### D.3 Bounded Selection Canary

A bounded posture in which lawful selection of a candidate is enabled only for a constrained scope under explicit resolution policy and exact compatibility reasoning.

This class is still subordinate to release contract profile, release index, safety posture, and review posture.

### D.4 Target-Scoped Canary

A canary constrained by exact target semantics rather than only by broad target family labels.

This class exists because target family alone is too coarse for concrete rollout meaning when binary or environment semantics matter.

### D.5 Channel-Scoped Canary

A canary constrained by channel or lane policy such as `beta` or `pinned`, while still preserving that channel membership is not enough without release identity and compatibility law.

Channel scope may support bounded rollout posture, but channels do not replace exact target and profile reasoning.

### D.6 Privileged Or Review-Gated Canary

A canary whose blast radius, publication consequence, trust implication, or runtime sensitivity is high enough that it remains behind explicit review or privileged operator posture.

This class is especially relevant when the canary touches external visibility, trust posture, or runtime-boundary-adjacent behavior.

## E. Deterministic Downgrade Classes

The following high-level downgrade classes are recognized:

### E.1 Policy-Driven Downgrade

A downgrade performed under a frozen, explicit resolution policy and explicit compatibility envelope.

This class depends on deterministic policy semantics rather than operator intuition.

### E.2 Operator-Directed Downgrade

A downgrade initiated by operator intent but still constrained by exact release identity, contract-profile admissibility, target scope, safety posture, and receipt continuity.

Operator direction does not suspend determinism requirements.

### E.3 Bounded Target Downgrade

A downgrade constrained by exact target, install profile, and scoped component set rather than broad family shorthand.

This class prevents target-family-only downgrades from masquerading as lawful exact downgrade execution.

### E.4 Channel Or Selection Downgrade

A downgrade driven through selection posture or lane posture, such as moving from a broader candidate to a narrower, older lawful candidate under explicit policy and receipt continuity.

This class must still preserve release identity and exact target reasoning.

### E.5 Recovery Downgrade

A downgrade used as a recovery move after a failed or unsafe forward path, while remaining distinct from rollback.

This class may rely on rollback-alignment evidence, but it is still a downgrade only if the action selects an older lawful target rather than simply restoring the recorded prior state.

### E.6 Non-Deterministic Or Prohibited Downgrade

Any downgrade based on "whichever older version seems fine", missing receipt continuity, unresolved compatibility posture, target-family-only approximation, or undefined policy is constitutionally non-deterministic and therefore prohibited.

## F. Relationship To Release Contract Profile And Release Index

Canaries and downgrades must remain compatible with release contract profile and release-index resolution law.

Therefore:

- a lower or older version string is never enough by itself
- "previous visible release" is not automatically a lawful downgrade target
- channel membership alone is not enough
- target family alone is not enough
- exact target, install profile, compatibility envelope, trust posture, and resolution policy remain relevant
- the same request and the same canonical inputs must resolve the same downgrade target under the same deterministic policy

The key rule is that canary and downgrade posture consume release truth; they do not redefine it.

## G. Relationship To Receipts And Provenance Continuity

Canary and downgrade execution must produce continuity-compatible receipts.

This means:

- partial exposure must remain reconstructable
- bounded selection movement must remain reconstructable
- downgrade intent, policy, scope, refusal posture, and resulting state must be reconstructable
- canary movement and downgrade movement must not disappear into dashboards, feed entries, filenames, or human memory

Receipt continuity is especially important because the repo already records rollback transaction fields such as `transaction_id`, `from_release_id`, `to_release_id`, `install_profile_id`, `resolution_policy_id`, `install_plan_hash`, `prior_component_set_hash`, and `selected_component_ids`. Later canary and downgrade execution must extend that continuity posture rather than bypassing it.

## H. Relationship To Rehearsal And Rollback Alignment

Canary or downgrade execution may depend on prior rehearsal and rollback-alignment doctrine, but those earlier doctrines do not themselves authorize live execution.

The governing consequences are:

- rehearsal success is not live permission
- rollback alignment and downgrade semantics remain distinct but connected
- a downgrade may depend on rollback-alignment evidence without becoming identical to rollback
- a canary may rely on rehearsal evidence without becoming proof of runtime cutover safety

This doctrine therefore inherits the `Υ-C0` ambiguity eliminations and narrows them for staged exposure and downgrade execution.

## I. Relationship To Safety Policy And Execution Envelope

Safety posture remains upstream.

Canary and downgrade classes are not automatically executable merely because they are now well defined. They still sit inside the release-ops execution envelope and may be:

- inspect-only
- rehearse-able
- validate-able
- bounded mutation
- review-gated execution
- privileged execution
- prohibited

Task catalog and MCP exposure do not imply canary or downgrade authority. Tooling may express requests, but tooling does not grant permission.

## J. Relationship To Runtime Doctrine

If canary or downgrade execution touches runtime lifecycle, replay, snapshot, isolation, or coexistence assumptions, those runtime doctrines remain binding.

This doctrine does not overclaim runtime cutover maturity. In particular:

- canary success is not proof of hotswap readiness
- downgrade success in control-plane terms is not proof that live replay continuity is solved
- bounded selection movement is not proof that restartless replacement is safe
- coexistence doctrine does not authorize live cutover by stealth

Runtime-sensitive canary or downgrade classes therefore remain review-heavy until later checkpoints explicitly say otherwise.

## K. Invalidity And Failure

The following invalidity and failure classes must remain explicit:

- canary_non_representative: the canary scope is too narrow or distorted to justify the claim being made
- canary_overbroad_scope: the supposed canary is too broad to count as bounded exposure
- canary_missing_exact_target_reasoning: target family or channel shorthand was used where exact target semantics were required
- downgrade_non_deterministic: the target depends on convenience, guesswork, or mutable ungoverned heuristics
- downgrade_target_not_lawful: the target exists but is incompatible, unsafe, blocked, or otherwise not lawful
- rollback_downgrade_conflation: rollback and downgrade were treated as interchangeable
- yanked_or_deprecated_semantics_flattened: yanked, deprecated, superseded, downgrade, and rollback postures were collapsed together
- receipt_continuity_missing: staged exposure or downgrade cannot be reconstructed canonically
- review_or_privilege_blocked: the action remains gated regardless of technical feasibility
- runtime_boundary_overclaim: the rollout or downgrade claim exceeds what lifecycle, replay, snapshot, isolation, or coexistence doctrine currently permits

Later checkpoints and tooling must not assume that all canaries are representative or that all downgrades are deterministic merely because the repo stores older artifacts.

## L. Canonical Vs Derived Distinctions

Canonical truth in this area lives in:

- the doctrine frozen here
- upstream governance, runtime, and release doctrine
- canonical release identity, contract-profile, resolution, and transaction receipts
- lawful review and safety posture

Derived surfaces include:

- dashboards
- CI summaries
- local tool output
- generated update feeds
- filenames
- human summaries

Derived views may display canary or downgrade posture, but they must not redefine:

- what counts as a canary
- what counts as deterministic downgrade execution
- what counts as rollback
- what counts as lawful scope

## M. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- `field/` and `fields/` are not interchangeable ownership roots
- `schema/` and `schemas/` are not interchangeable ownership roots
- `packs/` and `data/packs/` are not interchangeable ownership roots
- canonical artifacts remain upstream of projected or generated mirrors
- convenience roots, wrappers, feeds, and dashboards are not automatically canonical
- stale planning numbering or titles must not override the active checkpoint chain
- this doctrine must be extracted from current repo reality and already-frozen law rather than invented as generic deployment folklore

## N. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- canary equals vague small rollout
- downgrade equals choose previous version
- target family alone treated as sufficient downgrade compatibility
- channel membership alone treated as sufficient canary legality
- canary success treated as proof of hotswap readiness
- dashboards or CI wrappers treated as canary doctrine
- rollback, downgrade, yank, and deprecation treated as interchangeable
- staged exposure with no continuity-compatible receipt trail
- tool convenience silently redefining deterministic downgrade semantics

## O. Stability And Evolution

This artifact is `provisional` because it freezes a necessary execution-discipline layer before the next checkpoint and before any honest reconsideration of `Φ-B4`, but it does not claim live rollout or live cutover maturity.

Later work must consume this artifact as upstream law:

- `Υ-C2` for publication and trust execution maturity
- the next checkpoint before any move toward `Φ-B4`
- later reassessment of risky `Φ-B4` and `Φ-B5`
- future `Ζ` blocker reduction and live-ops planning

Updates to this doctrine must remain:

- explicit
- review-aware
- aligned with release, receipt, rehearsal, and runtime law
- non-silent about what still remains unproven

This document answers the current ambiguity set directly:

- canary is not generic rollout folklore
- downgrade is not prior version by convenience
- rehearsal is not live permission
- canary success is not hotswap readiness

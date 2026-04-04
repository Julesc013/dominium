Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-C1, Υ-C2, next checkpoint before Φ-B4, risky Φ-B4, risky Φ-B5, future Ζ planning
Replacement Target: later release-ops, downgrade, rollback, canary, publication, trust, and live-ops operational doctrine may refine procedures and tooling without replacing the rehearsal, sandbox, and rollback-alignment semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_YA_SAFE_REVIEW.md`, `docs/planning/CHECKPOINT_C_PHIB3_YB_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YA.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB3_YB.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`, `docs/release/MANUAL_AUTOMATION_PARITY_AND_REHEARSAL.md`, `docs/release/RELEASE_OPS_EXECUTION_ENVELOPE.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `tools/controlx/README.md`, `tools/controlx/controlx.py`, `tools/controlx/core/execution_router.py`, `tools/controlx/core/queue_runner.py`, `tools/xstack/testx/tests/test_dryrun_tool_runs.py`, `release/update_resolver.py`, `repo/release_policy.toml`, `updates/README.md`, `updates/stable.json`, `data/registries/release_resolution_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/refusal_code_registry.json`, `data/registries/remediation_playbooks.json`

# Release Rehearsal Sandbox And Proof-Backed Rollback Alignment

## A. Purpose And Scope

This doctrine exists to freeze the canonical meaning of release rehearsal sandboxing and proof-backed rollback alignment in the post-`Υ-A`, post-`Φ-B3`, and post-`Υ-B` execution band selected by `C-ΦB3ΥB_SAFE_REVIEW`.

It solves a specific problem. The repository already has real dry-run, refusal, remediation, release-resolution, install-transaction, archive, and trust surfaces, but later work could still drift into dangerous folklore:

- "dry-run" meaning a vague no-op with no compatibility or continuity semantics
- "sandbox" meaning any informal test environment
- rollback being assumed lawful because old artifacts still exist
- rehearsal and live execution producing incompatible evidence
- proof claims collapsing structural checks, compatibility checks, and actual rollback alignment into one story
- runtime cutover maturity being inferred from release-control convenience

This document governs:

- what a release rehearsal sandbox is in Dominium
- what rollback alignment and proof-backed rollback mean
- which release and control-plane action classes may be rehearsed, simulated, structurally validated, semantically validated, rollback-aligned, or remain only partially rehearse-able
- what evidence classes may support rollback alignment
- how those semantics remain subordinate to governance, safety, release, receipt, archive, publication, and runtime doctrine
- what later `Υ-C1`, `Υ-C2`, the next checkpoint, risky `Φ-B4`, risky `Φ-B5`, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- deployment-engine implementation
- rollback-engine implementation
- sandbox-infrastructure implementation
- live cutover workflow implementation
- trust-root rotation implementation
- publication automation
- hotswap implementation
- distributed authority implementation

This layer sits between the earlier parity and rehearsal doctrine, the receipt and provenance doctrine, the release-ops execution envelope, and the later canary, deterministic downgrade, publication or trust execution, and cutover-sensitive runtime prompts.

## B. Core Definition

A release rehearsal sandbox is a bounded, non-canonical execution or analysis envelope that preserves the same relevant release-selection, compatibility, operator-transaction, receipt, and continuity semantics needed for a later live action while explicitly declaring what it does not prove.

Rollback alignment is the constitutional condition in which a proposed rollback path remains lawfully compatible with:

- release identity
- release contract profile
- release-index and resolution semantics
- operator transaction class and review posture
- receipt and provenance continuity
- archive and mirror continuity requirements
- applicable runtime doctrine where cutover-like assumptions reach lifecycle, replay, snapshot, isolation, or coexistence boundaries

Proof-backed rollback means rollback readiness supported by explicit evidence classes rather than by folklore, filename convenience, or raw version ordering.

These concepts differ from adjacent ideas:

- generic testing checks software behavior broadly; rehearsal sandboxing preserves release and control-plane semantics specifically
- a no-op dry-run may prove only that no immediate validation error was found; it does not by itself prove rollback alignment
- archive retention preserves historical artifacts; it does not prove that a rollback path remains lawful or sufficiently evidenced
- downgrade semantics define how downward selection and supersession reasoning work; they do not alone prove that a concrete rollback path is aligned
- operator transaction doctrine defines typed actions and permissions; it does not by itself define the sandbox or proof classes needed before later live cutover work
- live cutover execution changes authoritative state and potentially runtime behavior; rehearsal sandboxing must remain explicitly distinct from that

## C. Why This Doctrine Is Necessary

Release operations now have enough upstream doctrine to describe typed actions, receipts, parity, and execution posture, but not yet enough to claim cutover-safe maturity merely because tools can simulate pieces of the path.

This doctrine is necessary because:

- later hotswap and distributed-authority work will otherwise inherit vague notions of rehearsal and rollback
- rollback readiness must preserve compatibility and selection law, not just artifact availability
- receipt continuity must remain coherent across rehearsal and live execution
- publication, trust, deprecation, yank, supersession, and downgrade work need clearer evidence boundaries
- current repo surfaces already show partial foundations, including dry-run execution routing, deterministic refusal classes, remediation playbooks, and install transaction logs, but those surfaces are not sufficient without one explicit doctrine tying them together

The result is a constitutional layer that keeps release rehearsal honest and keeps rollback claims proof-bearing rather than aspirational.

## D. Rehearsal Classes

The following high-level rehearsal classes are recognized:

### D.1 Structural Rehearsal

Exercises shape, presence, and admissibility checks without claiming semantic or rollback completeness.

Typical scope includes:

- artifact presence
- required field completeness
- schema or manifest shape checks
- deterministic packaging or routing preconditions

### D.2 Compatibility Rehearsal

Exercises the compatibility envelope defined by release contract profile, platform, target family, capability posture, and explicit refusal law.

Typical scope includes:

- contract-profile admissibility
- target-family compatibility
- stability or policy gate checks
- refusal-code driven incompatibility detection

### D.3 Selection And Release-Index Rehearsal

Exercises lawful release selection under release-index and resolution doctrine without claiming that the resulting target is live-executable.

Typical scope includes:

- channel and lane resolution
- release identity selection
- yanked or superseded visibility posture
- downgrade candidate discovery under explicit law

### D.4 Operator-Transaction Rehearsal

Exercises typed operator transaction framing, review posture, refusal posture, and receipt posture without performing the live transaction itself.

Typical scope includes:

- intended transaction class
- approval and review gates
- receipt shape and sequence anchors
- blocked or refused outcomes

### D.5 Rollback-Alignment Rehearsal

Exercises whether a rollback path appears lawfully alignable under current release, continuity, and runtime constraints.

Typical scope includes:

- source and target release identity continuity
- contract-profile continuity
- receipt continuity expectations
- bounded reversibility assumptions

### D.6 Publication Or Trust Adjacent Rehearsal

Exercises publication, trust, or licensing preconditions without claiming that public commitment, trust-root mutation, or live trust acceptance is ready.

This class remains heavily review-gated and may stay partial even when other rehearsal classes are stronger.

### D.7 Non-Rehearsable Or Only Partially Rehearse-Able Classes

Some actions cannot be fully rehearsed under current maturity. Examples include:

- live trust-root rotation
- public commitment changes with external distribution consequences
- runtime cutovers whose safety depends on unsolved lifecycle, replay, snapshot, isolation, coexistence, or hotswap boundaries
- distributed authority actions whose consensus or revocation semantics are not yet constitutionally complete

## E. Sandbox Classes

The following sandbox classes are recognized:

### E.1 Analysis-Only Sandbox

Non-mutating analysis environment for inspection, planning, and structural reasoning. It may evaluate inputs and consequences but must not claim live execution equivalence.

### E.2 Resolution Sandbox

Sandbox that exercises release-index, selection, compatibility, and refusal semantics under realistic policy inputs without committing authoritative release state.

### E.3 Operator-Transaction Rehearsal Sandbox

Sandbox that preserves typed operator transaction framing, review posture, refusal posture, and receipt expectations while keeping outcomes non-live.

### E.4 Bounded Rollback Sandbox

Sandbox that exercises rollback-alignment reasoning against bounded targets, known continuity evidence, and explicit reversibility assumptions without claiming full live rollback proof.

### E.5 Privileged Or Review-Gated Sandbox

Sandbox used only under explicit review or privileged posture because the action class touches publication, trust, licensing, irreversible visibility, or similarly sensitive consequences.

Sandbox classes are constitutional categories, not tool names. A specific script, CLI, or CI job may realize one or more sandbox classes, but no single implementation defines the doctrine.

## F. Rollback Proof Classes

Rollback alignment may be supported only by explicit evidence classes. The minimum recognized proof classes are:

### F.1 Structural Consistency Proof

Evidence that required artifacts, metadata, references, and deterministic identifiers exist in coherent shape for the proposed rollback path.

This is not enough by itself.

### F.2 Compatibility-Envelope Proof

Evidence that the proposed rollback target remains lawful under release contract profile, target family, capability posture, platform constraints, and refusal law.

This proof rejects the idea that "previous version exists" is sufficient.

### F.3 Target And Release-Identity Continuity Proof

Evidence that the rollback path preserves the real release identity and target semantics being reversed or restored, rather than substituting channel labels, filenames, or human shorthand.

### F.4 Receipt And Provenance Continuity Proof

Evidence that the rollback path preserves reconstructable linkage across operator transaction receipts, review posture, validation posture, refusal posture, rehearsal posture, and resulting live posture.

### F.5 Archive And Mirror Availability Proof

Evidence that required artifacts remain retrievable from the archive and, where policy-relevant, from mirror surfaces. This proof is necessary for some rollback paths but is never sufficient by itself.

### F.6 Bounded Reversibility Proof

Evidence that the proposed rollback path has explicit limits, expected resulting state, and known partial or non-reversible boundaries rather than assuming perfect reversal.

The proof classes above are not:

- proof of production success
- proof that runtime cutover safety is solved
- proof that a hotswap boundary is lawful
- proof that an operator may skip review or privilege gates

## G. Relationship To Operator Transaction Doctrine

This doctrine refines operator transaction doctrine; it does not replace it.

The following remain upstream:

- transaction classes
- actor and authority classes
- review posture
- downgrade, rollback, yank, deprecation, supersession, and recovery distinctions
- safety and permission posture

This doctrine adds the rehearsal and proof-bearing expectations around those transaction classes. Rollback alignment must stay compatible with downgrade, yank, supersession, and recovery semantics rather than flattening them into one "undo" concept.

## H. Relationship To Release Index And Release Contract Profile

Rollback alignment must preserve the real release-selection and compatibility envelope used for the live or proposed path.

This means:

- raw version strings are insufficient
- "previous visible release" is not automatically a lawful rollback target
- lane, channel, or feed labels are insufficient without identity and profile context
- rehearsal cannot ignore release contract profile
- proof-backed rollback must preserve target family, contract-profile, and resolution facts instead of using narrative shorthand

Release-index and contract-profile law remain upstream truth. This doctrine governs how rehearsal and rollback evidence must consume that truth.

## I. Relationship To Receipts And Provenance Continuity

Rehearsal and live execution must produce distinguishable but compatible evidence classes.

Therefore:

- rehearsal receipts must not be confused with live execution receipts
- live rollback receipts must preserve continuity with the rehearsed or planned path when such rehearsal was part of the lawful process
- provenance continuity depends on typed operator receipts, refusal posture, review posture, and result posture, not merely on artifact presence
- manual and automated paths must remain parity-compatible where upstream doctrine requires parity

Receipt and provenance doctrine remains the canonical evidence substrate. This doctrine adds the rehearsal and rollback-proof posture that later live work must honor.

## J. Relationship To Archive And Mirror Doctrine

Archive continuity is necessary for many rollback paths but never sufficient alone.

Mirror continuity may support availability reasoning, but mirror presence is not equivalent to rollback readiness, publication approval, or compatibility proof.

Accordingly:

- archive presence does not equal rollback proof
- mirror presence does not equal rollback proof
- rollback alignment may rely on archived retrievability while still failing because continuity, compatibility, or review conditions are not met
- archived existence without coherent receipts still leaves provenance ambiguous

## K. Relationship To Runtime Doctrine

When release operations imply runtime-facing assumptions, rehearsal and rollback alignment must respect:

- lifecycle doctrine
- replay doctrine
- snapshot doctrine
- isolation doctrine
- multi-version coexistence doctrine

This doctrine does not claim that runtime cutover is solved. It explicitly forbids overclaiming that release rehearsal proves:

- safe hotswap
- safe live coexistence handoff
- safe replay continuity across unproven cutover boundaries
- safe snapshot restoration under unsolved authority or isolation conditions

Release-control maturity and runtime cutover maturity remain related but distinct.

## L. Invalidity And Failure

The following invalidity and failure classes must remain explicit:

- rehearsal_incomplete: the rehearsal exercised only part of the needed path
- structural_valid_but_semantically_insufficient: shape checks passed without proving lawful compatibility or rollback alignment
- rollback_target_not_lawful: the proposed target exists but is not lawful under release or transaction doctrine
- archive_present_but_alignment_unproven: required artifacts exist but evidence for lawful rollback remains incomplete
- receipt_chain_incomplete: receipt or provenance continuity is missing, partial, contradictory, or non-canonical
- sandbox_non_representative: the sandbox omitted constraints material to the live path
- review_or_privilege_blocked: the action remains gated regardless of rehearsal strength
- non_reversible_or_partially_reversible: the path cannot be claimed as fully reversible
- runtime_boundary_overclaim: a proof claim exceeds what lifecycle, replay, snapshot, isolation, or coexistence doctrine currently allows

Later tools and checkpoints must not assume all rehearsed paths are equally lawful, equally reversible, or equally representative.

## M. Canonical Vs Derived Distinctions

Canonical truth in this area lives in:

- the doctrine frozen here
- upstream governance, safety, runtime, and release law
- canonical receipts and provenance continuity records
- lawful release identity, contract-profile, and resolution artifacts

Derived surfaces include:

- dashboards
- CI summaries
- local tool output
- filenames
- mirror listings
- human summaries

Derived views may summarize rehearsal or rollback status, but they must not redefine:

- what counts as a sandbox
- what counts as rollback alignment
- what counts as proof
- what counts as readiness

## N. Ownership And Anti-Reinvention Cautions

The following cautions remain binding:

- `field/` and `fields/` are not interchangeable ownership roots
- `schema/` and `schemas/` are not interchangeable ownership roots
- `packs/` and `data/packs/` are not interchangeable ownership roots
- canonical artifacts remain upstream of projected or generated mirrors
- thin convenience roots and tool wrappers are not automatically canonical because they are easier to read or execute
- older planning numbering or titles must not override the active checkpoint state
- this doctrine must be extracted from current repo reality and already-frozen law rather than invented as a greenfield release-ops story

## O. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- treating a dry-run result as rollback proof
- treating archive presence as rollback proof
- treating "previous version exists" as proof of lawful rollback
- treating downgrade semantics alone as rollback alignment
- treating rehearsal output as production success proof
- treating a sandbox as canonical merely because one tool implements it
- treating mirror visibility as rollback readiness
- treating release-control convenience as a license to bypass runtime, provenance, or review doctrine

## P. Stability And Evolution

This artifact is `provisional` because it freezes doctrine that is foundational for the next operational band but not yet proven by later live-cutover maturity work.

Later prompts must consume this artifact as upstream law:

- `Υ-C1` for canary and deterministic downgrade execution alignment
- `Υ-C2` for publication and trust execution maturity
- the next checkpoint before any move toward `Φ-B4`
- later reconsideration of risky `Φ-B4` and `Φ-B5`
- future `Ζ` blocker reduction and live-ops planning

Updates to this doctrine must remain:

- explicit
- review-aware
- aligned with receipts, release law, and runtime law
- non-silent about what changed and what remains unproven

This document answers the current checkpoint ambiguity directly:

- dry-run is not rollback proof
- archive presence is not rollback readiness
- downgrade semantics are not rollback alignment
- rehearsal is not live success proof

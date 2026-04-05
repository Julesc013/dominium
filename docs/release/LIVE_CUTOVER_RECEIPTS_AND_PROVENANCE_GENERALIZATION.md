Status: CANONICAL
Last Reviewed: 2026-04-05
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-D2, next checkpoint before Φ-B5, later Φ-B5 reassessment, future Ζ planning
Replacement Target: later live-cutover, publication, trust, distributed-authority, and live-ops operational doctrine may refine procedures and infrastructure without replacing the generalized receipt and provenance semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_YC_SAFE_REVIEW.md`, `docs/planning/CHECKPOINT_C_PRE_DISTRIBUTED_AUTHORITY_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YC.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB4.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/runtime/HOTSWAP_BOUNDARIES.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`, `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`, `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`, `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `security/trust/trust_verifier.py`, `release/update_resolver.py`, `data/registries/provenance_classification_registry.json`, `data/registries/provenance_event_type_registry.json`, `data/registries/refusal_code_registry.json`, `data/registries/remediation_playbooks.json`

# Live Cutover Receipts And Provenance Generalization

## A. Purpose And Scope

This doctrine exists because the post-`Φ-B4` checkpoint explicitly kept `live-cutover receipt and provenance generalization` in the remaining blocker cluster before any move toward `Φ-B5`.

It solves a specific problem: Dominium already has canonical operator transaction receipts, trust execution and revocation continuity, live trust-transition prerequisites, rehearsal and rollback-alignment law, canary and deterministic downgrade law, and hotswap boundaries. Those layers define what actions mean and when some of them may later become admissible. They do not yet define the stronger evidence model needed when a transition is boundary-sensitive, live-adjacent, trust-bearing, or potentially cutover-like.

Without one explicit doctrine, later work could drift into:

- live-cutover history represented only by ordinary logs
- hotswap-adjacent transitions recorded like simple release metadata edits
- trust and revocation continuity recorded with no boundary-sensitive anchors
- distributed-authority planning assuming receipt continuity that has never been frozen
- dashboards, filenames, mirror changes, or local traces being mistaken for canonical live-cutover evidence

This document governs:

- what a live cutover receipt is in Dominium
- what provenance generalization means for live or boundary-sensitive transitions
- which transition candidate classes require stronger receipt and provenance treatment
- what generalized receipt classes exist
- what continuity anchors must be preserved beyond ordinary operator receipts
- what later `Υ-D2`, the next checkpoint, `Φ-B5`, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- live cutover orchestration
- distributed tracing implementation
- receipt pipeline implementation
- distributed authority implementation
- trust-root rotation implementation
- publication automation

This is a constitutional receipt and provenance layer, not tooling.

## B. Core Definition

A `live cutover receipt` in Dominium is the canonical evidence artifact for a boundary-sensitive transition candidate or transition outcome whose meaning reaches live runtime continuity, trust-bearing posture, or cutover-like release/control-plane movement and therefore requires stronger continuity anchors than an ordinary operator transaction receipt alone.

`Provenance generalization` in this context means extending ordinary operator provenance continuity into live-boundary contexts by preserving:

- stronger continuity anchors
- explicit boundary-sensitive state references
- trust and revocation posture continuity
- archive, mirror, release-index, and release-identity continuity
- partial versus completed transition evidence
- live versus rehearsal distinction

These concepts differ from nearby surfaces:

- generic logs may preserve observations, but they do not automatically preserve canonical boundary-sensitive meaning
- ordinary operator transaction receipts preserve typed control-plane action meaning, but they do not by themselves guarantee boundary-sensitive cutover anchors
- changelog prose summarizes history for humans and does not preserve live-boundary evidence truth
- archive presence proves retention, not cutover continuity
- mirror visibility proves availability posture, not cutover proof
- local tracing or console output proves local observation, not canonical live-cutover truth

## C. Why This Doctrine Is Necessary

This doctrine is necessary because live boundary transitions require stronger evidence than normal release or control-plane actions.

The repo already shows the gap clearly:

- `release/update_resolver.py` records deterministic transaction anchors such as `transaction_id`, `install_plan_hash`, `prior_component_set_hash`, `selected_component_ids`, `trust_policy_id`, and `trust_result`
- `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md` already freezes ordinary receipt and provenance law
- `docs/runtime/HOTSWAP_BOUNDARIES.md` now freezes that some transitions are boundary-sensitive and cannot be inferred from coexistence, restart, or canary success
- `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md` now freezes that later trust-bearing live transitions require an admission layer before operationalization
- `data/registries/provenance_classification_registry.json` and `data/registries/provenance_event_type_registry.json` already preserve a layered provenance vocabulary rather than flattening evidence into one log stream

That foundation is enough to define the generalized evidence model. It is not enough to leave later live-boundary work to ad hoc logs or tool-specific traces.

## D. Transition Candidate Classes

The following high-level transition candidate classes require generalized receipt and provenance treatment.

### D.1 Bounded Runtime-Cutover Candidate

A bounded runtime-adjacent transition whose meaning reaches lifecycle, replay, snapshot, isolation, coexistence, or hotswap-boundary continuity without claiming that full live cutover is already operationalized.

### D.2 Trust-Transition-Linked Cutover Candidate

A boundary-sensitive transition whose meaning is partially defined by trust posture, signer or verifier acceptance, trust-root transition candidates, or live trust-admission posture.

### D.3 Revocation-Linked Continuity Candidate

A transition whose continuity meaning depends on revocation declaration, propagation posture, containment, restoration, or supersession remaining reconstructable across live-boundary-adjacent change.

### D.4 Release/Control-Plane Cutover Candidate

A bounded release or control-plane transition that changes selection, visibility, staged availability, or runtime-adjacent operational posture in a way that ordinary metadata receipts are too weak to represent by themselves.

### D.5 Future Distributed Handoff Candidate

A later transition candidate whose meaning would eventually depend on authority handoff, proof-anchor quorum, distributed replay continuity, or state-partition movement and therefore needs a stronger evidence floor before any honest `Φ-B5` work.

### D.6 Emergency Containment Or Restoration Candidate

A bounded high-urgency or high-sensitivity transition used for containment, restoration, or supersession where partial, blocked, or non-completed boundary movement must remain visible rather than collapsing into a generic success or failure story.

## E. Receipt Classes

The following high-level generalized receipt classes are recognized.

### E.1 Cutover-Intent Receipt

Records the typed intent to perform a boundary-sensitive transition, including scope, review posture, upstream doctrine inputs, and whether the candidate remains only planned, rehearsed, or blocked.

### E.2 Bounded-Transition Receipt

Records an explicitly bounded live-adjacent or runtime-adjacent transition outcome, including what changed, what did not change, and what continuity anchors remain in force.

### E.3 Trust-Linked Receipt

Records a cutover-relevant transition whose meaning depends on trust posture, trust admission prerequisites, signer or verifier posture, or trust-bearing refusal and acceptance rules.

### E.4 Revocation-Continuity Receipt

Records the continuity-bearing aspects of revocation-linked boundary movement, including declaration linkage, propagation posture, containment posture, and restoration or supersession posture.

### E.5 Proof-Anchor Continuity Receipt

Records the continuity anchors used to prove that a transition remained reconstructable across boundary movement, including stronger sequencing or linkage anchors than an ordinary operator receipt requires.

### E.6 Non-Live Or Rehearsal-Only Receipt

Records boundary-sensitive rehearsal, simulation, preflight, or proof-gathering outcomes while remaining explicitly non-live and non-completed.

### E.7 Blocked Or Refused Transition Receipt

Records that a boundary-sensitive transition was blocked, refused, under-specified, non-admissible, or otherwise not lawfully completed, while still preserving the attempted scope and reason for non-completion.

## F. Provenance Generalization

What generalizes from ordinary operator provenance into live-cutover contexts is not merely “more logs.” It is stronger continuity structure.

Generalized provenance must preserve:

- stronger continuity anchors that survive boundary-sensitive transitions
- explicit boundary-sensitive state references where realizations, cutover horizons, or live-adjacent scopes matter
- trust and revocation posture continuity where acceptance or refusal meaning changes
- archive, mirror, release-index, and release-identity continuity without collapsing those concepts together
- partial versus completed transition evidence
- live versus rehearsal distinction
- actor, authority, and review lineage across intent, proof, refusal, and result

Provenance generalization therefore means that ordinary operator provenance is extended, not replaced. The extension is needed because live-boundary transitions create more ways for history to become ambiguous if continuity anchors are too weak.

## G. Relationship To Operator Transaction Doctrine

This doctrine refines ordinary receipt doctrine for boundary-sensitive actions. It does not replace operator transaction classes, actor classes, or permission posture.

The governing consequences are:

- live-cutover receipts remain downstream of typed operator transactions
- generalized receipts provide stronger evidence classes, not new permissions
- ordinary operator receipt law remains the baseline
- later boundary-sensitive work must extend that baseline where stronger continuity anchors are required

This preserves the distinction between ordinary control-plane history and live-boundary-sensitive history.

## H. Relationship To Trust Prerequisites And Revocation Continuity

Trust-transition prerequisites remain upstream.

Therefore:

- a live-cutover receipt cannot claim trust-transition readiness that `Υ-D0` has not admitted
- revocation continuity must remain visible in the generalized receipt model
- trust-state changes and cutover receipts must remain distinguishable but composable
- local verifier behavior must stay subordinate to canonical trust and revocation truth

This doctrine therefore composes with trust law; it does not flatten trust transitions into generic boundary traces.

## I. Relationship To Release Contract Profile And Release Index

Live-cutover receipts must preserve the real compatibility and selection envelope used.

The governing consequences are:

- raw version strings are insufficient
- channel labels are insufficient
- target family labels are insufficient
- exact target and release identity remain relevant
- release contract profile and release-index context must remain reconstructable

Generalized provenance must preserve what was actually selected, what compatibility law applied, and what release identity was in scope rather than falling back to narrative shorthand.

## J. Relationship To Archive And Mirror Doctrine

Archive presence is necessary for some historical reconstruction, but it is not sufficient for cutover provenance continuity.

Mirror visibility is not receipt continuity and is not cutover proof.

Generalized receipts must therefore preserve:

- which historical artifacts remained recoverable
- which archive or mirror consequences followed
- why those consequences do or do not prove anything about boundary movement
- how historical reconstructability survives without confusing archive or mirror surfaces for proof

This keeps archive law and mirror law subordinate to canonical receipt and provenance truth.

## K. Relationship To Runtime Doctrine And Hotswap Boundaries

This doctrine must remain compatible with:

- lifecycle doctrine
- replay doctrine
- snapshot doctrine
- isolation doctrine
- coexistence doctrine
- hotswap-boundary law

It must not overclaim that live transitions are already operationalized.

The key rule is that generalized receipts may preserve that a runtime boundary was relevant, that a cutover candidate was intended, blocked, rehearsed, or bounded, and that stronger continuity anchors were required. They must not pretend that lawful live cutover, lawful distributed handoff, or lawful runtime convergence has already been proven.

## L. Invalidity And Failure

The following invalidity and failure classes must remain explicit:

- `log_only_evidence`
- `ordinary_receipt_only_for_boundary_sensitive_transition`
- `partial_transition_presented_as_completed`
- `noncanonical_or_local_only_trace`
- `boundary_anchor_missing`
- `release_or_target_context_missing`
- `trust_or_revocation_incoherent`
- `archive_or_mirror_inference_error`
- `rehearsal_live_confusion`
- `runtime_boundary_overclaim`
- `future_distributed_handoff_assumed`
- `non_reconstructable_cutover_history`

Later checkpoints and tools must not assume that every transition-shaped event has sufficient boundary-sensitive evidence merely because some logs, receipts, or retained artifacts exist.

## M. Canonical Vs Derived Distinctions

Canonical truth in this area lives in:

- this doctrine
- its paired machine-readable registry
- upstream operator receipt, trust, runtime, release, and hotswap doctrine
- canonical generalized receipt and provenance records where later doctrine explicitly defines them

Derived surfaces include:

- dashboards
- summaries
- filenames
- mirror listings
- local traces
- console output
- changelog prose

Derived views may summarize live-boundary evidence. They must not redefine cutover evidence truth.

## N. Ownership And Anti-Reinvention Cautions

The repo-wide cautions remain binding:

- ownership-sensitive roots remain active
- canonical versus projected/generated distinctions remain binding
- stale planning titles do not override the active checkpoint chain
- convenience surfaces are not automatically canonical
- doctrine must be extracted from current repo reality and already-frozen law rather than invented as a generic tracing system

Additional caution applies because operational logs, local tracing output, and support-style summaries can look more concrete than doctrine while still remaining derived only.

## O. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- local log treated as canonical cutover receipt
- ordinary operator receipt treated as sufficient for a live-boundary transition
- mirror disappearance treated as cutover proof
- changelog prose treated as provenance continuity
- receipt continuity assumed because old artifacts still exist
- dashboard, filename, or console output treated as canonical boundary truth
- trust or revocation continuity recorded with no boundary-sensitive anchors
- doctrine existence treated as implementation maturity

## P. Stability And Evolution

This artifact is `provisional` because it freezes a live-boundary evidence model before `Φ-B5`, not a completed live-cutover system.

It directly enables:

- `Υ-D2 — PUBLICATION_AND_TRUST_OPERATIONALIZATION_ALIGNMENT-0`
- the next checkpoint after the `Υ-D` band
- later reassessment of `Φ-B5 — DISTRIBUTED_AUTHORITY_FOUNDATIONS-0`
- future `Ζ` blocker reduction around distributed handoff, cutover proof, and trust convergence

Updates to this doctrine must remain:

- explicit
- review-aware
- aligned with trust, release, archive, hotswap, and runtime law
- non-silent about what remains unoperationalized

This document answers the current ambiguity set directly:

- logs are not live-cutover receipts
- archive presence is not cutover provenance continuity
- mirror visibility is not cutover proof
- doctrine existence is not live-boundary operational readiness

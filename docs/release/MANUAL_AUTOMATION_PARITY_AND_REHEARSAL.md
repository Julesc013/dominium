Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Υ-B1, Υ-B2, later checkpoints, risky Φ-B4, risky Φ-B5, future Ζ planning
Replacement Target: later release-ops, operator-transaction, publication, and live-ops operational doctrine may refine execution procedures and tooling without replacing the parity and rehearsal semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_YA_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YA.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`, `docs/blueprint/FOUNDATION_READINESS_MATRIX.md`, `docs/blueprint/FOUNDATION_PHASES.md`, `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md`, `tools/controlx/README.md`, `tools/controlx/controlx.py`, `tools/controlx/core/execution_router.py`, `tools/xstack/run.py`, `tools/xstack/controlx/README.md`, `tools/xstack/sessionx/README.md`, `tools/xstack/sessionx/stage_parity.py`, `tools/xstack/testx/tests/test_stage_parity_status_surfaces.py`, `tools/xstack/testx/tests/test_stage_parity_transitions_surfaces.py`, `tools/xstack/testx/tests/test_dryrun_tool_runs.py`, `release/update_resolver.py`, `repo/release_policy.toml`, `updates/README.md`

# Manual Automation Parity And Rehearsal

## A. Purpose And Scope

This doctrine exists to freeze the canonical meaning of manual and automation parity plus rehearsal after `Φ-B3` and inside the narrow post-`Υ-A` interleaving band chosen by `C-ΥA_SAFE_REVIEW`.

It solves a specific problem: the repository already contains real control-plane and execution surfaces across ControlX, XStack, release resolution, session-stage parity adapters, strict review gates, deterministic validation profiles, dry-run evidence, and rollback-aware release logic. Without one explicit doctrine, later work could still drift into unsafe folklore:

- automation becoming the real contract while the human path decays
- manual workarounds keeping different semantics from the automated path
- rehearsal meaning confidence theater instead of explicit preflight semantics
- tool wrappers silently becoming the operational law

This document governs:

- what manual and automation parity means in Dominium
- what rehearsal, dry-run, preflight, and simulation mean at a constitutional level
- which action classes require parity, limited parity, rehearsal, or intentionally non-parity
- how parity and rehearsal remain subordinate to governance, safety, runtime, and release doctrine
- what later `Υ-B1`, `Υ-B2`, the next checkpoint, risky `Φ-B4`, risky `Φ-B5`, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- deployment or orchestration tooling implementation
- dry-run engine implementation
- live release operations
- publication workflows
- trust-root rotation
- hotswap or distributed authority execution

This is a constitutional execution-envelope standard, not operational machinery.

## B. Core Definition

Manual and automation parity in Dominium means that when a lawful action class is exposed through both a human-operated path and an automated or tool-mediated path, both paths must preserve the same authoritative inputs, typed intent, preconditions, refusal rules, review posture, resulting state semantics, and audit anchors even if they differ in UX, transport, or convenience.

Rehearsal in Dominium means a governed pre-execution exercise of an action model that is explicitly typed as non-live, bounded-live, or structurally simulated and whose limits are declared up front.

Dry-run means a non-authoritative execution envelope that evaluates admissibility, sequencing, validation, and likely consequences without silently mutating authoritative state.

Preflight means a bounded admissibility and readiness check performed before a later action path proceeds.

Simulation in this doctrine means a governed model exercise that may approximate future behavior or selection outcomes without claiming that live cutover, live runtime exchange, or privileged publication effects have already been proven.

These meanings differ from nearby surfaces:

- automation availability
  - a script existing does not prove parity
- UI or operator convenience
  - a human-friendly wrapper does not define semantics
- testing in general
  - tests may support parity evidence but are not parity by themselves
- checkpoint creation
  - checkpoints record state and readiness; they are not rehearsals of live action classes by default
- speculative planning
  - planning may propose an action model without exercising it

Parity is therefore not symmetry of interface shape. It is symmetry of governed meaning.

## C. Why Parity Is Necessary

Parity is necessary because high-impact control-plane and runtime-adjacent actions must not become automation-only black boxes and must not remain manual folklore with subtly different effects.

The repo already shows real parity pressure:

- `tools/xstack/sessionx/stage_parity.py` routes `cli`, `tui`, and `gui` surfaces through shared session-control semantics
- `tools/xstack/testx/tests/test_stage_parity_status_surfaces.py` and `tools/xstack/testx/tests/test_stage_parity_transitions_surfaces.py` verify equal status and transition results across surfaces
- `tools/controlx/controlx.py` and `tools/controlx/core/execution_router.py` already distinguish dry-run from live routing while preserving gate-aware execution structure

Without parity doctrine, later release and rollback work would drift toward:

- one privileged automation lane with semantics humans cannot inspect or reproduce
- one manual lane with undocumented exceptions
- mismatched refusal behavior between wrapper, operator flow, and machine surface
- audit gaps where identical-looking actions mean different things depending on who invoked them

Parity is needed for:

- operator understanding
- auditability
- recovery
- explainability
- future live-ops maturity
- bounded review of later hotswap or distributed cutover work

## D. Why Rehearsal Is Necessary

Rehearsal is necessary because high-impact actions need explicit preflight semantics before later runtime or release-control work can claim operational maturity.

The repo already shows that rehearsal is expected, but not yet operationalized as final live machinery:

- `docs/blueprint/FOUNDATION_READINESS_MATRIX.md` marks compatibility-governed update rehearsal as ready-now while treating production-like rehearsal as foundation-ready but not implemented
- `docs/blueprint/STOP_CONDITIONS_AND_ESCALATION.md` repeatedly converts uncertainty into manual review and rehearsal-only design review rather than live rollout
- `tools/controlx/core/execution_router.py` already has an explicit dry-run path that preserves gate structure without silently claiming live success

Rehearsal provides:

- bounded confidence
- structural and policy visibility
- reviewable evidence
- early refusal and remediation signals
- safer comparison between manual and automated routes

Rehearsal is not:

- proof of production success
- proof of live cutover safety
- proof of hotswap legality
- proof of distributed authority handoff

## E. Action Classes And Parity Expectations

The constitutional action classes below define whether parity is required, desirable, limited, not applicable, or prohibited in automation.

### E1. Read And Inspect Actions

Examples include inspection of doctrine, release state, indices, manifests, logs, reports, and compatibility evidence.

Parity expectation: `required`.

The governing rule is:

- human and automated inspection paths must preserve the same underlying facts and must not silently redact, enrich, or reinterpret canonical truth differently by convenience

### E2. Planning And Checkpoint Actions

Examples include checkpoint review, sequencing, readiness analysis, and continuity reporting.

Parity expectation: `desirable`.

The governing rule is:

- manual and automated planning paths should preserve the same authority order, stop conditions, and checkpoint interpretation
- exact UX symmetry is not required because these are planning-heavy and prose-heavy tasks

### E3. Bounded Mutation Actions

Examples include scoped non-canon documentation or registry changes, deterministic support-artifact creation, and controlled local support-path mutation.

Parity expectation: `required_when_both_paths_exist`.

The governing rule is:

- if a bounded mutation can be done both manually and through automation, the authoritative inputs, mutation targets, refusal semantics, and validation floor must align

### E4. Operator Transactions

Examples include governed selection changes, rollback preparation, downgrade preparation, yank or supersession recording, and recovery or remediation requests.

Parity expectation: `required_with_review_posture_preserved`.

The governing rule is:

- manual and automated operator paths must not differ on typed intent, review requirements, transaction classification, reversibility posture, or traceability obligations

### E5. Release-Control Actions

Examples include release selection resolution, manifest preparation, index inspection, archive staging, and update-plan construction.

Parity expectation: `required_or_limited_by_gate`.

The governing rule is:

- parity is required for lawful inspection, planning, validation, and selection semantics
- parity may be limited for trust-bearing or publication-adjacent mutation because permission posture remains narrower than exposure posture

### E6. Publication, Trust, And Licensing Actions

Examples include publication approval, signer or trust-root posture change, and licensing posture change.

Parity expectation: `limited_and_strongly_review_gated`.

The governing rule is:

- a manual fallback understanding must exist
- automation may remain intentionally limited or prohibited
- parity does not erase privileged or review-heavy status

### E7. Risky Runtime-Affecting Actions

Examples include actions that touch lifecycle, replay, snapshot, isolation, coexistence, hotswap-sensitive, or distributed-authority-sensitive envelopes.

Parity expectation: `limited_or_prohibited_in_automation`.

The governing rule is:

- manual and automated semantics must still be comparable where both exist
- but automation may be constitutionally blocked until later doctrine and proof exist

### E8. Intrinsically Manual Or Manual-Review Actions

Examples include explicit human signoff, authority reassessment, or protected-root review.

Parity expectation: `not_applicable_or_prohibited_in_automation`.

The governing rule is:

- some action classes intentionally preserve a human-only boundary
- lack of automation parity here is constitutional, not a defect

## F. Rehearsal Classes

The constitutional rehearsal classes are:

### F1. No-Op Inspection

Read-only rehearsal of current state, inputs, and expected action envelope.

### F2. Dry-Run Planning

Non-mutating execution of sequencing, routing, gate checks, or action preparation. ControlX dry-run routing is repo evidence for this class.

### F3. Structural Validation Rehearsal

Validation of required artifacts, typing, manifests, registries, traces, or execution prerequisites without claiming live success.

### F4. Compatibility Rehearsal

Evaluation of release contract profile, target compatibility, downgrade admissibility, or coexistence admissibility under explicit refusal rules.

### F5. Release-Selection Rehearsal

Exercise of index, resolution, and policy logic to show what would be chosen or refused without silently performing privileged publication or cutover.

### F6. Operator Transaction Rehearsal

Typed rehearsal of rollback, downgrade, yank, remediation, or selection-affecting transaction envelopes without claiming that privileged live execution has already been approved.

### F7. Bounded Sandbox Rehearsal

Rehearsal in an explicitly separate or non-authoritative sandbox that may approximate live conditions while still remaining constitutionally distinct from live production state.

### F8. Non-Rehearsable Or Intrinsically Privileged Actions

Some actions remain non-rehearsable in any meaningful sense or cannot be automated into rehearsal without changing their nature. Trust-root posture changes and public-release approvals are examples of strongly review-heavy categories.

## G. Relationship To Task Catalog And MCP

Task cataloging does not imply parity.
MCP exposure does not imply parity.
Parity does not imply permission.

The governing consequences are:

- a task family may be cataloged yet still have no lawful automated parity path
- an MCP surface may be exposed yet still remain review-gated or proposal-only
- an action may achieve strong parity across manual and automated paths and still remain blocked by safety policy
- tool presence, wrapper presence, or endpoint presence must not silently become the operational contract

This preserves the stack already frozen in `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, and `docs/agents/AGENT_SAFETY_POLICY.md`.

## H. Relationship To Operator Transaction Doctrine

Operator transactions are the clearest parity-sensitive class in this band.

The governing consequences are:

- rollback, downgrade, yank, supersession, and recovery semantics must remain typed across manual and automated paths
- a scripted path must not skip transaction identity, review posture, reversibility classification, or traceability requirements
- a human path must not quietly apply different criteria than the automated path for admissibility or refusal
- rehearsal may be required before a live operator action class is considered operationally mature

Parity and rehearsal do not erase operator review posture. They standardize meaning across paths.

## I. Relationship To Release Doctrine

Parity and rehearsal remain subordinate to release doctrine.

The governing consequences are:

- build graph lock remains upstream
- release contract profile remains upstream compatibility truth
- release index and resolution alignment remain upstream selection law
- archive and mirror constitution remain upstream on availability versus history
- publication, trust, and licensing gates remain upstream on permission posture

This means:

- a manual release-selection rehearsal and an automated one must agree on admissibility and refusal semantics
- dry-run or simulated release work must not silently cross into publication approval
- archive presence or feed generation remains evidence or preparation, not publication

## J. Relationship To Runtime Doctrine

Parity and rehearsal must not flatten runtime distinctions.

The governing consequences are:

- actions touching lifecycle must preserve lifecycle posture rather than treating all transitions as generic operations
- actions touching replay must preserve causality and evidence boundaries
- actions touching snapshot must preserve the distinction between captured state and proved live handoff
- actions touching isolation must preserve containment semantics
- actions touching coexistence must consume `docs/runtime/MULTI_VERSION_COEXISTENCE.md` rather than treating side-by-side presence as operational permission

Most importantly:

- rehearsal does not prove live cutover
- rehearsal does not prove hotswap legality
- rehearsal does not prove distributed authority handoff

Those later claims require later doctrine and later checkpoints.

## K. Invalidity And Limits

Parity and rehearsal are not always total.

Parity may be:

- complete
- partial
- limited by privilege posture
- manual-only by doctrine
- automation-prohibited by doctrine

Rehearsal may be:

- complete for structural and selection semantics
- partial for bounded sandbox behavior
- structurally informative but non-authoritative
- blocked by policy
- incapable of proving live behavior

The main invalidity and limit categories are:

- `parity_unproven`
- `manual_path_missing`
- `automation_path_missing`
- `semantic_mismatch_between_paths`
- `refusal_mismatch_between_paths`
- `validation_floor_mismatch`
- `audit_anchor_mismatch`
- `permission_confused_with_exposure`
- `permission_confused_with_parity`
- `rehearsal_claims_live_proof`
- `rehearsal_mutates_authoritative_state`
- `runtime_boundary_overclaim`
- `publication_or_trust_overreach`

Later tooling must not assume that every action class is equally rehearseable or equally parity-complete.

## L. Canonical Vs Derived Distinctions

Canonical surfaces include:

- this doctrine
- its paired machine-readable registry
- upstream safety, runtime, release, and checkpoint doctrine
- typed operator and release-control records where later doctrine explicitly defines them

Derived surfaces include:

- UI flows
- CLI wrappers
- CI wrappers
- dashboards
- convenience logs
- status screens
- generated feed summaries

Derived flows may realize parity or rehearsal, but they must not redefine what parity or rehearsal means.

## M. Ownership And Anti-Reinvention Cautions

The repo-wide cautions remain fully active:

- `fields/` remains canonical semantic field substrate; `field/` remains transitional
- `schema/` remains canonical semantic contract law; `schemas/` remains projection-facing
- `packs/` remains canonical for runtime packaging and activation scope; `data/packs/` remains scoped authored-pack authority in residual split territory
- canonical versus projected/generated distinctions remain binding
- old planning-numbering drift does not override the active checkpoint chain
- parity and rehearsal law must be extracted from repo doctrine and current execution surfaces rather than invented greenfield

Additional caution:

- the thin presence of a script, wrapper, CI entrypoint, or dashboard does not prove that the script is the true semantic owner of an action class

## N. Anti-Patterns And Forbidden Shapes

The following shapes are constitutionally forbidden:

- automation-only control path for a high-impact action where doctrine requires a human-comprehensible mirror
- manual path with different semantics than the automated path
- automation exists, therefore parity is achieved
- task exposed, therefore parity is achieved
- parity achieved, therefore permission is granted
- dry-run that silently mutates authoritative state
- rehearsal treated as production-success proof
- UI or CI wrapper treated as parity law
- release/control path that becomes unrehearsable by convenience where doctrine requires rehearsal
- automation that bypasses operator transaction typing, release contract profile, or publication gates

## O. Stability And Evolution

This artifact is `provisional` but canonical.

It directly enables:

- `Υ-B1` follow-on work around deeper release-ops alignment
- `Υ-B2` follow-on work around broader operator-transaction implementation alignment
- the next checkpoint before any move into `Φ-B4`
- later guarded reassessment of `Φ-B4` and `Φ-B5`
- future `Ζ` blocker reduction around rehearsal, operator discipline, and operational-boundary maturity

Updates must remain:

- explicit
- auditable
- non-silent about changed parity posture
- non-silent about changed rehearsal limits

Later work may refine operational procedures and tooling, but it may not silently:

- collapse parity into exposure
- collapse exposure into permission
- collapse rehearsal into production proof
- let wrappers or CI flows redefine the control-plane contract

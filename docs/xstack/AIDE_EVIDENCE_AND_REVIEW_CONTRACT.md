Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: X-4, AIDE extraction review
Replacement Target: later explicit portable evidence/review checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `data/registries/derived_artifacts.json`, `validation/validation_engine.py`, `tools/xstack/controlx/orchestrator.py`, `tools/xstack/securex/check.py`, `tools/xstack/auditx/check.py`, `tools/xstack/testx/runner.py`, `appshell/command_registry.py`, `appshell/commands/command_engine.py`, `security/trust/trust_verifier.py`, `tools/review/xi4z_structure_approval_common.py`, `tools/review/xi5x2_common.py`, `data/restructure/xi4b_review_manifest.json`, `data/restructure/xi4z_decision_manifest.json`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/xstack/CI_GUARDRAILS.md`, `docs/xstack/ARCH_DRIFT_POLICY.md`

# AIDE Evidence and Review Contract

## A. Purpose and Scope

This artifact freezes the canonical portable evidence and review contract that later XStack/AIDE prompts may reuse.

It exists because:

- `X-0` froze what XStack means now and what remains outside the current series
- `X-1` classified which live surfaces are portable core, ops, runtime, Dominium-retained, legacy, or mixed
- `X-2` froze the portable task unit and explicitly required evidence, review, permission, and refusal hooks
- later extraction work still needs a smaller and stricter contract for evidence and review truth itself

This artifact solves a specific narrowing problem:

- the live repo already has findings, validation reports, trust verification records, refusal payloads, review manifests, readiness contracts, summaries, dashboards, and command-status views
- later AIDE work needs the portable minimum those surfaces imply
- that portable minimum must be frozen without smuggling in workflow-engine, scheduler, daemon, storage-backend, or product-shell semantics

This artifact governs:

- what portable evidence means in the live XStack/AIDE sense
- what portable review means in the live XStack/AIDE sense
- which fields every canonical portable evidence or review object must expose
- which boundaries must remain explicit
- which parts are portable now versus Dominium-retained now versus deferred until after the playable baseline exists
- which later prompts may treat this artifact as their fact base

This artifact is downstream of `X-0`, `X-1`, and `X-2`.
It does not reopen scope, inventory, or task-contract classification.
It narrows those earlier artifacts into the portable evidence and review truth only.

This artifact must preserve current repo reality:

- admissible `Zeta` doctrine and gating work is complete
- the immediate product priority remains the canonical repo-local playable baseline and repo stabilization
- XStack/AIDE work must support clarification, modularization, and contract extraction without competing with the baseline path

This artifact is a contract freeze.
It does not implement a review workflow engine, evidence storage platform, queue, daemon, scheduler, adapter layer, compiler, or broader AIDE runtime.

## B. Current-State Definition of Portable Evidence

Current definition:

Portable evidence is a canonical evidence object or canonical evidence reference that records a governed claim, result, finding, validation state, trust state, or review-relevant fact with stable identity, evidence class, provenance, subject linkage, integrity state, validation state, and portability limits, without embedding repo-local storage layout, workflow runtime, UI summary formatting, or product-shell execution details.

Portable evidence is portable now when it captures the minimum truth needed for another XStack/AIDE consumer to understand:

- what the evidence is
- where it came from
- what task, subject, or governed surface it concerns
- how it was collected or derived
- whether it is intact and valid
- whether it matters for review or gating
- what portability limits still bind it

The portable evidence model must distinguish the following.

### Canonical Evidence

Canonical evidence is the evidence truth that a governed consumer may rely on directly.
In the live repo this is already implied by sources such as `data/registries/derived_artifacts.json`, which classifies artifacts as `CANONICAL`, `DERIVED_VIEW`, or `RUN_META`, marks whether canonical hashing is required, and records whether the artifact is used for gating.

Canonical evidence is not defined by file extension or by whether it is convenient to read.
It is defined by the governing contract attached to the evidence object.

### Derived Evidence

Derived evidence is a deterministic projection, rendering, or summary produced from canonical evidence.
It may be useful and repeatable, but it does not redefine the underlying claim.
Examples in the live repo include markdown summaries and human-facing reports that derive from canonical JSON outputs.

### Evidence References

Evidence references are stable pointers to evidence objects or bundles, typically with path and integrity metadata such as `sha256`.
The live repo uses this pattern repeatedly in review manifests and decision manifests through bundle entries and source evidence hash lists.

Evidence references are portable now.
Concrete storage roots, retention automation, and publication backends are not.

### Evidence Summaries and Views

Summaries, dashboards, UI cards, markdown reports, and rendered inventories are derived views.
They may improve operator comprehension, but they must not redefine canonical evidence class, integrity status, validation status, or review relevance.

### Task-Linked Evidence Versus Broader Product or Runtime Telemetry

Task-linked evidence is evidence explicitly attached to a governed task, subject, or review decision.
Broader telemetry includes host details, timestamps, supervisor traces, IPC traces, run-cache metadata, and product-shell logging.

Task-linked evidence is part of the portable contract when it is canonical or referenceable.
Broader telemetry is real and useful inside Dominium, but it is not portable evidence truth by default.

### Portable Evidence Versus Dominium-Retained Evidence

Portable now:

- canonical evidence identity and class
- provenance and collection method
- subject and task linkage
- integrity and validation state
- review relevance and portability limits
- evidence references with stable integrity metadata

Dominium-retained now:

- exact write roots and storage layout
- host-specific run metadata
- operator-facing log routing
- AppShell and launcher status projections
- repo-local cache, retention, and cleanup rules

## C. Current-State Definition of Portable Review

Current definition:

Portable review is a canonical contract or canonical review linkage that records whether review is required, what subject is under review, what reviewer role or authority class is needed, what evidence must be considered, what state the review is in, what threshold or gate condition applies, and what outcome, escalation, or rejection semantics follow, without embedding workflow-engine, queue, assignment, or product-shell semantics.

Portable review is portable now when it captures the minimum truth needed for another XStack/AIDE consumer to understand:

- whether review is required
- what is being reviewed
- what kind of authority must review it
- what evidence the review depends on
- whether the review is pending, blocked, completed, acknowledged, approved, rejected, or escalated
- what outcome changes the governed state

The portable review model must distinguish the following.

### Review Requirement

A review requirement is the canonical declaration that a task, evidence object, decision candidate, or governed subject cannot be treated as complete, promoted, or accepted without review.
The requirement exists even before any human or runtime performs the review.

### Review State

Review state describes where the subject sits relative to the required review.
Examples supported by the live repo include pending, blocked by missing prerequisites, deferred, resolved, or approved-for-next-step style states.

### Review Outcome

Review outcome is the authoritative decision after required review is executed.
Outcomes may include approved, acknowledged, rejected, deferred, or escalated.

### Approval Versus Acknowledgement

Approval changes the governed decision state and satisfies a gate or readiness threshold.
Acknowledgement records that the evidence or issue was seen, but it does not imply that the governed subject is accepted.

The portable contract must preserve that difference.

### Escalation Versus Rejection Versus Refusal

Escalation means the current review posture is insufficient and a stronger or broader review is required.
Rejection means review occurred and produced a negative outcome on the subject.
Refusal means the system or operator will not even treat the requested review or action as lawful to begin with, usually because required authority, compatibility, policy, or prerequisite evidence is missing.

### Portable Review Versus Dominium-Retained Review Workflow

Portable now:

- review requirement
- review subject
- reviewer role or authority class
- review state
- review thresholds or gate conditions
- review outcome and escalation semantics
- review evidence linkage

Dominium-retained now:

- who exactly gets assigned
- where the review happens
- queueing and SLA behavior
- notification routing
- product-shell affordances
- repo-local command and exit-code behavior

## D. Portable Evidence Contract Fields

Every portable evidence object must specify the following fields.

| Field | Requirement | Meaning |
| --- | --- | --- |
| `evidence_id` | required | Stable canonical evidence identifier. It must survive rendering, relocation, or wrapper changes. |
| `evidence_kind` | required | Stable evidence category such as findings, validation report, trust verification record, review manifest, or readiness record. |
| `evidence_class` | required | Canonical evidence class. At minimum it must distinguish canonical evidence, derived view, run metadata, and reference-only evidence. |
| `provenance` | required | Producer, authoritative origin surface, and governing source chain for the evidence. |
| `subject_refs` | required | Stable references to the governed subject, artifact, decision candidate, or contract the evidence concerns. |
| `related_task_refs` | conditional | Task identifiers or task references when the evidence is tied to a portable task. |
| `collection_or_derivation_method` | required | How the evidence was collected, generated, or derived, including whether it is direct, computed, bundled, or projected from canonical sources. |
| `integrity_status` | required | Hash, signature, canonicalization, or corruption posture sufficient to judge whether the evidence is intact. |
| `validation_status` | required | Whether the evidence passed, failed, or bypassed validation checks relevant to its contract. |
| `review_relevance` | required | Whether the evidence is advisory, gate-bearing, escalation-bearing, or otherwise materially relevant to review. |
| `classification_level` | conditional | Classification, trust, sensitivity, or handling level when the evidence contract requires one. |
| `evidence_scope` | required | The bounded scope of what the evidence does and does not prove. |
| `evidence_refs` | conditional | Stable references to related evidence objects or bundle members when the object is a manifest, bundle, or linkage record rather than a standalone payload. |
| `stability_retention_notes` | required | Stability class, regeneration expectations, and retention posture for the evidence. |
| `portability_limits` | required | Repo-local assumptions, coupled roots, or product/runtime dependencies that still limit portability. |
| `compatibility_notes` | required | Version, schema, refusal-on-unknown, and compatibility expectations for the evidence contract itself. |
| `stability` | required | Current stability class and the threshold for future change. |

Operational notes:

- `evidence_class` is required because the live repo already distinguishes canonical, derived, and run metadata artifacts in `data/registries/derived_artifacts.json`
- `integrity_status` is required because canonical hashes, trust verification, and deterministic fingerprints are already part of live evidence surfaces
- `evidence_scope` is required so a summary or bundle does not get misread as proof of more than it actually establishes
- `evidence_refs` is conditional rather than universal because some evidence objects embed their own result payload while others act as manifests that point to hashed members

## E. Portable Review Contract Fields

Every portable review object or canonical review linkage must specify the following fields.

| Field | Requirement | Meaning |
| --- | --- | --- |
| `review_id` | required | Stable canonical review identifier. |
| `review_kind` | required | Stable review category such as approval review, acknowledgment review, escalation review, readiness review, or policy review. |
| `review_subject` | required | Stable reference to the task, evidence object, contract, decision candidate, or governed surface under review. |
| `required_reviewer_roles` | required | The reviewer role, authority class, or approval class needed for the review to be valid. This does not require naming specific people or queue owners. |
| `review_requirement` | required | Whether review is mandatory, advisory, or conditional, and what triggered that requirement. |
| `review_state` | required | Current review posture such as pending, blocked, deferred, completed, escalated, or rejected. |
| `review_thresholds_or_gate_conditions` | required | Gate conditions, decision thresholds, or readiness rules the subject must satisfy for review to conclude positively. |
| `review_outcome` | required | The authoritative result of review, including approval, acknowledgement, rejection, deferment, or escalation. |
| `escalation_rules` | required | Conditions that force stronger review, broader authority, or further evidence before a conclusive outcome is allowed. |
| `refusal_rejection_semantics` | required | Explicit distinction between refused review initiation, rejected review outcome, and blocked review posture. |
| `review_evidence_links` | required | Stable links or references to the evidence objects the review considered or depends on. |
| `portability_limits` | required | Repo-local assumptions, product coupling, or workflow-specific details that remain outside the portable review contract. |
| `compatibility_notes` | required | Version, schema, stability, and refusal-on-unknown expectations for the review contract itself. |
| `stability` | required | Current stability class and the threshold for future change. |

Operational notes:

- `required_reviewer_roles` is portable now because reviewer authority class is real and reusable, while specific assignment mechanics remain Dominium-retained
- `review_requirement` is separate from `review_state` because the live repo already distinguishes mandatory review from whether that review has started or completed
- `review_evidence_links` is required because live review manifests repeatedly point to hashed source evidence rather than redefining it inline

## F. Required Boundary Distinctions

The following boundaries remain mandatory.

### Evidence Versus Logs

Logs may help operators debug or reconstruct a run.
They are not canonical evidence by default.
An evidence object may reference logs, but raw logs do not become canonical evidence unless a stronger contract promotes them.

### Evidence Versus Metrics or Telemetry

Metrics and telemetry may support diagnosis, trend analysis, or operator visibility.
They do not automatically satisfy evidence obligations or review thresholds.
The portable evidence contract treats telemetry as advisory unless explicitly promoted by a stronger contract.

### Canonical Evidence Versus Rendered Summaries

Canonical evidence carries the governed claim.
Rendered summaries, dashboards, markdown reports, and UI cards are derived views.
They may not redefine evidence class, integrity status, validation status, review relevance, or scope.

### Review Requirement Versus Review Execution

Review requirement is the contract-level truth that review must happen.
Review execution is the runtime or human workflow that performs it.
Portable review freezes the requirement, roles, state, thresholds, outcome, and evidence links.
It does not freeze queues, assignment routing, notification policy, or workflow timing.

### Refusal Versus Rejection Versus Escalation

Refusal means the requested action or review is not lawful to initiate.
Rejection means review occurred and the subject did not pass.
Escalation means the current review posture is insufficient and stronger review is required.

### Evidence Production Versus Evidence Promotion or Reclassification

Evidence production creates or emits an evidence object under an existing contract.
Evidence promotion or reclassification changes the authority class of an evidence object, such as treating a derived view or shadow artifact as canonical truth.

Those must remain separate because the live repo already treats promotion toward canonical status as a stricter act than simply writing a report.

## G. Repo-Grounded Rationale

These fields and distinctions are the portable minimum because the live repo already relies on them.

### Validation and Orchestration Surfaces

- `validation/validation_engine.py` builds deterministic validation reports with identifiers, categories, messages, warnings, errors, metrics, fingerprints, and separate rendered outputs
- `tools/xstack/controlx/orchestrator.py` emits structured findings and artifact rows with severity, code, message, file and line references, artifact paths, and `sha256`
- `tools/xstack/testx/runner.py` ties execution results to deterministic fingerprints, changed files, impact scope, and emitted report objects

These surfaces prove that identity, provenance, integrity, validation state, and scope are not aspirational.
They are already part of how the repo judges governed outputs.

### Compat, Control, Secure, Audit, and Test Surfaces

- `tools/xstack/securex/check.py` emits structured findings and refusal-bearing security outcomes
- `tools/xstack/auditx/check.py` reads canonical findings and maps them into pass, fail, or refusal posture
- `tools/xstack/core/failure.py` already classifies failure classes that matter to evaluation and review
- `data/registries/derived_artifacts.json` explicitly distinguishes canonical, derived, and run metadata artifacts and records whether they are used for gating

These surfaces justify freezing portable evidence class, integrity state, validation status, review relevance, and refusal boundaries now.

### AppShell, Command, and Reporting Surfaces

- `appshell/command_registry.py` records refusal code mappings, stability, deterministic fingerprints, and output schema descriptors
- `appshell/commands/command_engine.py` produces structured refusal payloads with refusal codes, reason, remediation hints, nested refusal detail, and error rows
- those command surfaces show why product commands and operator responses must remain distinct from canonical review truth

They support the portable distinction between review and refusal, but they do not justify treating product command payloads as the portable review contract itself.

### Trust, Review, Classification, and Governance Patterns

- `security/trust/trust_verifier.py` already records trust level, signature status, refusal posture, and validation class for governed artifacts
- `tools/review/xi4z_structure_approval_common.py` defines decision classes, approved and deferred outputs, and readiness-contract relationships
- `tools/review/xi5x2_common.py` already carries `manual_review_required`, `resolution_status`, `semantic_risk_level`, `missing_precondition_type`, `xi6_blocker`, and `evidence_refs`
- `data/restructure/xi4b_review_manifest.json` and `data/restructure/xi4z_decision_manifest.json` bundle source evidence hashes, validation states, missing inputs, decision outcomes, and readiness status
- `docs/agents/AGENT_MIRROR_POLICY.md` reinforces canonical versus derived truth
- `docs/xstack/CI_GUARDRAILS.md` reinforces that prompts are not authoritative and gate-bearing outputs remain authoritative
- `docs/xstack/ARCH_DRIFT_POLICY.md` shows that architecture drift updates require stronger review and validation posture

These surfaces justify freezing reviewer role, review requirement, thresholds, outcome, evidence linkage, escalation, and evidence reclassification risk now.

## H. What Is Portable Now Versus Not Portable Now

### Portable Now

The following evidence and review elements are portable enough to freeze now:

- evidence identity, kind, and class
- provenance and collection or derivation method
- subject references and task references
- integrity status and validation status
- review relevance and evidence scope
- evidence references with stable integrity metadata
- reviewer role or authority class
- review requirement, state, thresholds, outcome, and evidence linkage
- explicit refusal, rejection, blocked, approval, acknowledgement, and escalation semantics
- portability limits, compatibility notes, and stability markers
- canonical-versus-derived markers

### Dominium-Retained Now

The following elements remain Dominium-owned or context-specific:

- concrete storage roots such as `docs/audit/**`, `.xstack_cache/**`, product-shell status locations, and local bundle write paths
- exact `FAST`, `STRICT`, and `FULL` gate wiring and repo-local enforcement rules
- AppShell exit-code dispatch, product command descriptors, and launcher or setup affordances
- concrete trust-root registries, release policy tables, pack signing policy identifiers, and repo-local trust plumbing
- exact reviewer identities, assignment rules, notification routing, and operator workflow expectations
- Xi-specific review manifests, readiness contracts, and restructuring workflows as live Dominium implementations rather than portable workflow law

### Deferred Until After the Playable Baseline

The following elements are intentionally deferred:

- evidence storage backends and lifecycle automation
- workflow engines, queues, SLAs, or review assignment services
- remote approval or multi-tenant review infrastructure
- adapter transport for cross-repo evidence publication or review submission
- automatic evidence promotion or reclassification engines
- cross-repo review federation and publishable evidence registries
- runtime policies for concurrency, batching, or long-lived review orchestration

This keeps X-3 aligned with the current playable-baseline priority.
It freezes reusable contract truth without competing with baseline assembly or repo stabilization.

## I. Failure, Refusal, Review, and Escalation Model

The portable model reuses the following distinctions.

| Class | Meaning |
| --- | --- |
| `missing_evidence` | Required evidence object or required evidence reference is absent. |
| `invalid_evidence` | Evidence exists but fails integrity, signature, schema, canonicalization, or other validation checks. |
| `insufficient_evidence` | Evidence exists and may even be valid, but it does not cover the required scope or threshold for the task or review. |
| `review_required` | The contract says review must occur before success, promotion, or acceptance may be claimed. |
| `review_blocked` | Review cannot conclude because prerequisite evidence, reviewer authority, or gate inputs are missing. |
| `review_rejected` | Review occurred and produced a negative outcome on the subject. |
| `review_escalated` | Review cannot conclude at the current authority or evidence level and must move to a stronger posture. |
| `review_completed` | Required review execution concluded. This does not imply approval. |
| `review_approved` | Review concluded positively and satisfied the required threshold or gate condition. |
| `review_acknowledged` | Review recorded that the subject or evidence was seen, but it did not satisfy an approval gate. |
| `refused` | The system or operator refused to begin the requested action or review because prerequisite law, compatibility, policy, or authority was not satisfied. |
| `evidence_reclassification_risk` | A request or flow attempts to promote derived, shadow, or parallel evidence toward canonical or stronger authority class. This requires stronger review and must not happen silently. |

Operational consequences:

- `missing_evidence`, `invalid_evidence`, and `insufficient_evidence` are not interchangeable
- `review_acknowledged` does not satisfy `review_approved`
- `refused` is distinct from `review_rejected` because refusal can happen before review begins
- `evidence_reclassification_risk` is not a normal validation failure; it is a governance-sensitive escalation trigger

## J. Canonical Versus Derived Distinctions

Canonical evidence and review truth means:

- the portable contract itself
- evidence objects explicitly classified as canonical or otherwise designated as gate-bearing by a stronger contract
- review records or review linkages that authoritatively state requirement, state, outcome, thresholds, or readiness posture

Derived views include:

- dashboards
- markdown summaries
- UI task cards
- operator status panels
- rendered reports
- convenience inventories

Derived views may summarize, sort, or reformat canonical truth.
They may not redefine:

- evidence class
- evidence integrity or validation status
- evidence scope
- review requirement
- review state or outcome
- review thresholds
- portability limits
- promotion or reclassification status

Canonical evidence or review truth must not be overridden by convenience summaries, chat memory, or product UI.

## K. Anti-Patterns and Forbidden Shapes

The following shapes are forbidden for this series:

- treating raw logs as canonical evidence by default
- treating metrics or telemetry as sufficient review evidence by default
- treating evidence location as proof of portability
- assuming that any JSON artifact is canonical just because it is machine-readable
- promoting derived summaries or run metadata into canonical evidence without explicit follow-up review
- embedding workflow-engine, queue, scheduler, or notification semantics into the portable contract
- treating every CLI, AppShell, launcher, or setup response as the portable review contract
- collapsing refusal, rejection, blocked review, and escalation into one generic failure state
- using future AIDE runtime ambitions to justify present repo churn or broad refactors
- using this artifact to compete with canonical playable-baseline work

## L. Stability and Evolution

Stability class: `stable`.

This artifact is the canonical portable evidence and review contract until a later explicit checkpoint replaces it.

Later prompts may consume it for:

- policy and permission shape extraction
- portable refusal and escalation contract extraction
- later AIDE evidence packaging or interface mapping work
- later extraction review of which live Dominium evidence and review surfaces can be wrapped versus retained

The following changes require an explicit follow-up artifact rather than silent drift:

- redefining evidence class semantics
- redefining review outcome or escalation semantics
- collapsing canonical and derived evidence classes
- promoting repo-local workflow details into the portable contract
- treating product telemetry or logs as canonical evidence by default
- broadening this contract into runtime, queue, daemon, or scheduler law

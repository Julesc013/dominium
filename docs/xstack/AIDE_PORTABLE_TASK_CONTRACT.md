Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: X-3, AIDE extraction review
Replacement Target: later explicit portable-contract checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/agents/XSTACK_TASK_CATALOG.md`

# AIDE Portable Task Contract

## A. Purpose and Scope

This artifact freezes the canonical portable task-unit contract that later XStack/AIDE prompts may reuse.

It exists because:

- `X-0` froze what XStack means now
- `X-1` classified which live surfaces are portable core, ops, runtime, Dominium-retained, legacy, or mixed
- later extraction work still needs a smaller and stricter contract for the task unit itself

This artifact solves a specific narrowing problem:

- the live repo has task families, runners, wrappers, commands, validation suites, session flows, and product shells
- later AIDE work needs the portable minimum that those surfaces imply
- that portable minimum must be frozen without smuggling in runtime, scheduler, daemon, or product-shell semantics

This artifact governs:

- what a portable task means in the live XStack/AIDE sense
- which contract fields every portable task must expose
- which boundaries must remain explicit
- which parts are portable now versus Dominium-retained now versus deferred until after the playable baseline exists
- which later prompts may treat this as their fact base

This artifact is downstream of `X-0` and `X-1`.
It does not reopen scope or inventory classification.
It narrows those earlier artifacts into the portable task-unit truth only.

This artifact must preserve current repo reality:

- admissible `Zeta` doctrine and gating work is complete
- the immediate product priority remains the canonical repo-local playable baseline and repo stabilization
- XStack/AIDE work must support clarification, modularization, and contract extraction without competing with the baseline path

This artifact is a contract freeze.
It does not implement a runtime, worker pool, daemon, adapter system, compiler, or broader AIDE platform.

## B. Current-State Definition of a Portable Task

Current definition:

A portable task is a canonical declarative contract for one bounded unit of governed work that specifies stable identity, task kind, intent, authoritative inputs, required and optional inputs, expected outputs, evidence obligations, review and permission hooks, refusal and failure classes, and repeatability limits without embedding scheduler, worker, session-runtime, or product-shell control semantics.

The portable task-unit shape is:

- a contract for what the work is
- a contract for what must already be true
- a contract for what outputs and evidence obligations apply
- a contract for what success, refusal, blockage, failure, or escalation mean

The portable task-unit shape is not:

- a daemon job model
- a worker or shard assignment
- a queue record
- a product command line
- an AppShell command descriptor
- a session lifecycle definition
- a gate profile runner

Dominium-specific task execution context remains separate.
Live repo evidence shows that execution context often includes:

- repo-root resolution
- workspace identifiers
- profile selection such as `FAST`, `STRICT`, or `FULL`
- cache, shard, and output-directory control
- session create, boot, stage, and control flows
- AppShell, launcher, setup, release, and loopback authority wiring

Those are real in the repo, but they belong to execution surfaces rather than the portable task contract itself.

Product-shell commands are also distinct from portable task contracts.
For example, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, and `appshell/commands/command_engine.py` are real command surfaces, but they package product and operator behavior around deeper contracts.
They may trigger or expose tasks; they do not define the portable task truth.

Out-of-scope orchestration and runtime concerns for this prompt include:

- scheduling
- worker selection
- daemon lifetime
- queueing
- grouping and sharding
- cache behavior
- session runtime placement
- adapter transport and remote execution

## C. Portable Task Contract Fields

Every portable task contract must specify the following fields.

| Field | Requirement | Meaning |
| --- | --- | --- |
| `task_id` | required | Stable canonical task identifier. It must survive wrapper, UI, or command renaming. |
| `task_kind` | required | Stable task family or category. This is the portable classification of the work, not a CLI verb or script filename. |
| `purpose` | required | One clear statement of intent and scoped outcome. |
| `authoritative_inputs` | required | Canonical doctrine, schemas, registries, or repo roots that govern lawful execution. This preserves authority order rather than letting the runner infer canon by convenience. |
| `required_inputs` | required | Inputs that must be present or resolved for the task to be valid and runnable. |
| `optional_inputs` | conditional | Inputs that may refine or narrow execution without changing the task identity. |
| `expected_outputs` | required | Declared outputs or result objects the task may lawfully emit. Each output must declare whether it is canonical, derived view, run metadata, or local integration-only evidence. |
| `preconditions` | required | Conditions that must hold before work may begin. Preconditions are distinct from runtime errors. |
| `postconditions` | required | Conditions that must hold for the task to count as successfully completed. |
| `evidence_obligations` | required | Evidence that must already exist before execution and evidence that must be emitted if the task is attempted, completed, refused, or partially completed. |
| `review_hooks` | required | Required review checkpoints, protected-area triggers, ownership-sensitive roots, or human approvals. |
| `permission_policy_hooks` | required | Policy, gate, or permission surfaces that may authorize, narrow, or refuse the task. |
| `refusal_states` | required | Enumerated lawful refusal classes that prevent attempted execution. |
| `failure_states` | required | Enumerated failure classes that can arise after execution starts or after outputs are evaluated. |
| `escalation_hooks` | required | Conditions that convert the task into review-required or escalation-required posture. |
| `determinism_expectations` | required | Repeatability, ordering, hashing, or result-stability expectations when applicable. If determinism is not required, that must be explicit. |
| `idempotence_notes` | conditional | Whether repeated execution is safe and what state or evidence changes remain acceptable. |
| `retry_notes` | conditional | What may be retried, what must be recomputed, and what must not be silently repeated. |
| `portability_limits` | required | Current repo-specific assumptions, retained bindings, or coupling that bound portability. |
| `compatibility_notes` | required | Version, stability, refusal-on-unknown, and compatibility expectations for the contract itself. |
| `stability` | required | Current contract stability class and the threshold for changing the shape later. |

Operational rule:

- these fields freeze portable task truth
- execution-only fields such as `repo_root`, `workspace_id`, `gate_command`, `plan_profile`, `cache_enabled`, `shards`, `shard_index`, and `output_dir` remain runtime or orchestration concerns

## D. Required Boundary Distinctions

The following distinctions are mandatory and may not be flattened.

### Task Definition vs Task Execution

- task definition describes the governed unit of work
- task execution describes where, when, and how that work is run
- runner context, cache state, shard allocation, workspace allocation, and output routing belong to execution

### Task Contract vs Scheduler or Runtime

- the portable task contract does not define daemons, workers, queue semantics, grouping, or scheduling policy
- scheduler and runtime surfaces may consume the contract later, but they may not redefine it

### Task Contract vs Product Command Surface

- product commands, AppShell commands, launcher commands, and setup commands are integration surfaces
- they may expose or orchestrate tasks, but they are not the canonical portable task contract

### Evidence Required vs Evidence Produced

- evidence required is the proof, approval, registry state, or doctrine packet needed before execution is lawful
- evidence produced is the output, log, report, refusal payload, or audit artifact emitted by attempting or finishing the task
- produced evidence may document the task outcome, but it does not redefine the contract

### Refusal vs Failure vs Escalation

- refusal means the task is valid enough to classify, but execution must not begin
- failure means execution began or completion was evaluated and the task did not satisfy postconditions
- escalation means additional human review, ownership review, or checkpoint review is required before claiming success or proceeding further

## E. Repo-Grounded Rationale

This contract freeze is based on live repo evidence rather than aspiration.

- `docs/agents/XSTACK_TASK_CATALOG.md` defines an XStack task as a stable, authority-aware task surface with bounded authoritative inputs, allowed output classes, default posture, review expectations, and later safety expectations. That directly supports `task_kind`, `authoritative_inputs`, `expected_outputs`, `review_hooks`, and `permission_policy_hooks`.
- `tools/xstack/core/runners_base.py` proves that live task-like units already expose stable identity, deterministic input hashing, declared produced artifacts, normalized results, and explicit failure-class reporting. That supports `task_id`, `expected_outputs`, `determinism_expectations`, and `failure_states`.
- `tools/xstack/extensions/example_x/extension.py` shows that extension-style runner registration already expects a stable runner id, artifact contract, version hash, and bounded scope subtrees. That supports freezing identity, expected outputs, compatibility notes, and portability limits without claiming a full extension platform.
- `tools/xstack/core/artifact_contract.py` classifies outputs into `CANONICAL`, `DERIVED_VIEW`, `RUN_META`, and `UNKNOWN`. That is the repo-grounded reason the portable contract must distinguish output classes instead of flattening all artifacts into one category.
- `tools/xstack/sessionx/pipeline_contract.py` uses explicit refusal payloads with reason codes, remediation hints, relevant ids, and path markers when preconditions or contract rows are invalid. That is the repo-grounded reason to freeze refusal as a first-class contract outcome distinct from generic failure.
- `tools/xstack/controlx/types.py` defines execution context fields such as `profile`, `cache_enabled`, `shards`, `shard_index`, and `output_dir`. Those are real and important, but they are execution-shape details, so they stay outside the portable task contract.
- `validation/validation_engine.py` maps live and legacy validation surfaces, replacement targets, evidence outputs, and status classes. That is the repo-grounded reason to require evidence obligations, compatibility notes, and review-aware failure reporting.
- `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, and `appshell/commands/command_engine.py` prove that the repo already has large command surfaces whose job is product integration and operator control. That is why the portable task contract must remain separate from product commands and shell wiring.

The portable minimum is therefore justified by implementation patterns already present in Dominium, while runtime placement and product shells remain intentionally excluded.

## F. What Is Portable Now vs Not Portable Now

### Portable Now

The following task-shape elements can be frozen as portable now:

- stable task identity and task kind
- bounded purpose and intent
- authoritative inputs and required or optional inputs
- expected outputs with explicit output-class markers
- preconditions and postconditions
- evidence obligations
- review hooks and permission or policy hooks
- refusal, blocked, failed, partial, and escalation outcome classes
- determinism expectations
- idempotence and retry notes where applicable
- portability limits
- compatibility and stability markers
- canonical-versus-derived markers for task truth and outputs

### Dominium-Retained Now

The following remain Dominium-retained and must not be frozen as portable task truth now:

- concrete `FAST`, `STRICT`, and `FULL` runner semantics
- `ControlX` orchestration flow and `RunContext` execution fields
- `SessionSpec` creation, boot, stage, SRZ, runtime, and session-control machinery
- pack, bundle, registry compile, and local universe materialization details
- AppShell, launcher, setup, and loopback authority command surfaces
- cache layout, workspace routing, shard assignment, and output-directory policy
- repo-local CI wiring, gate bridges, and product-shell refusal-to-exit behavior

### Deferred Until After the Playable Baseline

The following are plausible later AIDE topics but remain deferred now:

- scheduler and worker contracts
- daemon or service lifetime model
- portable adapter transport and remote execution surfaces
- cross-repo task registry publication
- task graph composition, bakeoff, or compiler layers
- portable queue and concurrency semantics
- portable runtime policy engines beyond the task-level permission and refusal hooks frozen here

## G. Failure, Refusal, and Escalation Model

The portable task contract must preserve the following outcome classes.

| Class | Meaning | Required Handling |
| --- | --- | --- |
| `invalid_task` | The contract itself is malformed, missing required fields, or internally contradictory. | Refuse interpretation and do not treat it as executable work. |
| `refused_task` | The task is classifiable, but policy, authority, permission, or refusal law says execution must not begin. | Emit refusal evidence with reason code and remediation where available. |
| `blocked_task` | The task is valid in shape, but required inputs, required evidence, required review, or prerequisite state are missing. | Preserve task identity and report missing dependencies without flattening into failure. |
| `failed_task` | Execution began or outputs were evaluated, and required postconditions were not met. | Emit failure evidence and do not claim completion. |
| `partially_completed_task` | Some work or evidence was produced, but not all required outputs or postconditions were satisfied. | Report partial completion explicitly and preserve outstanding obligations. |
| `review_or_escalation_required` | Human review, ownership review, checkpoint review, or protected-area escalation is required before proceeding or claiming success. | Halt autonomous completion claims until the required review is satisfied. |

Portable outcome rule:

- refusal is not failure
- blockage is not refusal
- partial completion is not success
- escalation is a review state, not a hidden subtype of failure

## H. Canonical vs Derived Distinctions

Canonical task truth means:

- the portable task contract itself
- the field definitions frozen in this artifact
- later machine-readable mirrors that faithfully project this canonical shape without adding competing semantics

Derived task views include:

- UI task cards
- queue entries
- shell help text
- prompt summaries
- run logs
- dashboards
- progress views
- audit summaries

Derived views may:

- summarize
- render
- sort
- filter
- attach run metadata

Derived views may not:

- redefine task identity
- redefine required fields
- erase refusal, review, or evidence obligations
- promote local shell flags into canonical task meaning
- promote emitted evidence into authority over the contract

## I. Anti-Patterns and Forbidden Shapes

The following shapes are forbidden for this series:

- embedding scheduler, daemon, worker, queue, or shard semantics into the portable task contract
- treating every CLI command or AppShell command as a portable task contract
- treating path location under `tools/xstack/` as proof of portability
- promoting wrappers, bridges, or stubs into portable core without evidence
- omitting refusal, review, permission, or evidence boundaries because a runner currently hardcodes them
- using future AIDE runtime ambitions to justify present contract expansion
- using this artifact to justify broad repo renaming, platformization, or product-shell refactors
- competing with playable-baseline assembly by extracting runtime-critical Dominium surfaces too early

## J. Stability and Evolution

Stability class: `stable`.

This artifact enables later prompts that need the portable task-unit truth, especially:

- evidence and review contract extraction
- permission and refusal contract mapping
- execution-surface mapping that consumes task truth without redefining it
- later extraction review over which live XStack surfaces can lawfully implement or expose the frozen task contract

This artifact must not change silently.
Any later prompt that changes:

- the definition of a portable task
- the required field set
- the refusal or escalation classes
- the portable-now versus Dominium-retained boundary
- the canonical-versus-derived distinction

must create an explicit follow-up checkpoint or replacement artifact rather than drifting this contract by convenience.

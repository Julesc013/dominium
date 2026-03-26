Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored prompt execution inventory after fresh repository mapping

# Final Prompt Inventory

## Current Boundary

This is the canonical prompt catalog for all post-XI series work.
It is planning only and must be reconciled against a fresh repository snapshot before any post-snapshot prompt executes.

## Safest Execution Doctrine

1. architecture docs and schemas first.
2. registries and validators second.
3. runtime implementation third.
4. live operations only after runtime foundations frozen.
5. packaging and publication only after convergence gates pass.
6. any AI execution is advisory and XStack-gated.

The matching execution doctrine is also anchored in `docs/blueprint/SERIES_EXECUTION_STRATEGY.md`.

## Global Stop Conditions

- `global.architecture_graph_changed`: If the architecture graph changes unexpectedly, stop. Escalation: Regenerate the snapshot mapping, reconcile drift, and require manual review.
- `global.semantic_contract_bump`: If a semantic contract bump is required, stop and escalate. Escalation: Route through contract review, migration or refusal planning, and CompatX review.
- `global.conflicting_live_subsystem`: If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile. Escalation: Apply keep/merge/replace/quarantine rules before implementation continues.
- `global.baseline_drift`: If deterministic baselines drift, stop. Escalation: Re-run OMEGA verification, identify the drift source, and do not continue live-runtime work.
- `global.runtime_boundaries_unclear`: If runtime or module boundaries are unclear, stop before PHI-series implementation. Escalation: Convert the uncertainty into architecture review and snapshot remapping.
- `global.unstated_zeta_foundation`: If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning. Escalation: Split the missing foundation into an earlier prompt and rerun dependency planning.

## Inventory Summary

| Series | Count |
| --- | --- |
| Σ | 7 |
| Φ | 15 |
| Υ | 13 |
| Ζ | 75 |

## Σ-Series - Human / Agent Interface & Governance

### `Σ-0` `AGENT-GOVERNANCE-0`

- Purpose: Freeze the human and agent governance contract, authority boundaries, and review doctrine.
- Inputs: AGENTS.md, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, docs/canon/constitution_v1.md, tools/xstack
- Outputs: design package for agent-governance-0, execution notes, governance or catalog artifact update, validation report
- Prerequisites: OMEGA-FREEZE, XI-8
- Dependent Prompts: Σ-1, Σ-2, Σ-5, Υ-12
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `low`
- Execution Class: `docs_only`
- Gate Profile Required: `FAST`
- Gates Required After Execution: RepoX FAST, AuditX FAST, TestX impacted subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Σ-1` `AGENT-MIRRORS-0`

- Purpose: Define mirrored human and agent surfaces so every governed action has an inspectable counterpart.
- Inputs: AGENTS.md, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, docs/canon/constitution_v1.md, tools/xstack
- Outputs: design package for agent-mirrors-0, execution notes, governance or catalog artifact update, validation report
- Prerequisites: Σ-0
- Dependent Prompts: Σ-2, Ζ-24, Ζ-31, Ζ-35
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `low`
- Execution Class: `docs_only`
- Gate Profile Required: `FAST`
- Gates Required After Execution: RepoX FAST, AuditX FAST, TestX impacted subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Σ-2` `NATURAL-LANGUAGE-TASK-BRIDGE-0`

- Purpose: Bind natural-language intent to deterministic task classes, validation levels, and refusals.
- Inputs: AGENTS.md, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, docs/canon/constitution_v1.md, tools/xstack
- Outputs: design package for natural-language-task-bridge-0, execution notes, governance or catalog artifact update, validation report
- Prerequisites: Σ-0, Σ-1
- Dependent Prompts: Σ-3, Σ-5, Ζ-4, Ζ-14
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Σ-3` `XSTACK-TASK-CATALOG-0`

- Purpose: Publish the canonical XStack task catalog that future humans and agents must target.
- Inputs: AGENTS.md, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, docs/canon/constitution_v1.md, tools/xstack
- Outputs: design package for xstack-task-catalog-0, execution notes, governance or catalog artifact update, validation report
- Prerequisites: Σ-2
- Dependent Prompts: Σ-4, Σ-6, Υ-4, Υ-12, Ζ-15, Ζ-27
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Σ-4` `MCP-INTERFACE-0`

- Purpose: Define the governed MCP interface surface for prompt execution, inspection, and refusal handling.
- Inputs: AGENTS.md, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, docs/canon/constitution_v1.md, tools/xstack
- Outputs: design package for mcp-interface-0, execution notes, governance or catalog artifact update, validation report
- Prerequisites: Σ-3
- Dependent Prompts: Σ-5, Σ-6
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Σ-5` `AGENT-SAFETY-POLICY-0`

- Purpose: Lock safety policy, manual review gates, and escalation rules for future automation.
- Inputs: AGENTS.md, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, docs/canon/constitution_v1.md, tools/xstack
- Outputs: design package for agent-safety-policy-0, execution notes, governance or catalog artifact update, validation report
- Prerequisites: Σ-0, Σ-2, Σ-4
- Dependent Prompts: Σ-6, Φ-14, Υ-10, Ζ-6, Ζ-10, Ζ-12, Ζ-16, Ζ-17, Ζ-18, Ζ-19, Ζ-20, Ζ-21, Ζ-22, Ζ-23, Ζ-32, Ζ-44, Ζ-50, Ζ-65
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Σ-6` `AGENT-PERFORMANCE-0`

- Purpose: Measure and tune governed agent throughput only after the live repository snapshot is mapped to real workflows.
- Inputs: AGENTS.md, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, docs/canon/constitution_v1.md, snapshot-mapping rows for the target prompt, tools/xstack
- Outputs: design package for agent-performance-0, execution notes, governance or catalog artifact update, validation report
- Prerequisites: Σ-3, Σ-4, Σ-5, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

## Φ-Series - Runtime Componentization & Service Kernel

### `Φ-0` `RUNTIME-KERNEL-MODEL-0`

- Purpose: Define the deterministic runtime kernel doctrine, service boundaries, and lawful state movement.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/
- Outputs: design package for runtime-kernel-model-0, execution notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: OMEGA-FREEZE, XI-8
- Dependent Prompts: Φ-1, Φ-4
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `docs_only`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-1` `COMPONENT-MODEL-0`

- Purpose: Define the component contract, ownership boundaries, and lifecycle vocabulary for runtime services.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/
- Outputs: design package for component-model-0, execution notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-0
- Dependent Prompts: Φ-2, Φ-3, Φ-4, Φ-6, Φ-7, Φ-9, Φ-10, Φ-11
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `docs_only`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-2` `MODULE-LOADER-0`

- Purpose: Insert a governed, capability-negotiated module loader into the live runtime after snapshot mapping.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for module-loader-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-1, SNAPSHOT-MAP
- Dependent Prompts: Φ-3, Φ-10, Ζ-2, Ζ-20, Ζ-44, Ζ-49, Ζ-52
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-3` `RUNTIME-SERVICES-0`

- Purpose: Separate runtime services from the kernel without violating process-only mutation.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for runtime-services-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-1, Φ-2, SNAPSHOT-MAP
- Dependent Prompts: Φ-5, Φ-6, Φ-10, Ζ-1, Ζ-3, Ζ-24, Ζ-25, Ζ-42, Ζ-61
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-4` `STATE-EXTERNALIZATION-0`

- Purpose: Define export/import, ownership, and replay-safe state movement before live cutovers.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/
- Outputs: design package for state-externalization-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-0, Φ-1
- Dependent Prompts: Φ-5, Φ-11, Φ-12, Φ-13, Ζ-5, Ζ-7
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-5` `LIFECYCLE-MANAGER-0`

- Purpose: Implement governed startup, shutdown, handoff, and rollback choreography for runtime services.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for lifecycle-manager-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-3, Φ-4, SNAPSHOT-MAP
- Dependent Prompts: Φ-8, Φ-12, Φ-13, Ζ-0, Ζ-1, Ζ-2, Ζ-3, Ζ-4, Ζ-7, Ζ-11, Ζ-48
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-6` `FRAMEGRAPH-0`

- Purpose: Introduce a framegraph-style render plan layer that separates render intent from backend execution.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for framegraph-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-1, Φ-3, SNAPSHOT-MAP
- Dependent Prompts: Φ-7, Φ-8, Φ-9, Ζ-0, Ζ-33, Ζ-34, Ζ-37
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-7` `RENDER-DEVICE-0`

- Purpose: Define the render device abstraction required for backend swap, validation renderers, and mirrored execution.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for render-device-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-1, Φ-6, SNAPSHOT-MAP
- Dependent Prompts: Φ-8, Ζ-0, Ζ-33, Ζ-34, Ζ-38, Ζ-40, Ζ-41, Ζ-42
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-8` `HOTSWAP-BOUNDARIES-0`

- Purpose: Freeze lawful replacement boundaries, state handoff points, and rollback obligations for hot-replaceable services.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for hotswap-boundaries-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-5, Φ-6, Φ-7, SNAPSHOT-MAP
- Dependent Prompts: Ζ-0, Ζ-2, Ζ-3, Ζ-4, Ζ-37
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-9` `ASSET-PIPELINE-0`

- Purpose: Build the governed asset and shader pipeline that live mount, streaming, and validation features depend on.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for asset-pipeline-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-1, Φ-6, SNAPSHOT-MAP
- Dependent Prompts: Ζ-34, Ζ-40, Ζ-41, Ζ-48
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-10` `SANDBOXING-0`

- Purpose: Add governed sandboxing and isolation boundaries for untrusted runtime extensions and mods.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for sandboxing-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-1, Φ-2, Φ-3, SNAPSHOT-MAP
- Dependent Prompts: Ζ-20, Ζ-45
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-11` `MULTI-VERSION-COEXISTENCE-0`

- Purpose: Define how multiple runtime, protocol, and module versions coexist during controlled migration windows.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/
- Outputs: design package for multi-version-coexistence-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-1, Φ-4
- Dependent Prompts: Φ-14, Ζ-2, Ζ-6, Ζ-44, Ζ-47, Ζ-49, Ζ-52, Ζ-56
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-12` `EVENT-LOG-0`

- Purpose: Create the deterministic event-log substrate required for replay, cutover, and distributed execution.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for event-log-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-4, Φ-5, SNAPSHOT-MAP
- Dependent Prompts: Φ-13, Φ-14, Ζ-29, Ζ-30, Ζ-57, Ζ-60
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-13` `SNAPSHOT-SERVICE-0`

- Purpose: Create the snapshot service and handoff format required for save migration, rollback, and distributed recovery.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for snapshot-service-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Φ-4, Φ-5, Φ-12, SNAPSHOT-MAP
- Dependent Prompts: Φ-14, Ζ-5, Ζ-7, Ζ-9, Ζ-29, Ζ-39, Ζ-57, Ζ-59, Ζ-60
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Φ-14` `DISTRIBUTED-AUTHORITY-0`

- Purpose: Define the lawful distributed authority model, handoff semantics, and proof obligations.
- Inputs: client/, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, engine/, server/, snapshot-mapping rows for the target prompt
- Outputs: design package for distributed-authority-0, rollback notes, runtime boundary artifact or componentization change, validation report
- Prerequisites: Σ-5, Φ-11, Φ-12, Φ-13, SNAPSHOT-MAP
- Dependent Prompts: Ζ-57, Ζ-58, Ζ-63, Ζ-73
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `schema_registry`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

## Υ-Series - Build, Release, Distribution, Control Plane

### `Υ-0` `BUILD-GRAPH-LOCK-0`

- Purpose: Lock the live build graph after snapshot mapping so future tooling runs against a stable substrate.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt, tools/xstack/
- Outputs: control-plane or release artifact update, design package for build-graph-lock-0, rollback notes, validation report
- Prerequisites: OMEGA-FREEZE, SNAPSHOT-MAP, XI-8
- Dependent Prompts: Υ-1, Υ-4, Υ-5, Ζ-28
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-1` `PRESET-CONSOLIDATION-0`

- Purpose: Consolidate presets and toolchains against the actual live repository layout.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt, tools/xstack/
- Outputs: control-plane or release artifact update, design package for preset-consolidation-0, rollback notes, validation report
- Prerequisites: Υ-0, SNAPSHOT-MAP
- Dependent Prompts: Υ-5
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `refactor`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-2` `VERSIONING-POLICY-0`

- Purpose: Freeze versioning, migration, and compatibility discipline for the post-XI control plane.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, tools/xstack/
- Outputs: control-plane or release artifact update, design package for versioning-policy-0, execution notes, validation report
- Prerequisites: OMEGA-FREEZE, XI-8
- Dependent Prompts: Υ-3, Υ-8, Υ-11, Υ-12
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `docs_only`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-3` `RELEASE-INDEX-POLICY-1`

- Purpose: Refine release index policy, publication semantics, and rollback lineage before pipeline work.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, tools/xstack/
- Outputs: control-plane or release artifact update, design package for release-index-policy-1, execution notes, validation report
- Prerequisites: Υ-2
- Dependent Prompts: Υ-6, Υ-7, Υ-8
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `docs_only`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-4` `MANUAL-AUTOMATION-PARITY-0`

- Purpose: Map manual operator workflows to automation steps so every automated release action has a human mirror.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt, tools/xstack/
- Outputs: control-plane or release artifact update, design package for manual-automation-parity-0, rollback notes, validation report
- Prerequisites: Σ-3, Υ-0, SNAPSHOT-MAP
- Dependent Prompts: Υ-6
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-5` `BUILD-REPRO-MATRIX-0`

- Purpose: Establish the reproducibility matrix for supported toolchains, profiles, and artifact classes.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt, tools/xstack/
- Outputs: control-plane or release artifact update, design package for build-repro-matrix-0, rollback notes, validation report
- Prerequisites: Υ-0, Υ-1, SNAPSHOT-MAP
- Dependent Prompts: Υ-6, Ζ-34
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-6` `RELEASE-PIPELINE-0`

- Purpose: Build the deterministic release pipeline once the live toolchain graph and parity map are known.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt, tools/xstack/
- Outputs: control-plane or release artifact update, design package for release-pipeline-0, rollback notes, validation report
- Prerequisites: Υ-3, Υ-4, Υ-5, SNAPSHOT-MAP
- Dependent Prompts: Υ-7, Υ-10
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-7` `ARCHIVE-MIRROR-0`

- Purpose: Build the governed archive mirror workflow and offline bundle publication path.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt, tools/xstack/
- Outputs: control-plane or release artifact update, design package for archive-mirror-0, rollback notes, validation report
- Prerequisites: Υ-3, Υ-6, SNAPSHOT-MAP
- Dependent Prompts: Υ-10
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `implementation`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-8` `PUBLICATION-MODELS-0`

- Purpose: Define publication models, promotion paths, and compatibility classes for release distribution.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, tools/xstack/
- Outputs: control-plane or release artifact update, design package for publication-models-0, execution notes, validation report
- Prerequisites: Υ-2, Υ-3
- Dependent Prompts: Υ-9, Υ-10
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `medium`
- Execution Class: `docs_only`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-9` `LICENSE-CAPABILITY-0`

- Purpose: Define how license, entitlement, and capability policy constrain distribution and operator workflows.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, tools/xstack/
- Outputs: control-plane or release artifact update, design package for license-capability-0, execution notes, validation report
- Prerequisites: Υ-8
- Dependent Prompts: Ζ-18, Ζ-20, Ζ-22, Ζ-45, Ζ-51
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-10` `RELEASE-OPS-0`

- Purpose: Create the governed release-operations controller and operator workflow surface.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt, tools/xstack/
- Outputs: control-plane or release artifact update, design package for release-ops-0, rollback notes, validation report
- Prerequisites: Σ-5, Υ-6, Υ-7, Υ-8, Υ-11, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: Ζ-10, Ζ-15, Ζ-16, Ζ-18, Ζ-23, Ζ-24, Ζ-27, Ζ-32, Ζ-42, Ζ-44, Ζ-50, Ζ-53, Ζ-54, Ζ-74
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-11` `DISASTER-DOWNGRADE-POLICY-0`

- Purpose: Lock downgrade, yank, and degraded-survival policy before live cutovers or automated rollback.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, tools/xstack/
- Outputs: control-plane or release artifact update, design package for disaster-downgrade-policy-0, rollback notes, validation report
- Prerequisites: Υ-2, Υ-12, OMEGA-FREEZE
- Dependent Prompts: Υ-10, Ζ-5, Ζ-10, Ζ-12, Ζ-43, Ζ-46, Ζ-62, Ζ-69, Ζ-70, Ζ-71, Ζ-74
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Υ-12` `OPERATOR-TRANSACTION-LOG-0`

- Purpose: Define the operator transaction log and explainable action ledger for cutovers, rollback, and rehearsal.
- Inputs: data/audit/build_graph.json, data/blueprint/series_execution_strategy.json, dist/, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, tools/xstack/
- Outputs: control-plane or release artifact update, design package for operator-transaction-log-0, rollback notes, validation report
- Prerequisites: Σ-0, Σ-3, Υ-2
- Dependent Prompts: Υ-10, Υ-11, Ζ-0, Ζ-1, Ζ-2, Ζ-3, Ζ-4, Ζ-5, Ζ-9, Ζ-10, Ζ-11, Ζ-13, Ζ-14, Ζ-16, Ζ-28, Ζ-30, Ζ-46, Ζ-56, Ζ-57, Ζ-74
- Snapshot Requirement: `pre_snapshot_safe`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

## Ζ-Series - Live Runtime Operations & Extreme Replaceability

### `Ζ-0` `HOTSWAP-RENDERERS-0`

- Purpose: Make renderers hot-swappable only after render boundaries, lifecycle control, and transaction logging are frozen.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for hotswap-renderers-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-5, Φ-6, Φ-7, Φ-8, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: Ζ-33, Ζ-37, Ζ-38, Ζ-40
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-1` `SERVICE-RESTARTS-0`

- Purpose: Enable governed service restarts with rollback and replay-safe recovery.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for service-restarts-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-3, Φ-5, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: Ζ-21
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-2` `PARTIAL-MODULE-RELOAD-0`

- Purpose: Support partial module reload only within frozen ABI, lifecycle, and rollback boundaries.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for partial-module-reload-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-2, Φ-5, Φ-8, Φ-11, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-3` `BACKEND-SWAP-AUDIO-INPUT-STORAGE-NET-0`

- Purpose: Allow backend swap for non-render services only after service boundaries and transaction logging are governed.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for backend-swap-audio-input-storage-net-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-3, Φ-5, Φ-8, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-4` `LIVE-UI-SHELL-REPLACEMENT-0`

- Purpose: Allow shell replacement without bypassing authority, law, or rollback discipline.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-ui-shell-replacement-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-2, Φ-5, Φ-8, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-5` `LIVE-SAVE-MIGRATION-0`

- Purpose: Perform live save migration with snapshot safety, rollback, and baseline verification discipline.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-save-migration-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-4, Φ-13, Υ-11, Υ-12, OMEGA-FREEZE, SNAPSHOT-MAP
- Dependent Prompts: Ζ-6, Ζ-8
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-6` `LIVE-STATE-SCHEMA-EVOLUTION-0`

- Purpose: Evolve runtime state schemas live only after save migration, coexistence, and manual review gates are satisfied.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-state-schema-evolution-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Φ-11, Ζ-5, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-7` `NONBLOCKING-SAVES-0`

- Purpose: Enable non-blocking save capture using lifecycle control and snapshot service boundaries.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for nonblocking-saves-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-4, Φ-5, Φ-13, SNAPSHOT-MAP
- Dependent Prompts: Ζ-8, Ζ-9
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-8` `PARTIAL-WORLD-RESTORE-0`

- Purpose: Restore selected world slices without violating snapshot isolation or replay equivalence.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for partial-world-restore-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-5, Ζ-7, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-9` `FORKABLE-SAVES-AND-BRANCHABLE-UNIVERSES-0`

- Purpose: Allow governed save forks and branchable universe lines without breaking provenance.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for forkable-saves-and-branchable-universes-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-13, Υ-12, Ζ-7, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-10` `CANARY-RELEASES-0`

- Purpose: Run canary releases with explicit exposure policy, rollback receipts, and operator signoff.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for canary-releases-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-10, Υ-11, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: Ζ-11, Ζ-13, Ζ-55
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-11` `INCREMENTAL-CUTOVERS-0`

- Purpose: Perform cutovers incrementally with explainable checkpoints and reversible steps.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for incremental-cutovers-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-5, Υ-12, Ζ-10, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-12` `SAFE-MODE-DEGRADED-BOOT-0`

- Purpose: Operationalize safe-mode degraded boot as a governed release and recovery path.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for safe-mode-degraded-boot-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-11, OMEGA-FREEZE, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `operations`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-13` `OPERATOR-REVERSIBLE-RELEASES-0`

- Purpose: Require every operator-driven release to carry a governed reversal path before promotion.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for operator-reversible-releases-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-12, Ζ-10, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-14` `EXPLAINABLE-UPGRADE-PLANS-0`

- Purpose: Emit explainable upgrade plans instead of imperative black-box rollout scripts.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for explainable-upgrade-plans-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-2, Υ-12, SNAPSHOT-MAP
- Dependent Prompts: Ζ-15, Ζ-26
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-15` `DETERMINISTIC-OPERATOR-PLAYBOOKS-0`

- Purpose: Build deterministic operator playbooks that map directly onto XStack validations and rollback hooks.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for deterministic-operator-playbooks-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-3, Υ-10, Ζ-14, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-16` `LIVE-TRUST-ROOT-ROTATION-0`

- Purpose: Rotate trust roots live without creating unverifiable upgrade windows.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-trust-root-rotation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-10, Υ-12, OMEGA-FREEZE, SNAPSHOT-MAP
- Dependent Prompts: Ζ-17
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-17` `LIVE-REVOCATION-PROPAGATION-0`

- Purpose: Propagate trust and capability revocations live with deterministic client and operator responses.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-revocation-propagation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Ζ-16, SNAPSHOT-MAP
- Dependent Prompts: Ζ-19
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-18` `RUNTIME-SIGNATURE-POLICY-0`

- Purpose: Enforce runtime signature policy for replaceable services, live content, and release operations.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for runtime-signature-policy-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-9, Υ-10, SNAPSHOT-MAP
- Dependent Prompts: Ζ-19, Ζ-21, Ζ-22, Ζ-51
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-19` `LIVE-PRIVILEGE-ESCALATION-REVOCATION-0`

- Purpose: Control live privilege escalation and revocation without bypassing law-gated authority.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-privilege-escalation-revocation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Ζ-17, Ζ-18, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-20` `UNTRUSTED-MOD-ISOLATION-0`

- Purpose: Isolate untrusted mods behind sandbox, signature, and capability policy boundaries.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for untrusted-mod-isolation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Φ-2, Φ-10, Υ-9, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-21` `ATTESTED-SERVICE-REPLACEMENT-0`

- Purpose: Require attested service replacement so cutovers can be proven, reviewed, and rolled back.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for attested-service-replacement-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Ζ-1, Ζ-18, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-22` `SEALED-EXECUTION-PROFILES-0`

- Purpose: Create sealed execution profiles that constrain live operations to reviewed and signed capability sets.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for sealed-execution-profiles-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-9, Ζ-18, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-23` `TWO-PERSON-APPROVAL-WORKFLOWS-0`

- Purpose: Require dual approval for the highest-risk live operations and trust changes.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for two-person-approval-workflows-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-10, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `schema_registry`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-24` `LIVE-TOPOLOGY-VISUALIZATION-0`

- Purpose: Visualize the live service and dependency topology for operators and reviewers.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-topology-visualization-0, execution notes, operations playbook or cutover artifact, validation report
- Prerequisites: Σ-1, Φ-3, Υ-10, SNAPSHOT-MAP
- Dependent Prompts: Ζ-25, Ζ-26, Ζ-31, Ζ-58
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-25` `SERVICE-DEPENDENCY-GRAPH-INSPECTION-0`

- Purpose: Inspect service dependency graphs live so cutovers and failures remain explainable.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for service-dependency-graph-inspection-0, execution notes, operations playbook or cutover artifact, validation report
- Prerequisites: Φ-3, Ζ-24, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-26` `CUTOVER-PLAN-VISUALIZATION-0`

- Purpose: Visualize cutover plans and rollback branches before operator approval.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for cutover-plan-visualization-0, execution notes, operations playbook or cutover artifact, validation report
- Prerequisites: Ζ-14, Ζ-24, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-27` `CONTINUOUS-INVARIANT-MONITOR-0`

- Purpose: Continuously watch the non-negotiable invariants that live operations must never violate.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for continuous-invariant-monitor-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-3, Υ-10, OMEGA-FREEZE, SNAPSHOT-MAP
- Dependent Prompts: Ζ-28, Ζ-29, Ζ-31, Ζ-32, Ζ-57
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-28` `RUNTIME-DRIFT-DETECTION-0`

- Purpose: Detect runtime drift against the frozen architecture and baseline expectations.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for runtime-drift-detection-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-0, Υ-12, Ζ-27, SNAPSHOT-MAP
- Dependent Prompts: Ζ-32
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-29` `PROOF-ANCHOR-HEALTH-MONITOR-0`

- Purpose: Monitor proof-anchor health and cutover viability during live operations.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for proof-anchor-health-monitor-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-12, Φ-13, Ζ-27, SNAPSHOT-MAP
- Dependent Prompts: Ζ-73
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-30` `TRACE-AND-REPLAY-PAIRING-0`

- Purpose: Pair live traces with deterministic replay verification so operator action remains explainable.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for trace-and-replay-pairing-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-12, Υ-12, OMEGA-FREEZE, SNAPSHOT-MAP
- Dependent Prompts: Ζ-68
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-31` `HUMAN-AND-MACHINE-HEALTH-SURFACES-0`

- Purpose: Surface runtime health in forms both humans and agents can inspect without ambiguity.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for human-and-machine-health-surfaces-0, execution notes, operations playbook or cutover artifact, validation report
- Prerequisites: Σ-1, Ζ-24, Ζ-27, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `no`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-32` `POLICY-DRIVEN-AUTO-REMEDIATION-0`

- Purpose: Allow bounded auto-remediation only where policy, rollback, and review thresholds are explicit.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for policy-driven-auto-remediation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-10, Ζ-27, Ζ-28, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-33` `MIRRORED-RENDER-EXECUTION-0`

- Purpose: Run mirrored render execution so backend changes can be validated side-by-side before promotion.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for mirrored-render-execution-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-6, Φ-7, Ζ-0, SNAPSHOT-MAP
- Dependent Prompts: Ζ-35, Ζ-36, Ζ-37, Ζ-42
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-34` `OFFSCREEN-VALIDATION-RENDERER-0`

- Purpose: Run an offscreen validation renderer to verify frame correctness without driving the live shell.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for offscreen-validation-renderer-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-6, Φ-7, Φ-9, Υ-5, SNAPSHOT-MAP
- Dependent Prompts: Ζ-35, Ζ-36, Ζ-43
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-35` `DEBUG-RENDERER-SIDECAR-0`

- Purpose: Attach a debug renderer sidecar without mutating truth or breaking replay equivalence.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for debug-renderer-sidecar-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-1, Ζ-33, Ζ-34, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-36` `HEADLESS-VISIBLE-COEXECUTION-0`

- Purpose: Run headless and visible render paths together to compare results before cutover.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for headless-visible-coexecution-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-33, Ζ-34, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-37` `LIVE-FRAMEGRAPH-MIGRATION-0`

- Purpose: Migrate framegraph plans live only within frozen replacement and rollback boundaries.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-framegraph-migration-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-6, Φ-8, Ζ-0, Ζ-33, SNAPSHOT-MAP
- Dependent Prompts: Ζ-38, Ζ-39
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-38` `GPU-RESOURCE-REBINDING-0`

- Purpose: Rebind GPU resources during cutover without breaking render state guarantees or rollback plans.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for gpu-resource-rebinding-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-7, Ζ-0, Ζ-37, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-39` `RENDERER-STATE-CHECKPOINTING-0`

- Purpose: Checkpoint renderer state so backend cutovers and validation reruns can be replayed safely.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for renderer-state-checkpointing-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-13, Ζ-37, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-40` `LIVE-SHADER-BACKEND-SWITCH-0`

- Purpose: Switch shader backends live only after the asset and render device surfaces are frozen.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-shader-backend-switch-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-7, Φ-9, Ζ-0, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-41` `VIRTUAL-DISPLAY-TARGETS-0`

- Purpose: Create virtual display targets for validation, remote execution, and rehearsal.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for virtual-display-targets-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-7, Φ-9, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `implementation`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-42` `REMOTE-RENDER-SERVICE-0`

- Purpose: Externalize rendering as a remote service only after render isolation and rollback controls are proven.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for remote-render-service-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-3, Φ-7, Υ-10, Ζ-33, SNAPSHOT-MAP
- Dependent Prompts: Ζ-43
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-43` `TIERED-RENDER-DEGRADATION-0`

- Purpose: Degrade rendering tiers explicitly under operator policy instead of silently diverging.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for tiered-render-degradation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-11, Ζ-34, Ζ-42, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `operations`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-44` `LIVE-PACK-MOUNT-UNMOUNT-0`

- Purpose: Mount and unmount packs live only through governed compatibility, rollback, and quarantine flows.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-pack-mount-unmount-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Φ-2, Φ-11, Υ-10, SNAPSHOT-MAP
- Dependent Prompts: Ζ-45, Ζ-47, Ζ-48, Ζ-50, Ζ-53, Ζ-54
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-45` `LIVE-MOD-ACTIVATION-0`

- Purpose: Activate mods live only after isolation, capability, and rollback controls are present.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-mod-activation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-10, Υ-9, Ζ-44, SNAPSHOT-MAP
- Dependent Prompts: Ζ-46, Ζ-49, Ζ-51, Ζ-52, Ζ-56
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-46` `MOD-QUARANTINE-AND-ROLLBACK-0`

- Purpose: Quarantine and roll back faulty mods without rebuilding the rest of the runtime from scratch.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for mod-quarantine-and-rollback-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-11, Υ-12, Ζ-45, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-47` `CONTENT-NAMESPACE-REBINDING-0`

- Purpose: Rebind content namespaces live while preserving pack identity and deterministic resolution order.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for content-namespace-rebinding-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-11, Ζ-44, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-48` `LIVE-ASSET-STREAMING-0`

- Purpose: Stream assets live only after asset pipeline, lifecycle, and pack mount boundaries are frozen.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-asset-streaming-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-5, Φ-9, Ζ-44, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-49` `LIVE-LOGIC-RECOMPILATION-0`

- Purpose: Recompile live logic only through module loader, coexistence, and rollback-safe cutover surfaces.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for live-logic-recompilation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-2, Φ-11, Ζ-45, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-50` `COMPATIBILITY-SCORED-MOD-INSERTION-0`

- Purpose: Score mods for live insertion against compatibility, policy, and rollback readiness.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for compatibility-scored-mod-insertion-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Υ-10, Ζ-44, SNAPSHOT-MAP
- Dependent Prompts: Ζ-55
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-51` `SIGNED-CAPABILITY-MODS-0`

- Purpose: Require signed capability-bearing mods before live activation or privileged content operations.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for signed-capability-mods-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-9, Ζ-18, Ζ-45, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `schema_registry`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-52` `MOD-ABI-LAYERS-0`

- Purpose: Create ABI compatibility layers so controlled mod version overlap can exist without blind breakage.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for mod-abi-layers-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-2, Φ-11, Ζ-45, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-53` `HOT-PATCH-NONCORE-DATA-0`

- Purpose: Allow hot patching of non-core data only through governed staging and rollback flows.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for hot-patch-noncore-data-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-10, Ζ-44, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `operations`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-54` `MOD-STAGING-BEFORE-ACTIVATION-0`

- Purpose: Stage mods before activation so compatibility, signatures, and rollback checks complete first.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for mod-staging-before-activation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-10, Ζ-44, SNAPSHOT-MAP
- Dependent Prompts: Ζ-55
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `medium`
- Execution Class: `tooling`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-55` `CANARY-MOD-DEPLOYMENT-0`

- Purpose: Roll mods out through canary cohorts before broad activation.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for canary-mod-deployment-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-10, Ζ-50, Ζ-54, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-56` `PER-INSTANCE-MOD-GRAPHS-0`

- Purpose: Maintain per-instance mod graphs so live content choices remain explicit and auditable.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, snapshot-mapping rows for the target prompt
- Outputs: design package for per-instance-mod-graphs-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-11, Υ-12, Ζ-45, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `STRICT`
- Gates Required After Execution: RepoX STRICT, AuditX STRICT, validate --all STRICT, TestX extended subset
- Manual Review Required: `no`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-57` `DETERMINISTIC-REPLICATED-SIM-0`

- Purpose: Replicate simulation deterministically only after event logs, snapshots, authority, and operator controls are frozen.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for deterministic-replicated-sim-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-12, Φ-13, Φ-14, Υ-12, Ζ-27, OMEGA-FREEZE, SNAPSHOT-MAP
- Dependent Prompts: Ζ-58, Ζ-59, Ζ-60, Ζ-61, Ζ-62, Ζ-63, Ζ-64, Ζ-65, Ζ-68, Ζ-69, Ζ-70, Ζ-72, Ζ-73, Ζ-74
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-58` `AUTHORITY-HANDOFF-WITHOUT-DISCONNECT-0`

- Purpose: Hand authority off live without disconnects only after replicated simulation and authority proofs exist.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for authority-handoff-without-disconnect-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-14, Ζ-24, Ζ-57, SNAPSHOT-MAP
- Dependent Prompts: Ζ-59, Ζ-67
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-59` `SHARD-RELOCATION-0`

- Purpose: Relocate shards only after replication, authority handoff, and snapshot transfer are proven.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for shard-relocation-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-13, Ζ-57, Ζ-58, SNAPSHOT-MAP
- Dependent Prompts: Ζ-66
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-60` `EVENT-TAIL-SYNCHRONIZATION-0`

- Purpose: Synchronize event tails deterministically so replica catch-up and replay remain lawful.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for event-tail-synchronization-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-12, Φ-13, Ζ-57, SNAPSHOT-MAP
- Dependent Prompts: Ζ-62, Ζ-68
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-61` `INTEREST-MANAGEMENT-0`

- Purpose: Govern distributed interest management without changing authoritative truth outcomes.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for interest-management-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-3, Ζ-57, SNAPSHOT-MAP
- Dependent Prompts: Ζ-67
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-62` `MULTI-SITE-FAILOVER-0`

- Purpose: Fail over between sites only after replicated simulation and downgrade policy are proven.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for multi-site-failover-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-11, Ζ-57, Ζ-60, Ζ-63, SNAPSHOT-MAP
- Dependent Prompts: Ζ-69, Ζ-71
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-63` `QUORUM-SHARD-OWNERSHIP-0`

- Purpose: Define quorum-based shard ownership before live distributed failover or migration.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for quorum-shard-ownership-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-14, Ζ-57, SNAPSHOT-MAP
- Dependent Prompts: Ζ-62, Ζ-64, Ζ-65, Ζ-70
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `schema_registry`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-64` `DETERMINISTIC-CONFLICT-RESOLUTION-0`

- Purpose: Resolve distributed conflicts deterministically so replay and rollback remain equivalent.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for deterministic-conflict-resolution-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-57, Ζ-63, SNAPSHOT-MAP
- Dependent Prompts: Ζ-66
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `implementation`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-65` `FEDERATED-WORLDS-0`

- Purpose: Coordinate federated worlds only after distributed authority and trust policy are stable.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for federated-worlds-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Σ-5, Ζ-57, Ζ-63, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-66` `CROSS-SHARD-ENTITY-MIGRATION-0`

- Purpose: Migrate entities across shards only after relocation and conflict resolution are proven.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for cross-shard-entity-migration-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-59, Ζ-64, SNAPSHOT-MAP
- Dependent Prompts: Ζ-67
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-67` `SEAMLESS-PLAYER-TRANSFER-0`

- Purpose: Transfer players seamlessly only after interest management and entity migration remain deterministic.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for seamless-player-transfer-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-58, Ζ-61, Ζ-66, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-68` `DISTRIBUTED-REPLAY-VERIFY-0`

- Purpose: Verify distributed replay equivalence before any replicated runtime is considered trustworthy.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for distributed-replay-verify-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-30, Ζ-57, Ζ-60, SNAPSHOT-MAP
- Dependent Prompts: Ζ-72
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `tooling`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-69` `PARTIAL-CLUSTER-RESTART-0`

- Purpose: Restart cluster slices only after replication, failover, and downgrade policy are stable.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for partial-cluster-restart-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-11, Ζ-57, Ζ-62, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-70` `NETWORK-PARTITION-MODES-0`

- Purpose: Define lawful partition behavior before distributed survival or rejoin logic is enabled.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for network-partition-modes-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-11, Ζ-57, Ζ-63, SNAPSHOT-MAP
- Dependent Prompts: Ζ-71, Ζ-72
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `schema_registry`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-71` `DISTRIBUTED-DEGRADED-SURVIVAL-0`

- Purpose: Survive distributed degradation only through explicit downgrade and quorum-aware policy.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for distributed-degraded-survival-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-11, Ζ-62, Ζ-70, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-72` `DETERMINISTIC-REJOIN-0`

- Purpose: Rejoin distributed partitions only after replay verification and partition policy are proven.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for deterministic-rejoin-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Ζ-57, Ζ-68, Ζ-70, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-73` `PROOF-ANCHOR-QUORUM-VERIFY-0`

- Purpose: Verify proof anchors by quorum before distributed authority is trusted for promotion.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for proof-anchor-quorum-verify-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Φ-14, Ζ-29, Ζ-57, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `extreme`
- Execution Class: `tooling`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

### `Ζ-74` `WHAT-IF-SIM-ON-UPDATES-0`

- Purpose: Run what-if simulation on updates only after distributed replay, release ops, and downgrade paths are proven.
- Inputs: OMEGA baseline artifacts, PHI runtime foundation outputs, UPSILON control-plane outputs, data/blueprint/series_execution_strategy.json, distributed replay verify reports, docs/blueprint/PRE_AND_POST_SNAPSHOT_PHASES.md, docs/blueprint/SERIES_EXECUTION_STRATEGY.md, proof-anchor health reports, snapshot-mapping rows for the target prompt
- Outputs: design package for what-if-sim-on-updates-0, operations playbook or cutover artifact, rollback notes, validation report
- Prerequisites: Υ-10, Υ-11, Υ-12, Ζ-57, SNAPSHOT-MAP
- Dependent Prompts: none
- Snapshot Requirement: `post_snapshot_required`
- Risk Level: `high`
- Execution Class: `operations`
- Gate Profile Required: `FULL`
- Gates Required After Execution: XStack CI FULL, RepoX FULL, AuditX FULL, Omega verification suite, trust strict suite when relevant
- Manual Review Required: `yes`
- Rollback Strategy Required: `yes`
- Stop Conditions: If a semantic contract bump is required, stop and escalate., If any ZETA prompt requires an unstated foundation, stop and move it back into SIGMA, PHI, or UPSILON planning., If deterministic baselines drift, stop., If required human review is unavailable or unresolved, stop., If rollback strategy is absent or unverified, stop., If runtime or module boundaries are unclear, stop before PHI-series implementation., If snapshot mapping for this prompt is incomplete or low-confidence, stop., If the architecture graph changes unexpectedly, stop., If the fresh live repository snapshot shows a conflicting subsystem already exists, stop and reconcile.

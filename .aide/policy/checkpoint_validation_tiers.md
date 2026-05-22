Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-CHECKPOINT-LOOP-01
Stability: provisional
Binding Sources: `.aide/policy/checkpoint_loop_law.md`, `.aide/policy/dev_main_policy.md`, `.aide/policy/evidence_requirements.md`

# AIDE Checkpoint Validation Tiers

## Purpose

This file defines validation tiers for AIDE checkpoint candidates. Validation
strength increases with scope and promotion target.

Ordinary development checkpoints are evidence gates, not release gates. T4 is
reserved for release/full-gate or explicit promotion policy.

## T0 - Coordinator Consistency

T0 checks whether coordinator-facing state is coherent.

Required checks:

- `.aide/queue/current.toml` parses when touched
- latest task packet, review packet, status report, and warning disposition
  match the active coordinator task when coordinator-owned
- task audit and next task agree with queue/status when coordinator-owned
- parallel-lane tasks did not mutate exclusive coordinator files without
  ownership
- checkpoint audit records whether coordinator update was applied or deferred

T0 failure outcomes:

- `CHECKPOINT_BLOCKED_MISSING_PREREQ` when required coordinator evidence is
  absent
- `CHECKPOINT_DEFERRED` when a lane task lacks coordinator ownership
- `CHECKPOINT_REPAIR_REQUIRED` for bounded stale packet or status drift

## T1 - Policy And Schema Consistency

T1 checks whether AIDE policy and schema foundations exist and align.

Required checks:

- `AIDE-WORKFLOW-LAW-01` audit exists
- WorkUnit schemas validate when WorkUnit fixtures are present
- `AIDE-DEV-MAIN-POLICY-01` audit exists
- warning disposition remains current and classified
- checkpoint-loop policy files exist
- touched JSON fixtures and schema artifacts parse

T1 failure outcomes:

- `CHECKPOINT_BLOCKED_MISSING_PREREQ` for missing workflow, WorkUnit, or
  dev/main prerequisites
- `CHECKPOINT_REPAIR_REQUIRED` for fixture or schema parse failures
- `CHECKPOINT_QUARANTINE_REQUIRED` for material schema meaning conflicts

## T2 - Foundation Fast Gate

T2 checks repository foundation surfaces affected by the checkpoint.

Candidate checks:

- dependency-direction strict
- public surface validation
- component matrix
- portability matrix
- command surface validation
- diagnostic registry validation
- artifact identity validation
- schema or contract validators for touched areas
- capability/refusal validators
- provider model validators
- module/app descriptor validators
- fast strict when the checkpoint scope justifies it

T2 is required when checkpointed work touches foundation governance,
contracts, public surfaces, dependency direction, portability, component
boundaries, command/refusal/result surfaces, provider/module/app descriptors,
or other shared foundations.

## T3 - Product-Spine Affected Gate

T3 checks product-spine proof surfaces when the checkpoint touches them.

Candidate checks:

- package mount validators when package surfaces are touched
- replay proof validators when replay/proof surfaces are touched
- barebones product shell tests when product shell surfaces are touched
- command/result/view projection tests when presentation or command projection
  surfaces are touched
- targeted smoke tests for affected product-spine slices

T3 does not authorize broad product/runtime work. It proves that touched
product-spine surfaces remain coherent in their declared fixture/proof scope.

## T4 - Full Or Release Gate

T4 checks release/full-gate readiness.

Candidate checks:

- full CTest
- compatibility corpus
- release promotion gate
- signing or provenance checks where applicable
- release, update, trust, archive, or publication policy checks

T4 is not required for ordinary dev checkpoints unless the promotion target,
release policy, trust policy, or explicit checkpoint policy requires it.

Full CTest remains T4/full-gate debt unless live repo evidence says otherwise.
No ordinary AIDE checkpoint may claim T4 green from T0-T3 evidence.

## Tier Selection Rules

- Docs-only lane checkpoint: T0, T1, `git diff --check`, and touched docs
  sanity checks.
- AIDE policy/schema checkpoint: T0, T1, targeted AIDE validators, JSON/TOML
  parse checks, and `git diff --check`.
- Foundation-affecting checkpoint: add T2.
- Product-spine-affecting checkpoint: add T3 for touched areas.
- Release/trust/main-publication checkpoint: add T4 when policy requires it.

Validation commands that are unavailable must be reported honestly. Unavailable
required validators may become `CHECKPOINT_BLOCKED_MISSING_PREREQ` or
`CHECKPOINT_DEFERRED` depending on scope.

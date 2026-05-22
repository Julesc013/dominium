Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `.aide/policies/evidence.toml`, `.aide/verification/evidence-packet.template.md`, `.aide/policies/promotion-rules.yaml`

# AIDE Evidence Requirements

Every task closeout must include changed files, commands run, validation output,
warnings, blockers, evidence refs, commit hash when committed, and next action.

| Task Type | Minimum Evidence |
| --- | --- |
| coordinator/status task | Queue/status fields changed, latest packet ownership, audit note, validation commands, warning disposition, next task. |
| contract/schema task | Contract/schema paths, parse results, compatibility impact, public surface impact if registered, validator output, migration/refusal notes. |
| validator task | Validator path, fixture path, pass/fail examples, targeted command output, false-positive/false-negative limits. |
| product slice | Product surface refs, public surface registration, capability/refusal/diagnostic impact, targeted app tests, non-goal preservation. |
| runtime implementation slice | Runtime boundary refs, deterministic impact, build/test proof, contract impact, rollback/repair path. |
| Workbench/presentation slice | Presentation-only boundary, command/result/view contract, no truth mutation proof, UI test or fixture evidence. |
| structure/move task | Move map, route rationale, affected references, generated refresh, rollback plan, strict layout/dependency validation. |
| repair task | Original blocker, repair scope, changed files, rerun validation, residual risks, original task link. |
| checkpoint task | Selected task branches/commits, merge conflict disposition, checkpoint validation, accepted warnings, rollback path. |
| promotion task | Checkpoint report, review decision, main target, commit hash, gate results, warning acceptance, post-promotion status. |

## Evidence Integrity

- Evidence must cite repo paths.
- Validation must distinguish run, not run, unavailable, and not applicable.
- Warnings must not be hidden as clean passes.
- Fixture-only or planned support must not be called implemented.
- Commit hashes must be recorded only after commits exist.

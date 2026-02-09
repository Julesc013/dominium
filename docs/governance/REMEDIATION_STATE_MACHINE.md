Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Remediation State Machine

## Overview

Remediation mode is entered automatically when any required gate fails.

## States

### R1 Diagnose

- Identify failing gate and exact error output.
- Classify blocker:
  - `TOOL_DISCOVERY`
  - `DERIVED_ARTIFACT`
  - `SCHEMA_MISMATCH`
  - `GOVERNANCE_RULE`
  - `CAPABILITY_MISSING`
  - `COMMAND_GRAPH_DRIFT`
  - `ENVIRONMENT_CONTRACT`
  - `DETERMINISM`
  - `DOCUMENTATION_DRIFT`
  - `OTHER` (with explicit justification)
- Derive semantic locality from failure evidence.

### R2 Enumerate Strategies

Minimum strategy classes:

- environment/adapter
- registry/schema alignment
- tooling integration
- build wiring
- governance rule
- TestX regression
- artifact regeneration

### R3 Safe Attempt

Apply strategies that satisfy:

- no simulation semantic change
- no governance weakening
- deterministic and reversible
- locality-bounded mutation

### R4 Verify and Prevent

- Re-run failed gate.
- Re-run upstream gates.
- Add at least one prevention artifact:
  - RepoX invariant, or
  - TestX regression, or
  - AuditX analyzer/finding.

### R5 Progress Check

Required measurable improvement:

- fewer failing gates, or
- reduced blocker severity/confidence, or
- narrower locality, or
- new prevention coverage.

If no improvement, switch strategy class and continue.

### R6 Semantic Escalation

Only for semantic ambiguity requiring human intent.

Required escalation template:

- `BLOCKER TYPE:`
- `FAILED GATE:`
- `ROOT CAUSE:`
- `ATTEMPTED FIXES:`
- `REMAINING OPTIONS:`
- `RECOMMENDED OPTION:`
- `RATIONALE:`

## Artifacts

Every failure cycle writes:

- `docs/audit/remediation/<timestamp>_<gate>_<type>/failure.json`
- `docs/audit/remediation/<timestamp>_<gate>_<type>/failure.md`
- `docs/audit/remediation/<timestamp>_<gate>_<type>/actions_taken.json`
- `docs/audit/remediation/<timestamp>_<gate>_<type>/verification.json`
- `docs/audit/remediation/<timestamp>_<gate>_<type>/prevention_links.json`
- `docs/audit/remediation/<timestamp>_<gate>_<type>/diff_summary.txt`


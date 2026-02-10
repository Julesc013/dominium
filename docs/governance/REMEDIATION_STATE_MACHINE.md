Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Remediation State Machine

## Purpose

Define mandatory autonomous remediation behavior for gate failures.

## States

### R1 Diagnose

- Capture exact failing gate and invariant.
- Classify blocker type.
- Record impacted files and subsystem scope.

### R2 Enumerate Strategy Classes

- Environment or adapter correction
- Registry or schema alignment
- Build wiring
- Governance rule or regression test reinforcement
- Derived artifact regeneration

### R3 Safe Remediation

- No simulation semantic changes.
- No governance weakening.
- Idempotent and reversible operations only.

### R4 Verify and Prevent

- Re-run affected gate and upstream gates.
- Attach prevention artifacts (RepoX, TestX, or AuditX).

### R5 Progress Check

- Require measurable improvement:
  - fewer failures, or
  - lower failure score/severity, or
  - narrower blast radius.

### R6 Semantic Escalation

- Escalate only for meaning decisions:
  - canon interpretation conflicts
  - trust/security policy meaning choices
  - ontology-level ambiguity

## Remediation Artifacts

Each remediation cycle writes:

- `failure.json`
- `failure.md`
- `actions_taken.json`
- `verification.json`
- `prevention_links.json`
- `diff_summary.txt`

Under:

- `docs/audit/remediation/<timestamp>_<gate>_<type>/`

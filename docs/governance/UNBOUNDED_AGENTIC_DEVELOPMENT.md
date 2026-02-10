Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Unbounded Agentic Development

## Purpose

Define canonical autonomous development behavior for RepoX, TestX, AuditX, CI, and developer shells.

## Core Rules

- Reasoning is unbounded.
- Mutation is bounded to diagnosed semantic locality plus explicit governance/test artifacts.
- Every remediation cycle must show measurable progress.
- Repeated failures require strategy-class switching.
- Fixes are incomplete without prevention artifacts.
- Human escalation is allowed only for semantic ambiguity.

## Gate Contract

Required gates, in order:

1. `RepoX`
2. strict build (`domino_engine`, `dominium_game`, `dominium_client`)
3. `testx_all`
4. `tool_ui_bind --check`

If any gate fails, remediation mode is mandatory.

## Non-Negotiables

- No gate bypass.
- No hidden defaults.
- No simulation semantic changes.
- No deterministic behavior regressions.
- No stage/era/progression semantics in runtime code, schemas, manifests, validators, or tests.

## Integration

- RepoX enforces remediation discipline and bounded mutation.
- TestX verifies blocker regressions, discoverability, anti-thrashing, and locality checks.
- AuditX tracks recurrence, thrash patterns, and prevention coverage.
- Gate flow and remediation state machine:
  - `docs/governance/GATE_AUTONOMY_POLICY.md`
  - `docs/governance/REMEDIATION_STATE_MACHINE.md`
  - `docs/governance/SEMANTIC_ESCALATION_POLICY.md`

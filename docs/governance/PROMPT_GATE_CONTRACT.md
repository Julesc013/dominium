Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Prompt Gate Contract

Prompts, automation, and queued runs must enter governance gates through `scripts/dev/gate.py`.

## Canonical Entry

- Use `python scripts/dev/gate.py precheck --repo-root <repo>` for minimal preflight.
- Use `python scripts/dev/gate.py exitcheck --repo-root <repo>` for strict completion.
- Use `python scripts/dev/gate.py verify --repo-root <repo>` for full precheck + exitcheck flow.

## Tool Invocation Rule

- Prompts must not call raw tool checks directly (example: `tool_ui_bind --check`).
- Raw tool invocations are allowed only inside gate automation and dedicated tests.
- `ui_bind_check` is a dependency gate controlled by `data/registries/gate_policy.json`.

## Dependency-Aware Behavior

- `PRECHECK_MIN` gates run first and remain bounded.
- `TASK_DEPENDENCY` gates run only when gate policy conditions match touched paths or requested targets.
- `EXIT_STRICT` gates always enforce strict completion requirements for the selected lane.

## Remediation Rule

- Mechanical failures are remediated in-process by `gate.py`.
- Successful/failed remediation attempts are recorded under `docs/audit/remediation/`.
- Semantic ambiguity is escalated per `docs/governance/SEMANTIC_ESCALATION_POLICY.md`.

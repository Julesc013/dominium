Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Prompt Gate Contract

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Prompts, automation, and queued runs must enter governance gates through `scripts/dev/gate.py`.

## Canonical Entry

- Use `python scripts/dev/gate.py precheck --repo-root <repo>` for minimal preflight.
- Use `python scripts/dev/gate.py taskcheck --repo-root <repo>` for dependency-only gate checks.
- Use `python scripts/dev/gate.py exitcheck --repo-root <repo>` for strict completion.
- Use `python scripts/dev/gate.py verify --repo-root <repo>` for full precheck + taskcheck + exitcheck flow.

## Tool Invocation Rule

- Prompts must not call raw tool checks directly (example: `tool_ui_bind --check`).
- Prompts must not call `scripts/ci/check_repox_rules.py` or `ctest` directly.
- Raw tool invocations are allowed only inside gate automation and dedicated tests.
- `ui_bind_check` is a dependency gate controlled by `data/registries/gate_policy.json`.
- Legacy entrypoints may use wrappers that forward to `gate.py`:
  - `python scripts/dev/gate_shim.py`
  - `python scripts/dev/run_repox.py`
  - `python scripts/dev/run_testx.py`

## Dependency-Aware Behavior

- `PRECHECK_MIN` gates run first and remain bounded.
- `TASK_DEPENDENCY` gates run only when gate policy conditions match touched paths or requested targets.
- `EXIT_STRICT` gates always enforce strict completion requirements for the selected lane.

## Remediation Rule

- Mechanical failures are remediated in-process by `gate.py`.
- Successful/failed remediation attempts are recorded under `docs/audit/remediation/<workspace_id>/`.
- Semantic ambiguity is escalated per `docs/governance/SEMANTIC_ESCALATION_POLICY.md`.

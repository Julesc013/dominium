Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# STATUS_SR3

- SR-3 adds SPLAT capability registry, deterministic selection rules, and selection audit evidence.
- New CLI commands expose `dump-splats` and `select-splat` for inspection and validation.
- Kernel remains orchestration-only; no install execution, job DAG, or resumability work yet.
- Legacy setup behavior is unchanged; setup still produces state/audit only.
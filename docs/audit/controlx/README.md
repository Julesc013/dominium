Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# ControlX Audit Artifacts

This directory stores ControlX run artifacts.

## Artifact Types

- `SANITIZATION.md`: prompt firewall sanitation details
- `RUNLOG.json`: deterministic per-run control log
- `remediation_links.json`: link set into gate remediation bundles
- `<queue_id>.QUEUE_RUNLOG.json`: queue summary log

## Determinism Notes

- Run logs avoid timestamps and machine-only data.
- Queue summaries are stable under identical prompt inputs and policy state.
- Mechanical remediation artifacts are linked, not duplicated.

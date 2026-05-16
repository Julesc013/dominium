Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# AIDE Workunit Idempotency

This reference summarizes portable task recovery and workunit idempotency. The
canonical policy surfaces are `.aide/policies/task-resumption.yaml`,
`.aide/policies/work-units.yaml`, and `.aide/policies/recovery.yaml`.

Repeated or resumed work should inspect the current task, status, evidence, and
dependencies before changing files. Recovery commands are evidence-producing and
must not hide partial work, delete evidence, or bypass review gates.

This document is guidance for target repositories importing the AIDE Lite pack.

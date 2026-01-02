# Setup2 v1 Read-Only Lock

Status: Setup2 v1 is frozen.

Rules:
- All changes require a new ladder starting at SR-0 for v2.
- Only documentation errata and test fixes (no behavior) are permitted without
  reopening the ladder.
- No schema, adapter, or behavior changes are permitted under v1.

Proposing v2:
- Provide a problem statement and scope.
- Provide impact analysis on determinism, resumability, and audit coverage.
- Provide schema migration plan (v1 -> v2) and backward-compatibility rules.
- Obtain approvals from project maintainers and release owners.

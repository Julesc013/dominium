# Worktree Leftovers Allowlist

Purpose: when running local governance scans on a non-clean worktree, every
intentional leftover path must be documented here with a brief reason.

RepoX rule: `INV-WORKTREE-HYGIENE`

Format (one entry per line):
- `relative/path.ext`: short reason
- `relative/path.ext`|short reason

Current entries:
- `docs/audit/TOPOLOGY_MAP.json`: deterministic topology artifact refresh produced by governance scans
- `docs/audit/TOPOLOGY_MAP.md`: deterministic topology artifact refresh produced by governance scans
- `docs/audit/auditx/FINDINGS.json`: deterministic AuditX findings refresh produced by governance scans
- `docs/audit/auditx/FINDINGS.md`: deterministic AuditX findings refresh produced by governance scans
- `docs/audit/auditx/INVARIANT_MAP.json`: deterministic AuditX invariant map refresh produced by governance scans
- `docs/audit/auditx/PROMOTION_CANDIDATES.json`: deterministic AuditX promotion candidate refresh produced by governance scans
- `docs/audit/auditx/RUN_META.json`: deterministic AuditX run metadata refresh produced by governance scans
- `docs/audit/auditx/SUMMARY.md`: deterministic AuditX summary refresh produced by governance scans
- `docs/audit/auditx/TRENDS.json`: deterministic AuditX trends refresh produced by governance scans

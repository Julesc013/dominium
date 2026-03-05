# Worktree Leftovers Allowlist

Purpose: when running local governance scans on a non-clean worktree, every
intentional leftover path must be documented here with a brief reason.

RepoX rule: `INV-WORKTREE-HYGIENE`

Format (one entry per line):
- `relative/path.ext`: short reason
- `relative/path.ext`|short reason

Current entries:
- `docs/audit/auditx/FINDINGS.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/FINDINGS.md`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/INVARIANT_MAP.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/PROMOTION_CANDIDATES.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/RUN_META.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/SUMMARY.md`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)
- `docs/audit/auditx/TRENDS.json`: pre-existing local AuditX run artifact (kept uncommitted for iterative governance scans)

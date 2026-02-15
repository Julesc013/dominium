Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: AuditX semantic outputs for Prompt 16 baseline.

# AuditX Reports

## Run Commands
- Full scan:
  - `python tools/auditx/auditx.py scan --repo-root .`
- Changed-only scan:
  - `python tools/auditx/auditx.py scan --repo-root . --changed-only`
- Verify mode (non-gating):
  - `python tools/auditx/auditx.py verify --repo-root .`
- Enforcement stub:
  - `python tools/auditx/auditx.py enforce --repo-root .`

## Output Files
AuditX writes deterministic artifacts under `docs/audit/auditx/`:
- `FINDINGS.json`: machine-readable findings payload.
- `FINDINGS.md`: human-readable findings list.
- `SUMMARY.md`: aggregate counts and rollups.
- `INVARIANT_MAP.json`: finding to invariant cross-map.

Additional derived files may be present; the four files above are the canonical baseline contract for this prompt.

## Severity and Confidence
- `severity` is impact class:
  - `INFO`: informational drift or weak signal.
  - `WARN`: moderate concern requiring review.
  - `RISK`: high-priority semantic risk.
  - `VIOLATION`: likely contract breach or boundary misuse.
- `confidence` is a deterministic analyzer confidence score (`0.0` to `1.0`).

## Triage Guidance
1. Prioritize by severity, then confidence.
2. For `RISK`/`VIOLATION` with high confidence, decide promotion path:
   - RepoX invariant (`ADD_RULE`), or
   - TestX regression (`ADD_TEST`).
3. Record disposition via finding `status`:
   - `OPEN`, `ACK`, `RESOLVED`, or `DEFERRED`.
4. Avoid direct runtime edits from AuditX-only output; route changes through normal feature/fix tasks.

## Changed-Only Notes
- `--changed-only` requires git availability.
- If git is unavailable, AuditX returns deterministic refusal code:
  - `refusal.git_unavailable`

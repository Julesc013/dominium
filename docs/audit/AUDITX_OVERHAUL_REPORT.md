Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# AuditX Overhaul Report

## Implemented

- Canonical output contract split:
  - `docs/audit/auditx/FINDINGS.json` (`CANONICAL`)
  - `docs/audit/auditx/INVARIANT_MAP.json` (`CANONICAL`)
  - `docs/audit/auditx/PROMOTION_CANDIDATES.json` (`CANONICAL`)
  - `docs/audit/auditx/TRENDS.json` (`CANONICAL`)
  - `docs/audit/auditx/RUN_META.json` (`RUN_META`)
  - `docs/audit/auditx/FINDINGS.md` and `SUMMARY.md` (`DERIVED_VIEW`)
- Canonicalization utility added: `tools/auditx/canonicalize.py`.
- Incremental cache engine added: `tools/auditx/cache_engine.py`.
- Workspace-scoped cache and trend history under `tools/auditx/cache/<WS_ID>/`.
- Analyzer suite expanded with semantic drift and structural risk analyzers.
- Promotion candidate output and trend output integrated.
- AuditX environment self-containment hardened using `env_tools_lib`.

## Determinism Guarantees

- Canonical artifacts are key-sorted and hash-stable across identical rescans.
- Canonical artifacts exclude run metadata fields (timestamps, host IDs, scan IDs).
- `RUN_META.json` is explicitly non-canonical and excluded from determinism proofs.
- Incremental reuse does not alter canonical ordering of findings.

## Incremental Behavior

- Full cache reuse when key inputs and content hash match.
- Partial changes trigger analyzer-level recomputation by watch-prefix routing.
- Unaffected analyzers reuse prior normalized findings.

## Promotion Flow

- AuditX emits deterministic promotion candidates only.
- RepoX validates candidate shape and policy before any manual promotion.
- No auto-activation path exists.

## Trend Tracking

- `TRENDS.json` records category and severity distributions from canonical findings.
- Delta is computed against the most recent distinct findings hash tracked in workspace cache.
- Trend canonical output remains stable across unchanged rescans.

## Remaining Risks

- Heuristic analyzers may surface advisory false positives by design.
- Cache effectiveness depends on quality of analyzer watch-prefix definitions.
- Additional analyzer tuning may be required for very large pack graphs.


# Q52 Readiness

Status: READY_FOR_Q52_WITH_WARNINGS

## Is Dominium Ready For Q52 Root Recycling Pilot?

Yes, with warnings. Q51 produced a tool inventory, classification, capability map, and wrapper plan. AIDE roots inventory is available. Unknown file/tool classifications remain and must be treated as review gates, not blockers for a low-risk evidence-only root pilot.

## Recommended First Root Family

Recommended first root: `ide/`.

Reason: `ide/` is small, tooling-adjacent, and outside product source/doctrine roots. AIDE root inventory still classifies it as high risk due unknown ownership, so Q52 should be evidence-only and should not move/delete/rewrite files.

Secondary candidates if `ide/` proves unsuitable:

- `performance/`
- `validation/`
- `meta/`

`governance/` should be handled later or with extra review because it is authority-sensitive even though it is a suggested low-risk family in the generic prompt.

## Tools / Validators Q52 Should Use As Evidence Only

- `.aide/roots/latest-root-inventory.*`
- `.aide/repo/latest-repo-intelligence.md`
- `.aide/tools/dominium-tool-inventory.json`
- `.aide/tools/dominium-tool-classification.json`
- `.aide/tools/dominium-tool-adapter-map.json`
- `.aide/tools/dominium-tool-wrap-plan.md`
- XStack/AuditX/RepoX/TestX references only; no direct execution unless a future task proves a specific command safe.

## Forbidden For Q52

- Product source roots: `runtime/**`, `engine/**`, `game/**`, `apps/**`, `content/**`.
- Doctrine/protected roots: `AGENTS.md`, `docs/canon/**`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`, `specs/reality/**`, `data/reality/**`.
- Tool roots: `tools/**`, `scripts/**`, `validation/**`, `repo/**`, `cmake/**` except read-only evidence.
- `.github/**`, `.git/**`, `.aide.local/**`, secrets, generated build/dist/out directories.

## What Q52 Must Preserve

- Dominium doctrine and authority ordering.
- Existing tool systems and validators.
- Target-specific `.aide/memory/**`, `.aide/queue/**`, `.aide/reports/dominium-*`, and generated evidence.
- No branch mutation and no provider/model/network calls.

## Validation Q52 Must Run

- `git status --short`
- `git diff --check`
- `git check-ignore .aide.local/`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py roots inventory`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py tools status`
- Targeted secret/local-state scan

## Warnings

- AIDE full eval timed out in Q51.
- Root inventory marks almost all roots high-risk due unknown ownership and mixed status.
- Tool inventory has 854 unknown candidates.
- No legacy tool should be run by Q52 without a specific safe command contract.

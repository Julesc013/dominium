# Next AIDE Task

Task: Q52 Dominium Root Recycling Pilot

## Goal

Run an evidence-only root recycling pilot using Q51 tool absorption outputs, without moving, deleting, rewriting, or executing unknown legacy tools.

## Recommended First Root

Start with `ide/`.

Reason: small, tooling-adjacent, and outside product source/doctrine roots. Treat it as high-risk until ownership and references are confirmed.

## Required Inputs

- `.aide/queue/DOMINIUM-AIDE-TOOL-ABSORPTION-01/evidence/q52-readiness.md`
- `.aide/tools/dominium-tool-inventory.json`
- `.aide/tools/dominium-tool-classification.json`
- `.aide/tools/dominium-tool-adapter-map.json`
- `.aide/tools/dominium-tool-wrap-plan.md`
- `.aide/roots/latest-root-inventory.*`
- `.aide/repo/latest-repo-intelligence.md`

## Non-Goals

- No product source edits.
- No doctrine edits.
- No root moves/deletes.
- No branch mutation.
- No unknown tool execution.
- No provider/model/network calls.

## Validation

- `git status --short`
- `git diff --check`
- `git check-ignore .aide.local/`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py roots inventory`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py tools status`
- targeted secret/local-state scan

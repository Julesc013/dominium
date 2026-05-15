# Validation

## Core

- `git remote -v`: confirmed `https://github.com/Julesc013/dominium.git`.
- `git rev-parse --show-toplevel`: `C:/Inbox/Git Repos/dominium`.
- `git branch --show-current`: `main`.
- `git rev-parse HEAD`: `80dc7bfb58a1cdc887ee1fed8a83fb22ff3028e0` before Q50 commit.
- `git check-ignore .aide.local/`: PASS, `.aide.local/`.
- `git diff --check`: PASS, with line-ending warnings only.

## AIDE Baseline Before Sync

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with stale review-reference warnings.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS 25/25 before sync.
- New install/upgrade commands were not supported by the old q24 target script.

## AIDE Post-Sync

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with two review-reference warnings for controller reports.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 0 errors; warnings are diff-scope and missing optional controller reports.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS, verifier result WARN.
- `py -3 .aide/scripts/aide_lite.py eval run --task intent_compile_install_prompt_golden`: PASS 1/1.
- Full post-sync `eval run` over 130 tasks timed out and was stopped; no provider/model/network calls were observed in the completed representative eval.

## New Capability Validation

- `intent validate`: PASS after `intent compile`.
- `repo validate`: WARN, unknown classifications: 1635.
- `quality validate`: PASS.
- `refactor validate`: PASS after plan/dry-run generation.
- `roots validate`: PASS.
- `tools validate`: PASS.
- `install validate`: PASS.
- `repair validate`: PASS.
- `upgrade validate`: PASS.
- `rollback validate`: PASS.
- `uninstall validate`: PASS.
- `changelog validate`: PASS.
- `gateway status`: PASS using report-only target fallback.
- `gateway smoke`: PASS using report-only target fallback.
- `provider status`: PASS using report-only target fallback.
- `provider validate`: PASS with warnings for source README omission and root helper fallback.

## Secret Scan

- Broad scan used the Q50 pattern against existing paths and returned policy/token terminology matches, not secret material.
- High-confidence scan returned only Q50 evidence text and test assertions that forbid `OPENAI_API_KEY=` and `BEGIN PRIVATE KEY`; no credential values were found.

# Post-Sync Validation

## PASS

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py intent compile --prompt "Plan Q51 Dominium Existing Tool Absorption"`
- `py -3 .aide/scripts/aide_lite.py intent validate`
- `py -3 .aide/scripts/aide_lite.py repo inventory`
- `py -3 .aide/scripts/aide_lite.py quality ledger`
- `py -3 .aide/scripts/aide_lite.py quality validate`
- `py -3 .aide/scripts/aide_lite.py refactor plan`
- `py -3 .aide/scripts/aide_lite.py refactor dry-run`
- `py -3 .aide/scripts/aide_lite.py refactor validate`
- `py -3 .aide/scripts/aide_lite.py roots inventory`
- `py -3 .aide/scripts/aide_lite.py roots plan`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py tools inventory`
- `py -3 .aide/scripts/aide_lite.py tools wrap-plan`
- `py -3 .aide/scripts/aide_lite.py tools validate`
- `py -3 .aide/scripts/aide_lite.py install observe`
- `py -3 .aide/scripts/aide_lite.py install plan`
- `py -3 .aide/scripts/aide_lite.py install dry-run`
- `py -3 .aide/scripts/aide_lite.py install validate`
- `py -3 .aide/scripts/aide_lite.py repair observe`
- `py -3 .aide/scripts/aide_lite.py repair diagnose`
- `py -3 .aide/scripts/aide_lite.py repair plan`
- `py -3 .aide/scripts/aide_lite.py repair dry-run`
- `py -3 .aide/scripts/aide_lite.py repair doctor`
- `py -3 .aide/scripts/aide_lite.py repair validate`
- `py -3 .aide/scripts/aide_lite.py upgrade observe-current`
- `py -3 .aide/scripts/aide_lite.py upgrade observe-source`
- `py -3 .aide/scripts/aide_lite.py upgrade compare`
- `py -3 .aide/scripts/aide_lite.py upgrade plan`
- `py -3 .aide/scripts/aide_lite.py upgrade dry-run`
- `py -3 .aide/scripts/aide_lite.py upgrade validate`
- `py -3 .aide/scripts/aide_lite.py rollback observe`
- `py -3 .aide/scripts/aide_lite.py rollback plan`
- `py -3 .aide/scripts/aide_lite.py rollback dry-run`
- `py -3 .aide/scripts/aide_lite.py rollback validate`
- `py -3 .aide/scripts/aide_lite.py uninstall observe`
- `py -3 .aide/scripts/aide_lite.py uninstall plan`
- `py -3 .aide/scripts/aide_lite.py uninstall dry-run`
- `py -3 .aide/scripts/aide_lite.py uninstall validate`
- `py -3 .aide/scripts/aide_lite.py changelog preview`
- `py -3 .aide/scripts/aide_lite.py changelog validate`
- `py -3 .aide/scripts/aide_lite.py gateway status`
- `py -3 .aide/scripts/aide_lite.py gateway smoke`
- `py -3 .aide/scripts/aide_lite.py provider status`
- `py -3 .aide/scripts/aide_lite.py provider validate`
- `py -3 .aide/scripts/aide_lite.py git detect`
- `py -3 .aide/scripts/aide_lite.py git policy`
- `py -3 .aide/scripts/aide_lite.py git plan`
- `py -3 .aide/scripts/aide_lite.py pack --task "Q51 Dominium Existing Tool Absorption"`
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`
- `git diff --check`
- `git check-ignore .aide.local/`

## WARN

- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 0 errors. Remaining warnings are active diff-scope mismatches and missing optional controller reports.
- `py -3 .aide/scripts/aide_lite.py repo validate`: WARN because 1635 files remain unknown-classified.

## PARTIAL

- `py -3 .aide/scripts/aide_lite.py eval run`: full 130-task run timed out and was stopped.
- `py -3 .aide/scripts/aide_lite.py eval run --task intent_compile_install_prompt_golden`: PASS 1/1.


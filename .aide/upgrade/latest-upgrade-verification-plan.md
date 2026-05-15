# Upgrade Verification Plan

- no_apply: true
- future upgrade apply must run local validation before and after mutation.

## Commands

- py -3 .aide/scripts/aide_lite.py doctor
- py -3 .aide/scripts/aide_lite.py validate
- py -3 .aide/scripts/aide_lite.py test
- py -3 .aide/scripts/aide_lite.py selftest
- py -3 .aide/scripts/aide_lite.py eval run
- py -3 .aide/scripts/aide_lite.py pack-status
- py -3 .aide/scripts/aide_lite.py install validate
- py -3 .aide/scripts/aide_lite.py repair validate
- py -3 .aide/scripts/aide_lite.py upgrade validate

## Boundary

- Q45 records verification expectations only. It does not activate upgrade apply, CI, GitHub settings, providers, or network calls.

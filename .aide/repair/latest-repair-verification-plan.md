# Repair Verification Plan

- no_apply: true
- future repair apply must run local validation before and after mutation.

## Commands

- py -3 .aide/scripts/aide_lite.py doctor
- py -3 .aide/scripts/aide_lite.py validate
- py -3 .aide/scripts/aide_lite.py test
- py -3 .aide/scripts/aide_lite.py selftest
- py -3 .aide/scripts/aide_lite.py install validate
- py -3 .aide/scripts/aide_lite.py repair validate
- py -3 .aide/scripts/aide_lite.py pack-status

## Boundary

- Q44 records verification expectations only. It does not activate repair apply, CI, GitHub settings, providers, or network calls.

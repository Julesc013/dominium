Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# SEMANTIC-LINTS Status

Result: PASS_WITH_WARNINGS.

POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS reproduced and repaired the two remaining semantic CTest blockers:

- `slice0_hardcoded_ids`: PASS after narrow exact-match allowlist.
- `slice1_hardcoded_constants`: PASS after narrow exact-match allowlist.

The task classified 1,104 reproduced findings:

- `preserve_doctrine_constant`: 213
- `preserve_fixture_literal`: 582
- `preserve_protocol_literal`: 264
- `preserve_schema_literal`: 45

No broad suppressions were added. The allowlist matches exact `test_name`, `file`, `line`, `validator_message`, and source-line `context_sha256`.

No source/product/runtime behavior changed.

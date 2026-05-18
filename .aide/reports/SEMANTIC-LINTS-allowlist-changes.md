Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# SEMANTIC-LINTS Allowlist Changes

Added `contracts/repo/semantic_lint_allowlist.json` with exact-match entries for the reproduced semantic lint findings.

Matching key:

- `test_name`
- `file`
- `line`
- `validator_message`
- `context_sha256`

No wildcard path, directory-wide, docs-wide, or message-wide suppressions were added.

| Disposition | Count |
| --- | ---: |
| `preserve_doctrine_constant` | 213 |
| `preserve_fixture_literal` | 582 |
| `preserve_protocol_literal` | 264 |
| `preserve_schema_literal` | 45 |

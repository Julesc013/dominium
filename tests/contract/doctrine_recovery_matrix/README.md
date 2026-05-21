Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Doctrine Recovery Matrix Fixtures

These fixtures exercise
`tools/validators/contracts/check_doctrine_recovery_matrix.py`.

The fixture suite is contract-only. It does not change canon, planning law,
schema law, status files, generated mirrors, runtime behavior, Workbench
behavior, release policy, or protected roots.

Expected behavior:

- `valid_matrix_entry.json` passes focused entry validation.
- `invalid_entry_missing_review_gate.json` fails because every drift case must
  name its review gate.
- `invalid_entry_generated_promotes_canon.json` fails because generated or
  status evidence must not be promoted into canon.
- `invalid_registry_authority_order.json` fails because authority order must
  begin with constitution, glossary, and `AGENTS.md`.
- `invalid_registry_missing_protected_roots.json` fails because protected roots
  must include the required governance and generated-evidence set.

Run:

```text
py -3 tools/validators/contracts/check_doctrine_recovery_matrix.py --repo-root . --strict --fixtures
```

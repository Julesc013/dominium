Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# CompatX

CompatX validates compatibility contracts, migration registries, and schema version policy.

## Commands

- `python tools/compatx/compatx.py verify --repo-root .`
- `python tools/compatx/compatx.py schema-diff --repo-root . --old-schema <path> --new-schema <path>`
- `python tools/compatx/compatx.py migrate --repo-root . --migration-id <id> --input-json <path> --output-json <path>`
- `python tools/compatx/compatx.py save-replay-validate --repo-root .`
- `python tools/compatx/compatx.py pack-validate --repo-root .`

## Outputs

- Canonical baseline: `docs/audit/compat/COMPAT_BASELINE.json`
- Derived summary: `docs/audit/compat/COMPAT_BASELINE.md`


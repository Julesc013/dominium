Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Data-First Doctrine

## Scope

- Runtime behavior changes must be anchored in `schema/`, `data/`, registries, or documented mechanism-only annotations.
- RepoX enforces this through:
  - `DATA_FIRST_BEHAVIOR`
  - `NEW_FEATURE_REQUIRES_DATA_FIRST`
  - `SCHEMA_ANCHOR_REQUIRED`
  - `NO_SILENT_DEFAULTS`

## Compliance

- Add schema/manifest updates before adding or changing runtime behavior.
- If a change is mechanism-only, annotate file-level intent with `@repox:mechanism_only`.
- If an infrastructure-only runtime adjustment is unavoidable, annotate with `@repox:infrastructure_only`.
- Do not introduce optional reads that default silently; use explicit schema defaults or explicit refusal behavior.

## Exemptions

- Core invariants are non-exemptable.
- Non-core exemptions use `@repox:allow(<rule_id>) reason="..." expires="YYYY-MM-DD"` or `repo/repox/repox_exemptions.json`.
- Missing reason, missing expiry, or expired entries fail RepoX.

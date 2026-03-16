Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none
Stability: stable
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Data-First Doctrine

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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

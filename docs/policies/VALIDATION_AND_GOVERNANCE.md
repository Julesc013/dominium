Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Validation and Governance (GOV0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


This document describes the unified governance validator and how it is used
in CI and local workflows.

## How to run locally

Build tools and run the validator:

```
cmake --build build/msvc-base --target validate_all
build/msvc-base/bin/validate_all --repo-root=.
```

Optional outputs:

```
build/msvc-base/bin/validate_all --repo-root=. --json-out=validate_all.json --text-out=validate_all.txt
```

CI and scripted usage:

```
python tools/ci/validate_all.py --strict
```

## What it checks

- Schema spec metadata (Status/Version presence in `schema/**/SPEC_*.md`).
- Determinism safety markers (no float schema fields in descriptors).
- Performance safety markers (no unbounded list markers; render features have requires/fallback/cost).
- Provenance and non-fabrication markers (no fabricated population or loot flags).
- Rendering canon (backend directories and game references to backend APIs).
- Epistemic UI boundary (no authoritative includes or API calls in UI/tool code).

## Reports

The validator emits:
- Human-readable text summary (stdout or `--text-out`).
- JSON report (`--json-out`).

Each refusal includes:
- Rule ID
- File reference
- Remediation guidance

## Adding validators

1) Add a new check in `tools/validation/validators_registry.cpp`.
2) Use a GOV-* rule ID from `docs/ci/CI_ENFORCEMENT_MATRIX.md`.
3) Add a fixture under `tools/validation/fixtures/`.
4) Add a failing CTest entry in `tools/CMakeLists.txt`.
5) Document the check in this file and in the CI matrix.

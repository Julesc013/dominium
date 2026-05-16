Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# Internal Pilot Release 0

## Current Status

Internal Pilot Release 0 is locally staged and validated with warnings.

Generated local root:

```text
.dominium.local/releases/internal-pilot-0
```

This root is ignored local proof evidence. It is not a public release, GitHub release, tag, upload, installer, or package publication.

## Required Inputs

| Input | Status | Evidence |
| --- | --- | --- |
| Native binary proof | accepted with warnings | `docs/release/NATIVE_BINARY_PROOF.md` |
| Product boot proof | accepted with warnings | `docs/release/PRODUCT_BOOT_PROOF.md` |
| Portable projection proof | proven | `docs/release/PORTABLE_PROJECTION_PROOF.md` |
| Warning ledger | present | `.aide/reports/latest-warning-disposition.md` |

## Staging Layout

```text
.dominium.local/releases/internal-pilot-0/
  projection/
  manifest/internal_pilot_release.manifest.json
  manifest/provenance.json
  manifest/checksums.sha256
  proof/native_binary_proof.md
  proof/product_boot_proof.md
  proof/portable_projection_proof.md
  proof/warning_ledger.md
  proof/validation_report.json
  docs/README_INTERNAL_PILOT.md
  docs/RUNBOOK.md
  docs/ROLLBACK.md
```

## Regenerate Locally

```text
python tools/release/stage_internal_pilot.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --release-root .dominium.local/releases/internal-pilot-0
```

## Validate Locally

```text
python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --strict
```

## Current Warnings

- Full promotion CTest was not run for RELEASE-00.
- No public package, installer, tag, GitHub release, upload, or release publication was created.
- The staging tree remains generated ignored output and must not be committed.

## Relationship to DOE-00

DOE-00 may proceed with warnings. RELEASE-00 proves the current local build/product/projection evidence can be assembled into one self-describing internal pilot artifact with manifests, checksums, provenance, proof reports, warning ledger, runbook, and rollback notes.

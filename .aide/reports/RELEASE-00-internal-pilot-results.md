# RELEASE-00 Internal Pilot Results

## Status

Result: PASS_WITH_WARNINGS.

The internal pilot release proof tree was staged under the ignored local root:

```text
.dominium.local/releases/internal-pilot-0
```

The release staging root validates with no blockers. It is local proof evidence only and was not committed.

## Portable Projection Input

| Input | Status | Path |
| --- | --- | --- |
| Portable projection | accepted pass-with-warnings | `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium` |

## Required Contents

| Item | Present | Notes |
| --- | --- | --- |
| Internal pilot manifest | yes | `manifest/internal_pilot_release.manifest.json` |
| Provenance | yes | `manifest/provenance.json` |
| Checksums | yes | `manifest/checksums.sha256`, 4718 entries |
| Projection manifests | yes | install, release, and semantic contract registry manifests present |
| Native binaries | yes | setup, launcher, client, server, tools |
| Proof reports | yes | native binary, product boot, portable projection, warning ledger, latest status |
| Runbook and rollback docs | yes | generated local operator notes |

## Validation

| Command | Result |
| --- | --- |
| `python tools/release/stage_internal_pilot.py --repo-root . --projection-root .dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium --release-root .dominium.local/releases/internal-pilot-0` | PASS |
| `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0` | PASS |
| `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict` | PASS |

## Warnings

- Full promotion CTest was not run for RELEASE-00.
- No public release, installer, tag, upload, or package publication was created.
- The staging root is generated local evidence under `.dominium.local/` and remains uncommitted.

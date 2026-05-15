# AIDE-MOVE-01-PLAN Review

## What Would Move

- `ide/README.md` -> `docs/architecture/IDE_PROJECTIONS.md`

## Why

This is the smallest useful move from the ROOT-06 `ide` candidate. It removes one binding documentation file from the transitional `ide/` root while leaving generated IDE projections and authoritative manifest metadata in place.

## What Would Not Move

- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/**`
- Generated `ide/**` projection outputs
- Any high-risk roots or source/build/runtime files

## What Would Be Rewritten

Apply-phase rewrites are planned for `.gitignore`, `scripts/verify_docs_sanity.py`, `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`, the moved document content, and the AIDE selector wording. Generated architecture registries require review/regeneration rather than blind hand editing.

## Validators

Tier 0 AIDE, strict layout/root/distribution/component validators, docs sanity, build-boundary, UI-shell, ABI-boundary, and git diff checks are required before and after apply. No build, CTest, package, release, or product binary run is required for this docs-only move unless AIDE-GATE-02 escalates.

## Rollback

Rollback is a single reverse move plus reverse reference rewrites. No shim is planned.

## Gate Readiness

This plan is ready for `AIDE-GATE-02` review, but it is not approved for application.

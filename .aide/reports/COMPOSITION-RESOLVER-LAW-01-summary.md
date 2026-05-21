# COMPOSITION-RESOLVER-LAW-01 Summary

Status: PASS_WITH_WARNINGS

## Summary

COMPOSITION-RESOLVER-LAW-01 adds the first machine-readable composition law for
apps, profiles, packs, modules, providers, capabilities, policies, lockfiles,
reports, diagnostics, refusals, and evidence.

Composition is modeled as the product. Runtime composition resolution, package
mounting, provider runtime selection, module loading, Workbench UI, renderer,
platform backend, gameplay, and release publication remain non-goals.

## Changed Files

- `contracts/composition/**`
- `contracts/lock/**`
- `contracts/profile/**`
- selected public surface, artifact, capability, refusal, and diagnostic
  registries
- `tools/validators/contracts/check_composition_plan.py`
- `tests/contract/composition/**`
- `tests/contract/lock/**`
- `tests/contract/profile/**`
- composition architecture, development, Workbench, and audit docs
- `docs/architecture/CANON_INDEX.md`
- `docs/archive/audit/identity_fingerprint.json`
- `.aide/reports/COMPOSITION-RESOLVER-LAW-01-*`

## Schemas Added

- `composition_plan.schema.json`
- `composition_decision.schema.json`
- `profile_composition.schema.json`
- `app_composition_lock.schema.json`
- `pack_mount_lock.schema.json`
- `module_plan_lock.schema.json`
- `provider_selection_lock.schema.json`
- `capability_report.schema.json`
- `refusal_report.schema.json`
- `compatibility_report.schema.json`
- `trust_report.schema.json`

## Fixtures Added

Positive and negative fixtures cover plans, decisions, lockfiles, capability
reports, refusal reports, profile composition, unknown references, forbidden
silent overlays, missing fallback traces, missing provider capabilities,
path-as-identity, source-truth lockfile claims, and fixture-only support claims.

## Validation

Targeted composition checks passed. Related contract validators passed. Fast
strict passed after adding required `CANON_INDEX` entries and refreshing the
derived identity fingerprint.

Detailed evidence is in
`.aide/reports/COMPOSITION-RESOLVER-LAW-01-validation.json` and
`.aide/reports/COMPOSITION-RESOLVER-LAW-01-fast-strict.md`.

## Warnings

- RepoX reports existing stale AuditX output.
- Dependency-direction strict remains PASS with existing warnings and 0
  violations.
- The local `python` 3.8 invocation of the document patch transaction validator
  cannot parse an existing multi-line TOML contract; `py -3` passes.
- Full CTest was not run.

## Next

DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01.

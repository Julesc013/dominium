# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

`PUBLIC-SURFACE-REGISTRY-01`

Create Dominium's machine-readable public surface registry for public,
internal, generated, fixture, historical, and retired surfaces.

## WHY

Future Foundation Lock work must not create accidental public APIs, artifact
formats, command contracts, provider interfaces, schemas, release promises, or
Workbench descriptors. Most surfaces should start internal or provisional until
proof and compatibility policy justify stable promotion.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `contracts/testing/test_tiers.contract.toml`
- `.aide/context/latest-context-packet.md`
- `.aide/verification/latest-verification-report.md`

## ALLOWED_PATHS

- `contracts/public_surface/**`
- `docs/architecture/public_surface_registry.md`
- `docs/development/public_surface_guidelines.md`
- `tools/validators/repo/check_public_surface.py`
- `tests/contract/public_surface/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/POST_RESTRUCTURE_PROOF.md`
- `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- build/projection/release generated outputs
- product, gameplay, renderer, platform, native GUI, provider, Workbench UI, or package runtime implementation paths
- public API/ABI rewrites outside registry classification

## IMPLEMENTATION

- Add kind and stability registries.
- Add the initial conservative public surface TOML contract.
- Add a stdlib validator with Python 3.8 TOML fallback.
- Add validator fixtures and public-surface docs.
- Update AIDE/repo status evidence narrowly.
- Do not mark unproven surfaces stable.

## VALIDATION

- `python -m py_compile tools/validators/repo/check_public_surface.py`
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- `python tools/validators/repo/check_public_surface.py --repo-root . --json`
- `python tools/validators/repo/check_public_surface.py --repo-root . --fixture-dir tests/contract/public_surface/fixtures`
- JSON/schema parse for the public surface registries and reports
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/PUBLIC-SURFACE-REGISTRY-01-fast-strict.json --md-out .aide/reports/PUBLIC-SURFACE-REGISTRY-01-fast-strict.md`
- `git diff --check`

## COMMITS

- Commit the completed task with audit-grade body after validation.
- Do not amend, rebase, reset, or force push.

## EVIDENCE

- `contracts/public_surface/public_surface.contract.toml`
- `contracts/public_surface/surface.schema.json`
- `contracts/public_surface/surface_kind.registry.json`
- `contracts/public_surface/surface_stability.registry.json`
- `.aide/reports/PUBLIC-SURFACE-REGISTRY-01-*`
- `docs/repo/audits/PUBLIC_SURFACE_REGISTRY_01.md`

## NON_GOALS

- No gameplay, Workbench UI, renderer, native GUI, worldgen, package runtime, provider model, command implementation, ABI rewrite, release artifact, or compatibility corpus work.
- No false stable claims for unproven surfaces.

## ACCEPTANCE

- Registry contract and schema exist.
- Kind and stability registries exist.
- Validator and fixtures pass.
- Fast strict gate is run and recorded.
- Feature work remains blocked pending Foundation Lock.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created files, surface counts, validator status, fast strict
status, warnings, worktree status, and next task.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1050
- budget_status: PASS
- warnings:
  - none

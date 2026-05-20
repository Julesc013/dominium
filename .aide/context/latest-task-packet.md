# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `ARTIFACT-IDENTITY-LAW-01` by defining Dominium's artifact identity,
manifest, kind, lifecycle, hash, compatibility, trust, artifact-reference,
validator, fixture, documentation, and evidence surfaces.

## WHY

Packs, profiles, bundles, saves, replays, diagnostics, evidence packets, release
artifacts, schemas, registries, generated reports, Workbench descriptors, app
descriptors, and future modules must not be identified by paths or filenames.
They need stable IDs, schema/version metadata, hash policy, compatibility,
migration/refusal, trust, and provenance fields.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `contracts/testing/test_tiers.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/evidence/evidence_packet.schema.json`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/artifact/**`
- `contracts/evidence/**` for narrow artifact reference alignment
- `contracts/diagnostics/**` for artifact diagnostic codes
- `contracts/public_surface/**` for narrow registry cross-reference
- `docs/architecture/artifact_identity_law.md`
- `docs/development/artifact_identity_guidelines.md`
- `tools/validators/contracts/check_artifact_identity.py`
- `tests/contract/artifact_identity/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- narrow repo status docs

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- build, projection, release, installer, upload, cache, and generated output roots
- gameplay, renderer, Workbench UI, native GUI, package runtime, artifact
  loading, save/replay runtime, and product behavior paths

## IMPLEMENTATION

- Add artifact identity/hash/compatibility/trust contracts.
- Add artifact manifest/ref schemas, kind registry, and lifecycle registry.
- Add provisional artifact diagnostics.
- Add an artifact identity validator and fixture suite.
- Register artifact identity surfaces in public-surface governance.
- Inventory existing artifact-like surfaces without migrating them.
- Record evidence honestly, including existing dependency-direction debt.

## VALIDATION

- `python -m py_compile tools/validators/contracts/check_artifact_identity.py`
- JSON parse for created/touched schemas, registries, fixtures, and reports.
- TOML parse/fallback for artifact contracts.
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict`
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --json`
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_artifact_identity.py --repo-root . --inventory`
- diagnostics/command/public-surface/dependency-direction/ABI validators.
- strict repo/root/distribution/component validators.
- docs/build/UI/ABI supplemental checks.
- `python tools/test/run_fast_strict.py --repo-root .`
- git diff checks.

## TOKEN_ESTIMATE

Expected review packet size is under 1,200 tokens. Detailed artifact identity
and validation evidence lives in `.aide/reports/ARTIFACT-IDENTITY-LAW-01-*`.

## COMMITS

Commit subject: `audit(artifact): add artifact identity law`

## EVIDENCE

- `.aide/reports/ARTIFACT-IDENTITY-LAW-01-status.md`
- `.aide/reports/ARTIFACT-IDENTITY-LAW-01-validation.md`
- `.aide/reports/ARTIFACT-IDENTITY-LAW-01-results.json`
- `.aide/reports/ARTIFACT-IDENTITY-LAW-01-initial-artifact-inventory.md`
- `.aide/reports/ARTIFACT-IDENTITY-LAW-01-fast-strict.json`
- `.aide/reports/ARTIFACT-IDENTITY-LAW-01-fast-strict.md`
- `docs/repo/audits/ARTIFACT_IDENTITY_LAW_01.md`

## NON_GOALS

No artifact loading, save/replay/package runtime, Workbench UI, compatibility
corpus, schema/protocol law, provider model, module composition, release
publication, tag, upload, or full CTest proof.

## ACCEPTANCE

Artifact identity law and validator exist, fixtures pass, initial artifact
diagnostics and public-surface entries are provisional and honest, surrounding
validators run, and feature work stays blocked pending Foundation Lock.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created contracts/schemas/docs/tools, artifact kind/lifecycle
counts, fixture status, inventory summary, public-surface update status,
diagnostics update status, validator status, fast strict status, known warnings,
worktree status, and next task.

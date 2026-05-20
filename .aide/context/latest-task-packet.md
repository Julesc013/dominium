# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `DEPENDENCY-DIRECTION-01` by defining Dominium's repository
dependency-direction law, validator, fixtures, documentation, public-surface
registration, and evidence.

## WHY

Canonical roots must not decay into new junk drawers after cleanup. Engine,
runtime, game, apps, contracts, content, tools, tests, release, and archive need
mechanically enforced dependency direction before feature work resumes.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `contracts/testing/test_tiers.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/abi/c_api.contract.toml`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/repo/dependency_directions.contract.toml`
- `contracts/repo/dependency_direction.schema.json`
- `contracts/repo/dependency_direction_exceptions.toml`
- `docs/architecture/dependency_direction_law.md`
- `docs/development/dependency_direction_guidelines.md`
- `tools/validators/repo/check_dependency_directions.py`
- `tests/contract/dependency_direction/**`
- `contracts/public_surface/**` for narrow registry cross-reference
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- narrow repo status docs

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- build, projection, release, installer, upload, cache, and generated output roots
- gameplay, renderer, Workbench UI, native GUI, package runtime, and product behavior implementation paths

## IMPLEMENTATION

- Add dependency direction contract, schema, and exception ledger.
- Add a tracked-file dependency direction validator.
- Add dependency direction fixtures and docs.
- Register dependency direction surfaces in the public surface registry.
- Record initial scan evidence honestly, including current violations.

## VALIDATION

- `python -m py_compile tools/validators/repo/check_dependency_directions.py`
- JSON parse for schema and fixtures.
- TOML parse for contract and exceptions.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- `python tools/validators/abi/check_public_headers.py --repo-root . --strict`
- strict repo/root/distribution/component validators.
- docs/build/UI/ABI supplemental checks.
- `python tools/test/run_fast_strict.py --repo-root .`
- git diff checks.

## TOKEN_ESTIMATE

Expected review packet size is under 1,200 tokens. Evidence files carry detailed
scan output so the prompt packet can remain compact.

## COMMITS

Commit subject: `audit(repo): add dependency direction law`

## EVIDENCE

- `.aide/reports/DEPENDENCY-DIRECTION-01-status.md`
- `.aide/reports/DEPENDENCY-DIRECTION-01-validation.md`
- `.aide/reports/DEPENDENCY-DIRECTION-01-results.json`
- `.aide/reports/DEPENDENCY-DIRECTION-01-initial-scan.md`
- `.aide/reports/DEPENDENCY-DIRECTION-01-initial-scan.json`
- `.aide/reports/DEPENDENCY-DIRECTION-01-fast-strict.json`
- `.aide/reports/DEPENDENCY-DIRECTION-01-fast-strict.md`
- `docs/repo/audits/DEPENDENCY_DIRECTION_01.md`

## NON_GOALS

No feature implementation, command surface contract, provider model,
compatibility corpus, package runtime change, Workbench UI work, public release,
tag, upload, or full CTest proof.

## ACCEPTANCE

Dependency law and validator exist, initial scan debt is recorded without broad
exceptions, surrounding governance validators run, and feature work stays blocked
pending Foundation Lock.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created files, roots/files scanned, violations/warnings,
validator status, fast strict status, worktree status, and next task.

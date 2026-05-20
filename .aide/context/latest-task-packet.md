# AIDE Task Packet

## PHASE

Foundation Lock.

## GOAL

Define Dominium's schema, registry, protocol, canonical serialization,
migration, and refusal evolution law without implementing runtime migration or
feature behavior.

## WHY

Durable data contracts must not change silently. Schemas, protocols,
registries, manifests, command/result formats, evidence packets, provider
descriptors, app/module descriptors, saves, replays, packs, and profiles need
explicit ID, version, compatibility, default, migration, and refusal policy.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/artifact/artifact_identity.contract.toml`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/public_surface/public_surface.contract.toml`
- `tools/test/run_fast_strict.py`

## ALLOWED_PATHS

- `contracts/schema/**`
- `contracts/protocol/**`
- `contracts/registry/**`
- `contracts/serialization/**`
- `contracts/migration/**`
- narrow cross-references under `contracts/artifact/**`, `contracts/diagnostics/**`, and `contracts/public_surface/**`
- `docs/architecture/schema_protocol_evolution.md`
- `docs/development/schema_protocol_guidelines.md`
- `tools/validators/contracts/check_schema_protocol_evolution.py`
- `tests/contract/schema_protocol/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- repo status docs

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- generated build/projection/release outputs
- runtime migration/product implementation files
- Workbench UI, gameplay, renderer, package/save/replay loader code

## IMPLEMENTATION

Add provisional law contracts, JSON schemas, policy registries, validator,
fixtures, documentation, public-surface registration, diagnostics integration,
inventory, AIDE status, and audit evidence.

## VALIDATION

Run schema/protocol validator strict/json/fixtures/inventory, parse touched
JSON/TOML, run related governance validators, run fast strict, and run git diff
checks. Full CTest remains T4 full/release proof and is not required.

## EVIDENCE

- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-status.md`
- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-validation.md`
- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-results.json`
- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-initial-schema-protocol-inventory.md`
- `.aide/reports/SCHEMA-PROTOCOL-LAW-01-fast-strict.md`
- `docs/repo/audits/SCHEMA_PROTOCOL_LAW_01.md`

## NON_GOALS

- No schema migration runtime.
- No protocol runtime.
- No package/save/replay loading behavior.
- No Workbench UI.
- No gameplay/domain/renderer/native GUI work.
- No broad rewrite of existing schemas.
- No compatibility corpus.

## ACCEPTANCE

Schema/protocol law exists, validator passes, fixtures pass, public-surface and
diagnostics integration validates, inventory is recorded, fast strict passes,
and the next task is `CAPABILITY-REFUSAL-LAW-01`.

## OUTPUT_SCHEMA

Result evidence follows `.aide/reports/SCHEMA-PROTOCOL-LAW-01-results.json`.

## TOKEN_ESTIMATE

Compact packet under 1,600 tokens.

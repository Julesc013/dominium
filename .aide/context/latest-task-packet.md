# AIDE Latest Task Packet

## PHASE

foundation-lock

## TASK

`MOD-PACK-TRUST-MODEL-01`

## GOAL

Define Dominium's mod/pack trust law for content packs, profile/theme/UI/module
packs, Workbench-authored modules, external process adapters, native providers,
permissions, sandbox expectations, review, deterministic impact, overlay policy,
diagnostics, refusals, and evidence.

## WHY

Dominium needs pack-driven extension without silent authority expansion,
unreviewed native code, hidden external adapters, undeclared permissions,
nondeterministic replay behavior, or silent content overwrites.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `contracts/capability/capability.contract.toml`
- `contracts/provider/provider.contract.toml`
- `contracts/module/module.schema.json`
- `contracts/replacement/replacement.contract.toml`
- `contracts/versioning/versioning.contract.toml`
- `.aide/reports/MOD-PACK-TRUST-MODEL-01-validation.md`

## SCOPE

- `contracts/trust/**`
- `contracts/modding/**`
- `tools/validators/package/check_mod_pack_trust.py`
- `tests/contract/mod_pack_trust/**`
- `docs/architecture/mod_pack_trust_model.md`
- `docs/development/mod_pack_trust_guidelines.md`
- `docs/modding/trust_ladder.md`
- `.aide/reports/MOD-PACK-TRUST-MODEL-01-*`
- `docs/repo/audits/MOD_PACK_TRUST_MODEL_01.md`
- narrow registry/status updates for diagnostics, refusals, capabilities, public
  surfaces, repo status, and AIDE status.

## ALLOWED_PATHS

- `contracts/trust/**`
- `contracts/modding/**`
- `tools/validators/package/check_mod_pack_trust.py`
- `tests/contract/mod_pack_trust/**`
- `docs/architecture/mod_pack_trust_model.md`
- `docs/development/mod_pack_trust_guidelines.md`
- `docs/modding/trust_ladder.md`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/migration_ledger.jsonl`
- `docs/repo/**`
- narrow registry updates named by the task.

## FORBIDDEN_PATHS

- `.aide.local/**`
- `.dominium.local/**`
- generated build/projection/release outputs
- runtime loader, sandbox, provider runtime, Workbench UI, gameplay, renderer,
  native GUI, release publication, and product behavior implementation paths.

## IMPLEMENTATION

Define contracts, registries, schemas, fixtures, validator, docs, evidence, and
registry cross-references only. Inventory existing packs descriptively and do
not migrate current manifests.

## NON_GOALS

No mod loader, scripting runtime, sandbox runtime, native plugin loader, dynamic
loader, provider runtime, package/profile mounting, Workbench UI, gameplay,
renderer, native GUI, release publication, or product behavior.

## VALIDATION

- `python tools/validators/package/check_mod_pack_trust.py --repo-root . --strict`
- `python tools/validators/package/check_mod_pack_trust.py --repo-root . --fixtures`
- `python tools/validators/package/check_mod_pack_trust.py --repo-root . --inventory`
- cross-contract validators for versioning, replacement, module/workbench/app,
  provider, capability/refusal, schema/protocol, artifact, diagnostics, command,
  public surface, dependency direction, and ABI.
- fast strict gate evidence:
  `.aide/reports/MOD-PACK-TRUST-MODEL-01-fast-strict.md`

## EVIDENCE

- `.aide/reports/MOD-PACK-TRUST-MODEL-01-status.md`
- `.aide/reports/MOD-PACK-TRUST-MODEL-01-validation.md`
- `.aide/reports/MOD-PACK-TRUST-MODEL-01-results.json`
- `.aide/reports/MOD-PACK-TRUST-MODEL-01-initial-trust-inventory.md`
- `.aide/reports/MOD-PACK-TRUST-MODEL-01-fast-strict.md`

## ACCEPTANCE

- trust contracts and registries exist;
- validator strict/json/fixtures pass;
- inventory is recorded without migration;
- public surface, diagnostics, refusal, and capability registries are updated;
- fast strict passes;
- next task is `PORTABILITY-MATRIX-01`.

## OUTPUT_SCHEMA

Result status: `PASS_WITH_WARNINGS`

Next task: `PORTABILITY-MATRIX-01`

## TOKEN_ESTIMATE

Compact packet; under 1,200 tokens.

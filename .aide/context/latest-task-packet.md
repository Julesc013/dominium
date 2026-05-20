# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `REPLACEMENT-PROTOCOL-01` by adding replacement protocol contracts,
replacement packet/impact/proof schemas, replacement kind/status registries,
rollback/conformance/migration-refusal policies, validator, fixtures, docs,
public-surface registration, diagnostics/refusal cross-references, inventory,
and evidence.

## WHY

Dominium must allow safe replacement while forbidding silent breakage.
Implementations, providers, modules, schemas, protocols, artifact formats,
command handlers, validators, and directory-owned surfaces need governed
packets with proof, rollback, migration/refusal behavior, diagnostics, and
evidence.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/replacement/replacement.contract.toml`
- `contracts/replacement/replacement_packet.schema.json`
- `contracts/replacement/replacement_kind.registry.json`
- `contracts/replacement/replacement_status.registry.json`
- `contracts/replacement/rollback_policy.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/provider/provider.contract.toml`
- `contracts/module/module.schema.json`
- `contracts/artifact/artifact_identity.contract.toml`
- `contracts/schema/schema_evolution.contract.toml`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/replacement/**`
- narrow `contracts/public_surface/**`, `contracts/diagnostics/**`, and
  `contracts/refusal/**` registry updates
- `docs/architecture/replacement_protocol.md`
- `docs/development/replacement_protocol_guidelines.md`
- `tools/validators/repo/check_replacement_packet.py`
- `tests/contract/replacement/**`
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
- generated build/projection/release outputs
- implementation replacements or broad directory moves
- migration runtime or rollback runtime
- provider runtime, Workbench UI, app behavior, gameplay, renderer, native GUI,
  package runtime, release publication, tags, installers, or GitHub settings

## IMPLEMENTATION

- Define replacement law only; do not perform an actual replacement.
- Keep packet identity independent from implementation paths.
- Register only provisional public surfaces.
- Inventory historical replacement evidence without retrofitting full packets.

## VALIDATION

- `python -m py_compile tools/validators/repo/check_replacement_packet.py`
- `python tools/validators/repo/check_replacement_packet.py --repo-root . --strict`
- `python tools/validators/repo/check_replacement_packet.py --repo-root . --fixtures`
- `python tools/validators/repo/check_replacement_packet.py --repo-root . --inventory`
- Existing module/workbench/app, provider, capability/refusal, schema/protocol,
  artifact, diagnostics, command, public-surface, dependency-direction, and ABI
  validators where present
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/REPLACEMENT-PROTOCOL-01-fast-strict.json --md-out .aide/reports/REPLACEMENT-PROTOCOL-01-fast-strict.md`
- `git diff --check`

## EVIDENCE

- `.aide/reports/REPLACEMENT-PROTOCOL-01-status.md`
- `.aide/reports/REPLACEMENT-PROTOCOL-01-validation.md`
- `.aide/reports/REPLACEMENT-PROTOCOL-01-results.json`
- `.aide/reports/REPLACEMENT-PROTOCOL-01-initial-replacement-inventory.md`
- `docs/repo/audits/REPLACEMENT_PROTOCOL_01.md`

## NON_GOALS

- No actual rewrite, replacement, migration, rollback, runtime loader, provider
  resolver, Workbench UI, app behavior, release output, or broad directory move.

## ACCEPTANCE

- Replacement protocol files exist.
- Validator passes strict and fixture modes.
- Public surface, diagnostics, and refusal registries validate.
- Fast strict proof is recorded.
- Next task is `VERSION-DEPRECATION-LAW-01`.

## OUTPUT_SCHEMA

Return a compact final report with branch, starting HEAD, ending HEAD,
origin/main, pushed status, result status, created files, replacement kind/status
counts, fixture validation, inventory summary, registry updates, validator
status, fast strict status, known warnings, worktree status, and next task.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4498
- approx_tokens: 1125
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`

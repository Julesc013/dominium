# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `CAPABILITY-REFUSAL-LAW-01` by adding capability/refusal contracts,
schemas, registries, validator, fixtures, docs, public-surface registration,
diagnostic/command cross-references, and evidence.

## WHY

Dominium must represent missing providers, unsupported platforms, invalid
artifacts, unavailable modules, and degraded optional systems as typed,
machine-readable capability decisions and refusals. Silent fallback and
free-text-only refusals remain forbidden.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/capability/capability.contract.toml`
- `contracts/refusal/refusal.contract.toml`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/command/command_surface.contract.toml`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/public_surface/public_surface.contract.toml`
- `docs/architecture/capability_refusal_law.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/capability/**`
- `contracts/refusal/**`
- `contracts/diagnostics/**` for narrow diagnostic additions
- `contracts/command/**` for narrow capability/refusal cross-references
- `contracts/public_surface/**` for conservative registration
- `docs/architecture/capability_refusal_law.md`
- `docs/development/capability_refusal_guidelines.md`
- `tools/validators/contracts/check_capability_refusal.py`
- `tests/contract/capability_refusal/**`
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
- runtime provider resolver implementation
- renderer/platform fallback implementation
- package/mod trust runtime implementation
- Workbench UI implementation
- gameplay/domain/renderer/native GUI feature code
- release publication, tags, installers, or GitHub settings

## IMPLEMENTATION

- Keep the task to governance, validation, fixtures, docs, and evidence.
- Define capability IDs, kinds, request/decision schemas, degradation/recovery
  policy, and refusal semantics.
- Merge refusal and diagnostic codes without renaming existing codes.
- Register only conservative provisional surfaces.
- Inventory current provider/capability candidates without migrating them.

## VALIDATION

- `python -m py_compile tools/validators/contracts/check_capability_refusal.py`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --json`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --inventory`
- Existing schema/protocol, artifact, diagnostics, command, public-surface, dependency-direction, and ABI validators where present
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/CAPABILITY-REFUSAL-LAW-01-fast-strict.json --md-out .aide/reports/CAPABILITY-REFUSAL-LAW-01-fast-strict.md`
- `git diff --check`

## EVIDENCE

- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-status.md`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-validation.md`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-results.json`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-initial-capability-inventory.md`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-fast-strict.md`
- `.aide/reports/CAPABILITY-REFUSAL-LAW-01-fast-strict.json`
- `docs/repo/audits/CAPABILITY_REFUSAL_LAW_01.md`

## NON_GOALS

- No provider runtime.
- No runtime capability resolver.
- No renderer/platform fallback.
- No package/mod trust runtime.
- No Workbench UI.
- No gameplay/domain/renderer/native GUI feature behavior.
- No release publication.
- No full CTest claim.

## ACCEPTANCE

- Capability/refusal validator compiles and passes strict mode.
- Fixture mode passes.
- Inventory mode reports candidates descriptively without migrating them.
- Public surface, diagnostics, and command contracts remain valid.
- Fast strict passes.
- Evidence and audit records are written.
- Worktree excludes local/generated forbidden outputs.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created contracts/schemas/docs/tools, registered capability and
refusal counts, fixture and inventory status, registry updates, validator
status, fast strict status, known warnings, worktree status, and next task.

## TOKEN_ESTIMATE

- method: bounded task packet
- approx_tokens: 1200
- budget_status: PASS

# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `PROVIDER-MODEL-01` by adding provider contracts, descriptor and
selection schemas, provider kind and lifecycle registries, conformance,
capability, and trust policies, validator, fixtures, docs, public-surface
registration, diagnostics/refusal/capability cross-references, and evidence.

## WHY

Dominium must make renderers, platforms, storage backends, package/profile
loaders, Workbench modules, external adapters, and future native providers
replaceable through typed provider identity, capability declarations, selection
decisions, refusals, degradation records, diagnostics, and conformance proof.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/provider/provider.contract.toml`
- `contracts/provider/provider.registry.json`
- `contracts/provider/provider_descriptor.schema.json`
- `contracts/provider/provider_selection_request.schema.json`
- `contracts/provider/provider_selection_decision.schema.json`
- `contracts/capability/capability.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/public_surface/public_surface.contract.toml`
- `docs/architecture/provider_model.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/provider/**`
- `contracts/capability/**` for narrow provider/capability cross-references
- `contracts/refusal/**` for narrow provider refusal additions
- `contracts/diagnostics/**` for narrow provider diagnostic additions
- `contracts/public_surface/**` for conservative registration
- `docs/architecture/provider_model.md`
- `docs/development/provider_guidelines.md`
- `tools/validators/contracts/check_provider_model.py`
- `tests/contract/provider/**`
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
- provider runtime resolver implementation
- plugin or dynamic loader implementation
- renderer/platform fallback implementation
- package/profile loader runtime behavior
- Workbench UI implementation
- gameplay/domain/renderer/native GUI feature code
- release publication, tags, installers, or GitHub settings

## IMPLEMENTATION

- Keep the task to governance, validation, fixtures, docs, and evidence.
- Define provider IDs, kinds, lifecycle, descriptors, selection request and
  decision schemas, conformance, capability, and trust policies.
- Register only conservative provisional provider descriptors.
- Merge provider diagnostic and refusal codes without renaming existing codes.
- Inventory current backend/provider-like surfaces without migrating them.

## VALIDATION

- `python -m py_compile tools/validators/contracts/check_provider_model.py`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --strict`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --json`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_provider_model.py --repo-root . --json --inventory`
- Existing capability/refusal, schema/protocol, artifact, diagnostics, command,
  public-surface, dependency-direction, and ABI validators where present
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/PROVIDER-MODEL-01-fast-strict.json --md-out .aide/reports/PROVIDER-MODEL-01-fast-strict.md`
- `git diff --check`

## EVIDENCE

- `.aide/reports/PROVIDER-MODEL-01-status.md`
- `.aide/reports/PROVIDER-MODEL-01-validation.md`
- `.aide/reports/PROVIDER-MODEL-01-results.json`
- `.aide/reports/PROVIDER-MODEL-01-initial-provider-inventory.md`
- `.aide/reports/PROVIDER-MODEL-01-fast-strict.md`
- `.aide/reports/PROVIDER-MODEL-01-fast-strict.json`
- `docs/repo/audits/PROVIDER_MODEL_01.md`

## NON_GOALS

- No provider runtime.
- No dynamic loader.
- No renderer/platform fallback.
- No package/profile loader runtime behavior.
- No Workbench UI.
- No gameplay/domain/renderer/native GUI feature behavior.
- No release publication.
- No full CTest claim.

## ACCEPTANCE

- Provider validator compiles and passes strict mode.
- Fixture mode passes.
- Inventory mode reports candidates descriptively without migrating them.
- Public surface, diagnostics, refusal, and capability registries remain valid.
- Fast strict passes.
- Evidence and audit records are written.
- Worktree excludes local/generated forbidden outputs.

## TOKEN_ESTIMATE

~1.3k tokens.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created contracts/schemas/docs/tools, provider kind and
lifecycle counts, fixture and inventory status, registry updates, validator
status, fast strict status, known warnings, worktree status, and next task.

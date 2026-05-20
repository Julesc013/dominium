# AIDE Latest Task Packet

## PHASE

foundation-lock

## GOAL

Complete `MODULE-COMPOSITION-LAW-01` by adding module, Workbench workspace, and
app composition contracts, schemas, validators, fixtures, docs, public-surface
registration, diagnostics/capability cross-references, and evidence.

## WHY

Dominium must distinguish component, service, provider, pack, module,
workspace, app, and artifact. Module identity must come from descriptors, not
folders, executable names, Workbench layout files, or private tool wiring.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/module/module_surface.contract.toml`
- `contracts/module/module.schema.json`
- `contracts/workbench/workspace.schema.json`
- `contracts/app/app_descriptor.schema.json`
- `contracts/command/command_surface.contract.toml`
- `contracts/capability/capability.registry.json`
- `contracts/provider/provider.registry.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/public_surface/public_surface.contract.toml`
- `docs/architecture/module_composition_law.md`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `contracts/module/**`
- `contracts/workbench/**`
- `contracts/app/**`
- `contracts/diagnostics/**` for narrow diagnostic additions
- `contracts/capability/**` for narrow capability additions
- `contracts/public_surface/**` for conservative registration
- `docs/architecture/module_composition_law.md`
- `docs/architecture/workbench_workspace_model.md`
- `docs/architecture/app_composition_model.md`
- `docs/development/module_development_guidelines.md`
- `docs/development/workbench_module_guidelines.md`
- `tools/validators/contracts/check_module_descriptors.py`
- `tools/validators/contracts/check_workbench_workspaces.py`
- `tools/validators/contracts/check_app_descriptors.py`
- `tests/contract/module/**`
- `tests/contract/workbench/**`
- `tests/contract/app/**`
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
- Workbench UI implementation
- runtime module loader implementation
- app composer implementation
- pack runtime or module discovery runtime
- provider runtime
- gameplay/domain/renderer/native GUI feature code
- release publication, tags, installers, or GitHub settings

## IMPLEMENTATION

- Keep the task to governance, validation, fixtures, docs, and evidence.
- Define module descriptors, module composition, module kinds, Workbench
  workspace/panel/view-binding schemas, app descriptors, and app composition.
- Register only conservative provisional surfaces.
- Inventory current app/workbench/module-like surfaces without migrating them.

## VALIDATION

- `python -m py_compile tools/validators/contracts/check_module_descriptors.py tools/validators/contracts/check_workbench_workspaces.py tools/validators/contracts/check_app_descriptors.py`
- `python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict`
- `python tools/validators/contracts/check_module_descriptors.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict`
- `python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --fixtures`
- `python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict`
- `python tools/validators/contracts/check_app_descriptors.py --repo-root . --fixtures`
- Existing provider, capability/refusal, schema/protocol, artifact,
  diagnostics, command, public-surface, dependency-direction, and ABI validators
  where present
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/MODULE-COMPOSITION-LAW-01-fast-strict.json --md-out .aide/reports/MODULE-COMPOSITION-LAW-01-fast-strict.md`
- `git diff --check`

## EVIDENCE

- `.aide/reports/MODULE-COMPOSITION-LAW-01-status.md`
- `.aide/reports/MODULE-COMPOSITION-LAW-01-validation.md`
- `.aide/reports/MODULE-COMPOSITION-LAW-01-results.json`
- `.aide/reports/MODULE-COMPOSITION-LAW-01-initial-module-inventory.md`
- `.aide/reports/MODULE-COMPOSITION-LAW-01-fast-strict.md`
- `.aide/reports/MODULE-COMPOSITION-LAW-01-fast-strict.json`
- `docs/repo/audits/MODULE_COMPOSITION_LAW_01.md`

## NON_GOALS

- No runtime module loader.
- No Workbench UI.
- No App Composer.
- No pack runtime or module discovery runtime.
- No provider runtime.
- No gameplay/domain/renderer/native GUI feature behavior.
- No release publication.
- No full CTest claim.

## ACCEPTANCE

- Module, Workbench, and app validators compile and pass strict mode.
- Fixture modes pass.
- Inventory modes report candidates descriptively without migrating them.
- Public surface, diagnostics, capability, provider, and command registries remain valid.
- Fast strict passes.
- Evidence and audit records are written.
- Worktree excludes local/generated forbidden outputs.

## TOKEN_ESTIMATE

~1.3k tokens.

## OUTPUT_SCHEMA

Final report includes branch, starting HEAD, ending HEAD, origin/main, push
status, result, created contracts/schemas/docs/tools, module kind count, fixture
and inventory status, registry updates, validator status, fast strict status,
known warnings, worktree status, and next task.

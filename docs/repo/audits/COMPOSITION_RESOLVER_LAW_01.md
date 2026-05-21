Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: COMPOSITION-RESOLVER-LAW-01
Result: PASS_WITH_WARNINGS

# COMPOSITION_RESOLVER_LAW_01 Audit

## Scope

This task defines composition resolver law for app, profile, pack, module,
provider, capability, trust, compatibility, lockfile, report, diagnostic,
refusal, and evidence surfaces.

It is contract, docs, validator, and fixture work only.

## Artifacts

- `contracts/composition/**`
- `contracts/lock/**`
- `contracts/profile/**`
- selected public surface, artifact, capability, refusal, and diagnostic
  registry entries for composition law
- `tools/validators/contracts/check_composition_plan.py`
- `tests/contract/composition/**`
- `tests/contract/lock/**`
- `tests/contract/profile/**`
- architecture, development, and Workbench docs
- `docs/archive/audit/identity_fingerprint.json` refreshed after the required
  `docs/architecture/CANON_INDEX.md` entries

## Invariants Upheld

- `docs/canon/constitution_v1.md`: deterministic order, process-only mutation,
  law-gated authority, pack-driven integration, truth/perceived/render
  separation, and contract compatibility discipline.
- `docs/canon/glossary_v1.md`: app, profile, pack, module, provider,
  capability, refusal, report, evidence, and lockfile terms keep canonical
  meaning.
- `AGENTS.md`: extend over replace, no silent drift, no path-as-identity, no
  runtime implementation in a contract/docs/validator slice, and honest
  validation reporting.
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`: ownership-sensitive pack,
  schema, planning, and projection roots are not collapsed.

## Contract And Schema Impact

Added provisional composition plan, decision, status, plan kind, deterministic
order policy, overlay conflict policy, report kind, profile composition, and
lock/report schemas.

Added provisional registry entries for composition diagnostics, refusals,
capability exposure, artifact kinds, and public surfaces. Existing app, module,
Workbench, provider, package, trust, release, runtime, and product launch
behavior was not changed.

## Lock And Report Types

- `app_composition.lock.json`
- `pack_mount.lock.json`
- `module_plan.lock.json`
- `provider_selection.lock.json`
- `capability_report.json`
- `refusal_report.json`
- `compatibility_report.json`
- `trust_report.json`

Checked-in schemas describe these artifact shapes under `contracts/lock/**`.
Lockfiles are derived evidence and are not source truth.

## Validator And Fixtures

Added `tools/validators/contracts/check_composition_plan.py`.

The fixture suite proves valid plan, decision, app composition lock, pack mount
lock, module plan lock, provider selection lock, capability report, refusal
report, compatibility report, trust report, and profile composition behavior.
Negative fixtures prove unknown references, silent overlay overwrite refusal,
degraded fallback trace requirements, provider capability requirements,
path-as-identity rejection, lockfile source-truth rejection, fixture-only
support-claim rejection, and refusal diagnostic/code requirements.

## Non-Goals

No runtime composition resolver, package mounting, provider resolver, module
loader, Workbench shell/UI, renderer, platform backend, gameplay, native GUI,
release publication, or product launch behavior is implemented.

## Validation

Recorded evidence:

- `.aide/reports/COMPOSITION-RESOLVER-LAW-01-summary.md`
- `.aide/reports/COMPOSITION-RESOLVER-LAW-01-validation.json`
- `.aide/reports/COMPOSITION-RESOLVER-LAW-01-fast-strict.json`
- `.aide/reports/COMPOSITION-RESOLVER-LAW-01-fast-strict.md`
- `.aide/reports/COMPOSITION-RESOLVER-LAW-01-repox-proof-manifest.json`
- `.aide/reports/COMPOSITION-RESOLVER-LAW-01-repox-profile.json`

Key results:

- `python -m py_compile tools/validators/contracts/check_composition_plan.py`:
  PASS.
- `python tools/validators/contracts/check_composition_plan.py --repo-root . --strict`:
  PASS, 0 errors, 0 warnings, 23 fixtures.
- `python tools/validators/contracts/check_composition_plan.py --repo-root . --json`:
  PASS.
- `python tools/validators/contracts/check_composition_plan.py --repo-root . --fixtures`:
  PASS, 23 fixtures.
- `python tools/validators/contracts/check_composition_plan.py --repo-root . --inventory`:
  PASS with descriptive inventory warning.
- Related app, module, Workbench, provider, capability/refusal, diagnostics,
  command, artifact, schema/protocol, project graph service, service
  conformance, replacement packet, version/deprecation, mod pack trust,
  portability, public surface, dependency direction, component matrix, docs,
  build boundary, UI shell, and ABI checks passed.
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/COMPOSITION-RESOLVER-LAW-01-fast-strict.json --md-out .aide/reports/COMPOSITION-RESOLVER-LAW-01-fast-strict.md`:
  PASS, 33 commands.
- `git diff --check`: PASS.

Warnings:

- RepoX still reports stale AuditX output:
  `INV-AUDITX-OUTPUT-STALE`.
- Dependency-direction strict remains PASS with existing warnings and 0
  violations.
- `python tools/validators/contracts/check_document_patch_transactions.py --repo-root . --strict`
  fails under the local `python` 3.8 fallback TOML parser on an existing
  multi-line-array contract outside this task's edit scope; the same validator
  passes with `py -3`.
- Full CTest was not run; fast strict ran `t2.ctest_smoke`.
- Runtime composition resolver, package mount runtime, provider resolver, and
  module loader remain future work.

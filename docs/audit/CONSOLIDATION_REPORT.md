Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Consolidation Report

## Scope
- Lock structural contracts for lens governance, AuthorityContext enforcement, material/tool/process foundations, survival vertical slice scaffolding, and profile/bundle stress coverage.
- Keep runtime semantics unchanged and keep survival behavior profile-driven (law + experience + parameter bundles).

## Consolidation Status
- Phase 1 (Lens system): Complete.
  - `schema/lens/lens.schema` defines diegetic vs nondiegetic lens contracts.
  - `data/registries/lenses.json` includes required baseline lenses.
  - `schema/law/law_profile.schema` and `data/registries/law_profiles.json` enforce survival diegetic allowlist + nondiegetic forbids.
  - RepoX invariant present: `INV-SURVIVAL-NO-NONDIEGETIC-LENSES`.
  - AuditX analyzer present: `C7_LENS_BYPASS_SMELL` (`tools/auditx/analyzers/c7_lens_bypass_smell.py`).
- Phase 2 (AuthorityContext enforcement): Complete.
  - RepoX invariants present: `INV-AUTHORITY-CONTEXT-REQUIRED`, `INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS`.
  - Intent/dispatch refusal paths include authority-context checks in client/server wiring.
  - TestX coverage present: `test_intent_without_authority_refused`, `test_survival_no_console`, `test_survival_no_freecam`, `test_server_rejects_capability_escalation`.
- Phase 3 (Affordance/material foundation): Complete.
  - Schemas present: `schema/material/material.schema`, `schema/tool/tool_capability.schema`, `schema/process/process_requirement.schema`.
  - Registries present: `data/registries/materials.json`, `data/registries/tool_capabilities.json`, `data/registries/process_requirements.json`.
  - Required structural process ids present: gather/craft/build/consume baseline set.
- Phase 4 (Minimal survival vertical slice): Complete (scaffolding level).
  - `data/registries/survival_vertical_slice.json` defines required agent/world fields, shelter assembly, and process list.
  - `data/registries/parameter_bundles.json` includes `survival.params.default` and `survival.params.harsh`.
  - `data/registries/experience_profiles.json` binds survival and hardcore profiles through law + parameter deltas.
  - TestX coverage present: `test_need_decay_deterministic`, `test_shelter_reduces_exposure`, `test_death_persists`, `test_hardcore_no_respawn`.
- Phase 5 (Profile switch + bundle removal stress): Complete.
  - Systemic suite present via `tests/systemic/profile_bundle_stress_suite.py`.
  - CTest entries present for:
    - `test_profile_switch_requires_restart`
    - `test_remove_optional_bundle_core_boots`
    - `test_survival_to_creative_transition`
    - `test_survival_hardcore_delta_only`
    - `test_bundle_not_installed_refusal`
- Phase 6 (Diegetic survival contract): Complete.
  - RepoX invariant present: `INV-SURVIVAL-DIEGETIC-CONTRACT`.
  - TestX coverage present: `test_survival_diegetic_only`.
  - Survival law profiles forbid nondiegetic console/debug/freecam lenses and preserve diegetic-only access markers.

## Validation Executed
- Gate precheck: `python scripts/dev/gate.py precheck --trace --profile-report` -> PASS.
- Strict exitcheck: `python scripts/dev/gate.py exitcheck --strict --trace --profile-report` -> PASS.
- Full gate profile: `python scripts/dev/gate.py full --trace --profile-report` -> PASS.
- AuditX scan: `python tools/auditx/auditx.py scan --format both` -> PASS; analyzers include:
  - `C2_MODE_FLAG_SMELL`
  - `C4_TERMINOLOGY_MISUSE`
  - `C6_AUTHORITY_BYPASS_SMELL`
  - `C7_LENS_BYPASS_SMELL`
- Direct monolithic `testx_all` build target attempt exceeded local command timeout; validation continued through shard-based gate full profile and strict exitcheck with successful completion.

## Determinism/Contract Notes
- This consolidation pass is structural and data-contract focused.
- No new simulation primitives were introduced.
- Existing profile-driven selection remains the source of survival/creative/hardcore deltas.

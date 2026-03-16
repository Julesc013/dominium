Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: CIV-4/4 demography optionality baseline
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Demography Optionality Baseline

## Policies Supported
- Demography policy registry:
  - `demo.policy.none`
  - `demo.policy.stable_no_birth`
  - `demo.policy.basic_births`
- Model registries:
  - `death_model_registry`
  - `birth_model_registry`
  - `migration_model_registry`
- Law and parameter integration:
  - law-gated `process.demography_tick`
  - law birth override support (`allow_births`)
  - parameter bundle tuning only (no structural logic):
    - `params.civ.nobirths`
    - `params.civ.basic_births`

## With/Without Procreation Behavior
- `births_enabled=false` policy path:
  - births remain zero
  - deaths still apply per death model
  - population remains fixed or declines by tuning
- `births_enabled=true` policy path:
  - cohort births computed deterministically using model rates and parameter multipliers
  - deterministic rounding and growth caps applied
  - law-forbidden births refuse with:
    - `refusal.civ.births_forbidden_by_law`
- Population safety:
  - cohort size is clamped to non-negative values
  - deterministic cohort processing order is `cohort_id` ascending

## Migration Model
- Migration process surface:
  - `process.cohort_relocate`
- Model-driven travel time:
  - instant path (`travel_time_policy_id=instant`) or
  - deterministic distance-band delayed travel
- Delayed migration behavior:
  - `in_transit_until_tick` tracked in cohort extensions
  - location updates only when arrival tick is reached
- Missing model refusal:
  - `refusal.civ.migration_model_missing`
- Orders integration:
  - `order.migrate` executes via `process.cohort_relocate`

## Multiplayer Integration Notes
- Lockstep:
  - demography remains deterministic process execution; outcomes are replay-hash stable.
- Server authoritative:
  - server runs demography tick and emits only authoritative deltas.
- Hybrid SRZ:
  - demography executes shard-locally with deterministic shard filtering.
  - cross-shard ownership remains deterministic and authority-controlled.
- Anti-cheat:
  - clients cannot directly mutate demographic state.

## Epistemic Observability Rules
- Population observability is filtered through observation policy/lens/law.
- Non-entitled observers receive quantized values (`estimated_size`) and band labels.
- Exact cohort sizes require explicit entitlement (`allow_hidden` / inspection).
- Cohort identity leak prevention:
  - non-entitled views use anonymous population row IDs instead of raw `cohort_id`.
- LOD invariance:
  - macro-to-micro refinement does not reveal extra exact population truth beyond policy.

## Validation Snapshot (2026-02-26)
- RepoX PASS:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: `status=pass`, findings=`0`.
- AuditX run:
  - `py -3 tools/auditx/auditx.py scan --repo-root . --changed-only --format json`
  - Result: `result=scan_complete`, findings=`959`.
- TestX PASS (CIV-4 required suite):
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.civilisation.demography_tick_deterministic,testx.civilisation.births_disabled_policy,testx.civilisation.births_forbidden_by_law_refusal,testx.civilisation.population_never_negative,testx.civilisation.migration_delay_deterministic,testx.civilisation.quantized_population_observability,testx.civilisation.lod_invariance_population_size`
  - Result: `status=pass` (`selected_tests=7`).
- strict build PASS:
  - `C:\Program Files\CMake\bin\cmake.exe --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
  - Result: build complete for strict targets.
- `ui_bind --check` PASS:
  - `py -3 tools/xstack/ui_bind.py --repo-root . --check`
  - Result: `result=complete`, `checked_windows=21`.

## Known Limitations
- Cohort demography is aggregate-only in CIV-4; individual-level reproduction/biology is intentionally out of scope.
- Quantized observability is policy-driven and may present approximation artifacts within allowed epistemic envelopes.

## Extension Points
- CIV-5+ biology domain integration (if canon-approved).
- Individual lifecycle simulation (future scoped and law/profile gated).
- Rich migration capacity and logistics models.
- Governance-coupled demographic modifiers layered through policy registries.

# Tier Transition Constitution Baseline (RS-4)

Date: 2026-02-26  
Status: Baseline complete (deterministic transition governance, invariant checks, epistemic safety, and multiplayer integration)

## 1) Canonical Tier Taxonomy

Implemented taxonomy and transition policy plumbing enforces:
- `tier.macro`
- `tier.meso`
- `tier.micro`
- `tier.render`

Transition behavior is policy-driven via:
- `tier_taxonomy_id`
- `transition_policy_id`
- deterministic arbitration rules (`arb.equal_share`, `arb.priority_by_distance`, `arb.server_authoritative_weighted`)
- deterministic hysteresis (`min_transition_interval_ticks`)

## 2) Transition Controller + Event Artifacts

Runtime transition control is deterministic and contract-bound:
- transition selection centralized in `src/reality/transitions/transition_controller.py`
- runtime integration in `tools/xstack/sessionx/process_runtime.py`
- deterministic ordering by quantized distance, priority, and stable IDs
- transition event artifacts emitted with:
  - `event_id`
  - `tick`, `shard_id`, `region_id`
  - `from_tier`/`to_tier`
  - invariant check results
  - deterministic fingerprint

## 3) Invariant Checks + Epistemic Safety

Boundary-only transition checks are enforced on expand/collapse:
- conservation checks (RS-2 ledger-backed)
- cohort conservation checks (CIV-2 alignment)
- transition materialization checks
- epistemic invariance checks (ED-4 integration)

Ranked strict behavior:
- LOD information gain on transition refuses with `refusal.ep.lod_information_gain`

Private/non-strict behavior:
- clamp + log path retained where law/policy allows

## 4) Multiplayer Integration

Transition constitution is integrated across A/B/C styles:
- handshake compatibility now includes `tier_taxonomy_id` and `transition_policy_id`
- authoritative and SRZ hybrid policy contexts now resolve and enforce transition policy/taxonomy
- per-tick multiplayer hash envelope now includes deterministic transition-event hash material

Additional strict-gate packaging fix:
- `tools/xstack/packagingx/dist_build.py` now sources registry export mapping from `sessionx.runner.REGISTRY_FILE_MAP` to prevent registry drift (including `arbitration_rule.registry.json`) during dist/lab validation.

## 5) RS4 Guardrails Added

### RepoX
- `INV-TRANSITIONS-POLICY-DRIVEN`
- `INV-TRANSITION-EVENT-RECORDED`
- `INV-NO-WALLCLOCK-IN-TRANSITION`

### AuditX
- `TransitionThrashSmell` (`E46_TRANSITION_THRASH_SMELL`)
- `NonDeterministicArbitrationSmell` (`E47_NONDETERMINISTIC_ARBITRATION_SMELL`)

### TestX
Added deterministic transition coverage:
- `testx.reality.transition_selection_deterministic`
- `testx.reality.hysteresis_no_thrash_deterministic`
- `testx.reality.invariant_checks_on_collapse_expand`
- `testx.reality.epistemic_invariance_on_expand`
- `testx.reality.multiplayer_distributed_players_arbitration`

## 6) Gate Execution

### RepoX PASS
- Command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
- Result: `pass` (warn-only findings present, no fail/refusal)

### AuditX Run
- Command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
- Result: `pass` (existing warn findings reported)

### TestX PASS (RS4 coverage subset + MP/epistemic regressions)
- Command:  
  `py -3 tools/xstack/testx/runner.py --profile STRICT --subset testx.reality.transition_selection_deterministic,testx.reality.hysteresis_no_thrash_deterministic,testx.reality.invariant_checks_on_collapse_expand,testx.reality.epistemic_invariance_on_expand,testx.reality.multiplayer_distributed_players_arbitration,testx.net.mp_authoritative_full_stack,testx.net.mp_srz_hybrid_full_stack,testx.regression.multiplayer_baseline_hash,testx.epistemics.lod_macro_to_micro_no_precision_gain,testx.epistemics.lod_precision_quantization_stable`
- Result: `pass` (10/10)

### Strict Build PASS (dist + validation path)
- Command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.rs4 --cache on --format json`
- Result: `complete` + embedded dist validation `complete`

Additional strict lab validation check:
- Command: `py -3 tools/xstack/testx/runner.py --profile STRICT --subset testx.lab_build.pipeline_validation`
- Result: `pass`

### ui_bind --check PASS
- Command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
- Result: `complete` (`checked_windows=21`)

## 7) Known Limitations

- Full end-to-end `py -3 tools/xstack/run.py strict --repo-root . --cache on` remains non-pass because of pre-existing unrelated strict-lane failures (compatx strict example requirements and broader pre-existing strict TestX baseline failures outside RS4 scope).
- RS4 transition constitution gates listed above are passing.

## 8) Extension Points

Future RS/MAT/DOM work can extend:
- richer per-domain invariant libraries at transition boundaries
- arbitration policies with explicit per-peer fairness budgets
- tighter coupling of transition cost models to PerformX policy simulation
- expanded structural invariants for material/solver domains

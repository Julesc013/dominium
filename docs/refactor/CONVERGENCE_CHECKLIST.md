# Convergence Checklist

- Generated: 2026-03-26

## Phase 1 - Safe merges (LOW risk)

- Execute merge actions for LOW-risk clusters and validate with FAST gates.
- Planned action count: 842
- Gate: `python tools/xstack/testx/runner.py --repo-root . --profile FAST`
- Gate: `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`

## Phase 2 - Medium risk merges

- Execute MED-risk merges, then run STRICT validation plus the four Ω regression verifies.
- Planned action count: 2163
- Gate: `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- Gate: `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- Gate: `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- Gate: `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- Gate: `python tools/mvp/tool_run_disaster_suite.py --repo-root .`

## Phase 3 - High risk merges (one per PR)

- Execute one HIGH-risk merge action per PR and require the full convergence gate.
- Planned action count: 4570
- Gate: `python tools/convergence/tool_run_convergence_gate.py --repo-root .`

## Phase 4 - Rewire sweep

- Update call sites and includes to the chosen canonical implementations, then rerun review and STRICT validation.
- Planned action count: 13814
- Gate: `python tools/review/tool_run_duplicate_impl_scan.py --repo-root .`
- Gate: `python tools/review/tool_run_implementation_scoring.py --repo-root .`
- Gate: `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`

## Phase 5 - Deprecation and quarantine decisions

- Review quarantined items manually, convert them to merge/rewire/deprecate, and record deprecations without deletion.
- Planned action count: 18056
- Gate: `python tools/review/tool_run_convergence_plan.py --repo-root .`
- Gate: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Phase 6 - SRC removal execution (Ξ-5)

- Remove source-like shadow surfaces only after all rewires complete and the convergence gate passes.
- Planned action count: 0
- Gate: `python tools/review/tool_run_convergence_plan.py --repo-root .`
- Gate: `python tools/convergence/tool_run_convergence_gate.py --repo-root .`

## SRC Policy

- Execute merge/rewire/deprecate actions for all source-like implementations before any removal work.
- Remove source-like directories only in Ξ-5 after rewires complete and Ω regression gates pass.


Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.2c02320c7416aafe`

- Symbol: `_write_canonical_json`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/mvp/mvp_smoke_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/audit/arch_audit_common.py`
- `tools/mvp/cross_platform_gate_common.py`
- `tools/mvp/mvp_smoke_common.py`
- `tools/mvp/stress_gate_common.py`
- `tools/time/time_anchor_common.py`

## Scorecard

- `tools/mvp/mvp_smoke_common.py` disposition=`canonical` rank=`1` total_score=`81.79` risk=`HIGH`
- `tools/mvp/cross_platform_gate_common.py` disposition=`quarantine` rank=`2` total_score=`81.43` risk=`HIGH`
- `tools/mvp/stress_gate_common.py` disposition=`quarantine` rank=`3` total_score=`76.49` risk=`HIGH`
- `tools/audit/arch_audit_common.py` disposition=`merge` rank=`4` total_score=`66.07` risk=`HIGH`
- `tools/time/time_anchor_common.py` disposition=`merge` rank=`5` total_score=`66.07` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/PRODUCT_BOUNDARIES.md, docs/architecture/CANON_INDEX.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/audit/ARCH_AUDIT0_RETRO_AUDIT.md, docs/audit/CANON_MAP.md, docs/audit/CONVERGENCE_FINAL.md, docs/audit/DIST_TREE_ASSEMBLY_FINAL.md, docs/audit/DOC_INDEX.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

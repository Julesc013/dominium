Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.5c7447be23d93f0f`

- Symbol: `build_parser`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/controlx/controlx.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/auditx/auditx.py`
- `tools/xstack/compatx/compatx.py`
- `tools/xstack/controlx/controlx.py`
- `tools/xstack/performx/performx.py`
- `tools/xstack/securex/securex.py`

## Scorecard

- `tools/xstack/controlx/controlx.py` disposition=`canonical` rank=`1` total_score=`80.21` risk=`HIGH`
- `tools/xstack/auditx/auditx.py` disposition=`quarantine` rank=`2` total_score=`78.96` risk=`HIGH`
- `tools/xstack/compatx/compatx.py` disposition=`merge` rank=`3` total_score=`68.93` risk=`HIGH`
- `tools/xstack/securex/securex.py` disposition=`merge` rank=`4` total_score=`68.93` risk=`HIGH`
- `tools/xstack/performx/performx.py` disposition=`merge` rank=`5` total_score=`63.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

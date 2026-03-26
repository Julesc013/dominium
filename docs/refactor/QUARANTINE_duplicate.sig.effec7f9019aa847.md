Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.effec7f9019aa847`

- Symbol: `load_manifest`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/pack/pack_validate.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `tests/contract/archive_presence_tests.py`
- `tools/pack/capability_inspect.py`
- `tools/pack/pack_validate.py`

## Scorecard

- `tools/pack/pack_validate.py` disposition=`canonical` rank=`1` total_score=`81.55` risk=`HIGH`
- `tools/pack/capability_inspect.py` disposition=`quarantine` rank=`2` total_score=`79.05` risk=`HIGH`
- `tests/contract/archive_presence_tests.py` disposition=`drop` rank=`3` total_score=`61.67` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/MODDER_GUIDE.md, docs/app/CLI_CONTRACTS.md, docs/app/OBSERVABILITY_PIPELINES.md, docs/app/TESTX_INVENTORY.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/SUPERVISOR_MODEL.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/BUNDLE_MODEL.md`

## Tests Involved

- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

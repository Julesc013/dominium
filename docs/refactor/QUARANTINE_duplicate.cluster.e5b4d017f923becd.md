Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.e5b4d017f923becd`

- Symbol: `refusal_payload`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/ai/ai_cli.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/ai/ai_cli.py`
- `tools/bugreport/bugreport_cli.py`
- `tools/launcher/launcher_cli.py`
- `tools/ops/ops_cli.py`
- `tools/setup/setup_cli.py`
- `tools/share/share_cli.py`

## Scorecard

- `tools/ai/ai_cli.py` disposition=`canonical` rank=`1` total_score=`76.79` risk=`HIGH`
- `tools/launcher/launcher_cli.py` disposition=`quarantine` rank=`2` total_score=`69.46` risk=`HIGH`
- `tools/setup/setup_cli.py` disposition=`merge` rank=`3` total_score=`61.61` risk=`HIGH`
- `tools/share/share_cli.py` disposition=`merge` rank=`4` total_score=`60.71` risk=`HIGH`
- `tools/ops/ops_cli.py` disposition=`merge` rank=`5` total_score=`60.12` risk=`HIGH`
- `tools/bugreport/bugreport_cli.py` disposition=`merge` rank=`6` total_score=`47.98` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/CAPABILITY_STAGES.md, docs/CONTRIBUTING.md, docs/FAQ.md, docs/GLOSSARY.md, docs/PHILOSOPHY.md, docs/SCHEMA_CANON_ALIGNMENT.md, docs/SCHEMA_EVOLUTION.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

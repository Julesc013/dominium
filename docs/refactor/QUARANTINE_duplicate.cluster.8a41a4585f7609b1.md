Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.8a41a4585f7609b1`

- Symbol: `_fingerprint`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/packs/compat/pack_verification_pipeline.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/packs/compat/pack_compat_validator.py`
- `src/packs/compat/pack_verification_pipeline.py`

## Scorecard

- `src/packs/compat/pack_verification_pipeline.py` disposition=`canonical` rank=`1` total_score=`59.17` risk=`HIGH`
- `src/packs/compat/pack_compat_validator.py` disposition=`quarantine` rank=`2` total_score=`57.38` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/XSTACK.md, docs/appshell/APPSHELL_CONSTITUTION.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/COMMANDS_AND_REFUSALS.md, docs/appshell/SUPERVISOR_MODEL.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/EXTENSION_MAP.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

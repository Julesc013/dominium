Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.df64bdb20af5a9d1`

- Symbol: `_file_hash`
- Cluster Kind: `exact`
- Cluster Resolution: `keep`
- Risk Level: `LOW`
- Canonical Candidate: `tools/auditx/cache_engine.py`
- Quarantine Reasons: `file_scope_ambiguity, phase_boundary_deferred, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate`

## Competing Files

- `src/appshell/supervisor/supervisor_engine.py`
- `tools/auditx/cache_engine.py`
- `tools/xstack/core/merkle_tree.py`
- `tools/xstack/core/runners.py`

## Scorecard

- `tools/auditx/cache_engine.py` disposition=`canonical` rank=`1` total_score=`81.61` risk=`LOW`
- `tools/xstack/core/merkle_tree.py` disposition=`drop` rank=`2` total_score=`76.11` risk=`LOW`
- `tools/xstack/core/runners.py` disposition=`drop` rank=`3` total_score=`67.01` risk=`HIGH`
- `src/appshell/supervisor/supervisor_engine.py` disposition=`drop` rank=`4` total_score=`55.65` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/AUDITX_BASELINE_REPORT.md, docs/audit/AUDITX_OVERHAUL_REPORT.md, docs/audit/BEHAVIORAL_COMPONENTS_BASELINE.md, docs/audit/BOM_AG_BASELINE.md, docs/audit/CANON_MAP.md, docs/audit/CAPABILITY_REGISTRY_BASELINE.md, docs/audit/CIVILISATION_SUBSTRATE_BASELINE.md`

## Tests Involved

- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

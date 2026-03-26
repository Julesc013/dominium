Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e25d376d755e45de`

- Symbol: `build_control_proof_bundle_from_decision_logs`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/control/proof/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/control/__init__.py`
- `src/control/proof/__init__.py`
- `src/control/proof/control_proof_bundle.py`

## Scorecard

- `src/control/proof/__init__.py` disposition=`canonical` rank=`1` total_score=`62.73` risk=`HIGH`
- `src/control/proof/control_proof_bundle.py` disposition=`quarantine` rank=`2` total_score=`59.8` risk=`HIGH`
- `src/control/__init__.py` disposition=`quarantine` rank=`3` total_score=`57.5` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CONTROL_NEGOTIATION_BASELINE.md, docs/audit/CTRL10_RETRO_AUDIT.md, docs/audit/FORCE_MOMENTUM_BASELINE.md, docs/audit/META_CONTRACT0_RETRO_AUDIT.md, docs/audit/MOB11_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/electric/PROTECTION_AND_FAULT_MODEL.md`

## Tests Involved

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

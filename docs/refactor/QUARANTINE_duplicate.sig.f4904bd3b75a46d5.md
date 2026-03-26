Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f4904bd3b75a46d5`

- Symbol: `_run_verify`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/compatx/compatx.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/compatx/compatx.py`
- `tools/securex/securex.py`

## Scorecard

- `tools/compatx/compatx.py` disposition=`canonical` rank=`1` total_score=`68.93` risk=`HIGH`
- `tools/securex/securex.py` disposition=`quarantine` rank=`2` total_score=`66.55` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/XSTACK.md, docs/architecture/CANON_INDEX.md, docs/architecture/astronomy_catalogs.md, docs/audit/CANON_MAP.md, docs/audit/COMPILED_MODEL_BASELINE.md, docs/audit/DEVELOPER_ACCELERATION_BASELINE.md, docs/audit/DIST2_RETRO_AUDIT.md, docs/audit/DOC_INDEX.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

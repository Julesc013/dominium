Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.799623cd10a4b4d8`

- Symbol: `release_index_target_rows`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/platform/target_matrix.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/platform/__init__.py`
- `src/platform/target_matrix.py`

## Scorecard

- `src/platform/target_matrix.py` disposition=`canonical` rank=`1` total_score=`65.48` risk=`MED`
- `src/platform/__init__.py` disposition=`quarantine` rank=`2` total_score=`63.1` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/archive/build/APR5_BUILD_INVENTORY.md, docs/audit/ARCH_AUDIT2_CONSTITUTION.md, docs/audit/ARCH_MATRIX0_RETRO_AUDIT.md, docs/audit/ARCH_MATRIX_FINAL.md, docs/audit/CANON_MAP.md, docs/audit/DIST_FINAL_DRYRUN.md, docs/audit/DOCS_AUDIT_PROMPT0.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

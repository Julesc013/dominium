Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.58bfd4143d059be5`

- Symbol: `build_boundary_invariant_row`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/system/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/system/__init__.py`
- `src/system/system_collapse_engine.py`

## Scorecard

- `src/system/__init__.py` disposition=`canonical` rank=`1` total_score=`71.79` risk=`HIGH`
- `src/system/system_collapse_engine.py` disposition=`quarantine` rank=`2` total_score=`65.11` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/architecture/ARCH0_CONSTITUTION.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/EXTENSION_MAP.md, docs/architecture/INVARIANTS.md, docs/audit/AUDITX_BASELINE_REPORT.md, docs/audit/CANON_CONFORMANCE_REPORT.md`

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

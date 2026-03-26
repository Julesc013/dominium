Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.2c3ca6e6ccda70b7`

- Symbol: `build_arbitration_state_row`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/logic/protocol/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/logic/__init__.py`
- `src/logic/protocol/__init__.py`
- `src/logic/protocol/rows.py`

## Scorecard

- `src/logic/protocol/__init__.py` disposition=`canonical` rank=`1` total_score=`78.45` risk=`HIGH`
- `src/logic/__init__.py` disposition=`quarantine` rank=`2` total_score=`69.64` risk=`HIGH`
- `src/logic/protocol/rows.py` disposition=`quarantine` rank=`3` total_score=`68.69` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/LOGIC10_RETRO_AUDIT.md, docs/audit/LOGIC1_RETRO_AUDIT.md, docs/audit/LOGIC9_RETRO_AUDIT.md, docs/audit/LOGIC_FINAL_BASELINE.md, docs/audit/LOGIC_PROTOCOL_BASELINE.md`

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

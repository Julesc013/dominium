Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.224a6c43b2b7d54c`

- Symbol: `enforce_negotiated_capability`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/compat/negotiation/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/compat/negotiation/__init__.py`
- `src/compat/negotiation/degrade_enforcer.py`

## Scorecard

- `src/compat/negotiation/__init__.py` disposition=`canonical` rank=`1` total_score=`55.45` risk=`HIGH`
- `src/compat/negotiation/degrade_enforcer.py` disposition=`quarantine` rank=`2` total_score=`48.61` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CAP_NEG4_RETRO_AUDIT.md, docs/governance/REPOX_RULESETS.md, docs/net/HANDSHAKE_AND_COMPATIBILITY.md`

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

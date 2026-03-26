Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.75b7daa540856d39`

- Symbol: `appshell_product_bootstrap`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/launcher/launch.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/server/server_main.py`
- `tools/launcher/launch.py`
- `tools/mvp/runtime_entry.py`

## Scorecard

- `tools/launcher/launch.py` disposition=`canonical` rank=`1` total_score=`64.25` risk=`HIGH`
- `tools/mvp/runtime_entry.py` disposition=`quarantine` rank=`2` total_score=`63.94` risk=`HIGH`
- `src/server/server_main.py` disposition=`quarantine` rank=`3` total_score=`55.6` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/PRODUCT_BOUNDARIES.md, docs/architecture/CANON_INDEX.md, docs/audit/APPSHELL0_RETRO_AUDIT.md, docs/audit/APPSHELL1_RETRO_AUDIT.md, docs/audit/APPSHELL2_RETRO_AUDIT.md, docs/audit/APPSHELL_BOOTSTRAP_BASELINE.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

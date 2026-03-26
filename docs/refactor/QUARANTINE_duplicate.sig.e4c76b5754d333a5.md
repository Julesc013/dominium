Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e4c76b5754d333a5`

- Symbol: `build_inspection_overlays`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/sessionx/interaction.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/client/interaction/inspection_overlays.py`
- `tools/xstack/sessionx/interaction.py`

## Scorecard

- `tools/xstack/sessionx/interaction.py` disposition=`canonical` rank=`1` total_score=`77.2` risk=`HIGH`
- `src/client/interaction/inspection_overlays.py` disposition=`quarantine` rank=`2` total_score=`72.98` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CTRL4_RETRO_AUDIT.md, docs/audit/FORM1_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/POLL1_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SPEC1_RETRO_AUDIT.md, docs/audit/THERM0_RETRO_AUDIT.md, docs/audit/UX0_RETRO_AUDIT.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

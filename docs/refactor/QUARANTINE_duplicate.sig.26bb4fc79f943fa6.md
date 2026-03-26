Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.26bb4fc79f943fa6`

- Symbol: `d_net_set_transport`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/net/d_net_transport.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/net/d_net_transport.c`
- `engine/modules/net/d_net_transport.h`

## Scorecard

- `engine/modules/net/d_net_transport.c` disposition=`canonical` rank=`1` total_score=`88.1` risk=`HIGH`
- `engine/modules/net/d_net_transport.h` disposition=`quarantine` rank=`2` total_score=`86.07` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/audit/APPSHELL2_RETRO_AUDIT.md, docs/audit/APPSHELL4_RETRO_AUDIT.md, docs/audit/CANON_MAP.md, docs/audit/CAP_NEG2_RETRO_AUDIT.md, docs/audit/CAP_NEGOTIATION_BASELINE.md`

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

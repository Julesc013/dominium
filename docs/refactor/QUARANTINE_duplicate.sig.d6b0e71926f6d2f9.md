Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d6b0e71926f6d2f9`

- Symbol: `dtlv_le_read_u64`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/io/container.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/io/container.h`
- `engine/modules/io/dtlv.c`

## Scorecard

- `engine/include/domino/io/container.h` disposition=`canonical` rank=`1` total_score=`76.64` risk=`HIGH`
- `engine/modules/io/dtlv.c` disposition=`quarantine` rank=`2` total_score=`67.44` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/specs/DATA_FORMATS.md, docs/specs/SPEC_CONTAINER_TLV.md, docs/specs/SPEC_UNIVERSE_BUNDLE.md, docs/specs/launcher/SPEC_LAUNCH_HANDSHAKE_GAME.md`

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

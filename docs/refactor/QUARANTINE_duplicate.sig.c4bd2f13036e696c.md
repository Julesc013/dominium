Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c4bd2f13036e696c`

- Symbol: `d_tlv_schema_register`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/d_tlv_schema.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/core/d_tlv_schema.c`
- `engine/modules/core/d_tlv_schema.h`

## Scorecard

- `engine/modules/core/d_tlv_schema.c` disposition=`canonical` rank=`1` total_score=`81.55` risk=`HIGH`
- `engine/modules/core/d_tlv_schema.h` disposition=`quarantine` rank=`2` total_score=`79.7` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/guides/ui_editor/SPEC_UI_DOC_TLV.md, docs/specs/SPEC_CONTENT.md, docs/specs/SPEC_CORE.md, docs/specs/SPEC_DOMINIUM_LAYER.md, docs/specs/SPEC_DOMINO_SUBSYSTEMS.md, docs/specs/SPEC_NET.md, docs/specs/SPEC_NETCODE.md`

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

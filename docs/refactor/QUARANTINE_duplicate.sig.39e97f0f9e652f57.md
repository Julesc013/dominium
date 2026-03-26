Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.39e97f0f9e652f57`

- Symbol: `d_tlv_blob`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/d_subsystem.h`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `engine/modules/content/d_content_schema.c`
- `engine/modules/core/d_subsystem.h`
- `engine/modules/core/d_tlv_schema.c`
- `engine/modules/core/d_tlv_schema.h`
- `engine/modules/net/d_net_schema.c`
- `engine/modules/world/d_serialize.c`
- `engine/modules/world/d_serialize.h`

## Scorecard

- `engine/modules/core/d_subsystem.h` disposition=`canonical` rank=`1` total_score=`76.19` risk=`HIGH`
- `engine/modules/core/d_tlv_schema.c` disposition=`quarantine` rank=`2` total_score=`74.4` risk=`HIGH`
- `engine/modules/world/d_serialize.h` disposition=`quarantine` rank=`3` total_score=`73.1` risk=`HIGH`
- `engine/modules/core/d_tlv_schema.h` disposition=`quarantine` rank=`4` total_score=`72.56` risk=`HIGH`
- `engine/modules/world/d_serialize.c` disposition=`quarantine` rank=`5` total_score=`70.36` risk=`HIGH`
- `engine/modules/content/d_content_schema.c` disposition=`quarantine` rank=`6` total_score=`68.89` risk=`HIGH`
- `engine/modules/net/d_net_schema.c` disposition=`merge` rank=`7` total_score=`64.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/specs/DATA_FORMATS.md, docs/specs/SPEC_CORE.md, docs/specs/SPEC_DETERMINISM.md, docs/specs/SPEC_DOMINO_SUBSYSTEMS.md, docs/specs/SPEC_ENV.md, docs/specs/SPEC_REPLAY.md, docs/specs/SPEC_RES.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

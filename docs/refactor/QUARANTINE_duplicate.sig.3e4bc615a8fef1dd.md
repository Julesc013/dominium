Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.3e4bc615a8fef1dd`

- Symbol: `transport_logic_sig_receipts`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/logic/protocol/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/logic/__init__.py`
- `src/logic/protocol/__init__.py`
- `src/logic/protocol/protocol_engine.py`

## Scorecard

- `src/logic/protocol/__init__.py` disposition=`canonical` rank=`1` total_score=`64.17` risk=`HIGH`
- `src/logic/__init__.py` disposition=`quarantine` rank=`2` total_score=`55.36` risk=`HIGH`
- `src/logic/protocol/protocol_engine.py` disposition=`merge` rank=`3` total_score=`45.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/LOGIC1_RETRO_AUDIT.md, docs/audit/LOGIC3_RETRO_AUDIT.md, docs/audit/LOGIC9_RETRO_AUDIT.md, docs/audit/LOGIC_FINAL_BASELINE.md, docs/audit/LOGIC_PROTOCOL_BASELINE.md, docs/audit/SIGNAL_BUS_BASELINE.md, docs/logic/PROTOCOL_SHARD_RULES.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

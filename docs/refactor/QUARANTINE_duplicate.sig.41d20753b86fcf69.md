Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.41d20753b86fcf69`

- Symbol: `sha256_bytes`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/distribution/dompkg_lib.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `game/tests/tests/vectors/gen_tlv_vectors.py`
- `setup/packages/scripts/packaging/dsumanifest.py`
- `tools/distribution/dompkg_lib.py`

## Scorecard

- `tools/distribution/dompkg_lib.py` disposition=`canonical` rank=`1` total_score=`67.64` risk=`HIGH`
- `setup/packages/scripts/packaging/dsumanifest.py` disposition=`drop` rank=`2` total_score=`59.61` risk=`HIGH`
- `game/tests/tests/vectors/gen_tlv_vectors.py` disposition=`quarantine` rank=`3` total_score=`58.33` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

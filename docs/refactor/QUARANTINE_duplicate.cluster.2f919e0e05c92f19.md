Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.2f919e0e05c92f19`

- Symbol: `REPORT_JSON_REL`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/security/trust_model_common.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/engine/concurrency_contract_common.py`
- `tools/security/trust_model_common.py`

## Scorecard

- `tools/security/trust_model_common.py` disposition=`canonical` rank=`1` total_score=`83.16` risk=`HIGH`
- `tools/engine/concurrency_contract_common.py` disposition=`quarantine` rank=`2` total_score=`74.32` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/XSTACK.md, docs/architecture/CANON_INDEX.md, docs/audit/ARCH_AUDIT2_RETRO_AUDIT.md, docs/audit/CANON_MAP.md, docs/audit/DISASTER_TEST0_RETRO_AUDIT.md, docs/audit/DIST_FINAL_DRYRUN.md, docs/audit/DOCS_AUDIT_PROMPT0.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

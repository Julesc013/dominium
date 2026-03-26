Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.14cd1ce542d17825`

- Symbol: `_command_sort_key`
- Cluster Kind: `exact`
- Cluster Resolution: `keep`
- Risk Level: `MED`
- Canonical Candidate: `src/appshell/command_registry.py`
- Quarantine Reasons: `cross_domain_helper_collision, file_scope_ambiguity, source_like_surface`
- Planned Action Kinds: `rewire, deprecate`

## Competing Files

- `src/appshell/command_registry.py`
- `tools/appshell/tool_generate_command_docs.py`

## Scorecard

- `src/appshell/command_registry.py` disposition=`canonical` rank=`1` total_score=`69.4` risk=`MED`
- `tools/appshell/tool_generate_command_docs.py` disposition=`drop` rank=`2` total_score=`67.11` risk=`LOW`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/LOGGING_AND_TRACING.md, docs/audit/APPSHELL2_RETRO_AUDIT.md, docs/audit/META_STABILITY0_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/OBSERVABILITY0_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/STABILITY_CLASSIFICATION_BASELINE.md, docs/audit/VALIDATION_STACK_MAP.md`

## Tests Involved

- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.

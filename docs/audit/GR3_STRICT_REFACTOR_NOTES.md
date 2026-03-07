# GR3 STRICT Refactor Notes

## Applied Refactors
1. `data/registries/action_template_registry.json`
- Added missing task templates required by strict action-grammar enforcement:
  - `task.assay`
  - `task.disassemble`
  - `task.scan`
- Corrected `record.extensions.template_count` to match entries.
- Filled missing deterministic fingerprints in pre-existing rows that failed strict validation.

2. `tools/xstack/sessionx/process_runtime.py`
- Removed a static-check false positive by renaming a local comprehension variable (`field` -> `sv_entry`) in hash-chain projection.
- No behavior change.

3. `src/meta/__init__.py`
- Broke package import cycle by replacing eager `src.meta.reference` imports with lazy wrappers:
  - `evaluate_reference_evaluator(...)`
  - `evaluate_reference_suite(...)`
- Prevents partial-init cycle when `src.system` imports `src.meta.profile`.

4. `tools/xstack/testx/tests/test_hidden_state_violation_detected.py`
- Migrated fixture from legacy debug toggle to canonical profile override path:
  - profile registry payload + profile binding for `rule.statevec.output_guard`.
- Keeps STATEVEC guard coverage while satisfying no-mode-flag policy.

5. `docs/audit/WORKTREE_LEFTOVERS.md`
- Added in-flight GR3 artifacts and touched paths so RepoX worktree hygiene gate remains explicit.

## Safety Statement
- No domain semantics changed.
- Deterministic ordering and hash logic preserved.
- Changes are registry hygiene, import-cycle hardening, and policy-path alignment only.

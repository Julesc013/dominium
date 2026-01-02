# Setup Parity With Launcher

Setup maintains contract parity with launcher invariants.

## Invariants
- Deterministic planning and selection.
- Capability registry model is rule-based and ordered.
- Job/journal semantics are deterministic and resumable.
- Audit output is always present.

## Automated checks
- `setup_parity_tests kernel_invariants_match_launcher`
- `setup_parity_tests capability_registry_semantics_match`
- `setup_parity_tests job_journal_semantics_match`

## Documentation anchors
These tests assert explicit markers in:
- `docs/setup/INVARIANTS.md`
- `docs/setup/SPLAT_SELECTION_RULES.md`
- `docs/setup/JOB_ENGINE.md`
- `source/dominium/launcher/core/README_launcher_core.md`

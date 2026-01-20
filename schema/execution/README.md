# Execution Schema (EXEC0)

Canonical Work IR and Access IR specifications for execution backends. This
folder defines declarative, deterministic representations only. No runtime
logic or scheduler code lives here.

## Contents
- `SPEC_WORK_IR.md` — TaskGraph and TaskNode representation.
- `SPEC_ACCESS_IR.md` — AccessSet declaration for reads/writes/reductions.
- `SPEC_COST_MODEL.md` — Cost model declarations and budget metadata.
- `SPEC_DETERMINISM_CLASSES.md` — Determinism classes and ordering rules.
- `SPEC_EXECUTION_POLICY.md` — Deterministic execution policy selection.
- `SPEC_BUDGET_PROFILES.md` — Budget profile inputs and outputs.

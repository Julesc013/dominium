Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CAPABILITIES_AND_SOLVER

This document defines the typed capabilities model and deterministic solver
contracts used by launcher/setup selection. Key IDs and rules are append-only
and must not change once shipped.

## Core caps (core_caps)
Caps are small typed entries used for selection and reporting:
- key_id (stable numeric ID, append-only)
- type (BOOL, I32, U32, I64, U64, STRING_ID, RANGE_U32, ENUM_ID)
- value (typed union)

Entries are kept in canonical order by key_id. No arbitrary strings; STRING_ID must refer to stable tokens.

Key catalog (current):
- 1 supports_gui_native_widgets
- 2 supports_gui_dgfx
- 3 supports_tui
- 4 supports_cli
- 5 supports_tls
- 6 supports_keychain
- 7 supports_stdout_capture
- 8 supports_file_picker
- 9 supports_open_folder
- 10 fs_permissions_model (enum: user/system/mixed/unknown)
- 11 os_family (enum: win32/unix/apple/unknown)
- 12 os_version_major
- 13 os_version_minor
- 14 arch (enum: x86_32/x86_64/arm_32/arm_64/unknown)
- 15 os_is_win32
- 16 os_is_unix
- 17 os_is_apple
- 18 determinism_grade (enum: D0/D1/D2)
- 19 perf_class (enum: baseline/compat/perf)
- 20 backend_priority
- 21 subsystem_id
- 22 setup_target_ok
- 23 setup_scope_ok
- 24 setup_ui_ok
- 25 setup_ownership_ok
- 26 setup_manifest_allowlist_ok
- 27 setup_required_caps_ok
- 28 setup_prohibited_caps_ok
- 29 setup_manifest_target_ok

Add new keys by appending to
`libs/contracts/include/dom_contracts/core_caps.h`. Never renumber or reuse IDs.

## Constraints (core_solver)
Each component declares:
- provides: caps exposed by the component
- requires: constraints that must be satisfied
- forbids: constraints that must not be satisfied
- prefers: soft constraints with weights (scoring only)
- conflicts: list of component_ids that cannot be selected together

Constraint operators:
- EQ, NE, GE, LE, IN_RANGE
- IN_RANGE uses RANGE_U32 values and evaluates against U32/ENUM/BOOL actuals.

Host caps are merged with component caps when evaluating constraints.

## Solver determinism and tie-breaks
Selection is deterministic:
- Categories are evaluated in ascending category_id order.
- Candidates within a category are ordered by component_id (case-insensitive).
- Overrides: if a category override is provided, only that component is eligible.
  Failure reasons are override_not_found or override_ineligible.
- Eligibility: fails on profile requires/forbids, component requires/forbids, or conflicts.
- Score: score_fn(comp) + sum(prefers weights satisfied; weight defaults to 1).
- Tie-break: higher score, then higher priority, then lexicographically smallest component_id.

Selected entries record reason (override or score), score, priority, and prefers_satisfied.

## Explain output
`core_solver_explain_write_tlv` emits machine-readable TLV:
- Selected: category_id, component_id, reason, score, priority, prefers_satisfied
- Rejected: category_id, component_id, reason, failing constraint, actual value, conflict id

## Implementation note
Current build targets expose the contracts in
`libs/contracts/include/dom_contracts/core_caps.h` and
`libs/contracts/include/dom_contracts/core_solver.h`. Solver implementations
are not linked into the launcher/setup targets in this repository.
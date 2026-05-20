Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Diagnostic Registry Fixtures

These fixtures document the first validation expectations for
`tools/validators/contracts/check_diagnostics_registry.py`.

The fixture suite is contract-only. It does not implement runtime diagnostic
dispatch, Workbench presentation, package validation behavior, or release
promotion.

Expected behavior:

- `valid_diagnostic_code.json` passes fixture validation.
- `invalid_missing_owner.json` fails because every diagnostic needs an owner.
- `invalid_unknown_severity.json` fails because severity must come from
  `contracts/diagnostics/diagnostic_severity.registry.json`.
- `valid_evidence_packet.json` passes evidence fixture validation.
- `invalid_evidence_missing_subject.json` fails because evidence must identify
  its subject.

Future tasks may add full JSON Schema assertion tests and CTest integration.

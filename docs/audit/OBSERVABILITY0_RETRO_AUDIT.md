Status: DERIVED
Stability: provisional
Future Series: OBSERVABILITY
Replacement Target: release-pinned observability guarantees and redaction policies

# OBSERVABILITY-0 Retro Audit

## Surfaces Reviewed

- `src/appshell/logging/log_engine.py`
- `src/diag/repro_bundle_builder.py`
- `src/appshell/diag/diag_snapshot.py`
- `src/appshell/bootstrap.py`
- `src/appshell/commands/command_engine.py`
- `src/appshell/supervisor/supervisor_engine.py`
- `tools/setup/setup_cli.py`
- `data/registries/log_category_registry.json`
- `data/registries/log_message_key_registry.json`

## Current Strengths

- AppShell logs are already structured, fingerprinted, and JSON-serializable.
- Repro bundles already sanitize obvious secret-like keys and capture canonical events, proof anchors, negotiation records, IPC attach records, and recent logs.
- Refusal surfaces already carry reason codes and remediation hints in payload form.

## Gaps Before OBSERVABILITY-0

- Guaranteed categories were not frozen as a contract; `lib`, `update`, and `supervisor` existed only implicitly in message-key naming or not at all.
- The log engine did not enforce category/message-key registry bindings or required category-specific fields.
- Repro bundles did not guarantee inclusion of install-plan, update-plan, or pack-verification artifacts.
- Some runtime categories in active use were not declared in `log_category_registry.json`.
- Structured refusal logging existed, but remediation hints were not guaranteed in the emitted refusal log params.
- There was no single baseline artifact summarizing guaranteed categories, minimum fields, redaction policy, and DIAG bundle expectations.

## Canonical vs Derived

- Canonical records already present:
  - negotiation records
  - proof anchors
  - install/update transaction records
  - refusal payloads
- Derived logs already present:
  - AppShell lifecycle logs
  - TUI and mode-entry logs
  - supervisor status/log summaries

## Audit Conclusion

OBSERVABILITY-0 needs to freeze the contract rather than invent new logging mechanisms. The correct path is registry-backed enforcement in the existing log engine, additive DIAG bundle minimums, and RepoX/AuditX/TestX checks that keep guaranteed categories and redaction behavior from drifting.

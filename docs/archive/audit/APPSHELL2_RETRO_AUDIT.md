Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL2 Retro Audit

## Scope

APPSHELL-2 audited the active shared shell and product-adopted entry surfaces:

- `src/appshell/bootstrap.py`
- `src/appshell/commands/command_engine.py`
- `src/appshell/logging_sink.py`
- `src/server/net/loopback_transport.py`
- `src/server/runtime/tick_loop.py`
- `tools/setup/setup_cli.py`
- `tools/launcher/launch.py`
- `tools/mvp/runtime_entry.py`

## Findings

1. Structured logging existed only as the minimal `logging_sink.py` helper and did
   not provide stable `event_id`, `build_id`, `session_id`, category/message-key
   separation, or bounded ring buffering.
2. AppShell bootstrap and command dispatch emitted product output deterministically
   but did not run through a shared log engine.
3. Server loopback/log streaming already existed but used an ad hoc event payload
   shape instead of the shared AppShell log contract.
4. Proof anchors existed in SERVER-MVP-0, but there was no shell-level
   deterministic diagnostic snapshot that bundled descriptors, session inputs, log
   ring tails, and recent anchors offline.
5. No evidence was found that host wall-clock fields were feeding authoritative
   simulation logic in the active AppShell/server surfaces. Remaining wall-clock
   use is host/meta only and must stay outside truth.

## Integration Notes

- Console log output must stay on `stderr` so JSON command responses on `stdout`
  remain stable for CLI/TestX consumers.
- `diag snapshot` can be added as a root command without changing the existing
  `diag` summary surface because the command registry already resolves the longest
  exact path deterministically.
- Refinement request logging should stay summary-only and must be emitted from a
  consumer path, not from the pure refinement planner itself.

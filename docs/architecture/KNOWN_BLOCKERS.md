Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# KNOWN_BLOCKERS

Status: binding.
Scope: known gaps in enforcement that must be closed without weakening invariants.

## INV-MUT-PROCESS-ONLY (PARTIAL)
- Current state: process guard scaffolding exists, but mutation sites are not yet uniformly wrapped.
- Impact: dynamic assertions only cover code paths that opt-in to `DOM_PROCESS_GUARD_MUTATION()`.
- Plan: integrate guard calls into authoritative mutation helpers and process execution entrypoints, then remove this blocker.
- Owner: engine/core + game/rules
Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# TOOLING_OVERVIEW (TOOL0)

Status: draft  
Version: 1

## Philosophy
- Tools observe, they do not mutate authoritative state.
- Tools replay and validate; they never "fix" or auto-repair data.
- Determinism is mandatory: no OS time, no randomness, no hidden ordering.
- Epistemic boundaries apply by default; privileged inspection is explicit and auditable.

## Available TOOL0 modules
- Replay Inspector: step through recorded events/commands and validate replay hashes.
- Provenance Browser: trace asset/person origin chains via provenance links only.
- Ledger Inspector: summarize flows and verify conservation without touching balances.
- Event Timeline View: list scheduled/past/refused events and spot due-tick issues.

## Epistemic vs privileged modes
- Epistemic mode is the default and returns only information allowed by the access context.
- Privileged mode must be requested explicitly and should be logged by the tool host.
- Tools must never silently elevate or expand knowledge.

## Determinism and replay safety
- Inspection must not alter input buffers, hashes, or ordering.
- Tool output must be identical for identical inputs and access contexts.

## Mod and content validation
- Validation runs through `validate_all` and reports deterministic failures.
- Tools report errors and remediation, but never rewrite or auto-heal mods.

## Not cheats
- Tooling does not grant gameplay advantage or hidden state.
- Any mutation request is explicitly refused by design.

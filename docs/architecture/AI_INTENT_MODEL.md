# AI Intent Model (AI0)

Status: FROZEN.  
Scope: AI agents as intent producers with no special privileges.

## Foundational Rule

**AI agents produce intents.  
Intents are validated by the same authority, law, and budgets as human players.  
There are no AI-specific mechanics.**

Implications:
- AI success/failure is governed by refusals.
- AI actions are replayable.
- AI cannot see hidden state beyond snapshots.
- AI cannot mutate state directly.

## Execution Modes (Hybrid Model)

All modes use the *same intent schema* and *same refusal semantics*.

Mode A: Embedded
- Runs in the server process.
- Submits intents via in-process interface.
- Uses the same validation and queues as remote clients.
- Subject to explicit AI budgets (meta-law).

Mode B: Sidecar
- Separate OS process.
- Communicates via IPC (pipe/socket).
- Uses the same client protocol (loopback).
- Can be restarted independently.

Mode C: Remote
- Full network client.
- Same protocol as human clients.
- Authenticated and capability-gated.

Rules (all modes):
- Identical intent schema.
- Identical refusal semantics.
- Identical budget enforcement.
- Identical replay behavior.

## Observability Constraints

AI agents observe only via:
- immutable snapshots,
- subscription-based event streams,
- explicit sensors/processes (when data provides them).

No direct access to authoritative internals is permitted.

## Determinism & Replay

AI decisions are deterministic given:
- snapshot inputs,
- intent history,
- named RNG streams.

RNG stream naming:
- `noise.stream.ai.<agent_id>.<purpose>`

Replays must reproduce AI behavior exactly.

## Ops & Compatibility

- All AI actions must emit compat_report metadata.
- Missing capabilities or budget exhaustion produces explicit refusals.
- Mixed semantics within a single authoritative domain are forbidden.

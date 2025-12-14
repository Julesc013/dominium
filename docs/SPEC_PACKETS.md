# SPEC_PACKETS — TLV-Versioned Packet Families

This spec defines the deterministic packet families used by SIM, replay, and
lockstep. It does not define platform transports; it defines stable content.

## Scope
Applies to:
- deterministic command streams (intents)
- deterministic state mutation streams (deltas)
- deterministic outputs (events/messages/observations)
- debug probes that MUST NOT affect simulation state

## Packet families (authoritative taxonomy)
Packet family names are semantic; actual encodings are TLV-versioned.

- **Intent**: external command input for tick `N` (from UI/tools/agents).
- **Action**: validated internal command representation (optional encoding).
- **Delta**: authoritative mutation record applied at commit points.
- **Event**: discrete fact about something that occurred this tick (derived).
- **Message**: directed/broadcast communication (derived, deterministic routing).
- **Field**: field update/sample framing (derived; fixed-point only).
- **Observation**: sampled outputs for observers/agents (derived).
- **Probe**: debug/query packet; MUST be read-only (no state mutation).

## TLV versioning rules
All packets are encoded as TLV records:
- `type` (u32): identifies family and schema
- `version` (u16): schema version for the type
- `length` (u32): payload byte length

Rules:
- Types are globally reserved by family ranges; introducing new types requires a
  registry update.
- Changing payload shape requires incrementing `version`.
- Unknown types MUST be skippable by length.
- Unknown versions MUST either be rejected explicitly or upgraded explicitly;
  silent reinterpretation is forbidden.

## Stable ID requirements
Packets that reference world objects MUST use stable numeric IDs:
- domain ids, entity ids, frame ids, graph node ids, etc.
- IDs MUST NOT be pointer-derived and MUST have a total order.

Within packet payloads:
- repeated elements MUST be emitted in canonical order (sorted by stable key)
- tie-breaking MUST be stable and explicit (see `docs/SPEC_DETERMINISM.md`)

For packet batches/streams:
- canonical ordering is `(tick, stream_id, family, primary_key..., seq)`

## Determinism guarantees
- Packet parsing and serialization MUST be platform-independent.
- Packets MUST NOT contain floats or platform-dependent representations.
- Packet order MUST be explicit; no implicit reliance on container iteration.

## Forbidden behaviors
- Encoding raw memory blobs that include padding/pointers.
- UI-driven mutation: UI/tools MUST emit intents only; they MUST NOT write
  directly to engine state.
- Platform-dependent fields (paths, timestamps, locale-dependent strings).

## Source of truth vs derived cache
**Source of truth:**
- intent streams (player/tool/agent commands)
- delta streams (authoritative state mutations)
- schema/version identifiers for packet interpretation

**Derived cache:**
- events/messages/observations (must be reproducible from state + deltas)
- debug probe outputs

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_SIM_SCHEDULER.md`
- `docs/SPEC_FIELDS_EVENTS.md`
- `docs/SPEC_VM.md`


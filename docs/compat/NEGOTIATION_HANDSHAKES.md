Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `docs/compat/ENDPOINT_DESCRIPTORS.md`, `schema/compat/negotiation_record.schema`, `schema/compat/handshake_message.schema`, and `schema/compat/compat_refusal.schema`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Negotiation Handshakes

## Purpose
- Define the deterministic handshake contract used by endpoint negotiation.
- Make negotiation mandatory for client/server and attach-console style connections.
- Ensure handshake outcomes are logged, replayable, and refusal-safe.

## Connection Rule
- Connections must not become authoritative or attach-capable before a completed negotiation result exists.
- Missing negotiation yields `refusal.connection.no_negotiation`.
- A replay or attach surface that cannot reproduce the same negotiation record yields `refusal.connection.negotiation_mismatch`.

## Client to Server Message Flow
1. `client_hello`
   - client endpoint descriptor hash
   - client endpoint descriptor payload or deterministic inline equivalent
   - read-only allowance bit when the client is willing to accept observation-only fallback
2. `server_hello`
   - server endpoint descriptor hash
   - server endpoint descriptor payload or deterministic inline equivalent
3. `negotiation_result`
   - deterministic `NegotiationRecord`
   - enabled capability subset
   - degrade-plan rows
   - compat refusal payload if the negotiation result is refusal
4. `client_ack`
   - client accepts the chosen mode, or refuses the degraded mode
5. `session_begin`
   - pack lock hash
   - chosen contract bundle hash
   - chosen compatibility mode
   - connection-scoped law override if read-only compatibility was negotiated

## IPC Attach Flow
- Tool and target product use the same handshake-message and negotiation-record surfaces.
- The only difference is role naming; the deterministic algorithm is unchanged.
- Attach refusal remains explicit and logs the same refusal payload surface.

## Deterministic Behavior
- Endpoint descriptors are compared in stable sort order.
- Highest common protocol version is selected by numeric compare, then `protocol_id`.
- Contract versions are chosen by exact match if available, otherwise highest common version.
- Unknown capabilities are ignored deterministically after registry filtering.
- NegotiationRecord and handshake messages must serialize in canonical sorted-key order.

## Compatibility Modes
- `compat.full`
- `compat.degraded`
- `compat.read_only`
- `compat.refuse`

`compat.read_only`:
- is lawful only when contract mismatch still permits observation-only interoperability
- binds connection law to `law.observer.default`
- forbids authoritative mutation for that connection
- must be logged as a negotiated exception from the default server mode

## Enforcement
- Loopback and future IPC attach surfaces must call the shared handshake engine.
- Degrade decisions must be explicit in the `NegotiationRecord`.
- Silent downgrade is forbidden.
- Refusal payloads must be deterministic and replayable.

## Proof and Replay
- Proof bundles include:
  - `negotiation_record_hash`
  - endpoint descriptor hashes
  - chosen contract bundle hash
- Replay recomputes negotiation from the recorded descriptors and chosen contract bundle hash.
- Mismatch refuses with `refusal.connection.negotiation_mismatch`.

## MVP Loopback Note
- The MVP loopback transport may batch `server_hello`, `negotiation_result`, and `session_begin` into a bounded deterministic exchange for the local transport.
- Batching does not remove any required handshake artifact; all message surfaces remain present in the logged transcript.

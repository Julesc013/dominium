Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/APPSHELL_CONSTITUTION.md`, `docs/appshell/COMMANDS_AND_REFUSALS.md`, `docs/appshell/LOGGING_AND_TRACING.md`, `docs/appshell/TUI_FRAMEWORK.md`, `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, and `docs/compat/NEGOTIATION_HANDSHAKES.md`.

# IPC Attach Consoles

## Purpose

APPSHELL-4 defines the local IPC attach/detach console contract for all
Dominium products.

It provides:

- deterministic local endpoint discovery
- negotiated console/status/log attach sessions
- multiplexed TUI console tabs for attached endpoints
- explicit read-only fallback and refusal behavior

## IPC Endpoint

Each product may expose a local endpoint when launched with `--ipc on`.

The endpoint is identified by:

- `endpoint_id`
- `product_id`
- `session_id`
- deterministic local address

Endpoint address derivation is deterministic from:

- `product_id`
- `session_id`

Transport policy:

- Unix domain sockets on Linux/macOS where available
- localhost loopback sockets on Windows fallback

No remote TCP transport is part of APPSHELL-4.

## Discovery

Discovery uses a deterministic manifest:

- `dist/runtime/ipc_endpoints.json`

Manifest ordering is stable:

1. sort by `endpoint_id`
2. tie-break by `product_id`
3. tie-break by `session_id`

Discovery is local-only and offline.

## Endpoint Channels

Each endpoint exposes these logical channels:

- `negotiation`
- `log`
- `console`
- `status`

Framing is deterministic:

- each channel has a monotonic `seq_no`
- buffers are bounded
- channel payloads are canonically serialized

## Attach Flow

Attach flow:

1. connector discovers candidate endpoints
2. connector exchanges CAP-NEG descriptors
3. connector and endpoint run the CAP-NEG-2 handshake
4. endpoint returns a `NegotiationRecord`
5. connector accepts or refuses the negotiated mode
6. endpoint opens console/status/log access for the session

Connections must not succeed without negotiation.

## Security And Authority

Default security posture:

- local machine only
- no shell escape to the operating system
- command execution restricted to AppShell command surfaces
- read-only attach is allowed when negotiated or policy requires

Authority rules:

- attach privileges are policy-bound
- negotiated `compat.read_only` must prevent mutation-capable console actions
- attach must not escalate privileges above the local product/session policy

## Multiplexed TUI Sessions

Attached endpoints are modeled as logical console sessions:

- one endpoint attach equals one logical session tab
- tab ordering is deterministic by `session_id`
- logs panel may subscribe to the active remote session log stream

Detach removes only the logical attachment state. It does not mutate the remote
product truth state.

## Determinism Rules

- handshake ordering is fixed
- discovery ordering is fixed
- frame serialization sorts keys deterministically
- sequence numbers increase monotonically per channel
- retries use bounded iteration counts, never wall-clock sleeps

## Refusals

APPSHELL-4 adds structured refusal behavior for:

- `refusal.connection.no_negotiation`
- `refusal.connection.negotiation_mismatch`
- `refusal.client.unauthorized`
- `refusal.law.attach_denied`
- `refusal.debug.feature_disabled`

Refusals must include remediation hints and stable exit-code mapping through the
AppShell command layer.

## Non-Goals

APPSHELL-4 does not:

- add remote networking beyond localhost
- add OS-native widgets
- bypass AuthorityContext or LawProfile rules
- use wall-clock timing for attach flow or frame sequencing

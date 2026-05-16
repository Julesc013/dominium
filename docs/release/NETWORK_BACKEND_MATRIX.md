Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Network Backend Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Backend Rows

| Backend | Status | Tier | Notes |
| --- | --- | --- | --- |
| loopback | provisional | T0 | Client/server loopback surfaces exist. |
| tcp | planned | T1 | Baseline network transport lane. |
| udp | planned | T2 | Datagram transport lane. |
| reliable_udp | research | T4 | Future reliable-datagram research. |
| relay_federation | research | T5 | Future relay/federation lane. |
| quic_webtransport | research | T5 | Mobile/web/exotic research lane. |

## Rules

Network transport is not authority semantics.

Server authority, replay, verification, compatibility, and refusal semantics remain separate contracts.

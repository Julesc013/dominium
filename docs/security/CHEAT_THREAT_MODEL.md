Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Cheat Threat Model

## Threat Classes
- `wallhack_esp`: reveal hidden entities by unauthorized client state.
- `replay_wallhack`: infer hidden truth from replay payloads.
- `packet_sniffing`: reconstruct hidden truth from network traffic.
- `client_forgery`: emit unauthorized commands or fabricated state.
- `memory_scraping`: read unauthorized data from local process memory.

## Primary Countermeasure
- Hidden truth is not sent to normal clients.
- Normal replay streams contain observation artifacts, not hidden truth.

## SRZ-0 Alignment
- Server-side authority verifies ProcessLogs and HashChains.
- Refusal semantics remain explicit and deterministic.

## Tooling Truth Access
- Truth access is entitlement-only.
- Tool truth outputs are watermarked.
- Tool truth accesses are audit logged.

## Residual Risks and Mitigations
- Out-of-band human communication cannot be fully prevented.
- Mitigation is uncertainty preservation:
  - observation limits
  - staleness
  - provenance/confidence surfaces


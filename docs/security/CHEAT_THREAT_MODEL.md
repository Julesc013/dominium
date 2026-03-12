Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Cheat Threat Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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

Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Cheating And Verification

## Threat Model
- Primary threat classes:
  - wallhack/ESP via hidden truth exposure
  - replay wallhack from over-disclosed replay payloads
  - packet sniffing of unauthorized payloads
  - client command/state forgery
  - local memory scraping

## Countermeasures
- Hidden truth is excluded from normal client payloads.
- Replay streams for normal play contain observation artifacts only.
- Tool-truth paths require explicit entitlement, watermarking, and audit logging.

## Provenance Verification
- Verification references server-side ProcessLogs and HashChains.
- SRZ verification remains authoritative; client artifacts are non-authoritative.
- Audit logs include capability/entitlement context for privileged disclosure paths.

## Replay Safety
- Observation-only replay is default.
- Tool-truth replay requires explicit entitlement and watermark.
- Refusal is mandatory when replay mode requests exceed entitlement.

## Residual Risk Handling
- Out-of-band human communication cannot be eliminated.
- Mitigation is bounded by epistemic uncertainty, provenance quality, and disclosure controls.

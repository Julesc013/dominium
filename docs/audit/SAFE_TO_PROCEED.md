Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Safe To Proceed Conditions (CA-0)

Continued development is safe only under the following conditions.

## Mandatory Conditions
- Keep `RepoX` and full `TestX` gates mandatory on every integration change.
- Do not treat stage/progression tokens as runtime law; capability/entitlement remains canonical.
- Preserve explicit refusal behavior for capability mismatch and entitlement failure paths.
- Keep strict build standards (`C89` engine, `C++98` game) and deterministic test gates active.

## Required Before High-Trust Claims
- Resolve doc contradiction between capability-only canon and stage-based derived runtime docs.
- Align declared capability registry with actual runtime checks for camera/tooling surfaces.
- Replace token-only anti-cheat checks with semantic checks over command and data flow.
- Expand process-only mutation enforcement beyond token scanning to stronger structural checks.
- Prove runtime solver/conformance consumption or downgrade docs to explicitly structural-only claims.

## Operational Guidance
- Continue small-scope maintenance, bug fixes, and enforcement hardening.
- Defer major new capability additions until red flags are resolved.
- Treat cheat resistance and process enforcement as partially trusted until semantic checks are strengthened.

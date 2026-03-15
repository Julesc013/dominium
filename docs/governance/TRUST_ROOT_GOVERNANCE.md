Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: GOVERNANCE/TRUST
Replacement Target: signed trust-root bundle publication and rotation policy

# Trust Root Governance

## Publication

- Official trust roots are published as deterministic offline bundles and registries.
- Release indices may reference official signer ids, but trust verification remains offline-first.
- Mock releases may remain unsigned under `trust.default_mock`; hashes remain mandatory.

## Rotation And Revocation

- Trust root rotation is versioned by registry hash.
- Revocation lists are optional and offline-first.
- Rotation or revocation must publish migration notes and a replacement registry hash.

## Third-Party Roots

- Setup may import third-party trust roots through deterministic offline bundles.
- Third-party ecosystems must use their own signer ids and must not impersonate official roots.
- Strict servers must declare allowed signer ids explicitly.

## Server Policy

- Ranked or strict servers must declare the trust policy and permitted signer ids.
- Trust policy does not bypass pack compatibility or negotiation.
- Unsigned artifacts remain policy-governed rather than silently accepted.

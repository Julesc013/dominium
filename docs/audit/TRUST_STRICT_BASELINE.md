Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen strict trust baseline and offline commercialization hook for v0.0.0-mock distribution gating.

# Trust Strict Baseline

- result: `complete`
- deterministic_fingerprint: `95e373bfe1439bdbe74df555ec8b66472cfdb2577b279f1eae456b77787f4000`

## Policy Summary

- mod_policy.lab -> `trust.default_mock`
- mod_policy.strict -> `trust.strict_ranked`
- mod_policy.anarchy -> `trust.anarchy`

## Fixture Outcomes

- `default_mock_accepts_unsigned_release_index` -> result=`complete` refusal=`-`
- `strict_ranked_refuses_unsigned_release_index` -> result=`complete` refusal=`refusal.trust.signature_missing`
- `strict_ranked_refuses_unsigned_official_pack` -> result=`complete` refusal=`refusal.trust.signature_missing`
- `strict_ranked_accepts_signed_artifacts` -> result=`complete` refusal=`-`
- `license_capability_requires_trusted_signature` -> result=`complete` refusal=`refusal.trust.signature_missing`
- `license_capability_availability_display` -> result=`complete` refusal=`-`

## Commercialization Hook

- artifact kind: `artifact.license_capability`
- schema id: `dominium.schema.security.license_capability_artifact`
- capability namespace: `cap.premium.*`
- runtime effect scope: `capability_availability_only`

## Readiness

- Ready for Ω-8 archive offline verification once RepoX, AuditX, TestX, and strict build remain green.

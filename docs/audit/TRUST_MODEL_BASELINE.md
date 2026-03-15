Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: TRUST/UPDATE-MODEL
Replacement Target: release-index governed trust-root bundles and signed acquisition policy

# Trust Model Baseline

## Policies

- Declared policies: trust.anarchy, trust.default_mock, trust.strict_ranked
- Server default trust policy: `trust.default_mock`
- Mock-channel default behavior: hashes mandatory, signatures optional with warnings.
- Strict ranked behavior: signatures required for governed release and pack artifacts.
- Anarchy behavior: unsigned artifacts allowed, but hashes remain mandatory.

## Default Behavior For Mock Channel

- Missing hash: refused with `refusal.trust.hash_missing`.
- Unsigned governed artifact under default policy: complete with `warn.trust.signature_missing`.
- Unsigned governed artifact under strict policy: refused with `refusal.trust.signature_missing`.
- Invalid signature: refused with `refusal.trust.signature_invalid`.

## Integration Points

- `setup verify` and pack verification route through `src/security/trust/trust_verifier.py`.
- `setup update` passes the resolved trust policy into `src/release/update_resolver.py`.
- `tool_verify_release_manifest` and DIST-2 verification use trust-aware manifest verification.
- Server policy binding is declared in `data/registries/server_config_registry.json`.

## Canonical Verification Cases

- `anarchy_unsigned`: result=`complete` refusal=`-`
- `default_unsigned`: result=`warn` refusal=`-`
- `hash_missing`: result=`refused` refusal=`refusal.trust.hash_missing`
- `invalid_signature`: result=`refused` refusal=`refusal.trust.signature_invalid`
- `strict_signed`: result=`complete` refusal=`-`
- `strict_unsigned`: result=`refused` refusal=`refusal.trust.signature_missing`

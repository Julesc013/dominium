Status: CANONICAL
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: TRUST
Replacement Target: signed release and pack trust constitution after trust roots, revocation, and remote acquisition are release-pinned

# Trust And Signing Model

## Purpose

TRUST-MODEL-0 defines the offline-first trust policy for releases, packs, and updates.
Hashes are always mandatory.
Signatures are policy-controlled and additive.

## Trust Objects

- trust roots are signer public keys stored in versioned trust-root registries
- signed artifacts may include:
  - `release_index.json`
  - `release_manifest.json`
  - `pack.compat.json`
  - pack contents
- trust policies select whether missing or untrusted signatures are refused or only warned

## Trust Policies

- `trust.strict_ranked`
  - signatures required for governed release and pack artifacts
  - untrusted signer roots refuse
- `trust.default_mock`
  - hashes required
  - unsigned artifacts warn for mock and beta-style offline flows
- `trust.anarchy`
  - hashes required
  - unsigned artifacts accepted without warning escalation

## Offline-First Policy

- content hashes are always verified and never optional
- signatures are verified locally against installed trust roots only
- missing network access never blocks hash verification
- if no local release index is present, update resolution refuses with remediation

## Trust Levels Mapping

Dominium maps trust policy to mod-policy trust levels through these ids:

- `trust.official_signed`
- `trust.thirdparty_signed`
- `trust.unsigned`
- `trust.local_dev`

For MVP packs, signed-pack enforcement uses a bridge:
`pack.trust.json` levels `trust.official_signed` and `trust.thirdparty_signed` satisfy signed-pack policy even before detached pack signatures become first-class governed artifacts.

## Revocation / Rotation

- trust root lists are versioned by content hash
- revocation bundles are optional and offline
- Setup may import additional trust-root bundles into the local install manifest surface

## Refusals

- `refusal.trust.hash_missing`
- `refusal.trust.signature_missing`
- `refusal.trust.signature_invalid`
- `refusal.trust.root_not_trusted`
- `refusal.trust.policy_missing`

## Integration Points

- `setup verify`
- pack verification through the AppShell pack verifier adapter
- update resolution and release-index verification
- distribution verification
- server trust policy bindings through server config and mod policy

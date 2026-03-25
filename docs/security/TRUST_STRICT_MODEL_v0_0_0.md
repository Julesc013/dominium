Status: CANONICAL
Last Reviewed: 2026-03-25
Supersedes: none
Superseded By: none
Stability: stable
Future Series: GOVERNANCE/COMMERCIAL
Replacement Target: full licensing system if commercialization is later productized

# Trust Strict Model v0.0.0

## Trust Modes

### `trust.default_mock`

- hashes mandatory
- signatures optional for governed release and pack artifacts
- missing signatures emit warning keys rather than refusal

### `trust.strict_ranked`

- signatures required for:
  - `artifact.release_index`
  - `artifact.release_manifest`
  - official packs and pack compatibility artifacts
- unsigned or untrusted artifacts refuse

### `trust.anarchy`

- hashes mandatory
- signatures optional everywhere

## Deterministic Trust Decisions

- Same artifact bytes plus same trust policy produces the same decision.
- Trust decisions are logged with:
  - refusal code or warning key
  - remediation hint
- No network access is required or consulted.
- No silent fallback from strict to default or anarchy is allowed.

## Commercialization Hook

The prompt-level commercialization hook is mapped onto the frozen governance namespace `GOVERNANCE/COMMERCIAL` so it remains inside the convergence allowlist without changing trust semantics.

### New Artifact Kind

- `artifact.license_capability`

### Artifact Properties

- content-addressed
- offline-verifiable
- signed by official trust root
- declares enabled capabilities in `cap.premium.*`

### Enforcement Rule

- License capability artifacts are only accepted when signature verification succeeds under trusted official roots.
- Acceptance only affects capability availability surfaces.
- No payment logic is implemented.
- No online account binding is implemented.
- No runtime simulation behavior changes.

### Availability Scope

- Setup and runtime may verify the artifact offline.
- Verified artifacts may expose `cap.premium.*` in negotiation or degrade-display surfaces.
- Unverified or missing artifacts leave premium capabilities unavailable and visibly degraded.

## Stability

- `trust_strict_version = 0`
- `stability_class = stable`
